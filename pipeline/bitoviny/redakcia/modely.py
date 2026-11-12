"""Štruktúrované výstupy agentov a stav grafu."""

from __future__ import annotations

from typing import Literal, TypedDict

from pydantic import BaseModel, Field

Sekcia = Literal["ai", "bezpecnost", "hardver", "mobil", "softver", "veda", "biznis", "slovensko-eu"]


class VybranaTema(BaseModel):
    cislo: int = Field(description="Číslo témy zo zoznamu")
    sekcia: Sekcia
    dovod: str = Field(description="Jedna veta po slovensky, prečo tému vybrať")


class VyberTem(BaseModel):
    vybrane: list[VybranaTema] = Field(description="Vybrané témy od najdôležitejšej")


class Koncept(BaseModel):
    titulok: str = Field(description="Titulok po slovensky, najviac 100 znakov")
    perex: str = Field(description="Jedna až dve vety, 80 až 300 znakov")
    sekcia: Sekcia
    tagy: list[str] = Field(description="Dva až päť tagov")
    telo: str = Field(description="Telo článku v Markdowne, 350 až 600 slov, medzititulky ##")
    pouzite_zdroje: list[str] = Field(description="URL zdrojov, z ktorých článok čerpá")
    prompt_ilustracie: str = Field(description="Anglický prompt na symbolickú ilustráciu, jedna veta")
    poznamky_pre_editora: str = Field(description="Po slovensky: čo overiť, kde si zdroje odporovali")


class StavClanku(TypedDict, total=False):
    tema: dict  # téma zo Zberača: titulok, spravy[], zdroje[]
    sekcia_navrh: str
    dovod_vyberu: str
    koncept: Koncept
    upozornenia: list[str]
