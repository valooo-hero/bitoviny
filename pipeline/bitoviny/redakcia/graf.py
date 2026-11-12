"""Redakčný graf v LangGraphe.

Fáza 3: výber tém a autorka. Ďalšie fázy pridajú uzly factcheck (so slučkou
späť na autorku), korektúra a fotoeditor.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from ..llm import KOREN, model_pre
from .modely import Koncept, StavClanku, VyberTem

PROMPTY = Path(__file__).parent / "prompty"
ZASADY = KOREN / "docs" / "REDAKCNE-ZASADY.md"

MAX_ZNAKOV_ZDROJA = 7000
MAX_ZDROJOV = 5


def _prompt(nazov: str) -> str:
    return (PROMPTY / f"{nazov}.md").read_text(encoding="utf-8")


def _bez_znaciek(text: str) -> str:
    """Zdrojový text nesmie vedieť predčasne ukončiť svoj obal."""
    return re.sub(r"</?\s*zdroj[^>]*>", "", text, flags=re.IGNORECASE)


# ---------- výber tém ----------


def sprava_vyberu(kandidati: list[dict], pocet: int) -> str:
    riadky = []
    for i, t in enumerate(kandidati, 1):
        titulky = "; ".join(_bez_znaciek(s["titulok"])[:140] for s in t["spravy"][:3])
        riadky.append(f"{i}. [{t['pocet_zdrojov']} zdroje, HN {t['signal_hn']}] {titulky}")
    return f"Vyber {pocet} tém z tohto zoznamu.\n\n<temy>\n" + "\n".join(riadky) + "\n</temy>"


def vyber_temy(kandidati: list[dict], pocet: int, model: Any | None = None, config: dict | None = None) -> list[StavClanku]:
    model = model or model_pre("vyber_tem", VyberTem)
    vyber: VyberTem = model.invoke(
        [SystemMessage(_prompt("vyber_tem")), HumanMessage(sprava_vyberu(kandidati, pocet))], config=config
    )
    stavy, pouzite = [], set()
    for v in vyber.vybrane:
        # Model môže vrátiť číslo mimo rozsahu alebo duplicitu: také položky zahodíme.
        if not (1 <= v.cislo <= len(kandidati)) or v.cislo in pouzite:
            continue
        pouzite.add(v.cislo)
        stavy.append(StavClanku(tema=kandidati[v.cislo - 1], sekcia_navrh=v.sekcia, dovod_vyberu=v.dovod))
    return stavy[:pocet]


# ---------- autorka ----------


def sprava_autorky(stav: StavClanku) -> str:
    tema = stav["tema"]
    spravy = sorted(tema["spravy"], key=lambda s: len(s.get("text", "")), reverse=True)[:MAX_ZDROJOV]
    casti = [
        f"Téma: {_bez_znaciek(tema['titulok'])}",
        f"Navrhovaná sekcia: {stav.get('sekcia_navrh', 'podľa vlastného úsudku')}",
        "",
    ]
    for s in spravy:
        text = _bez_znaciek(s.get("text") or s.get("zhrnutie") or "")[:MAX_ZNAKOV_ZDROJA]
        casti.append(
            f'<zdroj nazov="{s["zdroj_nazov"]}" url="{s["url"]}" publikovane="{s["publikovane"]}">\n'
            f"Titulok: {_bez_znaciek(s['titulok'])}\n\n{text}\n</zdroj>\n"
        )
    return "\n".join(casti)


def skontroluj_koncept(k: Koncept, tema: dict) -> tuple[Koncept, list[str]]:
    """Mechanické kontroly, ktoré nepotrebujú jazykový model."""
    upozornenia: list[str] = []
    zname = {s["url"] for s in tema["spravy"]}

    nezname = [u for u in k.pouzite_zdroje if u not in zname]
    if nezname:
        upozornenia.append(f"Autorka uviedla zdroje, ktoré nedostala: {nezname}. Boli odstránené.")
    zdroje = [u for u in k.pouzite_zdroje if u in zname] or sorted(zname)
    if len(zdroje) < 2 and len(zname) >= 2:
        upozornenia.append("Článok čerpá len z jedného zdroja, hoci ich bolo viac.")

    if len(k.titulok) > 110:
        upozornenia.append(f"Titulok má {len(k.titulok)} znakov, limit webu je 110.")
    if not (40 <= len(k.perex) <= 320):
        upozornenia.append(f"Perex má {len(k.perex)} znakov, web vyžaduje 40 až 320.")
    slov = len(k.telo.split())
    if not (250 <= slov <= 800):
        upozornenia.append(f"Telo má {slov} slov, cieľ je 350 až 600.")
    if re.search(r"^#\s", k.telo, flags=re.MULTILINE):
        upozornenia.append("Telo obsahuje nadpis prvej úrovne.")

    k = k.model_copy(update={"pouzite_zdroje": zdroje, "tagy": [t.strip() for t in k.tagy if t.strip()][:5]})
    return k, upozornenia


def uzol_autorka(model: Any | None = None) -> Callable[[StavClanku], dict]:
    def autorka(stav: StavClanku) -> dict:
        m = model or model_pre("autorka", Koncept)
        system = _prompt("autorka").replace("{zasady}", ZASADY.read_text(encoding="utf-8"))
        koncept: Koncept = m.invoke([SystemMessage(system), HumanMessage(sprava_autorky(stav))])
        koncept, upozornenia = skontroluj_koncept(koncept, stav["tema"])
        return {"koncept": koncept, "upozornenia": upozornenia}

    return autorka


def zostav_graf(model_autorky: Any | None = None):
    g = StateGraph(StavClanku)
    g.add_node("autorka", uzol_autorka(model_autorky))
    g.add_edge(START, "autorka")
    g.add_edge("autorka", END)
    return g.compile()
