from datetime import date, datetime, timezone

import numpy as np

from bitoviny.zber.modely import Sprava, Zdroj, nacitaj_zdroje
from bitoviny.zber.rss import okno_dna, spravy_z_kanala, vcera
from bitoviny.zber.stranka import obrazky_zo_stranky
from bitoviny.zber.zoskupenie import pridaj_signal, vyber, zoskup

ZDROJ = Zdroj(id="test", name="Test", feed="https://example.com/feed", role="source", fetch_page=False)

KANAL = """<?xml version="1.0"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:media="http://search.yahoo.com/mrss/">
<channel><title>Test</title>
<item><title>Vcerajsia sprava</title><link>https://example.com/a</link>
  <pubDate>Wed, 11 Nov 2026 10:00:00 GMT</pubDate>
  <description>Kratke zhrnutie.</description>
  <content:encoded><![CDATA[<p>Prvy odsek.</p><figure><img src="https://example.com/a.jpg" alt="Cip"/>
    <figcaption>Novy cip na stole. <span class="credit">Foto: Jana Novakova / Getty Images</span></figcaption></figure>
    <p>Druhy odsek.</p>]]></content:encoded>
  <media:content url="https://example.com/a.jpg" medium="image"/>
</item>
<item><title>Tesne pred polnocou</title><link>https://example.com/b</link>
  <pubDate>Tue, 10 Nov 2026 22:30:00 GMT</pubDate><description>x</description></item>
<item><title>Tesne po polnoci dalsieho dna</title><link>https://example.com/c</link>
  <pubDate>Wed, 11 Nov 2026 23:30:00 GMT</pubDate><description>x</description></item>
<item><title>Bez datumu</title><link>https://example.com/d</link></item>
</channel></rss>"""


def test_zdroje_sa_nacitaju():
    zdroje = nacitaj_zdroje()
    assert len(zdroje) >= 10
    assert sum(z.role == "signal" for z in zdroje) == 1
    assert all(z.feed.startswith("https://") for z in zdroje)


def test_okno_dna_je_v_slovenskom_case():
    zaciatok, koniec = okno_dna(date(2026, 11, 11))
    # V novembri je Bratislava UTC+1.
    assert zaciatok.astimezone(timezone.utc) == datetime(2026, 11, 10, 23, 0, tzinfo=timezone.utc)
    assert (koniec - zaciatok).total_seconds() == 86400


def test_vcera():
    teraz = datetime(2026, 11, 12, 0, 30, tzinfo=timezone.utc)  # 01:30 v Bratislave
    assert vcera(teraz) == date(2026, 11, 11)


def test_filter_dna_a_obsah():
    spravy = spravy_z_kanala(ZDROJ, KANAL, date(2026, 11, 11))
    # 22:30 GMT 10. 11. je 23:30 v Bratislave, teda ešte 10. 11.
    # 23:30 GMT 11. 11. je 00:30 v Bratislave, teda už 12. 11.
    assert [s.url for s in spravy] == ["https://example.com/a"]
    s = spravy[0]
    assert "Prvy odsek." in s.text and "Druhy odsek." in s.text
    assert "Novy cip" not in s.text  # popisok obrázka nepatrí do textu
    assert s.text_povod == "rss"


def test_obrazok_z_rss_ma_popisok_a_kredit():
    s = spravy_z_kanala(ZDROJ, KANAL, date(2026, 11, 11))[0]
    assert len(s.obrazky) == 1  # media:content a figure sú ten istý obrázok
    o = s.obrazky[0]
    assert o.alt == "Cip"
    assert o.popisok.startswith("Novy cip na stole")
    assert "Getty Images" in o.kredit


def test_obrazky_zo_stranky():
    html = """<html><head>
      <meta property="og:image" content="/img/hero.jpg"/>
      <script type="application/ld+json">{"@type":"NewsArticle","image":{"@type":"ImageObject",
        "url":"https://example.com/img/hero.jpg","creditText":"Reuters","license":"https://example.com/lic"}}</script>
      </head><body><article><p>Text.</p>
      <figure><img src="https://example.com/img/2.jpg" alt="Graf"/><figcaption>Graf predaja <cite>Zdroj: IDC</cite></figcaption></figure>
      <img src="https://example.com/img/reklama.jpg" alt="bez popisku"/>
      </article></body></html>"""
    obrazky = obrazky_zo_stranky(html, "https://example.com/clanok")
    podla_url = {o.url: o for o in obrazky}
    assert podla_url["https://example.com/img/hero.jpg"].kredit == "Reuters"
    assert podla_url["https://example.com/img/hero.jpg"].licencia == "https://example.com/lic"
    assert podla_url["https://example.com/img/2.jpg"].kredit == "Zdroj: IDC"
    assert "https://example.com/img/reklama.jpg" not in podla_url  # bez popisku aj kreditu


def _sprava(zdroj: str, titulok: str, text: str = "") -> Sprava:
    return Sprava(zdroj=zdroj, zdroj_nazov=zdroj, titulok=titulok, url=f"https://{zdroj}/{titulok}",
                  publikovane=datetime(2026, 11, 11, 12, tzinfo=timezone.utc), text=text)


def _falosny_embedder(mapa: dict[str, list[float]]):
    def embed(texty):
        return np.array([next(v for k, v in mapa.items() if k in t) for t in texty], dtype=np.float32)
    return embed


def test_zoskupenie_a_vyber():
    embed = _falosny_embedder({"cip": [1, 0, 0], "utok": [0, 1, 0], "mobil": [0, 0, 1]})
    spravy = [
        _sprava("a", "novy cip A", "x" * 900),
        _sprava("b", "novy cip B"),
        _sprava("c", "novy cip C"),
        _sprava("a", "utok na banku"),
        _sprava("b", "utok hackerov"),
        _sprava("a", "mobil roka"),
    ]
    temy = zoskup(spravy, embed)
    assert sorted(len(t.spravy) for t in temy) == [1, 2, 3]

    pridaj_signal(temy, [_sprava("hn", "utok")], embed)
    vybrane = vyber(temy, pocet=2)
    assert [len(t.zdroje) for t in vybrane] == [3, 2]
    assert vybrane[1].signal == 1
    # Jednozdrojová téma sa dostane do výberu až po viaczdrojových.
    assert len(vyber(temy, pocet=3)[2].zdroje) == 1


def test_uplne_spajanie_nereťazi():
    # B je podobné A aj C, ale A a C spolu nesúvisia: nesmú skončiť v jednej téme.
    embed = _falosny_embedder({"A": [1, 0], "B": [0.8, 0.6], "C": [0.28, 0.96]})
    temy = zoskup([_sprava("a", "A"), _sprava("b", "B"), _sprava("c", "C")], embed, prah=0.74)
    assert max(len(t.spravy) for t in temy) == 2


def test_logo_vydavatela_sa_nepocita_a_kredit_sa_odescapuje():
    html = """<html><head><script type="application/ld+json">{"@type":"NewsArticle",
      "publisher":{"@type":"Organization","logo":{"@type":"ImageObject","url":"https://example.com/logo.png"}},
      "image":{"@type":"ImageObject","url":"https://example.com/foto.jpg","creditText":"Tom&amp;#39;s Hardware"}}</script>
      </head><body><article><p>Text.</p></article></body></html>"""
    obrazky = obrazky_zo_stranky(html, "https://example.com/clanok")
    assert [o.url for o in obrazky] == ["https://example.com/foto.jpg"]
    assert obrazky[0].kredit == "Tom's Hardware"
