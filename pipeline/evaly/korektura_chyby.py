"""Skúška korektúry na texte so známymi chybami.

    python evaly/korektura_chyby.py

Spustí celý uzol korektúry (jazykový model, pevné pravidlá, LanguageTool) na
krátkom článku s vloženými chybami a vypíše, ktoré opravil, ktoré nie a či
niečo pokazil. Ochrany (čísla, mená) sa overujú tiež.
"""

from __future__ import annotations

import sys

from bitoviny.redakcia.graf import uzol_korektura
from bitoviny.redakcia.modely import Koncept

TELO = """V virtualizovanom prostredí beží technológia MEXT na 145 serveroch. Gary Smerdon tvrdí že výkon ostáva na 95%.

## Plány

Firma plánuje rozšírenie v klastéri Azure. Nové servery ktoré prídu budúci rok, budú mať menej pamäte.

Spoločnosť to oznámila s svojim partnerom HPE. Podľa nej sa zmena dotkne aj firiem z Slovenska a Česka."""

# (popis, správny tvar, ktorý má v texte po korektúre byť)
OCAKAVANE = [
    ("vokalizácia v → vo", "Vo virtualizovanom"),
    ("čiarka pred že", "tvrdí, že"),
    ("medzera pred %", "95 %"),  # bežná aj nezalomiteľná medzera, porovnáva sa po zjednotení
    ("klastéri → klastri", "v klastri"),
    ("čiarka pred ktoré", "servery, ktoré"),
    ("vokalizácia s → so", "so svoj"),
    ("vokalizácia z → zo", "zo Slovenska"),
    ("svojim → svojím", "svojím partnerom"),
]
# Čo sa zmeniť nesmie.
NEMENNE = ["145 serveroch", "Gary Smerdon", "HPE", "Azure", "Slovenska"]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    k = Koncept(
        titulok="AMD tvrdí, že udrží výkon s polovicou pamäte",
        perex="Technológia MEXT presúva málo používané dáta z pamäte na disk a výkon pritom podľa firmy takmer neklesá.",
        sekcia="hardver", tagy=["AMD"], telo=TELO, pouzite_zdroje=[], prompt_ilustracie="", poznamky_pre_editora="",
    )
    vysledok = uzol_korektura()({"koncept": k})
    po = vysledok["koncept"].telo.replace("\u00a0", " ")
    kor = vysledok["korektura"]

    print("Úpravy:")
    for u in kor["upravy"]:
        print(f"  [{u['stav']}] {u['povodne'][:45]!r} → {u['opravene'][:45]!r} | {u['dovod'][:50]} {u['poznamka']}")
    if kor.get("chyba"):
        print("  " + kor["chyba"])
    print(f"Podozrivé slová: {[p['text'] for p in kor.get('podozrive', [])]}")

    print("\nOpravené chyby:")
    opravene = 0
    for popis, spravne in OCAKAVANE:
        ok = spravne in po
        opravene += ok
        print(f"  {'ÁNO' if ok else 'NIE '}  {popis}")
    pokazene = [n for n in NEMENNE if n not in po]
    print(f"\nOpravených {opravene} z {len(OCAKAVANE)}. Pokazené chránené výrazy: {pokazene or 'žiadne'}")
    return 0 if not pokazene else 1


if __name__ == "__main__":
    raise SystemExit(main())
