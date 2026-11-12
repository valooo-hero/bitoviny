"""Factcheck: jazykový model overí tvrdenia voči zdrojom, mechanické kontroly
overia model. Čísla sa hľadajú v zdrojoch priamo a každý „dôkaz“, ktorý
factchecker cituje, sa musí v zdroji naozaj nachádzať.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Literal

from pydantic import BaseModel, Field

from .modely import Koncept

Verdikt = Literal["potvrdene", "nepresne", "nepodlozene", "v_rozpore"]


class Tvrdenie(BaseModel):
    text: str = Field(description="Tvrdenie tak, ako je v koncepte")
    typ: Literal["cislo", "datum", "meno", "citat", "ine"]
    verdikt: Verdikt
    zdroj: str = Field(default="", description="Názov zdroja s oporou alebo rozporom")
    dokaz: str = Field(default="", description="Doslovný úryvok zo zdroja, najviac 25 slov")
    komentar: str = Field(default="", description="Jedna veta po slovensky")
    navrh_opravy: str = Field(default="", description="Správne znenie alebo „vypustiť“")


class Factcheck(BaseModel):
    tvrdenia: list[Tvrdenie]
    celkove_hodnotenie: str = Field(description="Dve vety po slovensky")


class Nalez(BaseModel):
    """Jeden problém pre autorku a editora, od modelu alebo z mechanickej kontroly."""

    povod: Literal["factchecker", "kontrola_cisel", "kontrola_dokazu"]
    zavaznost: Literal["chyba", "upozornenie"]
    text: str
    komentar: str = ""
    navrh_opravy: str = ""


# ---------- mechanické kontroly ----------

_CISLO = re.compile(r"\d+(?:[.,]\d+)?")


def _norm_cisla_en(text: str) -> str:
    text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)  # 2,000 -> 2000
    return text


def _norm_cisla_sk(text: str) -> str:
    text = re.sub(r"(?<=\d)[   ](?=\d{3}\b)", "", text)  # 2 000 -> 2000
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)  # 1,5 -> 1.5
    return text


def cisla(text: str, jazyk: str) -> set[str]:
    norm = _norm_cisla_sk(text) if jazyk == "sk" else _norm_cisla_en(text)
    najdene = set()
    for m in _CISLO.findall(norm):
        c = m.replace(",", ".")
        if "." in c:
            c = c.rstrip("0").rstrip(".")
        najdene.add(c)
    return najdene


def cisla_bez_opory(koncept: Koncept, zdrojove_texty: list[str]) -> list[str]:
    """Čísla z konceptu, ktoré sa v žiadnom zdroji nevyskytujú.

    Jednociferné čísla sa preskakujú: v zdrojoch bývajú slovom (five) a dávali
    by falošné poplachy.
    """
    v_zdrojoch: set[str] = set()
    for t in zdrojove_texty:
        v_zdrojoch |= cisla(t, "en")
    v_koncepte = cisla(f"{koncept.titulok}\n{koncept.perex}\n{koncept.telo}", "sk")
    return sorted((c for c in v_koncepte - v_zdrojoch if len(c.replace(".", "")) >= 2), key=float)


def _norm_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-"}))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def dokaz_je_v_zdroji(dokaz: str, zdrojove_texty: list[str]) -> bool:
    """Úryvok musí byť v zdroji doslova (bez ohľadu na interpunkciu a veľkosť písmen).

    Model smie úryvok skrátiť tromi bodkami, preto stačí, keď sedí každá časť.
    """
    casti = [_norm_text(c) for c in re.split(r"\.{3}|…|\[\.\.\.\]", dokaz)]
    casti = [c for c in casti if len(c) >= 12]
    if not casti:
        return True  # príliš krátky úryvok sa nedá spoľahlivo overiť
    zdroje = [_norm_text(t) for t in zdrojove_texty]
    return all(any(c in z for z in zdroje) for c in casti)


def zostav_nalezy(fc: Factcheck, koncept: Koncept, zdrojove_texty: list[str]) -> list[Nalez]:
    nalezy: list[Nalez] = []

    for t in fc.tvrdenia:
        if t.verdikt != "potvrdene":
            nalezy.append(
                Nalez(
                    povod="factchecker",
                    zavaznost="chyba",
                    text=t.text,
                    komentar=f"[{t.verdikt}] {t.komentar}".strip(),
                    navrh_opravy=t.navrh_opravy,
                )
            )
        if t.dokaz and not dokaz_je_v_zdroji(t.dokaz, zdrojove_texty):
            # Factchecker si úryvok vymyslel alebo upravil: jeho verdiktu sa nedá veriť.
            # Autorka to opraviť nevie, preto je to upozornenie pre editora, nie dôvod na ďalšie kolo.
            nalezy.append(
                Nalez(
                    povod="kontrola_dokazu",
                    zavaznost="upozornenie",
                    text=t.text,
                    komentar=f"Factchecker cituje úryvok, ktorý sa v zdrojoch doslova nenachádza: „{t.dokaz[:160]}“",
                    navrh_opravy="Overiť v zdrojoch ručne." if t.verdikt == "potvrdene" else t.navrh_opravy,
                )
            )

    oznacene = " ".join(n.text for n in nalezy)
    for c in cisla_bez_opory(koncept, zdrojove_texty):
        if c in cisla(oznacene, "sk"):
            continue  # číslo už namietol factchecker
        nalezy.append(
            Nalez(
                povod="kontrola_cisel",
                zavaznost="chyba",
                text=f"Číslo {c}",
                komentar="Číslo je v koncepte, ale v žiadnom zdroji sa nenachádza.",
                navrh_opravy="Opraviť podľa zdroja alebo vypustiť. Ak ide o prepočet, uviesť to v poznámkach.",
            )
        )
    return nalezy


def treba_opravit(nalezy: list[Nalez]) -> bool:
    return any(n.zavaznost == "chyba" for n in nalezy)
