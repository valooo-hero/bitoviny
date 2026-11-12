"""Zoskupenie správ o tej istej udalosti a výber najdôležitejších tém."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence

import numpy as np

from .modely import Sprava

Embedder = Callable[[Sequence[str]], np.ndarray]

MODEL = "BAAI/bge-small-en-v1.5"
PRAH_TEMY = 0.74  # kosínusová podobnosť, od ktorej sú dve správy tá istá téma
PRAH_SIGNALU = 0.70


def lokalny_embedder(model: str = MODEL) -> Embedder:
    """Malý ONNX model bežiaci lokálne, bez API a bez limitov."""
    from fastembed import TextEmbedding

    te = TextEmbedding(model_name=model)

    def embed(texty: Sequence[str]) -> np.ndarray:
        return np.array(list(te.embed(list(texty))), dtype=np.float32)

    return embed


def _normalizuj(m: np.ndarray) -> np.ndarray:
    normy = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.clip(normy, 1e-9, None)


def text_na_embedding(s: Sprava) -> str:
    return f"{s.titulok}. {(s.zhrnutie or s.text)[:400]}"


@dataclass
class Tema:
    spravy: list[Sprava]
    signal: int = 0  # počet zhôd so signálnymi zdrojmi (Hacker News)
    skore: float = 0.0
    centroid: np.ndarray | None = field(default=None, repr=False)

    @property
    def zdroje(self) -> list[str]:
        return sorted({s.zdroj for s in self.spravy})

    @property
    def titulok(self) -> str:
        return max(self.spravy, key=lambda s: len(s.text)).titulok

    def na_dict(self) -> dict:
        return {
            "titulok": self.titulok,
            "skore": round(self.skore, 3),
            "pocet_zdrojov": len(self.zdroje),
            "zdroje": self.zdroje,
            "signal_hn": self.signal,
            "spravy": [s.na_dict() for s in sorted(self.spravy, key=lambda s: s.publikovane)],
        }


def zoskup(spravy: list[Sprava], embed: Embedder, prah: float = PRAH_TEMY) -> list[Tema]:
    """Úplné spájanie (complete linkage): do témy patrí správa len vtedy,
    keď je dosť podobná každej správe, ktorá v nej už je. Bráni to reťazeniu
    nesúvisiacich správ cez spoločné slová."""
    if not spravy:
        return []
    vektory = _normalizuj(embed([text_na_embedding(s) for s in spravy]))
    podobnost = vektory @ vektory.T

    skupiny: list[list[int]] = []
    poradie = sorted(range(len(spravy)), key=lambda i: spravy[i].publikovane)
    for i in poradie:
        najlepsia, najlepsie = None, prah
        for g, clenovia in enumerate(skupiny):
            minimum = float(podobnost[i, clenovia].min())
            if minimum >= najlepsie:
                najlepsia, najlepsie = g, minimum
        if najlepsia is None:
            skupiny.append([i])
        else:
            skupiny[najlepsia].append(i)

    temy = []
    for clenovia in skupiny:
        c = vektory[clenovia].mean(axis=0)
        temy.append(Tema(spravy=[spravy[i] for i in clenovia], centroid=c / max(np.linalg.norm(c), 1e-9)))
    return temy


def pridaj_signal(temy: list[Tema], signalne: list[Sprava], embed: Embedder, prah: float = PRAH_SIGNALU) -> None:
    """Téma, o ktorej sa hovorí aj na Hacker News, dostane vyššiu váhu."""
    if not temy or not signalne:
        return
    sv = _normalizuj(embed([s.titulok for s in signalne]))
    centroidy = np.stack([t.centroid for t in temy])
    zhody = (centroidy @ sv.T) >= prah
    for t, riadok in zip(temy, zhody):
        t.signal = int(riadok.sum())


def ohodnot(temy: list[Tema]) -> None:
    for t in temy:
        n = len(t.zdroje)
        ma_text = any(len(s.text) > 800 for s in t.spravy)
        # Počet nezávislých zdrojov rozhoduje, signál a dostupnosť textu dolaďujú.
        t.skore = n + 0.5 * min(t.signal, 2) + (0.25 if ma_text else 0.0)


def vyber(temy: list[Tema], pocet: int = 5, min_zdrojov: int = 2) -> list[Tema]:
    """Najprv témy potvrdené viacerými zdrojmi; ak ich je málo, doplnia sa
    jednozdrojové (v článku potom musí byť pôvodný zdroj výslovne uvedený)."""
    ohodnot(temy)
    zoradene = sorted(temy, key=lambda t: (t.skore, max(s.publikovane for s in t.spravy)), reverse=True)
    viac = [t for t in zoradene if len(t.zdroje) >= min_zdrojov]
    jeden = [t for t in zoradene if len(t.zdroje) < min_zdrojov]
    return (viac + jeden)[:pocet]
