"""Koncept ako pull request: python -m bitoviny.redakcia.publikacia data/koncepty/.../x.md

Z uloženého konceptu vytvorí vetvu koncept/<dátum>-<slug> s dvoma súbormi:

    content/clanky/<slug>.md       článok v tvare, aký číta web, so zástupným obrázkom
    redakcia/spravy/<slug>.json    redakčná správa pre editora (factcheck, korektúra, obrázky)

a otvorí pull request. Zverejniť ho smie až človek v redakčnom rozhraní.
Token sa berie z premennej GITHUB_TOKEN, repozitár z GITHUB_REPOSITORY.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml

log = logging.getLogger("publikacia")

REPO = os.getenv("GITHUB_REPOSITORY", "valooo-hero/bitoviny")
API = "https://api.github.com"
ZASTUPNY_OBRAZOK = "/obrazky/zastupny.jpg"
PREDPONA_VETVY = "koncept/"


def bez_html(text: str) -> str:
    """Markdown na webe vykresľuje aj surové HTML. Text od modelu, ktorý čítal cudzie
    weby, ho obsahovať nesmie."""
    # Len skutočné značky: nerovnosť „2 < 3“ musí ostať.
    text = re.sub(r"</?[a-zA-Z!][^>]{0,500}>", "", text)
    # Odkazy smú viesť len na web, e-mail alebo v rámci stránky (žiadne javascript: a podobne).
    return re.sub(r"\]\(\s*(?!https?:|mailto:|/|#)(?:[^()]|\([^()]*\))*\)", "]()", text, flags=re.IGNORECASE)


def rozdel_koncept(markdown: str) -> tuple[dict, str]:
    hlavicka = re.match(r"^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)", markdown)
    if hlavicka is None:
        raise ValueError("Článok nemá platnú YAML hlavičku.")
    return yaml.safe_load(hlavicka[1]), markdown[hlavicka.end():].strip()


def clanok_pre_web(fm: dict, telo: str, teraz: datetime) -> str:
    """Frontmatter podľa src/content.config.ts. Bez odkazu na trace (je súkromný)
    a bez schvalil: ten doplní redakčné rozhranie pri zverejnení."""
    web = {
        "title": bez_html(fm["title"]),
        "perex": bez_html(fm["perex"]),
        "sekcia": fm["sekcia"],
        "tagy": [bez_html(t) for t in fm.get("tagy", [])],
        "publikovane": teraz.isoformat(timespec="seconds"),
        "obrazok": {
            "src": ZASTUPNY_OBRAZOK,
            "alt": "Zástupný obrázok, čaká na výber editora",
            "popisok": "Obrázok čaká na výber editora.",
            "kredit": "Bitoviny",
            "licencia": "vlastná ilustrácia",
        },
        "redaktori": {k: v for k, v in fm.get("redaktori", {}).items() if k in ("autor", "factcheck", "korektura")},
        "zdroje": fm["zdroje"],
    }
    return "---\n" + yaml.safe_dump(web, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n" + bez_html(telo) + "\n"


def redakcna_sprava(fm: dict, slug: str, telo: str = "") -> dict:
    k = fm.get("koncept", {})
    return {
        "slug": slug,
        "datum_sprav": k.get("datum_sprav"),
        "dovod_vyberu": k.get("dovod_vyberu", ""),
        "poznamky_pre_editora": k.get("poznamky_pre_editora", ""),
        "upozornenia": k.get("upozornenia", []),
        "factcheck": k.get("factcheck"),
        "korektura": k.get("korektura"),
        "obrazky": k.get("obrazky"),
        "prompt_ilustracie": k.get("prompt_ilustracie", ""),
        "trace": fm.get("trace"),
        # Text tak, ako ho odovzdali agenti. Porovnaním so zverejnenou verziou
        # vzniká miera zásahov editora na stránke Ako to funguje.
        "text_agentov": {"titulok": bez_html(fm["title"]), "perex": bez_html(fm["perex"]), "telo": bez_html(telo).strip()},
    }


def popis_pr(fm: dict, sprava: dict) -> str:
    fc, kor, obr = sprava.get("factcheck") or {}, sprava.get("korektura") or {}, sprava.get("obrazky") or {}
    kola = fc.get("kola", [])
    riadky = [
        "Koncept pripravený redakčnou pipeline. **Nezlučovať ručne**: zverejňuje sa v redakčnom rozhraní `/admin/`.",
        "",
        f"- **Sekcia:** {fm['sekcia']}",
        f"- **Zdroje:** {len(fm['zdroje'])}",
        f"- **Factcheck:** {len(kola)} kolo/kolá, neuzavretých nálezov: {len(fc.get('otvorene_nalezy', []))}",
        f"- **Korektúra:** vykonaných úprav: {sum(u['stav'] == 'vykonana' for u in kor.get('upravy', []))}",
        f"- **Obrázok:** {(obr.get('odporucanie') or {}).get('poznamka', 'čaká na výber')}",
    ]
    if sprava.get("upozornenia"):
        riadky += ["", "**Upozornenia:**", *[f"- {u}" for u in sprava["upozornenia"]]]
    return "\n".join(riadky)


class GitHub:
    def __init__(self, token: str | None, repo: str = REPO, *, transport=None):
        self.repo = repo
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "bitoviny-pipeline"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.http = httpx.Client(base_url=f"{API}/repos/{repo}", headers=headers, timeout=20, transport=transport)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.http.close()

    def _get(self, cesta: str) -> httpx.Response:
        for pokus in range(3):
            try:
                odpoved = self.http.get(cesta)
            except httpx.TransportError:
                if pokus == 2:
                    raise
                time.sleep(2 ** pokus)
                continue
            retry_after = odpoved.headers.get("Retry-After")
            vycerpany_limit = odpoved.headers.get("X-RateLimit-Remaining") == "0"
            retry = odpoved.status_code in {429, 500, 502, 503, 504} or (
                odpoved.status_code == 403 and (retry_after is not None or vycerpany_limit)
            )
            if not retry or pokus == 2:
                return odpoved
            if retry_after and retry_after.isdigit():
                cakanie = int(retry_after)
            elif vycerpany_limit and odpoved.headers.get("X-RateLimit-Reset", "").isdigit():
                cakanie = max(0, int(odpoved.headers["X-RateLimit-Reset"]) - time.time())
            elif odpoved.status_code in {403, 429}:
                return odpoved
            else:
                cakanie = 2 ** pokus
            if cakanie > 20:
                return odpoved
            time.sleep(cakanie)
        raise RuntimeError("GitHub neodpovedal.")

    def citaj(self, cesta: str) -> dict:
        return self._ok(self._get(cesta))

    def strany(self, cesta: str):
        cakajuce = set()
        while cesta:
            if cesta in cakajuce:
                raise RuntimeError("GitHub zopakoval adresu pri stránkovaní.")
            cakajuce.add(cesta)
            odpoved = self._get(cesta)
            strana = self._ok(odpoved)
            if not isinstance(strana, list):
                raise RuntimeError("GitHub nevrátil zoznam záznamov.")
            yield from strana
            dalsia = odpoved.links.get("next", {}).get("url")
            if dalsia:
                url = httpx.URL(dalsia)
                if url.scheme != "https" or url.host != "api.github.com" or url.port or url.userinfo:
                    raise RuntimeError("GitHub vrátil neočakávanú adresu ďalšej strany.")
            cesta = dalsia

    def _ok(self, r: httpx.Response) -> dict:
        if r.status_code >= 400:
            raise RuntimeError(f"GitHub {r.request.method} {r.request.url.path}: {r.status_code} {r.text[:300]}")
        return r.json() if r.content else {}

    def vetva_existuje(self, vetva: str) -> bool:
        odpoved = self._get(f"/git/ref/heads/{vetva}")
        if odpoved.status_code == 404:
            return False
        self._ok(odpoved)
        return True

    def vytvor_vetvu(self, vetva: str, zaklad: str = "main") -> None:
        sha = self.citaj(f"/git/ref/heads/{zaklad}")["object"]["sha"]
        self._ok(self.http.post("/git/refs", json={"ref": f"refs/heads/{vetva}", "sha": sha}))

    def zapis_subor(self, cesta: str, obsah: str, vetva: str, sprava: str) -> None:
        self._ok(
            self.http.put(
                f"/contents/{cesta}",
                json={"message": sprava, "branch": vetva, "content": base64.b64encode(obsah.encode("utf-8")).decode("ascii")},
            )
        )

    def otvor_pr(self, vetva: str, titulok: str, popis: str) -> str:
        return self._ok(self.http.post("/pulls", json={"title": titulok, "head": vetva, "base": "main", "body": popis}))["html_url"]


def publikuj(subor: Path, gh: GitHub | None = None, teraz: datetime | None = None) -> str | None:
    """Vytvorí pull request z uloženého konceptu. Vráti jeho adresu, alebo None, ak už existuje."""
    fm, telo = rozdel_koncept(subor.read_text(encoding="utf-8"))
    slug = subor.stem
    datum = (fm.get("koncept") or {}).get("datum_sprav") or datetime.now(timezone.utc).date().isoformat()
    vetva = f"{PREDPONA_VETVY}{datum}-{slug}"[:120]

    gh = gh or GitHub(os.environ["GITHUB_TOKEN"])
    if gh.vetva_existuje(vetva):
        log.info("Vetva %s už existuje, koncept preskakujem.", vetva)
        return None

    teraz = teraz or datetime.now(timezone.utc)
    sprava = redakcna_sprava(fm, slug, telo)
    gh.vytvor_vetvu(vetva)
    gh.zapis_subor(f"content/clanky/{slug}.md", clanok_pre_web(fm, telo, teraz), vetva, f"Koncept: {fm['title']}")
    gh.zapis_subor(
        f"redakcia/spravy/{slug}.json", json.dumps(sprava, ensure_ascii=False, indent=2) + "\n", vetva, "Redakčná správa ku konceptu"
    )
    return gh.otvor_pr(vetva, f"Koncept: {fm['title']}", popis_pr(fm, sprava))


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    subory = [Path(a) for a in (argv if argv is not None else sys.argv[1:])]
    if not subory:
        print(__doc__)
        return 2
    from .archiv import ArchivGitHub, prekazka_zapisu
    from .duplicity import KontrolaTem, z_hlavicky

    with GitHub(os.environ["GITHUB_TOKEN"]) as gh:
        archiv = ArchivGitHub(gh, datetime.now(timezone.utc))
        kontrola = KontrolaTem()
        for s in subory:
            hlavicka, _ = rozdel_koncept(s.read_text(encoding="utf-8"))
            tema = z_hlavicky(f"lokalny:{s.stem}", hlavicka)
            prekazka = prekazka_zapisu(archiv, kontrola, s.stem, tema)
            if prekazka:
                print(f"{s.name}: {prekazka}")
                continue
            url = publikuj(s, gh)
            print(f"{s.name}: {url or 'už existuje'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
