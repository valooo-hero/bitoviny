"""Zberač: python -m bitoviny.zber [--datum RRRR-MM-DD] [--pocet 5]

Výstup je JSON s vybranými témami a podkladmi. Zdrojové texty sa do repozitára
neukladajú, výstupný priečinok data/raw je v .gitignore.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

from .modely import KOREN, nacitaj_zdroje
from .rss import spravy_z_kanala, stiahni_kanal, vcera
from .stranka import Stahovac, dopln_zo_stranky
from .zoskupenie import lokalny_embedder, pridaj_signal, vyber, zoskup

log = logging.getLogger("zber")

# Kratší text z RSS býva len výňatok, vtedy sa stiahne stránka článku.
MIN_TEXT = 2500


def spusti(den: date, pocet: int, vystup: Path, stahuj_stranky: bool = True) -> dict:
    zdroje = nacitaj_zdroje()
    spravy, signalne, stav_zdrojov = [], [], {}

    with httpx.Client(http2=False) as klient:
        for z in zdroje:
            surovy = stiahni_kanal(klient, z)
            if surovy is None:
                stav_zdrojov[z.id] = {"stav": "chyba", "spravy": 0}
                continue
            # Signálny zdroj berieme celý, jeho položky nemajú spoľahlivý dátum udalosti.
            polozky = spravy_z_kanala(z, surovy, None if z.role == "signal" else den)
            stav_zdrojov[z.id] = {"stav": "ok", "spravy": len(polozky)}
            (signalne if z.role == "signal" else spravy).extend(polozky)
            log.info("%-18s %3d správ", z.id, len(polozky))

        if not spravy:
            log.warning("Za %s sa nenašla žiadna správa.", den)

        embed = lokalny_embedder()
        temy = zoskup(spravy, embed)
        pridaj_signal(temy, signalne, embed)
        vybrane = vyber(temy, pocet=pocet)

        if stahuj_stranky:
            podla_id = {z.id: z for z in zdroje}
            stahovac = Stahovac(klient)
            for t in vybrane:
                for s in t.spravy:
                    if podla_id[s.zdroj].fetch_page or len(s.text) < MIN_TEXT or not s.obrazky:
                        dopln_zo_stranky(s, stahovac)

    vysledok = {
        "datum": den.isoformat(),
        "vytvorene": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pocet_sprav": len(spravy),
        "pocet_tem": len(temy),
        "zdroje": stav_zdrojov,
        "temy": [t.na_dict() for t in vybrane],
    }
    vystup.parent.mkdir(parents=True, exist_ok=True)
    vystup.write_text(json.dumps(vysledok, ensure_ascii=False, indent=2), encoding="utf-8")
    return vysledok


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Zberač správ portálu Bitoviny")
    p.add_argument("--datum", type=date.fromisoformat, default=None, help="deň, predvolene včera (Europe/Bratislava)")
    p.add_argument("--pocet", type=int, default=5, help="počet vybraných tém")
    p.add_argument("--vystup", type=Path, default=None)
    p.add_argument("--bez-stranok", action="store_true", help="nesťahovať stránky článkov, len RSS")
    a = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    for hlucny in ("httpx", "httpcore", "huggingface_hub", "trafilatura"):
        logging.getLogger(hlucny).setLevel(logging.WARNING)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    den = a.datum or vcera()
    vystup = a.vystup or KOREN / "data" / "raw" / f"temy-{den.isoformat()}.json"
    v = spusti(den, a.pocet, vystup, stahuj_stranky=not a.bez_stranok)

    print(f"\n{den}: {v['pocet_sprav']} správ, {v['pocet_tem']} tém, vybraných {len(v['temy'])}")
    for i, t in enumerate(v["temy"], 1):
        znakov = sum(len(s["text"]) for s in t["spravy"])
        obrazkov = sum(len(s["obrazky"]) for s in t["spravy"])
        print(f"{i}. [{t['skore']}] {t['titulok']}")
        print(f"   zdroje: {', '.join(t['zdroje'])} | HN: {t['signal_hn']} | text: {znakov} znakov | obrázky: {obrazkov}")
    print(f"\nVýstup: {vystup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
