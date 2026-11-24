"""Redakcia: python -m bitoviny.redakcia [--datum RRRR-MM-DD] [--pocet 5]

Vezme témy zo Zberača, jazykový model vyberie tie najzaujímavejšie a autorka
ku každej napíše koncept. Koncepty idú do data/koncepty/ (mimo repozitára).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

from ..llm import KOREN, langfuse_klient, nazvy_modelov
from ..zber.__main__ import spusti as spusti_zber
from ..zber.rss import vcera
from .archiv import ArchivGitHub, prekazka_zapisu
from .duplicity import KontrolaTem, Zaznam, popis_vysledku, z_temy
from .factcheck import cisty_factcheck
from .graf import uzol_factcheck, vyber_temy, zostav_graf
from .modely import Koncept, StavClanku
from .publikacia import GitHub, publikuj
from .titulny import vygeneruj_titulny

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
    """Markdown s frontmatterom webu a redakčnou správou v kľúči „koncept“."""
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


def overeny_obsah(stav: StavClanku) -> bool:
    koncept = stav["koncept"]
    return stav.get("overeny_text") == (koncept.titulok, koncept.perex, koncept.telo)


def spusti(
    den: date, pocet: int, max_clankov: int | None = None,
    *, gh: GitHub | None = None, pr: bool = False, iba_kontrola: bool = False, automaticky: bool = False,
    teraz: datetime | None = None,
) -> list[Path]:
    teraz = teraz or datetime.now(timezone.utc)
    temy_subor = KOREN / "data" / "raw" / f"temy-{den.isoformat()}.json"
    if not temy_subor.exists():
        log.info("Témy za %s chýbajú, spúšťam Zberača.", den)
        spusti_zber(den, KANDIDATOV, temy_subor)
    kandidati = json.loads(temy_subor.read_text(encoding="utf-8"))["temy"]
    if not kandidati:
        log.warning("Žiadne témy za %s.", den)
        return []

    if gh is None:
        token = os.environ["GITHUB_TOKEN"] if pr else os.getenv("GITHUB_TOKEN")
        with GitHub(token) as klient:
            return spusti(
                den, pocet, max_clankov, gh=klient, pr=pr, iba_kontrola=iba_kontrola,
                automaticky=automaticky, teraz=teraz,
            )

    lf = langfuse_klient()
    archiv = ArchivGitHub(gh, teraz)
    snimka = archiv.nacitaj()
    kontrola = KontrolaTem()
    log.info("Záznamov na kontrolu originality: %d.", len(snimka.zaznamy))
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
        lambda cfg: vyber_temy(kandidati, pocet, config=cfg, s_rezervou=True),
    )
    log.info("Vybraných %d tém z %d kandidátov.", len(vybrane), len(kandidati))

    schvalene: list[tuple[StavClanku, Zaznam]] = []
    ciel = min(pocet, max_clankov) if max_clankov is not None else pocet
    for i, stav in enumerate(vybrane, 1):
        if len(schvalene) >= ciel:
            break
        tema = z_temy(stav["tema"], i)
        nalez = kontrola.over(tema, snimka.zaznamy + [z for _, z in schvalene])
        log.info("Róbert | %s | %s", tema.titulok, popis_vysledku(nalez))
        if nalez.postupuje:
            schvalene.append((stav, tema))

    log.info("Róbert schválil tém: %d.", len(schvalene))
    if iba_kontrola or not schvalene:
        if lf is not None:
            lf.flush()
        return []

    graf = zostav_graf()
    vystup_dir = KOREN / "data" / "koncepty" / den.isoformat()
    vystup_dir.mkdir(parents=True, exist_ok=True)
    neuspechy = 0
    pouzite_cesty = set()
    for i, (stav, tema) in enumerate(schvalene):
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
            neuspechy += 1
            continue
        k: Koncept = vysledok["koncept"]
        id_clanku = slug(k.titulok)
        if id_clanku in pouzite_cesty:
            log.warning("Róbert | %s | titulok by prepísal koncept z tohto behu.", k.titulok)
            continue
        pouzite_cesty.add(id_clanku)
        ilustracia = None
        if automaticky:
            if cisty_factcheck(factcheck_do_spravy(vysledok)) and not overeny_obsah(vysledok):
                try:
                    novy_factcheck, _ = s_trasovanim(
                        "factcheck-po-korekture", {"tema": titulok},
                        lambda _: uzol_factcheck()({**stav, **vysledok}),
                    )
                    vysledok.update(novy_factcheck)
                except Exception as e:
                    upozornenie = "Kontrolu po korektúre sa nepodarilo dokončiť."
                    vysledok["upozornenia"] = [*vysledok.get("upozornenia", []), upozornenie]
                    log.warning("%s %s: %s", upozornenie, id_clanku, e)

            prompt = k.prompt_ilustracie.strip() or f"Symbolic editorial illustration without text: {k.titulok}"
            try:
                ilustracia = vygeneruj_titulny(prompt)
            except (RuntimeError, httpx.HTTPError) as e:
                neuspechy += 1
                vysledok["upozornenia"] = [
                    *vysledok.get("upozornenia", []), "Titulnú ilustráciu sa nepodarilo pripraviť.",
                ]
                log.error("Titulný obrázok pre %s: %s", id_clanku, e)

        if pr:
            prekazka = prekazka_zapisu(archiv, kontrola, id_clanku, tema, snimka.zaznamy)
            if prekazka:
                log.warning("Róbert | %s | %s", k.titulok, prekazka)
                continue
        subor = vystup_dir / f"{id_clanku}.md"
        subor.write_text(koncept_na_markdown(k, {**stav, **vysledok}, den, trace), encoding="utf-8")
        hotove.append(subor)
        log.info("Koncept: %s", subor.name)
        if pr:
            try:
                url = publikuj(
                    subor, gh, ilustracia=ilustracia,
                    automaticky=automaticky and overeny_obsah(vysledok),
                )
                log.info("PR: %s", url or "už existuje")
            except (RuntimeError, OSError, httpx.HTTPError) as e:
                neuspechy += 1
                log.error("Práca s pull requestom pre %s zlyhala: %s", subor.name, e)

    if lf is not None:
        lf.flush()
    if neuspechy and (pr or not hotove):
        raise RuntimeError(f"Počet zlyhaných redakčných operácií: {neuspechy}.")
    return hotove


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Redakcia portálu Bitoviny: výber tém a písanie konceptov")
    p.add_argument("--datum", type=date.fromisoformat, default=None, help="deň správ, predvolene včera")
    p.add_argument("--pocet", type=int, default=5, help="počet tém, ktoré má model vybrať")
    p.add_argument("--max-clankov", type=int, default=None, help="napísať najviac toľko konceptov (šetrí limity)")
    p.add_argument("--pr", action="store_true", help="z každého konceptu otvoriť pull request (treba GITHUB_TOKEN)")
    p.add_argument("--iba-kontrola", action="store_true", help="vypíše verdikty bez písania konceptov a otvárania PR")
    p.add_argument("--automaticky", action="store_true", help="pripraví titulné ilustrácie a zverejní overené články")
    a = p.parse_args(argv)
    if a.pr and a.iba_kontrola:
        p.error("Použite buď --pr, alebo --iba-kontrola.")
    if a.automaticky and not a.pr:
        p.error("Automatické zverejňovanie vyžaduje --pr.")
    if a.pocet < 1 or (a.max_clankov is not None and a.max_clankov < 1):
        p.error("Počet článkov musí byť kladný.")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    for hlucny in ("httpx", "httpcore", "huggingface_hub", "trafilatura", "google_genai", "langchain_google_genai"):
        logging.getLogger(hlucny).setLevel(logging.WARNING)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    den = a.datum or vcera()
    print(f"Modely autorky: {', '.join(nazvy_modelov('autorka'))}")
    try:
        hotove = spusti(
            den, a.pocet, a.max_clankov, pr=a.pr, iba_kontrola=a.iba_kontrola, automaticky=a.automaticky,
        )
    except (RuntimeError, ValueError, KeyError, httpx.HTTPError) as e:
        log.error("Redakciu sa nepodarilo dokončiť: %s", e)
        return 1
    if not a.iba_kontrola:
        print(f"\n{den}: {len(hotove)} konceptov")
        for h in hotove:
            print(f"  {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
