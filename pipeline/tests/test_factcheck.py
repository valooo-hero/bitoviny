from langchain_core.runnables import RunnableLambda

from bitoviny.redakcia.factcheck import (
    Factcheck,
    Tvrdenie,
    cisla,
    cisla_bez_opory,
    dokaz_je_v_zdroji,
    treba_opravit,
    zostav_nalezy,
)
from bitoviny.redakcia.graf import MAX_OPRAV, sprava_opravy, zostav_graf
from bitoviny.redakcia.korektura import Korektura
from bitoviny.redakcia.modely import Koncept
from bitoviny.redakcia.obrazky import Dopyty

ZDROJ = (
    "AMD says servers kept 95% of performance with half the DRAM. MEXT runs on 145 servers today, "
    "with plans to expand to 2,000 servers in 2027. Flash is about 1.5 times cheaper, “Five minutes "
    "is an eternity for Epyc,” Smerdon said."
)


# Uzly za factcheckom nahradíme falošnými, aby testy nevolali modely ani fotobanky.
BEZ_SIETE = dict(
    model_korektury=RunnableLambda(lambda _: Korektura(upravy=[])),
    model_fotoeditora=RunnableLambda(lambda _: Dopyty(dopyty=["server"])),
    hladac_obrazkov=lambda dopyty: [],
    jazykova_sluzba=None,
)


def _tema() -> dict:
    return {
        "titulok": "AMD MEXT",
        "pocet_zdrojov": 2,
        "signal_hn": 0,
        "spravy": [
            {"zdroj": "a", "zdroj_nazov": "Zdroj A", "titulok": "AMD MEXT", "url": "https://a.example/1",
             "publikovane": "2026-11-11T10:00:00+00:00", "zhrnutie": "", "text": ZDROJ, "obrazky": []},
            {"zdroj": "b", "zdroj_nazov": "Zdroj B", "titulok": "AMD memory", "url": "https://b.example/1",
             "publikovane": "2026-11-11T11:00:00+00:00", "zhrnutie": "", "text": "AMD acquired MEXT in June.", "obrazky": []},
        ],
    }


def _koncept(telo: str) -> Koncept:
    return Koncept(
        titulok="AMD udrží 95 % výkonu s polovicou pamäte",
        perex="Technológia MEXT beží na 145 serveroch a firma ju chce rozšíriť na 2 000 serverov v roku 2027.",
        sekcia="hardver",
        tagy=["AMD"],
        telo=telo,
        pouzite_zdroje=["https://a.example/1", "https://b.example/1"],
        prompt_ilustracie="A memory chip.",
        poznamky_pre_editora="",
    )


def _tvrdenie(text: str, verdikt: str = "potvrdene", dokaz: str = "", **kw) -> Tvrdenie:
    return Tvrdenie(text=text, typ="cislo", verdikt=verdikt, zdroj="Zdroj A", dokaz=dokaz, **kw)


def test_cisla_sa_normalizuju_podla_jazyka():
    assert cisla("2,000 servers, 1.5 times, 95%", "en") == {"2000", "1.5", "95"}
    assert cisla("2 000 serverov, 1,5-krát, 95 %", "sk") == {"2000", "1.5", "95"}
    assert cisla("2 000 a 10,50 eur", "sk") == {"2000", "10.5"}


def test_cisla_bez_opory_najdu_len_vymyslene():
    dobry = _koncept("Flash je asi 1,5-krát lacnejší. " + "slovo " * 400)
    assert cisla_bez_opory(dobry, [ZDROJ]) == []
    zly = _koncept("Server udrží 85 % výkonu na 450 serveroch. Má 3 fázy. " + "slovo " * 400)
    # 85 a 450 v zdroji nie sú; jednociferná 3 sa zámerne nehlási.
    assert cisla_bez_opory(zly, [ZDROJ]) == ["85", "450"]


def test_dokaz_musi_byt_v_zdroji_doslova():
    assert dokaz_je_v_zdroji("kept 95% of performance with half the DRAM", [ZDROJ])
    assert dokaz_je_v_zdroji("“Five minutes is an eternity for Epyc,”", [ZDROJ])  # iné úvodzovky nevadia
    assert dokaz_je_v_zdroji("MEXT runs on 145 servers ... expand to 2,000 servers", [ZDROJ])  # skrátenie
    assert not dokaz_je_v_zdroji("kept 99% of performance with half the DRAM", [ZDROJ])
    assert not dokaz_je_v_zdroji("AMD confirmed the technology is free for everyone", [ZDROJ])


def test_nalezy_spajaju_model_a_mechanicke_kontroly():
    k = _koncept("MEXT beží na 450 serveroch. Výkon je 85 %. " + "slovo " * 400)
    fc = Factcheck(
        tvrdenia=[
            _tvrdenie("MEXT beží na 450 serveroch", "v_rozpore", "MEXT runs on 145 servers today",
                      komentar="Zdroj uvádza 145.", navrh_opravy="MEXT beží na 145 serveroch."),
            _tvrdenie("AMD kúpilo MEXT v júni", "potvrdene", "AMD bought MEXT for a billion dollars"),
        ],
        celkove_hodnotenie="Jedna chyba.",
    )
    nalezy = zostav_nalezy(fc, k, [ZDROJ, "AMD acquired MEXT in June."])
    podla = {n.povod: n for n in nalezy}
    assert podla["factchecker"].zavaznost == "chyba" and "145" in podla["factchecker"].navrh_opravy
    # Vymyslený dôkaz pri „potvrdenom“ tvrdení ide editorovi ako upozornenie.
    assert podla["kontrola_dokazu"].zavaznost == "upozornenie"
    # 450 už namietol factchecker, mechanicky sa hlási len 85.
    assert [n.text for n in nalezy if n.povod == "kontrola_cisel"] == ["Číslo 85"]
    assert treba_opravit(nalezy)


def test_cisty_koncept_nema_nalezy():
    k = _koncept("Výkon ostáva na 95 %. " + "slovo " * 400)
    fc = Factcheck(tvrdenia=[_tvrdenie("95 % výkonu", dokaz="kept 95% of performance")], celkove_hodnotenie="V poriadku.")
    assert zostav_nalezy(fc, k, [ZDROJ]) == []


def _falosny_factchecker():
    """Namieta číslo 450, kým v koncepte je."""

    def fc(spravy):
        koncept = spravy[-1].content.split("<koncept>")[-1]
        if "450" in koncept:
            return Factcheck(
                tvrdenia=[_tvrdenie("MEXT beží na 450 serveroch", "v_rozpore", "MEXT runs on 145 servers today",
                                    komentar="Zdroj uvádza 145.", navrh_opravy="145 serveroch")],
                celkove_hodnotenie="Chyba v čísle.",
            )
        return Factcheck(tvrdenia=[_tvrdenie("MEXT beží na 145 serveroch", dokaz="MEXT runs on 145 servers today")],
                         celkove_hodnotenie="V poriadku.")

    return RunnableLambda(fc)


def test_slucka_opravi_chybu_a_skonci():
    volania = {"n": 0}

    def autorka(spravy):
        volania["n"] += 1
        # Prvé volanie je písanie, druhé oprava (v správe sú nálezy).
        if "<nalezy>" in spravy[-1].content:
            return _koncept("MEXT beží na 145 serveroch. " + "slovo " * 400)
        return _koncept("MEXT beží na 450 serveroch. " + "slovo " * 400)

    graf = zostav_graf(model_autorky=RunnableLambda(autorka), model_factchecku=_falosny_factchecker(), **BEZ_SIETE)
    v = graf.invoke({"tema": _tema()})
    assert volania["n"] == 2
    assert v["kolo"] == 2 and "145" in v["koncept"].telo
    assert [h["chyb"] for h in v["historia"]] == [1, 0]
    assert v["nalezy"] == []


def test_slucka_sa_zastavi_ked_autorka_chybu_neopravi():
    tvrdohlava = RunnableLambda(lambda _: _koncept("MEXT beží na 450 serveroch. " + "slovo " * 400))
    graf = zostav_graf(model_autorky=tvrdohlava, model_factchecku=_falosny_factchecker(), **BEZ_SIETE)
    v = graf.invoke({"tema": _tema()})
    # Jedno písanie, MAX_OPRAV opráv, po každej factcheck: nálezy ostanú pre editora.
    assert v["kolo"] == MAX_OPRAV + 1
    assert treba_opravit(v["nalezy"])


def test_sprava_opravy_obsahuje_len_chyby():
    k = _koncept("MEXT beží na 450 serveroch. " + "slovo " * 400)
    fc = Factcheck(
        tvrdenia=[
            _tvrdenie("MEXT beží na 450 serveroch", "v_rozpore", "MEXT runs on 145 servers today", navrh_opravy="145"),
            _tvrdenie("AMD kúpilo MEXT", "potvrdene", "vymyslený úryvok, ktorý v zdroji nie je"),
        ],
        celkove_hodnotenie="",
    )
    stav = {"tema": _tema(), "koncept": k, "nalezy": zostav_nalezy(fc, k, [ZDROJ, "AMD acquired MEXT in June."])}
    sprava = sprava_opravy(stav)
    assert "<nalezy>" in sprava and "450 serveroch" in sprava.split("<nalezy>")[1]
    assert "vymyslený úryvok" not in sprava  # upozornenie pre editora autorke nejde
