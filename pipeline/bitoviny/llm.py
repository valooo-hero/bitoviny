"""Jazykové modely podľa roly, so zálohami, a napojenie na Langfuse."""

from __future__ import annotations

import logging
import os
import re
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from langchain_core.runnables import RunnableConfig, RunnableLambda
from dotenv import load_dotenv

KOREN = Path(__file__).resolve().parents[2]
MODELY_YAML = KOREN / "config" / "modely.yaml"
log = logging.getLogger(__name__)

load_dotenv(KOREN / ".env")
# Langfuse SDK číta adresu z LANGFUSE_HOST alebo LANGFUSE_BASE_URL podľa verzie.
if os.getenv("LANGFUSE_HOST") and not os.getenv("LANGFUSE_BASE_URL"):
    os.environ["LANGFUSE_BASE_URL"] = os.environ["LANGFUSE_HOST"]


@lru_cache
def konfiguracia() -> dict:
    return yaml.safe_load(MODELY_YAML.read_text(encoding="utf-8"))["roly"]


def _vytvor(spec: dict, teplota: float):
    provider, model = spec["provider"], spec["model"]
    kluce = {
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "deepinfra": "DEEPINFRA_API_KEY",
    }
    if provider not in kluce:
        raise ValueError(f"Nepovolený poskytovateľ textového modelu: {provider}")
    if provider == "openrouter" and not model.endswith(":free"):
        raise ValueError(f"OpenRouter vyžaduje konkrétny model s príponou :free: {model}")
    kluc = os.getenv(kluce[provider])
    if not kluc or not kluc.strip():
        return None

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model, api_key=kluc, vertexai=False, max_retries=1, timeout=75)
    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=model, api_key=kluc, temperature=teplota, max_retries=1, timeout=75)

    from langchain_openai import ChatOpenAI

    if provider == "openai":
        return ChatOpenAI(
            model=model,
            api_key=kluc,
            base_url="https://api.openai.com/v1",
            use_responses_api=True,
            reasoning={"effort": spec.get("reasoning", "medium")},
            verbosity=spec.get("verbosity", "low"),
            max_tokens=spec.get("max_output_tokens", 8192),
            store=False,
            timeout=180,
            max_retries=1,
        )
    if provider == "deepinfra":
        return ChatOpenAI(
            model=model,
            api_key=kluc,
            base_url="https://api.deepinfra.com/v1/openai",
            temperature=teplota,
            timeout=120,
            max_retries=1,
        )

    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=kluc,
        model=model,
        temperature=teplota,
        max_retries=1,
        timeout=75,
        extra_body={"provider": {"require_parameters": True, "max_price": {"prompt": 0, "completion": 0}}},
    )


def _over_vystup(vystup):
    # Pri chýbajúcom volaní nástroja môže parser LangChain vrátiť None.
    if vystup is None:
        raise ValueError("Model nevrátil požadovaný štruktúrovaný výstup.")
    return vystup


def _pokus_modelu(model, rola: str, provider: str, nazov: str):
    def spusti(spravy, config: RunnableConfig):
        for pokus in range(2):
            try:
                return model.invoke(spravy, config=config)
            except Exception as chyba:
                stav = getattr(chyba, "status_code", None) or getattr(chyba.__cause__, "code", None)
                detail = f"HTTP {stav}" if isinstance(stav, int) else type(chyba).__name__
                if type(chyba) is ValueError:
                    detail = str(chyba).splitlines()[0][:180] if str(chyba) else detail
                log.warning("%s | %s:%s | %s", rola, provider, nazov, detail)
                if pokus or rola != "kontrola_duplicit" or provider != "google":
                    raise
                sprava = str(chyba)
                if "429 RESOURCE_EXHAUSTED" not in sprava or "per minute" not in sprava:
                    raise
                limit = re.search(r"Please retry in (\d+(?:\.\d+)?)s", sprava)
                if limit is None or not 0 <= float(limit[1]) <= 60:
                    raise
                pauza = float(limit[1]) + 1
                log.info("%s | %s | opakovanie dávky o %.1f s", rola, nazov, pauza)
                time.sleep(pauza)

    return RunnableLambda(spusti)


def model_pre(rola: str, schema: Any | None = None, *, so_zdrojom: bool = False, over_vystup=None):
    """Model pre danú rolu. Ak je daná schéma, vracia overený štruktúrovaný výstup."""
    cfg = konfiguracia()[rola]
    teplota = cfg.get("teplota", 0.3)
    modely = []
    for s in cfg["modely"]:
        m = _vytvor(s, teplota)
        if m is None:
            continue
        if schema is not None:
            kw = {"method": s["metoda"]} if s.get("metoda") else {}
            m = m.with_structured_output(schema, **kw) | RunnableLambda(_over_vystup)
        if over_vystup is not None:
            def over(spravy, m=m):
                vystup = m.invoke(spravy)
                over_vystup(vystup, spravy)
                return vystup

            m = RunnableLambda(over)
        if so_zdrojom:
            # Zdroj sa pripája až po úspešnom overení výstupu konkrétneho modelu.
            zdroj = f"{s['model']} ({s['provider']})"
            m = m | RunnableLambda(lambda vystup, zdroj=zdroj: (vystup, zdroj))
        modely.append(_pokus_modelu(m, rola, s["provider"], s["model"]))
    if not modely:
        raise RuntimeError(f"Pre rolu {rola} chýba API kľúč poskytovateľa.")
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
