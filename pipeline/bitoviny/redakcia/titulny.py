"""Titulná ilustrácia z Cloudflare Workers AI vo formáte používanom na webe."""
from __future__ import annotations

import base64
import os
import re
from io import BytesIO

import httpx
from PIL import Image, ImageOps

MODEL = "@cf/black-forest-labs/flux-1-schnell"
MAX_BAJTOV = 6 * 1024 * 1024


def vygeneruj_titulny(prompt: str, *, klient: httpx.Client | None = None) -> bytes:
    ucet = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    token = os.getenv("CLOUDFLARE_API_TOKEN", "")
    if not re.fullmatch(r"[0-9a-fA-F]{32}", ucet) or not token:
        raise RuntimeError("Chýba platné CLOUDFLARE_ACCOUNT_ID alebo CLOUDFLARE_API_TOKEN.")
    prompt = prompt.strip()
    if not prompt:
        raise RuntimeError("Koncept nemá zadanie na titulnú ilustráciu.")

    if klient is None:
        with httpx.Client(timeout=85) as http:
            return vygeneruj_titulny(prompt, klient=http)

    url = f"https://api.cloudflare.com/client/v4/accounts/{ucet}/ai/run/{MODEL}"
    odpoved = klient.post(
        url, headers={"Authorization": f"Bearer {token}"}, json={"prompt": prompt[:2048], "steps": 4},
    )
    if not odpoved.is_success:
        raise RuntimeError(f"Workers AI pri generovaní obrázka vrátil HTTP {odpoved.status_code}.")
    try:
        data = odpoved.json()
        obrazok = (data.get("result") or {}).get("image")
        if data.get("success") is not True or not obrazok or len(obrazok) > MAX_BAJTOV * 4 // 3 + 4:
            raise ValueError("Chýbajúce alebo príliš veľké obrazové dáta.")
        bajty = base64.b64decode(obrazok, validate=True)
        if len(bajty) > MAX_BAJTOV:
            raise ValueError("Príliš veľký obrázok.")
        with Image.open(BytesIO(bajty)) as original:
            if not (256 <= original.width <= 2048 and 256 <= original.height <= 2048):
                raise ValueError("Neočekávané rozmery obrázka.")
            titulny = ImageOps.fit(original.convert("RGB"), (1200, 675), Image.Resampling.LANCZOS)
            vystup = BytesIO()
            titulny.save(vystup, "WEBP", quality=75)
            return vystup.getvalue()
    except (AttributeError, TypeError, ValueError, OSError, Image.DecompressionBombError) as e:
        raise RuntimeError("Workers AI nevrátil platný titulný obrázok.") from e
