import json
from datetime import datetime, timezone

import yaml

from bitoviny.redakcia.publikacia import ZASTUPNY_OBRAZOK, bez_html, publikuj

KONCEPT = """---
title: AMD udrží výkon s polovicou pamäte
perex: Technológia MEXT presúva dáta z pamäte na disk a výkon pritom takmer neklesá.
sekcia: hardver
tagy: [AMD, MEXT]
zdroje:
- nazov: 'Zdroj A: Titulok'
  url: https://a.example/1
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
trace: https://cloud.langfuse.com/project/x/traces/y
koncept:
  datum_sprav: '2026-11-11'
  dovod_vyberu: Dôležité.
  prompt_ilustracie: A memory chip.
  poznamky_pre_editora: Nič.
  upozornenia: [Pozor.]
  factcheck:
    hodnotenie: V poriadku.
    kola: [{kolo: 1, tvrdeni: 3, potvrdenych: 3, chyb: 0, upozorneni: 0}]
    otvorene_nalezy: []
    tvrdenia: []
  korektura:
    upravy: [{pole: telo, povodne: a, opravene: b, dovod: c, stav: vykonana, poznamka: ''}]
    diff: ''
  obrazky:
    odporucanie: {typ: ilustracia, url: '', poznamka: Vygenerovať ilustráciu.}
    povodne: []
    alternativy: []
---

## Medzititulok

Text článku <script>alert(1)</script> s <b>HTML</b>.
"""


class FalosnyGitHub:
    def __init__(self, existuje=False):
        self.existuje, self.subory, self.pr = existuje, {}, None

    def vetva_existuje(self, vetva):
        return self.existuje

    def vytvor_vetvu(self, vetva, zaklad="main"):
        self.vetva = vetva

    def zapis_subor(self, cesta, obsah, vetva, sprava):
        self.subory[cesta] = obsah

    def otvor_pr(self, vetva, titulok, popis):
        self.pr = (vetva, titulok, popis)
        return "https://github.example/pr/1"


def test_bez_html():
    assert bez_html("a <script>x</script> b <b>c</b>") == "a x b c"
    assert bez_html("2 < 3 a 5 > 4") == "2 < 3 a 5 > 4"  # nerovnosti nie sú značky
    assert bez_html('<img src=x onerror="alert(1)">text<!-- skryté -->') == "text"
    assert bez_html("[klik](javascript:alert(1)) a [ok](https://a.example) a [kotva](#x)") == "[klik]() a [ok](https://a.example) a [kotva](#x)"


def test_publikuj_vytvori_clanok_a_spravu(tmp_path):
    subor = tmp_path / "amd-udrzi-vykon.md"
    subor.write_text(KONCEPT, encoding="utf-8")
    gh = FalosnyGitHub()
    url = publikuj(subor, gh, teraz=datetime(2026, 11, 12, 0, 30, tzinfo=timezone.utc))
    assert url.endswith("/pr/1")
    assert gh.vetva == "koncept/2026-11-11-amd-udrzi-vykon"
    assert set(gh.subory) == {"content/clanky/amd-udrzi-vykon.md", "redakcia/spravy/amd-udrzi-vykon.json"}

    _, fm, telo = gh.subory["content/clanky/amd-udrzi-vykon.md"].split("---\n", 2)
    web = yaml.safe_load(fm)
    # Presne polia, ktoré číta web. Trace je súkromný a schválenie doplní až editor.
    assert set(web) == {"title", "perex", "sekcia", "tagy", "publikovane", "obrazok", "redaktori", "zdroje"}
    assert web["obrazok"]["src"] == ZASTUPNY_OBRAZOK
    assert web["redaktori"] == {"autor": "klara", "factcheck": "tomas", "korektura": "ciarka"}
    assert "<script>" not in telo and "<b>" not in telo and "## Medzititulok" in telo

    sprava = json.loads(gh.subory["redakcia/spravy/amd-udrzi-vykon.json"])
    assert sprava["slug"] == "amd-udrzi-vykon" and sprava["prompt_ilustracie"] == "A memory chip."
    assert sprava["factcheck"]["kola"][0]["tvrdeni"] == 3
    assert "Nezlučovať ručne" in gh.pr[2] and "Pozor." in gh.pr[2]


def test_existujuca_vetva_sa_preskoci(tmp_path):
    subor = tmp_path / "x.md"
    subor.write_text(KONCEPT, encoding="utf-8")
    gh = FalosnyGitHub(existuje=True)
    assert publikuj(subor, gh) is None and gh.subory == {}
