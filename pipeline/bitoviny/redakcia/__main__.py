"""Redakcia: python -m bitoviny.redakcia [--datum RRRR-MM-DD] [--pocet 5]

Vezme témy zo Zberača, jazykový model vyberie tie najzaujímavejšie a autorka
ku každej napíše koncept. Koncepty idú do data/koncepty/ (mimo repozitára):
zverejniť ich smie až človek.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import date
from pathlib import Path

from ..llm import KOREN, langfuse_klient, nazvy_modelov
from ..zber.__main__ import spusti as spusti_zber
from ..zber.rss import vcera
from .graf import vyber_temy, zostav_graf
from .modely import Koncept, StavClanku

log = logging.getLogger("redakcia")

KANDIDATOV = 12
PAUZA_S = 13  # bezplatná tarifa Gemini Flash: 5 požiadaviek za minútu


def slug(text: str) -> str:
    import re
    import unicodedata

    t = unicodedata.normalize("NFD", text)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:80].rstrip("-")


def koncept_na_markdown(k: Koncept, stav: StavClanku, den: date, trace: str | None) -> str:
    """Markdown s frontmatterom v tvare, aký čaká web, plus redakčná správa v kľúči „koncept“.
    Hlavný obrázok vyberie až editor z ponuky v koncept.obrazky."""
    nazvy = {s["url"]: s["zdroj_nazov"] + ": " + s["titulok"] for s in stav["tema"]["spravy"]}
    fm = {
        "title": k.titulok,
        "perex": k.perex,
        "sekcia": k.sekcia,
        "tagy": k.tagy,
        "zdroje": [{"nazov": nazvy.get(u, u), "url": u} for u in k.pouzite_zdroje],
        "redaktori": {"autor": "klara", "factcheck": "tomas", "korektura": "ciarka"},
        "trace": trace,
        "koncept": {
            "datum_sprav": den.isoformat(),
            "dovod_vyberu": stav.get("dovod_vyberu", ""),
            "prompt_ilustracie": k.prompt_ilustracie,
            "poznamky_pre_editora": k.poznamky_pre_editora,
            "upozornenia": stav.get("upozornenia", []),
            "factcheck": factcheck_do_spravy(stav),
            "korektura": stav.get("korektura"),
            "obrazky": stav.get("obrazky"),
        },
    }
    import yaml

    return "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n" + k.telo.strip() + "\n"


def factcheck_do_spravy(stav: StavClanku) -> dict | None:
    """Súhrn factchecku pre editora: priebeh kôl, otvorené nálezy a tabuľka tvrdení."""
    fc = stav.get("factcheck")
    if fc is None:
        return None
    return {
        "hodnotenie": fc.celkove_hodnotenie,
        "kola": stav.get("historia", []),
        "otvorene_nalezy": [n.model_dump() for n in stav.get("nalezy", [])],
        "tvrdenia": [t.model_dump() for t in fc.tvrdenia],
    }


def spusti(den: date, pocet: int, max_clankov: int | None = None) -> list[Path]:
    temy_subor = KOREN / "data" / "raw" / f"temy-{den.isoformat()}.json"
    if not temy_subor.exists():
        log.info("Témy za %s chýbajú, spúšťam Zberača.", den)
        spusti_zber(den, KANDIDATOV, temy_subor)
    kandidati = json.loads(temy_subor.read_text(encoding="utf-8"))["temy"]
    if not kandidati:
        log.warning("Žiadne témy za %s.", den)
        return []

    lf = langfuse_klient()
    graf = zostav_graf()
    vystup_dir = KOREN / "data" / "koncepty" / den.isoformat()
    vystup_dir.mkdir(parents=True, exist_ok=True)
    hotove: list[Path] = []

    def s_trasovanim(nazov: str, vstup: dict, fn):
        """Spustí fn(config) v jednom Langfuse trace a vráti (výsledok, url)."""
        if lf is None:
            return fn({}), None
        from langfuse.langchain import CallbackHandler

        with lf.start_as_current_observation(name=nazov, as_type="chain", input=vstup) as koren:
            vysledok = fn({"callbacks": [CallbackHandler()]})
            koren.update(output=getattr(vysledok, "model_dump", lambda: None)() or str(vysledok)[:2000])
            return vysledok, lf.get_trace_url()

    vybrane, _ = s_trasovanim(
        "vyber-tem",
        {"datum": den.isoformat(), "kandidatov": len(kandidati)},
        lambda cfg: vyber_temy(kandidati, pocet, config=cfg),
    )
    log.info("Vybraných %d tém z %d kandidátov.", len(vybrane), len(kandidati))

    for i, stav in enumerate(vybrane[: max_clankov or pocet]):
        if i:
            time.sleep(PAUZA_S)
        titulok = stav["tema"]["titulok"]
        try:
            vysledok, trace = s_trasovanim(
                "clanok",
                {"tema": titulok, "zdroje": [s["url"] for s in stav["tema"]["spravy"]]},
                lambda cfg: graf.invoke(stav, config=cfg),
            )
        except Exception as e:  # limit alebo výpadok všetkých modelov: článok sa odloží, beh pokračuje
            log.error("Článok „%s“ sa nepodarilo napísať: %s", titulok[:60], str(e)[:300])
            continue
        k: Koncept = vysledok["koncept"]
        subor = vystup_dir / f"{slug(k.titulok)}.md"
        subor.write_text(koncept_na_markdown(k, {**stav, **vysledok}, den, trace), encoding="utf-8")
        hotove.append(subor)
        log.info("Koncept: %s", subor.name)

    if lf is not None:
        lf.flush()
    return hotove


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Redakcia portálu Bitoviny: výber tém a písanie konceptov")
    p.add_argument("--datum", type=date.fromisoformat, default=None, help="deň správ, predvolene včera")
    p.add_argument("--pocet", type=int, default=5, help="počet tém, ktoré má model vybrať")
    p.add_argument("--max-clankov", type=int, default=None, help="napísať najviac toľko konceptov (šetrí limity)")
    a = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    for hlucny in ("httpx", "httpcore", "huggingface_hub", "trafilatura", "google_genai", "langchain_google_genai"):
        logging.getLogger(hlucny).setLevel(logging.WARNING)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    den = a.datum or vcera()
    print(f"Modely autorky: {', '.join(nazvy_modelov('autorka'))}")
    hotove = spusti(den, a.pocet, a.max_clankov)
    print(f"\n{den}: {len(hotove)} konceptov")
    for h in hotove:
        print(f"  {h}")
    return 0 if hotove else 1


if __name__ == "__main__":
    raise SystemExit(main())
