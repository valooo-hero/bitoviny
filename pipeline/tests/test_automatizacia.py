import base64
import json
from datetime import date
from io import BytesIO

import httpx
import pytest
from PIL import Image

from bitoviny.redakcia import __main__ as redakcia
from bitoviny.redakcia.archiv import Snimka
from bitoviny.redakcia.factcheck import Factcheck, Tvrdenie
from bitoviny.redakcia.modely import Koncept
from bitoviny.redakcia.publikacia import GitHub
from bitoviny.redakcia.titulny import MODEL, vygeneruj_titulny


def test_workers_ai_pripravi_webp(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "a" * 32)
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
    jpeg = BytesIO()
    Image.new("RGB", (500, 500), "blue").save(jpeg, "JPEG")

    def odpoved(req):
        assert req.url.host == "api.cloudflare.com"
        assert req.url.path.endswith("/ai/run/" + MODEL)
        assert req.headers["Authorization"] == "Bearer test-token"
        assert json.loads(req.content) == {"prompt": "A blue square", "steps": 4}
        data = {"success": True, "result": {"image": base64.b64encode(jpeg.getvalue()).decode()}}
        return httpx.Response(200, json=data)

    with httpx.Client(transport=httpx.MockTransport(odpoved)) as klient:
        obrazok = Image.open(BytesIO(vygeneruj_titulny("A blue square", klient=klient)))
        assert obrazok.size == (1200, 675)
        assert obrazok.format == "WEBP"


def test_workers_ai_zlyha_bez_konfiguracie(monkeypatch):
    monkeypatch.delenv("CLOUDFLARE_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="CLOUDFLARE_ACCOUNT_ID"):
        vygeneruj_titulny("A blue square")


def test_git_commit_obsahuje_clanok_a_obrazok_pred_vytvorenim_vetvy():
    zaznam = []

    def odpoved(req):
        cesta = req.url.path.removeprefix("/repos/test/bitoviny")
        telo = json.loads(req.content) if req.content else None
        zaznam.append((cesta, telo))
        vysledky = {
            "/git/ref/heads/main": {"object": {"sha": "main-commit"}},
            "/git/commits/main-commit": {"tree": {"sha": "main-tree"}},
            "/git/blobs": {"sha": "obrazok-sha"},
            "/git/trees": {"sha": "strom-sha"},
            "/git/commits": {"sha": "commit-sha"},
            "/git/refs": {},
        }
        return httpx.Response(200, json=vysledky[cesta])

    subory = {"content/clanky/test.md": "# Článok", "public/obrazky/test.webp": b"webp"}
    with GitHub("test-token", "test/bitoviny", transport=httpx.MockTransport(odpoved)) as gh:
        assert gh.zapis_koncept("koncept/test", subory, "Koncept") == "commit-sha"

    strom = zaznam[-3][1]
    assert [item["path"] for item in strom["tree"]] == list(subory)
    assert strom["tree"][1]["sha"] == "obrazok-sha"
    assert zaznam[-1] == ("/git/refs", {"ref": "refs/heads/koncept/test", "sha": "commit-sha"})


@pytest.mark.parametrize(("zmena", "zlyhanie", "schvalenie"), [
    (False, False, True),
    (True, False, True),
    (True, True, False),
])
def test_workflow_overi_upraveny_text_aj_pripravi_obrazok(tmp_path, monkeypatch, zmena, zlyhanie, schvalenie):
    den = date(2026, 11, 12)
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    zdroj = {"url": "https://example.org/clanok", "zdroj_nazov": "Test", "titulok": "Správa"}
    tema = {"titulok": "Technologická správa", "spravy": [zdroj]}
    (raw / f"temy-{den}.json").write_text(json.dumps({"temy": [tema]}), encoding="utf-8")
    koncept = Koncept(
        titulok="Technologická správa dňa", perex="Táto skúšobná správa má dostatočne dlhý perex.",
        sekcia="veda", tagy=["veda"], telo="Overený článok.", pouzite_zdroje=[zdroj["url"]],
        prompt_ilustracie="A telescope", poznamky_pre_editora="",
    )
    factcheck = Factcheck(
        tvrdenia=[Tvrdenie(text="Tvrdenie", typ="ine", verdikt="potvrdene", zdroj="Test", dokaz="A telescope.")],
        celkove_hodnotenie="Overené.",
    )
    finalny_text = (koncept.titulok, koncept.perex, koncept.telo)
    meno_kola = {"kolo": 1, "tvrdeni": 1, "potvrdenych": 1, "chyb": 0, "upozorneni": 0}
    pred = {
        "koncept": koncept, "factcheck": factcheck, "nalezy": [], "historia": [meno_kola],
        "overeny_text": (*finalny_text[:2], "Pôvodný text.") if zmena else finalny_text,
    }
    volania = []

    class Graf:
        def invoke(self, *args, **kwargs):
            return dict(pred)

    def factcheck_final(stav):
        volania.append("factcheck")
        assert stav["koncept"].telo == koncept.telo
        if zlyhanie:
            raise RuntimeError("Limit testovacej služby.")
        return {"overeny_text": finalny_text}

    def ilustracia(prompt):
        volania.append(prompt)
        return b"webp"

    def pr(subor, gh, **kwargs):
        volania.append(kwargs)
        return "test"

    monkeypatch.setattr(redakcia, "KOREN", tmp_path)
    monkeypatch.setattr(redakcia, "langfuse_klient", lambda: None)
    monkeypatch.setattr(redakcia.ArchivGitHub, "nacitaj", lambda _: Snimka([], set()))
    monkeypatch.setattr(redakcia, "vyber_temy", lambda *a, **kw: [{"tema": tema}])
    monkeypatch.setattr(redakcia, "zostav_graf", Graf)
    monkeypatch.setattr(redakcia, "uzol_factcheck", lambda: factcheck_final)
    monkeypatch.setattr(redakcia, "vygeneruj_titulny", ilustracia)
    monkeypatch.setattr(redakcia, "prekazka_zapisu", lambda *a: None)
    monkeypatch.setattr(redakcia, "publikuj", pr)

    assert len(redakcia.spusti(den, 1, gh=object(), pr=True, automaticky=True)) == 1
    assert ("factcheck" in volania) is zmena
    assert volania[-2:] == ["A telescope", {"ilustracia": b"webp", "automaticky": schvalenie}]

    volania.clear()
    assert len(redakcia.spusti(den, 1, gh=object(), pr=True, titulne_obrazky=True)) == 1
    assert volania == ["A telescope", {"ilustracia": b"webp", "automaticky": False}]
