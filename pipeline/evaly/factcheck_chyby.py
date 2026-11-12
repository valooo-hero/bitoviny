"""Skúška factcheckera na zámerne pokazenom článku.

    python evaly/factcheck_chyby.py data/koncepty/2026-11-11/nazov.md

Vezme hotový koncept, vloží doň známe chyby a spustí jedno kolo factchecku so
skutočným modelom. Vypíše, ktoré chyby factchecker (alebo mechanická kontrola)
zachytil. Koncept ani témy sa nemenia.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

from bitoviny.llm import KOREN, langfuse_klient
from bitoviny.redakcia.graf import uzol_factcheck
from bitoviny.redakcia.modely import Koncept

# (čo nahradiť, čím, kľúčové slová, podľa ktorých spoznáme, že nález hovorí o tejto chybe)
ZAMENY = [
    ("95 percent výkonu", "85 percent výkonu", ["85"]),
    ("MEXT beží na 145 serveroch", "MEXT beží na 450 serveroch", ["450"]),
    ("odkúpilo v júni", "odkúpilo v marci", ["marc"]),
    ("exkluzívny pre hardvér AMD", "dostupný aj pre procesory Intel", ["Intel"]),
]
VYMYSLENA_VETA = (
    "Generálna riaditeľka AMD Lisa Su podľa portálu The Register oznámila, "
    "že MEXT bude pre všetkých zákazníkov zadarmo."
)


def nacitaj(cesta: Path) -> tuple[Koncept, dict]:
    _, fm, telo = cesta.read_text(encoding="utf-8").split("---\n", 2)
    d = yaml.safe_load(fm)
    koncept = Koncept(
        titulok=d["title"], perex=d["perex"], sekcia=d["sekcia"], tagy=d["tagy"], telo=telo.strip(),
        pouzite_zdroje=[z["url"] for z in d["zdroje"]], prompt_ilustracie="", poznamky_pre_editora="",
    )
    temy = json.loads((KOREN / "data" / "raw" / f"temy-{d['koncept']['datum_sprav']}.json").read_text(encoding="utf-8"))
    urls = set(koncept.pouzite_zdroje)
    tema = next(t for t in temy["temy"] if urls & {s["url"] for s in t["spravy"]})
    return koncept, tema


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    koncept, tema = nacitaj(Path(sys.argv[1]))

    telo, vlozene = koncept.telo, []
    for stare, nove, kluce in ZAMENY:
        if stare in telo:
            telo = telo.replace(stare, nove, 1)
            vlozene.append((f"{stare} -> {nove}", kluce))
        else:
            print(f"(preskakujem, v koncepte nie je: {stare!r})")
    telo += "\n\n" + VYMYSLENA_VETA
    vlozene.append(("vymyslená veta o Lise Su", ["Lisa Su", "zadarmo"]))
    pokazeny = koncept.model_copy(update={"telo": telo})

    lf = langfuse_klient()
    stav = {"tema": tema, "koncept": pokazeny}
    if lf:
        from langfuse.langchain import CallbackHandler
        from langchain_core.runnables import RunnableLambda

        with lf.start_as_current_observation(name="eval-factcheck-chyby", as_type="evaluator"):
            vysledok = RunnableLambda(uzol_factcheck()).invoke(stav, config={"callbacks": [CallbackHandler()]})
            print("Trace:", lf.get_trace_url())
        lf.flush()
    else:
        vysledok = uzol_factcheck()(stav)

    fc, nalezy = vysledok["factcheck"], vysledok["nalezy"]
    print(f"\nTvrdení: {len(fc.tvrdenia)}, potvrdených: {sum(t.verdikt == 'potvrdene' for t in fc.tvrdenia)}, nálezov: {len(nalezy)}")
    print(f"Hodnotenie: {fc.celkove_hodnotenie}\n")
    for n in nalezy:
        print(f"- [{n.povod}/{n.zavaznost}] {n.text[:110]}\n    {n.komentar[:200]}")

    print("\nZachytenie vložených chýb:")
    zachytene = 0
    for popis, kluce in vlozene:
        kto = sorted({n.povod for n in nalezy if any(k.lower() in f"{n.text} {n.komentar}".lower() for k in kluce)})
        zachytene += bool(kto)
        print(f"  {'ÁNO' if kto else 'NIE '}  {popis}  {kto or ''}")
    print(f"\nZachytené {zachytene} z {len(vlozene)}.")
    return 0 if zachytene == len(vlozene) else 1


if __name__ == "__main__":
    raise SystemExit(main())
