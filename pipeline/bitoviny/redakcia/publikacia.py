"""Koncept ako pull request: python -m bitoviny.redakcia.publikacia data/koncepty/.../x.md

Z uloženého konceptu vytvorí vetvu koncept/<dátum>-<slug> so súbormi článku:

    content/clanky/<slug>.md       článok v tvare, aký číta web
    redakcia/spravy/<slug>.json    redakčná správa pre editora (factcheck, korektúra, obrázky)

a otvorí pull request. Pripravený titulný obrázok je uložený v tej istej vetve.
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
from urllib.parse import quote

import httpx
import yaml

from .factcheck import cisty_factcheck

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


def clanok_pre_web(
    fm: dict, telo: str, teraz: datetime, *, obrazok: dict | None = None, schvaleny: bool = False,
) -> str:
    """Frontmatter podľa schémy obsahovej kolekcie Astro."""
    redaktori = {k: v for k, v in fm.get("redaktori", {}).items() if k in ("autor", "factcheck", "korektura")}
    if schvaleny:
        redaktori["schvalil"] = "redakcia"
    web = {
        "title": bez_html(fm["title"]),
        "perex": bez_html(fm["perex"]),
        "sekcia": fm["sekcia"],
        "tagy": [bez_html(t) for t in fm.get("tagy", [])],
        "publikovane": teraz.isoformat(timespec="seconds"),
        "obrazok": obrazok or {
            "src": ZASTUPNY_OBRAZOK,
            "alt": "Zástupný obrázok, čaká na výber editora",
            "popisok": "Obrázok čaká na výber editora.",
            "kredit": "Bitoviny",
            "licencia": "vlastná ilustrácia",
        },
        "redaktori": redaktori,
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

    def zapis_koncept(self, vetva: str, subory: dict[str, str | bytes], sprava: str) -> str:
        """Článok, obrázok a redakčná správa sa vo vetve objavia naraz."""
        zaklad = self.citaj("/git/ref/heads/main")["object"]["sha"]
        povodny_strom = self.citaj(f"/git/commits/{zaklad}")["tree"]["sha"]
        polozky = []
        for cesta, obsah in subory.items():
            polozka = {"path": cesta, "mode": "100644", "type": "blob"}
            if isinstance(obsah, bytes):
                blob = {"encoding": "base64", "content": base64.b64encode(obsah).decode("ascii")}
                polozka["sha"] = self._ok(self.http.post("/git/blobs", json=blob))["sha"]
            else:
                polozka["content"] = obsah
            polozky.append(polozka)
        strom = self._ok(self.http.post("/git/trees", json={"base_tree": povodny_strom, "tree": polozky}))["sha"]
        commit = {"message": sprava, "tree": strom, "parents": [zaklad]}
        sha = self._ok(self.http.post("/git/commits", json=commit))["sha"]
        self._ok(self.http.post("/git/refs", json={"ref": f"refs/heads/{vetva}", "sha": sha}))
        return sha

    def otvor_pr(self, vetva: str, titulok: str, popis: str) -> dict:
        pr = {"title": titulok, "head": vetva, "base": "main", "body": popis}
        try:
            odpoved = self.http.post("/pulls", json=pr)
        except httpx.TransportError:
            existujuce = self.otvoreny_pr(vetva)
            if existujuce:
                return existujuce
            raise
        if odpoved.status_code == 422:
            existujuce = self.otvoreny_pr(vetva)
            if existujuce:
                return existujuce
        return self._ok(odpoved)

    def otvoreny_pr(self, vetva: str) -> dict | None:
        vlastnik = self.repo.partition("/")[0]
        head = quote(f"{vlastnik}:{vetva}", safe="")
        return next(self.strany(f"/pulls?state=open&base=main&head={head}"), None)

    def zluc(self, cislo: int, sha: str, titulok: str) -> None:
        cesta = f"/pulls/{cislo}/merge"
        telo = {"merge_method": "squash", "commit_title": f"Článok: {titulok}", "sha": sha}
        for pokus in range(6):
            try:
                odpoved = self.http.put(cesta, json=telo)
            except httpx.TransportError:
                if self.citaj(f"/pulls/{cislo}")["merged"]:
                    return
                raise
            if odpoved.status_code not in {405, 409} or pokus == 5:
                if not self._ok(odpoved).get("merged"):
                    raise RuntimeError(f"Pull request #{cislo} sa nezlúčil.")
                return
            stav = self.citaj(f"/pulls/{cislo}")
            if stav["merged"]:
                return
            if stav["state"] != "open" or stav["head"]["sha"] != sha:
                raise RuntimeError(f"Pull request #{cislo} sa pred zverejnením zmenil.")
            time.sleep(2)


def publikuj(
    subor: Path, gh: GitHub | None = None, teraz: datetime | None = None,
    *, ilustracia: bytes | None = None, automaticky: bool = False,
) -> str | None:
    """Vytvorí pull request. Pri povolenej automatizácii môže pripravený článok aj zlúčiť."""
    if gh is None:
        with GitHub(os.environ["GITHUB_TOKEN"]) as klient:
            return publikuj(subor, klient, teraz, ilustracia=ilustracia, automaticky=automaticky)
    fm, telo = rozdel_koncept(subor.read_text(encoding="utf-8"))
    slug = subor.stem
    datum = (fm.get("koncept") or {}).get("datum_sprav") or datetime.now(timezone.utc).date().isoformat()
    vetva = f"{PREDPONA_VETVY}{datum}-{slug}"[:120]

    if gh.vetva_existuje(vetva):
        log.info("Vetva %s už existuje, koncept preskakujem.", vetva)
        return None

    teraz = teraz or datetime.now(timezone.utc)
    sprava = redakcna_sprava(fm, slug, telo)
    titulok, perex = fm["title"], fm["perex"]
    platny_text = (
        10 <= len(titulok) <= 110 and 40 <= len(perex) <= 320
        and len(telo) >= 200 and bool(fm["zdroje"])
        and all(bez_html(text) == text for text in (titulok, perex, telo))
    )
    titulok = bez_html(titulok)
    schvaleny = bool(automaticky and ilustracia and platny_text and cisty_factcheck(sprava["factcheck"]))
    subory: dict[str, str | bytes] = {}
    obrazok = None
    if ilustracia:
        cesta = f"/obrazky/{slug}.webp"
        obrazok = {
            "src": cesta, "alt": "Ilustrácia k článku: " + titulok,
            "popisok": "Ilustračný obrázok.", "kredit": "Bitoviny / FLUX.1-schnell",
            "licencia": "vygenerované AI", "ai": True,
        }
        subory[f"public{cesta}"] = ilustracia
    subory[f"content/clanky/{slug}.md"] = clanok_pre_web(fm, telo, teraz, obrazok=obrazok, schvaleny=schvaleny)
    subory[f"redakcia/spravy/{slug}.json"] = json.dumps(sprava, ensure_ascii=False, indent=2) + "\n"

    sha = gh.zapis_koncept(vetva, subory, f"Koncept: {titulok}")
    pr = gh.otvor_pr(vetva, f"Koncept: {titulok}", popis_pr(fm, sprava))
    if schvaleny:
        gh.zluc(pr["number"], sha, titulok)
        log.info("Zverejnený článok: %s", slug)
    return pr["html_url"]


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
