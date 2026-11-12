"""Jazykové modely podľa roly, so zálohami, a napojenie na Langfuse."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

KOREN = Path(__file__).resolve().parents[2]
MODELY_YAML = KOREN / "config" / "modely.yaml"

load_dotenv(KOREN / ".env")
# Langfuse SDK číta adresu z LANGFUSE_HOST alebo LANGFUSE_BASE_URL podľa verzie.
if os.getenv("LANGFUSE_HOST") and not os.getenv("LANGFUSE_BASE_URL"):
    os.environ["LANGFUSE_BASE_URL"] = os.environ["LANGFUSE_HOST"]


@lru_cache
def konfiguracia() -> dict:
    return yaml.safe_load(MODELY_YAML.read_text(encoding="utf-8"))["roly"]


def _vytvor(spec: dict, teplota: float):
    provider, model = spec["provider"], spec["model"]
    # max_retries=1: pri chybe alebo limite radšej rýchlo prejsť na zálohu.
    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        # Novšie modely Gemini teplotu ignorujú, preto sa neposiela.
        return ChatGoogleGenerativeAI(model=model, max_retries=1, timeout=75)
    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=model, temperature=teplota, max_retries=1)
    if provider == "openrouter":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model,
            temperature=teplota,
            max_retries=1,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
    raise ValueError(f"Neznámy provider: {provider}")


def model_pre(rola: str, schema: Any | None = None):
    """Model pre danú rolu. Ak je daná schéma, vracia overený štruktúrovaný výstup."""
    cfg = konfiguracia()[rola]
    teplota = cfg.get("teplota", 0.3)
    modely = []
    for s in cfg["modely"]:
        m = _vytvor(s, teplota)
        if schema is not None:
            kw = {"method": s["metoda"]} if s.get("metoda") else {}
            m = m.with_structured_output(schema, **kw)
        modely.append(m)
    retazec = modely[0].with_fallbacks(modely[1:]) if len(modely) > 1 else modely[0]
    return retazec.with_config(run_name=rola)


def nazvy_modelov(rola: str) -> list[str]:
    return [f"{s['provider']}:{s['model']}" for s in konfiguracia()[rola]["modely"]]


def langfuse_klient():
    """Vráti klienta Langfuse, alebo None, keď kľúče nie sú nastavené."""
    if not (os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")):
        return None
    from langfuse import get_client

    return get_client()
