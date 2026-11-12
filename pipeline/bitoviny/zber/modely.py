"""Dátové typy Zberača. Všetko, čo príde z cudzích webov, je nedôveryhodný údaj, nikdy pokyn."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import yaml

KOREN = Path(__file__).resolve().parents[3]
ZDROJE_YAML = KOREN / "config" / "sources.yaml"

USER_AGENT = "BitovinyBot/0.1 (+https://bitoviny.pages.dev/ako-to-funguje/)"


@dataclass
class Zdroj:
    id: str
    name: str
    feed: str
    role: str  # "source" alebo "signal"
    fetch_page: bool
    sections: list[str] = field(default_factory=list)


@dataclass
class Obrazok:
    url: str
    alt: str = ""
    popisok: str = ""
    kredit: str = ""
    licencia: str = ""
    povod: str = ""  # rss | og | figure | jsonld

    def kluc(self) -> str:
        return self.url.split("?")[0]


@dataclass
class Sprava:
    zdroj: str
    zdroj_nazov: str
    titulok: str
    url: str
    publikovane: datetime
    zhrnutie: str = ""
    text: str = ""
    obrazky: list[Obrazok] = field(default_factory=list)
    text_povod: str = ""  # rss | stranka | ziadny
    poznamka: str = ""

    def na_dict(self) -> dict:
        d = asdict(self)
        d["publikovane"] = self.publikovane.isoformat()
        return d


def nacitaj_zdroje(cesta: Path = ZDROJE_YAML) -> list[Zdroj]:
    data = yaml.safe_load(cesta.read_text(encoding="utf-8"))
    return [Zdroj(**z) for z in data["sources"]]
