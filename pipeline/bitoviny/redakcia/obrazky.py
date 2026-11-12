"""Fotoeditor: posúdenie práv k obrázkom zo zdrojov a hľadanie voľných náhrad.

Zaradenie robia pravidlá, nie jazykový model: musí byť predvídateľné a dať sa
skontrolovať. Východisko je, že obrázok je chránený, kým sa nepreukáže opak.
Model sa používa len na vymyslenie hľadaných výrazov pre náhrady.
"""

from __future__ import annotations

import logging
import re
from typing import Literal

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ..zber.modely import USER_AGENT

log = logging.getLogger(__name__)

Zaradenie = Literal["volne", "tlacove", "chranene", "nejasne"]

AGENTURY = (
    "getty", "reuters", "associated press", "ap photo", "afp", "shutterstock", "bloomberg", "alamy",
    "istock", "nurphoto", "epa", "imago", "zuma", "sipa", "anadolu", "picture alliance", "tasr", "čtk", "profimedia",
)
VOLNE_LICENCIE = re.compile(
    r"creativecommons\.org|\bcc[ -]?(by|0|zero)\b|\bcc by(-sa)?\b|public domain|\bpdm\b|unsplash license|pexels license",
    re.IGNORECASE,
)
# Voľné licencie, ktoré nedovoľujú komerčné použitie alebo úpravy, za voľné nepovažujeme.
OBMEDZENE_CC = re.compile(r"\b(nc|nd)\b|by-nc|by-nd|noncommercial|noderivs", re.IGNORECASE)
PREDPONA_KREDITU = re.compile(r"^\W*(image credit|photo credit|credit|image|photo|foto|zdroj|source|courtesy of)\W*:?\s*", re.IGNORECASE)


class Dopyty(BaseModel):
    dopyty: list[str] = Field(description="Dva až tri anglické hľadané výrazy pre fotobanku, každý 1 až 3 slová")


class PosudenyObrazok(BaseModel):
    url: str
    zdroj_clanku: str
    alt: str = ""
    popisok: str = ""
    kredit: str = ""
    licencia: str = ""
    zaradenie: Zaradenie
    dovod: str


class Alternativa(BaseModel):
    url: str
    nahlad: str = ""
    nazov: str = ""
    autor: str = ""
    licencia: str
    licencia_url: str = ""
    stranka: str  # stránka s pôvodom a licenciou, editor ju má pred použitím otvoriť
    povod: Literal["wikimedia", "openverse"]
    dopyt: str = ""


def ocisti_kredit(kredit: str) -> str:
    return PREDPONA_KREDITU.sub("", kredit.strip().strip("()[]")).strip(" .()[]")


def zarad(obrazok: dict, firmy: set[str], vydavatel: str) -> tuple[Zaradenie, str]:
    """Pravidlá v poradí od najsilnejšieho signálu."""
    kredit = ocisti_kredit(obrazok.get("kredit", ""))
    vsetko = " ".join([obrazok.get("kredit", ""), obrazok.get("popisok", ""), obrazok.get("alt", "")]).lower()
    licencia = obrazok.get("licencia", "")

    for a in AGENTURY:
        if re.search(rf"\b{re.escape(a)}\b", vsetko):
            return "chranene", f"Fotografia agentúry alebo fotobanky ({a.title()})."
    if "©" in vsetko or "all rights reserved" in vsetko or "copyright" in vsetko:
        return "chranene", "Popisok alebo kredit obsahuje výhradu autorských práv."

    licencny_text = f"{licencia} {vsetko}"
    if VOLNE_LICENCIE.search(licencny_text):
        if OBMEDZENE_CC.search(licencny_text):
            return "chranene", "Licencia Creative Commons zakazuje komerčné použitie alebo úpravy."
        return "volne", f"Uvedená voľná licencia: {licencia or kredit or 'v popisku'}."
    if licencia:
        return "nejasne", f"Uvedená licencia, ktorú nevieme posúdiť: {licencia}."

    if not kredit:
        return "nejasne", "Bez kreditu a licencie. Predvolene sa považuje za chránené."
    if kredit.lower() in {f.lower() for f in firmy}:
        return "tlacove", f"Kredit uvádza firmu, o ktorej je článok ({kredit}): pravdepodobne tlačový materiál."
    if vydavatel and (kredit.lower() in vydavatel.lower() or vydavatel.lower() in kredit.lower()):
        return "chranene", f"Vlastný obrázok vydavateľa ({kredit})."
    return "chranene", f"Uvedený autor alebo zdroj bez voľnej licencie: {kredit}."


def posud_obrazky(tema: dict, firmy: set[str]) -> list[PosudenyObrazok]:
    vysledok, videne = [], set()
    for s in tema["spravy"]:
        for o in s.get("obrazky", []):
            kluc = o["url"].split("?")[0]
            if kluc in videne:
                continue
            videne.add(kluc)
            zaradenie, dovod = zarad(o, firmy, s["zdroj_nazov"])
            vysledok.append(
                PosudenyObrazok(
                    url=o["url"], zdroj_clanku=s["zdroj_nazov"], alt=o.get("alt", ""), popisok=o.get("popisok", ""),
                    kredit=o.get("kredit", ""), licencia=o.get("licencia", ""), zaradenie=zaradenie, dovod=dovod,
                )
            )
    poradie = {"volne": 0, "tlacove": 1, "nejasne": 2, "chranene": 3}
    return sorted(vysledok, key=lambda p: poradie[p.zaradenie])


# ---------- voľné náhrady ----------


def _text(html: str) -> str:
    return BeautifulSoup(html or "", "lxml").get_text(" ", strip=True)[:200]


def hladaj_wikimedia(klient: httpx.Client, dopyt: str, limit: int = 4) -> list[Alternativa]:
    r = klient.get(
        "https://commons.wikimedia.org/w/api.php",
        params={
            "action": "query", "format": "json", "generator": "search", "gsrsearch": f"{dopyt} filetype:bitmap",
            "gsrnamespace": 6, "gsrlimit": limit * 2, "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 1200,
        },
        headers={"User-Agent": USER_AGENT}, timeout=20,
    )
    r.raise_for_status()
    najdene = []
    for strana in sorted(r.json().get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        info = (strana.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        licencia = meta.get("LicenseShortName", {}).get("value", "")
        if not licencia or not VOLNE_LICENCIE.search(licencia) or OBMEDZENE_CC.search(licencia):
            continue
        if info.get("width", 0) < 800:
            continue
        najdene.append(
            Alternativa(
                # Commons pridáva k náhľadom sledovacie parametre, tie nepotrebujeme.
                url=(info.get("thumburl") or info.get("url", "")).split("?")[0], nahlad=info.get("thumburl", "").split("?")[0],
                nazov=strana.get("title", "").removeprefix("File:"), autor=_text(meta.get("Artist", {}).get("value", "")),
                licencia=licencia, licencia_url=meta.get("LicenseUrl", {}).get("value", ""),
                stranka=info.get("descriptionurl", ""), povod="wikimedia", dopyt=dopyt,
            )
        )
    return najdene[:limit]


def hladaj_openverse(klient: httpx.Client, dopyt: str, limit: int = 3) -> list[Alternativa]:
    r = klient.get(
        "https://api.openverse.org/v1/images/",
        params={"q": dopyt, "license": "cc0,pdm,by,by-sa", "page_size": limit, "mature": "false"},
        headers={"User-Agent": USER_AGENT}, timeout=20,
    )
    r.raise_for_status()
    return [
        Alternativa(
            url=x["url"], nahlad=x.get("thumbnail", ""), nazov=x.get("title") or "", autor=x.get("creator") or "",
            licencia=f"{x['license'].upper()} {x.get('license_version') or ''}".strip(), licencia_url=x.get("license_url") or "",
            stranka=x.get("foreign_landing_url") or x["url"], povod="openverse", dopyt=dopyt,
        )
        for x in r.json().get("results", [])
    ]


def hladaj_alternativy(dopyty: list[str], klient: httpx.Client | None = None, maximum: int = 8) -> list[Alternativa]:
    vlastny = klient is None
    klient = klient or httpx.Client()
    skupiny: list[list[Alternativa]] = []
    try:
        for dopyt in dopyty[:3]:
            for hladac in (hladaj_wikimedia, hladaj_openverse):
                try:
                    skupiny.append(hladac(klient, dopyt))
                except (httpx.HTTPError, KeyError, ValueError) as e:
                    log.warning("%s pre „%s“ zlyhal: %s", hladac.__name__, dopyt, str(e)[:120])
    finally:
        if vlastny:
            klient.close()
    # Striedavo z každého dopytu a fotobanky, aby ponuku nezaplnil prvý dopyt.
    jedinecne: dict[str, Alternativa] = {}
    for poradie in range(max((len(s) for s in skupiny), default=0)):
        for skupina in skupiny:
            if poradie < len(skupina):
                jedinecne.setdefault(skupina[poradie].url, skupina[poradie])
    return list(jedinecne.values())[:maximum]


def odporucanie(povodne: list[PosudenyObrazok], alternativy: list[Alternativa]) -> dict:
    """Čo navrhnúť editorovi ako hlavný obrázok. Chránené a nejasné sa nikdy nenavrhujú."""
    for p in povodne:
        if p.zaradenie == "volne":
            return {"typ": "povodny", "url": p.url, "poznamka": "Voľná licencia, stačí uviesť autora a licenciu."}
    for p in povodne:
        if p.zaradenie == "tlacove":
            return {"typ": "povodny", "url": p.url, "poznamka": "Pravdepodobne tlačový materiál. Editor musí potvrdiť pôvod."}
    if alternativy:
        return {"typ": "alternativa", "url": alternativy[0].url, "poznamka": "Voľná náhrada. Editor musí overiť licenciu na stránke pôvodu."}
    return {"typ": "ilustracia", "url": "", "poznamka": "Nenašiel sa použiteľný obrázok. Vygenerovať ilustráciu z promptu."}
