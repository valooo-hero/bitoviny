"""Korektúra: jazykový model navrhne jednotlivé úpravy, kód ich overí a vykoná.

Model text neprepisuje. Vracia zoznam „pôvodný úryvok -> opravený úryvok“ a
každá úprava musí prejsť kontrolou: nesmie zmeniť čísla ani vlastné mená a
nesmie byť prepísaním obsahu. Čo neprejde, sa nevykoná a ide editorovi.
"""

from __future__ import annotations

import difflib
import logging
import re
import unicodedata
from typing import Literal

import httpx

from pydantic import BaseModel, Field

from .factcheck import cisla
from .modely import Koncept

log = logging.getLogger(__name__)

MAX_DLZKA_UPRAVY = 400
MIN_PODOBNOST = 0.55


class Uprava(BaseModel):
    pole: Literal["titulok", "perex", "telo"]
    povodne: str = Field(description="Úryvok presne tak, ako je v texte, vrátane okolitých slov na jednoznačné určenie")
    opravene: str = Field(description="Ten istý úryvok po oprave")
    dovod: str = Field(description="Stručne po slovensky, napr. „čiarka pred ktorý“")


class Korektura(BaseModel):
    upravy: list[Uprava] = Field(description="Zoznam úprav. Prázdny, ak je text v poriadku")


class VysledokUpravy(BaseModel):
    pole: str
    povodne: str
    opravene: str
    dovod: str
    stav: Literal["vykonana", "zamietnuta", "nenajdena"]
    poznamka: str = ""


def _bez_diakritiky(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def vlastne_mena(text: str) -> set[str]:
    """Kmene slov s veľkým začiatočným písmenom. Kmeň (prvé štyri písmená) toleruje
    opravu pádovej koncovky, ale zachytí zámenu mena."""
    slova = re.findall(r"\b[A-ZÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽ][\w-]{3,}", text)
    return {_bez_diakritiky(s)[:4].lower() for s in slova}


def dovod_zamietnutia(u: Uprava) -> str | None:
    if u.povodne == u.opravene:
        return "úprava nič nemení"
    if len(u.povodne) > MAX_DLZKA_UPRAVY:
        return "úryvok je príliš dlhý, vyzerá to na prepis"
    if cisla(u.povodne, "sk") != cisla(u.opravene, "sk"):
        return "mení čísla"
    # Prvé slovo úryvku môže byť začiatok vety, kde sa veľké písmeno mení legitímne.
    prve_slova = vlastne_mena(u.povodne.split(" ", 1)[0]) | vlastne_mena(u.opravene.split(" ", 1)[0])
    if (vlastne_mena(u.povodne) ^ vlastne_mena(u.opravene)) - prve_slova:
        return "mení vlastné mená"
    if difflib.SequenceMatcher(None, u.povodne, u.opravene).ratio() < MIN_PODOBNOST:
        return "príliš veľká zmena, vyzerá to na prepis obsahu"
    if u.povodne.count("#") != u.opravene.count("#") or u.povodne.count("\n") != u.opravene.count("\n"):
        return "mení štruktúru textu"
    return None


def vykonaj(koncept: Koncept, korektura: Korektura) -> tuple[Koncept, list[VysledokUpravy]]:
    texty = {"titulok": koncept.titulok, "perex": koncept.perex, "telo": koncept.telo}
    vysledky: list[VysledokUpravy] = []

    for u in korektura.upravy:
        zaklad = dict(pole=u.pole, povodne=u.povodne, opravene=u.opravene, dovod=u.dovod)
        dovod = dovod_zamietnutia(u)
        if dovod:
            vysledky.append(VysledokUpravy(**zaklad, stav="zamietnuta", poznamka=dovod))
            continue
        pocet = texty[u.pole].count(u.povodne)
        if pocet == 0:
            vysledky.append(VysledokUpravy(**zaklad, stav="nenajdena", poznamka="úryvok sa v texte nenachádza"))
            continue
        if pocet > 1:
            vysledky.append(VysledokUpravy(**zaklad, stav="zamietnuta", poznamka=f"úryvok je v texte {pocet}-krát, nie je jednoznačný"))
            continue
        texty[u.pole] = texty[u.pole].replace(u.povodne, u.opravene, 1)
        vysledky.append(VysledokUpravy(**zaklad, stav="vykonana"))

    return koncept.model_copy(update=texty), vysledky


def rozdiel(pred: Koncept, po: Koncept) -> str:
    """Zjednotený diff pre editora."""

    def riadky(k: Koncept) -> list[str]:
        return [f"# {k.titulok}", "", k.perex, "", *k.telo.splitlines()]

    return "\n".join(difflib.unified_diff(riadky(pred), riadky(po), "pred korektúrou", "po korektúre", lineterm="", n=0))


# ---------- pevné pravidlá a LanguageTool ----------
#
# Jazykový model opravuje slovenčinu slabo, preto korektúru dopĺňajú dva zdroje
# bez modelu. Všetky ich úpravy prechádzajú tou istou kontrolou ako návrhy modelu.

LANGUAGETOOL_URL = "https://api.languagetool.org/v2/check"
# Pravidlá LanguageTool, ktorým veríme natoľko, že sa úprava vykoná sama.
# Návrhy pri preklepoch (MORFOLOGIK) bývajú zlé, napríklad „virtualizovanom“
# na „aktualizovanom“, preto idú editorovi len ako podozrivé slová.
SPOLAHLIVE_PRAVIDLA_LT = {"ZE", "KTORY", "CO", "ABY", "LEBO", "ALE", "COMMA_PARENTHESIS_WHITESPACE", "WHITESPACE_RULE", "DOUBLE_PUNCTUATION"}

_VOKALIZACIA = [
    (re.compile(r"\b([Vv]) (?=[VvFf]\w)"), lambda m: m.group(1) + "o "),
    (re.compile(r"\b([Ss]) (?=[SsZzŠšŽž]\w)"), lambda m: m.group(1) + "o "),
    (re.compile(r"\b([Zz]) (?=[SsZzŠšŽž]\w)"), lambda m: m.group(1) + "o "),
    (re.compile(r"\b([Kk]) (?=[KkGg]\w)"), lambda m: m.group(1) + "u "),
]
_PERCENTO = re.compile(r"(?<=\d)%")


def _jedinecny_uryvok(text: str, zaciatok: int, koniec: int) -> tuple[str, int] | None:
    """Rozšíri úsek o okolité slová, kým nie je v texte jedinečný. Vráti (úryvok, posun začiatku úseku v úryvku)."""
    z, k = zaciatok, koniec
    for _ in range(8):
        uryvok = text[z:k]
        if uryvok.strip() and text.count(uryvok) == 1:
            return uryvok, zaciatok - z
        nz = text.rfind(" ", 0, max(z - 1, 0))
        nk = text.find(" ", min(k + 1, len(text)))
        z = 0 if nz < 0 else nz + 1
        k = len(text) if nk < 0 else nk
        if "\n" in text[z:k]:
            break
    return None


def _uprava(pole: str, text: str, zaciatok: int, koniec: int, nahrada: str, dovod: str) -> Uprava | None:
    najdene = _jedinecny_uryvok(text, zaciatok, koniec)
    if not najdene:
        return None
    uryvok, posun = najdene
    opravene = uryvok[:posun] + nahrada + uryvok[posun + (koniec - zaciatok):]
    return Uprava(pole=pole, povodne=uryvok, opravene=opravene, dovod=dovod)


def _polia(k: Koncept) -> dict[str, str]:
    return {"titulok": k.titulok, "perex": k.perex, "telo": k.telo}


def pevne_pravidla(k: Koncept) -> list[Uprava]:
    """Vokalizácia predložiek (v na vo, s na so, z na zo, k na ku) a medzera pred znakom percenta."""
    upravy: list[Uprava] = []
    for pole, text in _polia(k).items():
        for vzor, nahrada in _VOKALIZACIA:
            for m in vzor.finditer(text):
                u = _uprava(pole, text, m.start(), m.end(), nahrada(m), "vokalizácia predložky")
                if u:
                    upravy.append(u)
        for m in _PERCENTO.finditer(text):
            u = _uprava(pole, text, m.start(), m.end(), "\u00a0%", "medzera pred znakom percenta")
            if u:
                upravy.append(u)
    return upravy


def languagetool(k: Koncept, klient: httpx.Client | None = None) -> tuple[list[Uprava], list[dict]]:
    """Spoľahlivé gramatické nálezy ako úpravy, ostatné ako podozrivé miesta pre editora.
    Pri výpadku služby vráti prázdne zoznamy: korektúra nesmie zastaviť článok."""
    upravy: list[Uprava] = []
    podozrive: list[dict] = []
    vlastny = klient is None
    klient = klient or httpx.Client(timeout=30)
    try:
        for pole, text in _polia(k).items():
            try:
                r = klient.post(
                    LANGUAGETOOL_URL,
                    data={"text": text, "language": "sk-SK"},
                    headers={"User-Agent": "BitovinyBot/0.1 (+https://bitoviny.pages.dev/ako-to-funguje/)"},
                )
                r.raise_for_status()
                nalezy = r.json().get("matches", [])
            except (httpx.HTTPError, ValueError) as e:
                log.warning("LanguageTool zlyhal: %s", str(e)[:120])
                return [], []
            for m in nalezy:
                zaciatok, koniec = m["offset"], m["offset"] + m["length"]
                navrhy = [x["value"] for x in m.get("replacements", [])]
                pravidlo = m.get("rule", {}).get("id", "")
                if pravidlo in SPOLAHLIVE_PRAVIDLA_LT and len(navrhy) == 1:
                    u = _uprava(pole, text, zaciatok, koniec, navrhy[0], f"LanguageTool: {' '.join(m.get('message', '').split())[:80]}")
                    if u:
                        upravy.append(u)
                        continue
                podozrive.append({
                    "pole": pole,
                    "text": text[zaciatok:koniec],
                    "kontext": text[max(0, zaciatok - 40):koniec + 40],
                    "navrhy": navrhy[:3],
                    "dovod": " ".join(m.get("message", "").split())[:120],
                })
    finally:
        if vlastny:
            klient.close()
    return upravy, podozrive
