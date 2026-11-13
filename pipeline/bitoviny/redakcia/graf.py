"""Redakčný graf v LangGraphe.

    START -> autorka -> factcheck -+-> korektura -> fotoeditor -> END
                           ^       |
                           +- oprava (najviac MAX_OPRAV kôl)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from ..llm import KOREN, model_pre
from .factcheck import Factcheck, treba_opravit, zostav_nalezy
from .korektura import Korektura, languagetool, pevne_pravidla, rozdiel, vykonaj
from .obrazky import Dopyty, hladaj_alternativy, odporucanie, posud_obrazky
from .modely import Koncept, StavClanku, VyberTem

PROMPTY = Path(__file__).parent / "prompty"
ZASADY = KOREN / "docs" / "REDAKCNE-ZASADY.md"

MAX_ZNAKOV_ZDROJA = 7000
MAX_ZDROJOV = 5
MAX_OPRAV = 2  # koľkokrát smie factchecker vrátiť článok autorke


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
    # Článok má stáť na aspoň dvoch nezávislých zdrojoch. Jednozdrojové témy sa
    # modelu ponúknu len vtedy, keď viaczdrojových nie je dosť.
    viac = [t for t in kandidati if t.get("pocet_zdrojov", 0) >= 2]
    if len(viac) >= pocet:
        kandidati = viac
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
    # Modely pri prepise adresy menia veľkosť písmen alebo koncové lomítko, preto
    # porovnávame normalizovane a do článku dávame pôvodnú adresu zo Zberača.
    def norm(u: str) -> str:
        return u.strip().lower().rstrip("/")

    zname = {norm(s["url"]): s["url"] for s in tema["spravy"]}

    nezname = [u for u in k.pouzite_zdroje if norm(u) not in zname]
    if nezname:
        upozornenia.append(f"Autorka uviedla zdroje, ktoré nedostala: {nezname}. Boli odstránené.")
    zdroje = list(dict.fromkeys(zname[norm(u)] for u in k.pouzite_zdroje if norm(u) in zname)) or sorted(zname.values())
    if len(zdroje) < 2 and len(zname) >= 2:
        upozornenia.append("Článok čerpá len z jedného zdroja, hoci ich bolo viac.")
    if len(zname) < 2:
        upozornenia.append("Téma má len jeden zdroj. Redakčné zásady žiadajú aspoň dva, zvážte doplnenie alebo zahodenie.")

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


# ---------- factcheck a oprava ----------


def zdrojove_texty(tema: dict) -> list[str]:
    # Adresa je súčasť toho, čo model vidí, a jej slug býva plný titulok s číslami.
    return ["\n".join([s["titulok"], s["url"], s.get("zhrnutie", ""), s.get("text", "")]) for s in tema["spravy"]]


def koncept_ako_text(k: Koncept) -> str:
    return "\n".join(["<koncept>", f"Titulok: {k.titulok}", "", f"Perex: {k.perex}", "", k.telo, "</koncept>"])


def uzol_factcheck(model: Any | None = None) -> Callable[[StavClanku], dict]:
    def factcheck(stav: StavClanku) -> dict:
        m = model or model_pre("factcheck", Factcheck)
        k = stav["koncept"]
        sprava = "\n".join([sprava_autorky(stav), koncept_ako_text(k)])
        fc: Factcheck = m.invoke([SystemMessage(_prompt("factcheck")), HumanMessage(sprava)])
        nalezy = zostav_nalezy(fc, k, zdrojove_texty(stav["tema"]))
        kolo = stav.get("kolo", 0) + 1
        zaznam = {
            "kolo": kolo,
            "tvrdeni": len(fc.tvrdenia),
            "potvrdenych": sum(t.verdikt == "potvrdene" for t in fc.tvrdenia),
            "chyb": sum(n.zavaznost == "chyba" for n in nalezy),
            "upozorneni": sum(n.zavaznost == "upozornenie" for n in nalezy),
        }
        return {"factcheck": fc, "nalezy": nalezy, "kolo": kolo, "historia": stav.get("historia", []) + [zaznam]}

    return factcheck


def po_factchecku(stav: StavClanku) -> str:
    if treba_opravit(stav["nalezy"]) and stav["kolo"] <= MAX_OPRAV:
        return "oprava"
    return "koniec"


def sprava_opravy(stav: StavClanku) -> str:
    riadky = []
    for i, n in enumerate((n for n in stav["nalezy"] if n.zavaznost == "chyba"), 1):
        riadky += [
            f"{i}. {n.text}",
            f"   Problém: {n.komentar}",
            f"   Návrh: {n.navrh_opravy or 'opraviť podľa zdroja'}",
        ]
    return "\n".join([sprava_autorky(stav), koncept_ako_text(stav["koncept"]), "<nalezy>", *riadky, "</nalezy>"])


def uzol_oprava(model: Any | None = None) -> Callable[[StavClanku], dict]:
    def oprava(stav: StavClanku) -> dict:
        m = model or model_pre("autorka", Koncept)
        system = _prompt("oprava").replace("{zasady}", ZASADY.read_text(encoding="utf-8"))
        koncept: Koncept = m.invoke([SystemMessage(system), HumanMessage(sprava_opravy(stav))])
        koncept, upozornenia = skontroluj_koncept(koncept, stav["tema"])
        return {"koncept": koncept, "upozornenia": upozornenia}

    return oprava


# ---------- korektúra ----------


def clanok_ako_text(k: Koncept) -> str:
    return "\n".join(["<clanok>", f"[titulok] {k.titulok}", "", f"[perex] {k.perex}", "", "[telo]", k.telo, "</clanok>"])


def uzol_korektura(model: Any | None = None, jazykova_sluzba: Callable | None = languagetool) -> Callable[[StavClanku], dict]:
    """Tri vrstvy: jazykový model, pevné pravidlá a LanguageTool. Každá úprava prejde
    tou istou kontrolou (čísla, mená, rozsah) a vykoná sa nad textom po predošlej vrstve."""

    def korektura(stav: StavClanku) -> dict:
        pred = stav["koncept"]
        aktualny, vysledky, chyba = pred, [], ""
        try:
            m = model or model_pre("korektura", Korektura)
            navrh: Korektura = m.invoke([SystemMessage(_prompt("korektura")), HumanMessage(clanok_ako_text(pred))])
            aktualny, vysledky = vykonaj(aktualny, navrh)
        except Exception as e:  # výpadok korektorky nesmie zahodiť overený článok
            chyba = f"Jazykový model neprebehol: {str(e)[:200]}"

        aktualny, z_pravidiel = vykonaj(aktualny, Korektura(upravy=pevne_pravidla(aktualny)))
        z_lt, podozrive = [], []
        if jazykova_sluzba is not None:
            upravy_lt, podozrive = jazykova_sluzba(aktualny)
            aktualny, z_lt = vykonaj(aktualny, Korektura(upravy=upravy_lt))

        vysledok = {
            "upravy": [v.model_dump() for v in [*vysledky, *z_pravidiel, *z_lt]],
            "podozrive": podozrive,
            "diff": rozdiel(pred, aktualny),
        }
        if chyba:
            vysledok["chyba"] = chyba
        return {"koncept": aktualny, "korektura": vysledok}

    return korektura


# ---------- fotoeditor ----------


def uzol_fotoeditor(model: Any | None = None, hladac: Callable[[list[str]], list] | None = None) -> Callable[[StavClanku], dict]:
    def fotoeditor(stav: StavClanku) -> dict:
        k = stav["koncept"]
        povodne = posud_obrazky(stav["tema"], firmy=set(k.tagy))
        try:
            m = model or model_pre("fotoeditor", Dopyty)
            vstup = f"Titulok: {k.titulok}\nPerex: {k.perex}\nTagy: {', '.join(k.tagy)}"
            dopyty = [d.strip() for d in m.invoke([SystemMessage(_prompt("fotoeditor")), HumanMessage(vstup)]).dopyty if d.strip()]
        except Exception:
            dopyty = k.tagy[:2]  # bez modelu hľadáme aspoň podľa tagov
        alternativy = (hladac or hladaj_alternativy)(dopyty)
        return {
            "obrazky": {
                "odporucanie": odporucanie(povodne, alternativy),
                "povodne": [p.model_dump() for p in povodne],
                "dopyty": dopyty,
                "alternativy": [a.model_dump() for a in alternativy],
                "prompt_ilustracie": k.prompt_ilustracie,
            }
        }

    return fotoeditor


def zostav_graf(
    model_autorky: Any | None = None,
    jazykova_sluzba: Callable | None = languagetool,
    model_factchecku: Any | None = None,
    model_korektury: Any | None = None,
    model_fotoeditora: Any | None = None,
    hladac_obrazkov: Callable[[list[str]], list] | None = None,
):
    g = StateGraph(StavClanku)
    g.add_node("autorka", uzol_autorka(model_autorky))
    g.add_node("factcheck", uzol_factcheck(model_factchecku))
    g.add_node("oprava", uzol_oprava(model_autorky))
    g.add_node("korektura", uzol_korektura(model_korektury, jazykova_sluzba))
    g.add_node("fotoeditor", uzol_fotoeditor(model_fotoeditora, hladac_obrazkov))
    g.add_edge(START, "autorka")
    g.add_edge("autorka", "factcheck")
    g.add_conditional_edges("factcheck", po_factchecku, {"oprava": "oprava", "koniec": "korektura"})
    g.add_edge("oprava", "factcheck")
    g.add_edge("korektura", "fotoeditor")
    g.add_edge("fotoeditor", END)
    return g.compile()
