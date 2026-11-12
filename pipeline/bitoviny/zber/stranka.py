"""Stiahnutie stránky článku: plný text a obrázky s popiskami a kreditmi.

Používa sa len tam, kde RSS neobsahuje text alebo obrázky. Rešpektuje robots.txt
a medzi požiadavkami na tú istú doménu čaká.
"""

from __future__ import annotations

import json
import logging
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
import trafilatura
from bs4 import BeautifulSoup

from .modely import USER_AGENT, Obrazok, Sprava
from .rss import _bez_duplicit, obrazky_z_html

log = logging.getLogger(__name__)

ODSTUP_S = 3.0
MAX_TEXT = 20_000


class Stahovac:
    def __init__(self, klient: httpx.Client, odstup_s: float = ODSTUP_S):
        self.klient = klient
        self.odstup_s = odstup_s
        self._robots: dict[str, RobotFileParser | None] = {}
        self._posledne: dict[str, float] = {}

    def _smie(self, url: str) -> bool:
        casti = urlparse(url)
        koren = f"{casti.scheme}://{casti.netloc}"
        if koren not in self._robots:
            rp = RobotFileParser()
            try:
                r = self.klient.get(f"{koren}/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=15, follow_redirects=True)
                if r.status_code == 200:
                    rp.parse(r.text.splitlines())
                    self._robots[koren] = rp
                else:
                    self._robots[koren] = None  # bez robots.txt je prístup povolený
            except httpx.HTTPError:
                self._robots[koren] = None
        rp = self._robots[koren]
        return True if rp is None else rp.can_fetch(USER_AGENT, url)

    def _pockaj(self, url: str) -> None:
        domena = urlparse(url).netloc
        od = time.monotonic() - self._posledne.get(domena, 0.0)
        if od < self.odstup_s:
            time.sleep(self.odstup_s - od)
        self._posledne[domena] = time.monotonic()

    def html(self, url: str) -> str | None:
        if not self._smie(url):
            log.info("robots.txt zakazuje %s", url)
            return None
        self._pockaj(url)
        try:
            r = self.klient.get(url, headers={"User-Agent": USER_AGENT}, timeout=30, follow_redirects=True)
            r.raise_for_status()
            return r.text
        except httpx.HTTPError as e:
            log.warning("Stránka %s zlyhala: %s", url, e)
            return None


def text_zo_stranky(html: str) -> str:
    text = trafilatura.extract(html, include_comments=False, include_tables=False, favor_precision=True) or ""
    return text[:MAX_TEXT]


def _z_jsonld(soup: BeautifulSoup) -> list[Obrazok]:
    """schema.org ImageObject nesie kredit a licenciu najspoľahlivejšie."""
    najdene: list[Obrazok] = []

    def prejdi(uzol):
        if isinstance(uzol, list):
            for u in uzol:
                prejdi(u)
        elif isinstance(uzol, dict):
            typ = uzol.get("@type")
            typy = typ if isinstance(typ, list) else [typ]
            if "ImageObject" in typy and isinstance(uzol.get("url") or uzol.get("contentUrl"), str):
                autor = uzol.get("creator") or uzol.get("author") or {}
                if isinstance(autor, list):
                    autor = autor[0] if autor else {}
                meno = autor.get("name", "") if isinstance(autor, dict) else str(autor)
                najdene.append(
                    Obrazok(
                        url=uzol.get("url") or uzol.get("contentUrl"),
                        popisok=str(uzol.get("caption") or uzol.get("description") or ""),
                        kredit=str(uzol.get("creditText") or uzol.get("copyrightNotice") or meno or ""),
                        licencia=str(uzol.get("license") or ""),
                        povod="jsonld",
                    )
                )
            for kluc, hodnota in uzol.items():
                # Logo vydavateľa nie je obrázok k článku.
                if kluc in ("logo", "publisher"):
                    continue
                if isinstance(hodnota, (dict, list)):
                    prejdi(hodnota)

    for skript in soup.find_all("script", type="application/ld+json"):
        try:
            prejdi(json.loads(skript.string or ""))
        except (json.JSONDecodeError, TypeError):
            continue
    return najdene


def obrazky_zo_stranky(html: str, url: str) -> list[Obrazok]:
    soup = BeautifulSoup(html, "lxml")
    najdene: list[Obrazok] = _z_jsonld(soup)

    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        alt = soup.find("meta", property="og:image:alt")
        najdene.append(Obrazok(url=urljoin(url, og["content"]), alt=(alt.get("content", "") if alt else ""), povod="og"))

    telo = soup.find("article") or soup.find("main") or soup
    najdene.extend(o for o in obrazky_z_html(str(telo), povod="figure") if o.popisok or o.kredit)
    return _bez_duplicit(najdene)[:8]


def dopln_zo_stranky(sprava: Sprava, stahovac: Stahovac) -> None:
    """Doplní správe plný text a obrázky zo stránky článku."""
    html = stahovac.html(sprava.url)
    if not html:
        sprava.poznamka = "stránku sa nepodarilo stiahnuť alebo to zakazuje robots.txt"
        return
    text = text_zo_stranky(html)
    if len(text) > len(sprava.text):
        sprava.text = text
        sprava.text_povod = "stranka"
    sprava.obrazky = _bez_duplicit(obrazky_zo_stranky(html, sprava.url) + sprava.obrazky)[:8]
