"""Živý prehľad publikovaných článkov a otvorených konceptov na GitHube."""
from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath
from urllib.parse import quote

from .duplicity import CLANKY, KontrolaTem, Zaznam, popis_vysledku, publikovane_v_okne, z_hlavicky
from .publikacia import PREDPONA_VETVY, GitHub, rozdel_koncept

CESTA_CLANKU = re.compile(r"^content/clanky/(.+)\.md$")


@dataclass
class Snimka:
    zaznamy: list[Zaznam]
    cesty_main: set[str]


class ArchivGitHub:
    def __init__(self, gh: GitHub, teraz: datetime):
        self.gh = gh
        self.teraz = teraz
        self._hlavicky: dict[str, dict] = {}
        self._koncepty: dict[tuple[int, str], list[tuple[str, str]]] = {}
        self._stromy: dict[str, list[dict]] = {}

    def _hlavicka(self, sha: str) -> dict:
        if sha not in self._hlavicky:
            data = self.gh.citaj(f"/git/blobs/{quote(sha, safe='')}")
            if data["encoding"] != "base64":
                raise RuntimeError("GitHub vrátil nepodporovaný formát článku.")
            markdown = base64.b64decode(data["content"]).decode("utf-8-sig")
            self._hlavicky[sha] = rozdel_koncept(markdown)[0]
        return self._hlavicky[sha]

    def _strom(self, sha: str, rekurzivne: bool = False) -> list[dict]:
        cesta = f"/git/trees/{quote(sha, safe='')}" + ("?recursive=1" if rekurzivne else "")
        if cesta not in self._stromy:
            data = self.gh.citaj(cesta)
            if data["truncated"]:
                raise RuntimeError("GitHub vrátil neúplný strom archívu.")
            self._stromy[cesta] = data["tree"]
        return self._stromy[cesta]

    def _main(self) -> list[dict]:
        commit = self.gh.citaj("/git/ref/heads/main")["object"]["sha"]
        sha_stromu = self.gh.citaj(f"/git/commits/{quote(commit, safe='')}")["tree"]["sha"]
        for priecinok in ("content", "clanky"):
            strom = self._strom(sha_stromu)
            polozka = next((s for s in strom if s["path"] == priecinok and s["type"] == "tree"), None)
            if polozka is None:
                raise RuntimeError(f"V archíve na main chýba priečinok {priecinok}.")
            sha_stromu = polozka["sha"]
        return [s for s in self._strom(sha_stromu, True) if s["type"] == "blob" and s["path"].endswith(".md")]

    def _otvorene(self) -> list[Zaznam]:
        zaznamy = []
        for pr in self.gh.strany("/pulls?state=open&base=main&per_page=100"):
            hlava = pr["head"]
            if not hlava["ref"].startswith(PREDPONA_VETVY) or (hlava["repo"] or {}).get("full_name") != self.gh.repo:
                continue
            kluc = pr["number"], hlava["sha"]
            if kluc not in self._koncepty:
                subory = [
                    (s["filename"], s["sha"]) for s in self.gh.strany(f"/pulls/{pr['number']}/files?per_page=100")
                    if CESTA_CLANKU.fullmatch(s["filename"]) and s["status"] != "removed"
                ]
                if not subory:
                    raise RuntimeError(f"V otvorenom koncepte #{pr['number']} chýba čitateľný článok.")
                # Zoznam súborov sa mohol zmeniť medzi volaniami. Použi len potvrdenú revíziu.
                stav = self.gh.citaj(f"/pulls/{pr['number']}")
                if stav["head"]["sha"] != hlava["sha"]:
                    raise RuntimeError(f"Koncept #{pr['number']} sa počas čítania zmenil. Spustite kontrolu znova.")
                self._koncepty[kluc] = subory
            for cesta, sha in self._koncepty[kluc]:
                zaznamy.append(z_hlavicky(f"pr:{pr['number']}:{cesta}", self._hlavicka(sha), pr["html_url"]))
        return zaznamy

    def nacitaj(self, kontrolovane_do: datetime | None = None) -> Snimka:
        # PR čítaj pred main. Ak sa medzitým zlúči, jeho článok nájdeme aj na main.
        koncepty = self._otvorene()
        publikovane, cesty = [], set()
        for subor in self._main():
            cesta = CLANKY + subor["path"]
            slug = str(PurePosixPath(subor["path"]).with_suffix(""))
            cesty.add(cesta)
            hlavicka = self._hlavicka(subor["sha"])
            if publikovane_v_okne(hlavicka, self.teraz, kontrolovane_do or self.teraz):
                odkaz = f"https://github.com/{self.gh.repo}/blob/main/{quote(cesta)}"
                publikovane.append(z_hlavicky(f"clanok:{slug}", hlavicka, odkaz))
        return Snimka(publikovane + koncepty, cesty)


def prekazka_zapisu(
    archiv: ArchivGitHub,
    kontrola: KontrolaTem,
    slug: str,
    tema: Zaznam,
    overene: list[Zaznam] | None = None,
    *, teraz: datetime | None = None,
) -> str | None:
    snimka = archiv.nacitaj(teraz or datetime.now(timezone.utc))
    if f"{CLANKY}{slug}.md" in snimka.cesty_main:
        return f"Článok s adresou {slug} už existuje na main."
    zmeny = [z for z in snimka.zaznamy if z not in (overene or [])]
    nalez = kontrola.over(tema, zmeny)
    return None if nalez.postupuje else popis_vysledku(nalez)
