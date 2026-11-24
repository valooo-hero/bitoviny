import base64
import json
from datetime import date, datetime, timedelta, timezone

import httpx
import pytest
import yaml
from langchain_core.runnables import RunnableLambda

from bitoviny.redakcia import __main__ as redakcia
from bitoviny.redakcia.archiv import ArchivGitHub, prekazka_zapisu
from bitoviny.redakcia.duplicity import DAVKA, KontrolaTem, PosudenieTemy, Zaznam, normalizuj_url
from bitoviny.redakcia.publikacia import GitHub

TERAZ = datetime(2026, 11, 17, 12, tzinfo=timezone.utc)
REPO = "test/bitoviny"


def markdown(titulok, url, publikovane=TERAZ, **polia):
    fm = {"title": titulok, "publikovane": publikovane, "zdroje": [{"url": url}], **polia}
    return "---\n" + yaml.safe_dump(fm) + "---\nText."


def test_kanonicke_url_zachova_vyznam_parametrov():
    assert normalizuj_url("https://www.example.org/sprava/?utm_source=RSS&id=4#obsah") == "//example.org/sprava?id=4"
    assert normalizuj_url("http://example.org/sprava?id=8&fbclid=xyz") == "//example.org/sprava?id=8"


def test_kontrola_prejde_aj_poslednu_davku_a_zablokuje_rovnaku_udalost():
    archiv = [Zaznam(str(i), "Iný článok") for i in range(DAVKA)]
    archiv.append(Zaznam("pr:1", "Starý otvorený koncept", odkaz="https://example.org/pull/1"))
    volania = []

    def odpoved(spravy):
        ids = [z["id"] for z in json.loads(spravy[-1].content)["existujuce"]]
        volania.append(ids)
        if "pr:1" in ids:
            return PosudenieTemy(verdikt="duplicita", odkaz_id="pr:1", dovod="Rovnaká udalosť.")
        return PosudenieTemy(verdikt="nova", odkaz_id="", dovod="Bez zhody.")

    vysledok = KontrolaTem(RunnableLambda(odpoved)).over(Zaznam("t", "Parafráza konceptu v angličtine"), archiv)
    assert len(volania) == 2
    assert not vysledok.postupuje and vysledok.zhoda == archiv[-1]


@pytest.mark.parametrize(("verdikt", "postupuje"), [("novy_vyvoj", True), ("nejasna", False)])
def test_novy_vyvoj_a_nejasna_zhoda(verdikt, postupuje):
    existujuci = Zaznam("clanok", "Výpadok služby")
    model = RunnableLambda(
        lambda _: PosudenieTemy(verdikt=verdikt, odkaz_id=existujuci.id, dovod="Prevádzkovateľ zverejnil príčinu.")
    )
    assert KontrolaTem(model).over(Zaznam("tema", "Príčina výpadku"), [existujuci]).postupuje is postupuje


def test_model_nemoze_odkazat_na_neexistujuci_clanok():
    odpoved = PosudenieTemy(verdikt="duplicita", odkaz_id="vymyslene", dovod="Zhoda.")
    with pytest.raises(ValueError, match="neplatný záznam"):
        KontrolaTem(RunnableLambda(lambda _: odpoved)).over(Zaznam("tema", "Téma"), [Zaznam("id", "Článok")])


def github_fixture(*, chyba_strany=False):
    volania = []
    pr = {"number": 42, "html_url": "https://github.com/test/bitoviny/pull/42", "created_at": "2025-09-03T00:00:00Z",
          "head": {"ref": "koncept/2025-09-03-stary", "sha": "head", "repo": {"full_name": REPO}}}
    podklady = {
        "na-hranici": markdown("Na hranici", "https://priklad.sk/hranica", TERAZ - timedelta(days=7), stiahnute=True),
        "prilis-stary": markdown("Mimo okna", "https://priklad.sk/mimo", TERAZ - timedelta(days=7, seconds=1)),
        "buducnost": markdown("Budúci", "https://priklad.sk/buduci", TERAZ + timedelta(seconds=1)),
        "bez-schvalenia": markdown("Neschválený", "https://priklad.sk/pokus", redaktori={"autor": "klara"}),
        "koncept": markdown("Starý koncept", "https://priklad.sk/koncept"),
    }
    prefix = f"/repos/{REPO}"

    def odpoved(request):
        cesta = request.url.path.removeprefix(prefix)
        volania.append((cesta, request.url.query))
        if cesta == "/pulls":
            return httpx.Response(200, json=[], headers={"link": '<https://api.github.com/repositories/7/pulls?page=2>; rel="next"'})
        if cesta == "/repositories/7/pulls":
            return httpx.Response(403 if chyba_strany else 200, json=[pr])
        if cesta == "/pulls/42/files":
            return httpx.Response(200, json=[{"filename": "content/clanky/stary.md", "sha": "koncept", "status": "added"}])
        odpovede = {
            "/pulls/42": pr,
            "/git/ref/heads/main": {"object": {"sha": "main-commit"}},
            "/git/commits/main-commit": {"tree": {"sha": "koren"}},
            "/git/trees/koren": {"truncated": False, "tree": [{"path": "content", "type": "tree", "sha": "obsah"}]},
            "/git/trees/obsah": {"truncated": False, "tree": [{"path": "clanky", "type": "tree", "sha": "clanky"}]},
            "/git/trees/clanky": {"truncated": False, "tree": [
                {"path": sha + ".md", "type": "blob", "sha": sha} for sha in podklady if sha != "koncept"
            ]},
        }
        if cesta.startswith("/git/blobs/"):
            sha = cesta.rsplit("/", 1)[-1]
            data = {"encoding": "base64", "content": base64.b64encode(podklady[sha].encode()).decode()}
        else:
            data = odpovede[cesta]
        return httpx.Response(200, json=data)

    return GitHub("test-token", REPO, transport=httpx.MockTransport(odpoved)), volania


def test_archiv_berie_vsetky_pr_a_presny_cas_zverejnenia():
    gh, volania = github_fixture()
    with gh:
        archiv = ArchivGitHub(gh, TERAZ)
        pred = archiv.nacitaj()
        assert [z.titulok for z in pred.zaznamy] == ["Na hranici", "Starý koncept"]
        assert prekazka_zapisu(archiv, KontrolaTem(), "prilis-stary", Zaznam("tema", "Téma"), pred.zaznamy)
        pocet_blobov = sum(cesta.startswith("/git/blobs/") for cesta, _ in volania)
        assert pocet_blobov == 5
        assert any(cesta == "/repositories/7/pulls" for cesta, _ in volania)


def test_neuplne_strankovanie_zastavi_kontrolu():
    gh, _ = github_fixture(chyba_strany=True)
    with gh, pytest.raises(RuntimeError, match="403"):
        ArchivGitHub(gh, TERAZ).nacitaj()


def test_zmeny_medzi_vyberom_a_zapisom_su_predmetom_novej_kontroly():
    gh, _ = github_fixture()
    with gh:
        archiv = ArchivGitHub(gh, TERAZ)
        tema = Zaznam("t", "Nový titulok", zdroje=(("", "https://priklad.sk/koncept?utm_campaign=test"),))
        vysledok = prekazka_zapisu(archiv, KontrolaTem(), "novy-titulok", tema)
        assert "pull/42" in vysledok


def test_pred_zapisom_sa_zohladni_clanok_zverejneny_pocas_behu():
    gh, _ = github_fixture()
    with gh:
        archiv = ArchivGitHub(gh, TERAZ)
        povodne = archiv.nacitaj()
        tema = Zaznam("t", "Správa z tohto behu", zdroje=(("", "https://priklad.sk/buduci"),))
        vysledok = prekazka_zapisu(
            archiv, KontrolaTem(), "iny-slug", tema, povodne.zaznamy,
            teraz=TERAZ + timedelta(seconds=2),
        )
        assert "buducnost.md" in vysledok


def test_beh_nahradi_duplicitu_rezervnou_temou_a_dry_run_nezapisuje(tmp_path, monkeypatch, caplog):
    den = date(2026, 11, 12)
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)

    def kandidat(titulok, url):
        return {"titulok": titulok, "spravy": [{"titulok": titulok, "url": url}]}

    vstup = [
        kandidat("Nadpis starého konceptu v inom jazyku", "https://priklad.sk/koncept?utm_source=zdroj"),
        kandidat("Prvá nová", "https://priklad.sk/nova"),
        kandidat("Prvá nová premenovaná", "https://priklad.sk/nova?utm_medium=RSS"),
        kandidat("Druhá nová", "https://priklad.sk/druha"),
    ]
    (raw / f"temy-{den}.json").write_text(json.dumps({"temy": vstup}), encoding="utf-8")

    def vyber(kandidati, pocet, *, config, s_rezervou):
        assert s_rezervou and pocet == 2
        return [{"tema": tema} for tema in kandidati]

    falosny_model = RunnableLambda(lambda _: PosudenieTemy(verdikt="nova", odkaz_id="", dovod="Bez zhody."))
    monkeypatch.setattr(redakcia, "KOREN", tmp_path)
    monkeypatch.setattr(redakcia, "langfuse_klient", lambda: None)
    monkeypatch.setattr(redakcia, "vyber_temy", vyber)
    monkeypatch.setattr(redakcia, "KontrolaTem", lambda: KontrolaTem(falosny_model))
    monkeypatch.setattr(redakcia, "zostav_graf", lambda: pytest.fail("Dry run nesmie spustiť písanie."))
    gh, _ = github_fixture()
    with gh, caplog.at_level("INFO"):
        assert redakcia.spusti(den, 2, gh=gh, iba_kontrola=True, teraz=TERAZ) == []
    assert caplog.text.count("duplicita –") == 2
    assert "Róbert | Druhá nová | nova" in caplog.text
    assert "Róbert schválil tém: 2" in caplog.text
    assert not (tmp_path / "data" / "koncepty").exists()


def test_neplatny_odkaz_spusti_zalozny_model(monkeypatch):
    from bitoviny import llm

    class Provider:
        def __init__(self, id):
            self.id = id

        def with_structured_output(self, schema, **kwargs):
            return RunnableLambda(
                lambda _: schema(verdikt="duplicita", odkaz_id=self.id, dovod="Rovnaká udalosť.")
            )

    config = {"kontrola_duplicit": {"modely": [{"id": "mimo-vstupu"}, {"id": "clanok"}]}}
    monkeypatch.setattr(llm, "konfiguracia", lambda: config)
    monkeypatch.setattr(llm, "_vytvor", lambda spec, _: Provider(spec["id"]))
    vysledok = KontrolaTem().over(Zaznam("tema", "Nová téma"), [Zaznam("clanok", "Starší článok")])
    assert vysledok.zhoda.id == "clanok"
