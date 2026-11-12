"""Čítanie RSS a Atom kanálov a výber správ z daného dňa."""

from __future__ import annotations

import calendar
import html as html_lib
import logging
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import feedparser
import httpx
from bs4 import BeautifulSoup

from .modely import USER_AGENT, Obrazok, Sprava, Zdroj

log = logging.getLogger(__name__)

BRATISLAVA = ZoneInfo("Europe/Bratislava")


def okno_dna(den: date) -> tuple[datetime, datetime]:
    """Začiatok a koniec kalendárneho dňa v slovenskom čase."""
    zaciatok = datetime.combine(den, time.min, tzinfo=BRATISLAVA)
    return zaciatok, zaciatok + timedelta(days=1)


def vcera(teraz: datetime | None = None) -> date:
    teraz = teraz or datetime.now(BRATISLAVA)
    return teraz.astimezone(BRATISLAVA).date() - timedelta(days=1)


def _cas(polozka) -> datetime | None:
    for kluc in ("published_parsed", "updated_parsed"):
        t = polozka.get(kluc)
        if t:
            return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc)
    return None


def html_na_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for znacka in soup(["script", "style", "figure", "figcaption", "iframe"]):
        znacka.decompose()
    odseky = [p.get_text(" ", strip=True) for p in soup.find_all(["p", "li", "h2", "h3", "blockquote"])]
    odseky = [o for o in odseky if o]
    return "\n\n".join(odseky) if odseky else soup.get_text(" ", strip=True)


def _obrazky_z_polozky(polozka, obsah_html: str) -> list[Obrazok]:
    najdene: list[Obrazok] = []

    for m in polozka.get("media_content", []) or []:
        url = m.get("url")
        if url and (m.get("medium") in (None, "image") or str(m.get("type", "")).startswith("image")):
            najdene.append(Obrazok(url=url, povod="rss"))
    for m in polozka.get("media_thumbnail", []) or []:
        if m.get("url"):
            najdene.append(Obrazok(url=m["url"], povod="rss"))
    for odkaz in polozka.get("links", []) or []:
        if odkaz.get("rel") == "enclosure" and str(odkaz.get("type", "")).startswith("image"):
            najdene.append(Obrazok(url=odkaz["href"], povod="rss"))

    kredit = ""
    kredity = polozka.get("media_credit")
    if kredity:
        kredit = kredity[0].get("content", "") if isinstance(kredity, list) else str(kredity)
    popis = polozka.get("media_description", "") or ""
    for o in najdene:
        o.kredit = o.kredit or kredit
        o.popisok = o.popisok or popis

    if obsah_html:
        najdene.extend(obrazky_z_html(obsah_html, povod="rss"))
    return _bez_duplicit(najdene)


def _je_trieda_kreditu(trieda: str | None) -> bool:
    return bool(trieda) and any(k in trieda.lower() for k in ("credit", "source", "copyright", "byline"))


def obrazky_z_html(html: str, povod: str) -> list[Obrazok]:
    """Obrázky vo figure s popiskom a kreditom, potom ostatné img."""
    soup = BeautifulSoup(html, "lxml")
    vysledok: list[Obrazok] = []
    spracovane = set()

    for fig in soup.find_all("figure"):
        img = fig.find("img")
        if not img:
            continue
        url = img.get("src") or img.get("data-src") or ""
        if not url.startswith("http"):
            continue
        spracovane.add(id(img))
        cap = fig.find("figcaption")
        popisok, kredit = "", ""
        if cap:
            kredit_el = cap.find(class_=_je_trieda_kreditu) or cap.find("cite")
            if kredit_el:
                kredit = kredit_el.get_text(" ", strip=True)
                kredit_el.extract()
            popisok = cap.get_text(" ", strip=True)
        vysledok.append(Obrazok(url=url, alt=img.get("alt", "") or "", popisok=popisok, kredit=kredit, povod=povod))

    for img in soup.find_all("img"):
        if id(img) in spracovane:
            continue
        url = img.get("src") or img.get("data-src") or ""
        if not url.startswith("http"):
            continue
        try:
            if int(img.get("width", 9999)) < 200:
                continue
        except ValueError:
            pass
        vysledok.append(Obrazok(url=url, alt=img.get("alt", "") or "", povod=povod))
    return vysledok


def _bez_duplicit(obrazky: list[Obrazok]) -> list[Obrazok]:
    podla_kluca: dict[str, Obrazok] = {}
    for o in obrazky:
        k = o.kluc()
        if k not in podla_kluca:
            podla_kluca[k] = o
            continue
        # Zachovaj záznam s viac metadátami.
        stary = podla_kluca[k]
        for pole in ("alt", "popisok", "kredit", "licencia"):
            if not getattr(stary, pole) and getattr(o, pole):
                setattr(stary, pole, getattr(o, pole))
    for o in podla_kluca.values():
        for pole in ("alt", "popisok", "kredit"):
            # Kanály bývajú escapované dvakrát (&amp;#39;).
            setattr(o, pole, html_lib.unescape(html_lib.unescape(getattr(o, pole))).strip())
    return list(podla_kluca.values())


def spravy_z_kanala(zdroj: Zdroj, surovy: bytes | str, den: date | None = None) -> list[Sprava]:
    """Rozparsuje kanál. Ak je daný deň, vráti len správy publikované v ten deň."""
    kanal = feedparser.parse(surovy)
    okno = okno_dna(den) if den else None
    spravy: list[Sprava] = []

    for p in kanal.entries:
        cas = _cas(p)
        url = p.get("link", "")
        titulok = BeautifulSoup(p.get("title", ""), "lxml").get_text(" ", strip=True)
        if not (cas and url and titulok):
            continue
        if okno and not (okno[0] <= cas < okno[1]):
            continue

        obsah_html = ""
        if p.get("content"):
            obsah_html = max((c.get("value", "") for c in p["content"]), key=len)
        zhrnutie_html = p.get("summary", "") or ""
        text = html_na_text(obsah_html)

        spravy.append(
            Sprava(
                zdroj=zdroj.id,
                zdroj_nazov=zdroj.name,
                titulok=titulok,
                url=url,
                publikovane=cas,
                zhrnutie=html_na_text(zhrnutie_html)[:1000],
                text=text,
                text_povod="rss" if text else "ziadny",
                obrazky=_obrazky_z_polozky(p, obsah_html or zhrnutie_html),
            )
        )
    return spravy


def stiahni_kanal(klient: httpx.Client, zdroj: Zdroj) -> bytes | None:
    try:
        r = klient.get(zdroj.feed, headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=30)
        r.raise_for_status()
        return r.content
    except httpx.HTTPError as e:
        log.warning("Kanál %s zlyhal: %s", zdroj.id, e)
        return None
