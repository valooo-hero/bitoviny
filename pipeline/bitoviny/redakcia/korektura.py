"""Korektúra: jazykový model navrhne jednotlivé úpravy, kód ich overí a vykoná.

Model text neprepisuje. Vracia zoznam „pôvodný úryvok -> opravený úryvok“ a
každá úprava musí prejsť kontrolou: nesmie zmeniť čísla ani vlastné mená a
nesmie byť prepísaním obsahu. Čo neprejde, sa nevykoná a ide editorovi.
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from typing import Literal

from pydantic import BaseModel, Field

from .factcheck import cisla
from .modely import Koncept

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
