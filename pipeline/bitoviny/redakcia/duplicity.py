"""Porovnanie nových tém s publikovanými článkami a konceptmi."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from ..llm import model_pre

OKNO = timedelta(days=7)
CLANKY = "content/clanky/"
DAVKA = 8
SLEDOVACIE_PARAMETRE = {"fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid", "igshid"}
PROMPT = Path(__file__).parent / "prompty" / "kontrola_duplicit.md"


def normalizuj_url(url: str) -> str:
    try:
        u = urlsplit(url)
        if u.scheme not in {"https", "http"} or not u.hostname or u.username or u.password:
            return ""
        host = u.hostname.removeprefix("www.")
        if ":" in host:
            host = f"[{host}]"
        if u.port and (u.scheme, u.port) not in {("http", 80), ("https", 443)}:
            host += f":{u.port}"
    except ValueError:
        return ""
    query = [
        (k, v) for k, v in parse_qsl(u.query, keep_blank_values=True)
        if not (k.lower().startswith("utm_") or k.lower() in SLEDOVACIE_PARAMETRE)
    ]
    return urlunsplit(("", host, u.path.rstrip("/"), urlencode(sorted(query)), ""))


@dataclass(frozen=True)
class Zaznam:
    id: str
    titulok: str
    perex: str = ""
    zdroje: tuple[tuple[str, str], ...] = ()
    odkaz: str = ""

    def pre_model(self) -> dict:
        return {
            "id": self.id,
            "titulok": self.titulok[:160],
            "perex": self.perex[:250],
            "zdroje": [{"titulok": nazov[:110], "url": url[:140]} for nazov, url in self.zdroje[:3]],
        }


def z_temy(tema: dict, cislo: int) -> Zaznam:
    spravy = tema["spravy"]
    perex = next((s.get("zhrnutie") or s.get("text") for s in spravy if s.get("zhrnutie") or s.get("text")), "")
    return Zaznam(
        f"tema:{cislo}", tema["titulok"], perex,
        tuple((s["titulok"], s["url"]) for s in spravy),
    )


def z_hlavicky(id: str, hlavicka: dict, odkaz: str = "") -> Zaznam:
    return Zaznam(
        id, hlavicka["title"], hlavicka.get("perex", ""),
        tuple((s.get("nazov", ""), s["url"]) for s in hlavicka.get("zdroje", [])), odkaz,
    )


def publikovane_v_okne(hlavicka: dict, zaciatok_behu: datetime, kontrolovane_do: datetime) -> bool:
    # Aj stiahnutý článok už vyšiel a patrí do kontroly.
    if (hlavicka.get("obrazok") or {}).get("src") in {"/obrazky/zastupny.svg", "/obrazky/zastupny.jpg"}:
        return False
    redaktori = hlavicka.get("redaktori")
    if redaktori is not None and not redaktori.get("schvalil"):
        return False
    datum = hlavicka["publikovane"]
    if not isinstance(datum, datetime):
        datum = datetime.fromisoformat(str(datum))
    if datum.tzinfo is None:
        datum = datum.replace(tzinfo=timezone.utc)
    return zaciatok_behu - OKNO <= datum <= kontrolovane_do


def tie_iste_zdroje(tema: Zaznam, existujuci: Zaznam) -> bool:
    nove = {normalizuj_url(url) for _, url in tema.zdroje} - {""}
    stare = {normalizuj_url(url) for _, url in existujuci.zdroje} - {""}
    return bool(nove and nove <= stare)


class PosudenieTemy(BaseModel):
    verdikt: Literal["nova", "duplicita", "novy_vyvoj", "nejasna"]
    odkaz_id: str = Field(description="Presné ID položky zo zoznamu, prázdne pri verdikte nova")
    dovod: str


@dataclass(frozen=True)
class Vysledok:
    verdikt: str
    dovod: str
    zhoda: Zaznam | None = None

    @property
    def postupuje(self) -> bool:
        return self.verdikt in {"nova", "novy_vyvoj"}


class KontrolaTem:
    def __init__(self, model: Any = None):
        self.model = model
        self.prompt = PROMPT.read_text(encoding="utf-8")

    def over(self, tema: Zaznam, archiv: list[Zaznam]) -> Vysledok:
        for zaznam in archiv:
            if tie_iste_zdroje(tema, zaznam):
                return Vysledok("duplicita", "Všetky zdrojové URL už boli použité.", zaznam)

        vysledok = Vysledok("nova", "V skontrolovaných záznamoch sa nenašla zhoda.")
        for zaciatok in range(0, len(archiv), DAVKA):
            davka = archiv[zaciatok:zaciatok + DAVKA]
            if self.model is None:
                self.model = model_pre("kontrola_duplicit", PosudenieTemy, over_vystup=self._over_odkaz)
            vstup = {"tema": tema.pre_model(), "existujuce": [z.pre_model() for z in davka]}
            spravy = [SystemMessage(self.prompt), HumanMessage(json.dumps(vstup, ensure_ascii=False))]
            try:
                odpoved = self.model.invoke(spravy)
            except Exception:
                return Vysledok(
                    "neoverena", "Kontrola duplicít nedostupná. Téma vyžaduje ručné posúdenie.",
                )
            self._over_odkaz(odpoved, spravy)
            zhoda = next((z for z in davka if z.id == odpoved.odkaz_id), None)
            if odpoved.verdikt == "duplicita":
                return Vysledok(odpoved.verdikt, odpoved.dovod, zhoda)
            if odpoved.verdikt == "nejasna" or (odpoved.verdikt == "novy_vyvoj" and vysledok.verdikt == "nova"):
                vysledok = Vysledok(odpoved.verdikt, odpoved.dovod, zhoda)
        return vysledok

    @staticmethod
    def _over_odkaz(vystup: PosudenieTemy, spravy: list) -> None:
        if not isinstance(vystup, PosudenieTemy) or not (0 < len(vystup.dovod.strip()) <= 400):
            raise ValueError("Model nevrátil platné posúdenie témy.")
        ids = {z["id"] for z in json.loads(spravy[-1].content)["existujuce"]}
        if vystup.odkaz_id not in ({""} if vystup.verdikt == "nova" else ids):
            raise ValueError("Verdikt Róberta odkazuje na neplatný záznam.")


def popis_vysledku(vysledok: Vysledok) -> str:
    zhoda = vysledok.zhoda
    return f"{vysledok.verdikt} – {vysledok.dovod}" + (
        f" [{zhoda.titulok}] {zhoda.odkaz or zhoda.id}" if zhoda else ""
    )
