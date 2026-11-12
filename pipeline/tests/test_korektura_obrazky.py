from langchain_core.runnables import RunnableLambda

from bitoviny.redakcia.factcheck import Factcheck
from bitoviny.redakcia.graf import zostav_graf
from bitoviny.redakcia.korektura import Korektura, Uprava, dovod_zamietnutia, rozdiel, vykonaj
from bitoviny.redakcia.modely import Koncept
from bitoviny.redakcia.obrazky import Alternativa, Dopyty, ocisti_kredit, odporucanie, posud_obrazky, zarad

TELO = (
    "V virtualizovanom prostredí beží MEXT na 145 serveroch. Gary Smerdon tvrdí že výkon ostáva na 95 %.\n\n"
    "## Čo ďalej\n\nFirma AMD plánuje rozšírenie v klastéri Azure."
)


def _koncept(telo: str = TELO) -> Koncept:
    return Koncept(
        titulok="AMD udrží výkon s polovicou pamäte", perex="Technológia MEXT presúva dáta z pamäte na disk a výkon pritom takmer neklesá.",
        sekcia="hardver", tagy=["AMD", "MEXT"], telo=telo, pouzite_zdroje=["https://a.example/1"],
        prompt_ilustracie="A memory chip.", poznamky_pre_editora="",
    )


def _u(povodne: str, opravene: str, pole: str = "telo") -> Uprava:
    return Uprava(pole=pole, povodne=povodne, opravene=opravene, dovod="test")


# ---------- korektúra ----------


def test_platne_upravy_sa_vykonaju():
    k, vysledky = vykonaj(
        _koncept(),
        Korektura(upravy=[
            _u("V virtualizovanom prostredí", "Vo virtualizovanom prostredí"),
            _u("Smerdon tvrdí že výkon", "Smerdon tvrdí, že výkon"),
            _u("v klastéri Azure", "v klastri Azure"),
        ]),
    )
    assert [v.stav for v in vysledky] == ["vykonana"] * 3
    assert k.telo.startswith("Vo virtualizovanom") and "tvrdí, že" in k.telo and "klastri" in k.telo
    assert "## Čo ďalej" in k.telo


def test_uprava_nesmie_zmenit_cislo():
    assert dovod_zamietnutia(_u("beží MEXT na 145 serveroch", "beží MEXT na 154 serveroch")) == "mení čísla"
    assert dovod_zamietnutia(_u("ostáva na 95 %", "ostáva na 95%")) is None  # typografia áno, hodnota nie


def test_uprava_nesmie_zmenit_meno_ale_smie_koncovku():
    assert dovod_zamietnutia(_u("Gary Smerdon tvrdí", "Gary Smerdan tvrdí")) is None  # ten istý kmeň, len koncovka
    assert dovod_zamietnutia(_u("podľa Garyho Smerdona platí", "podľa Garyho Smerdonu platí")) is None
    assert dovod_zamietnutia(_u("Firma AMD plánuje", "Firma Intel plánuje")) == "mení vlastné mená"
    assert dovod_zamietnutia(_u("tvrdí Gary Smerdon dnes", "tvrdí Lisa Su dnes")) == "mení vlastné mená"


def test_uprava_nesmie_byt_prepis():
    dovod = dovod_zamietnutia(_u("Firma AMD plánuje rozšírenie", "Firma AMD podľa všetkého nič také v dohľadnej dobe nechystá a čaká"))
    assert dovod is not None and "prepis" in dovod
    assert dovod_zamietnutia(_u("## Čo ďalej", "### Čo ďalej")) == "mení štruktúru textu"
    assert dovod_zamietnutia(_u("rovnaké", "rovnaké")) == "úprava nič nemení"


def test_nenajdena_a_nejednoznacna_uprava():
    k, vysledky = vykonaj(
        _koncept("na serveri a na serveri. Koniec."),
        Korektura(upravy=[_u("toto v texte nie je", "toto v texte nieje"), _u("na serveri", "na serveroch")]),
    )
    assert [v.stav for v in vysledky] == ["nenajdena", "zamietnuta"]
    assert k.telo == "na serveri a na serveri. Koniec."


def test_diff_ukazuje_len_zmeny():
    pred = _koncept()
    po, _ = vykonaj(pred, Korektura(upravy=[_u("V virtualizovanom prostredí", "Vo virtualizovanom prostredí")]))
    d = rozdiel(pred, po)
    assert "-V virtualizovanom" in d and "+Vo virtualizovanom" in d
    assert "Čo ďalej" not in d
    assert rozdiel(pred, pred) == ""


# ---------- práva k obrázkom ----------


def test_zaradenie_podla_pravidiel():
    firmy, vyd = {"AMD", "MEXT"}, "Tom's Hardware"
    assert zarad({"kredit": "Peter Dazeley/Getty Images"}, firmy, vyd)[0] == "chranene"
    assert zarad({"kredit": "Getty Images | NurPhoto"}, firmy, vyd)[0] == "chranene"
    assert zarad({"popisok": "A chip. © 2026 Jane Doe"}, firmy, vyd)[0] == "chranene"
    assert zarad({"kredit": "(Image credit: AMD)"}, firmy, vyd)[0] == "tlacove"
    assert zarad({"kredit": "Tom's Hardware"}, firmy, vyd)[0] == "chranene"  # vlastný obrázok vydavateľa
    assert zarad({"kredit": "Jane Doe"}, firmy, vyd)[0] == "chranene"  # autor bez licencie
    assert zarad({}, firmy, vyd)[0] == "nejasne"  # bez kreditu
    assert zarad({"kredit": "Jane Doe", "licencia": "https://creativecommons.org/licenses/by/4.0/"}, firmy, vyd)[0] == "volne"
    assert zarad({"kredit": "Jane Doe, CC BY-SA 4.0"}, firmy, vyd)[0] == "volne"
    # Nekomerčná licencia nestačí.
    assert zarad({"licencia": "https://creativecommons.org/licenses/by-nc/4.0/"}, firmy, vyd)[0] == "chranene"
    # Agentúra má prednosť aj pred uvedenou licenciou.
    assert zarad({"kredit": "Reuters", "licencia": "CC BY 4.0"}, firmy, vyd)[0] == "chranene"


def test_ocistenie_kreditu():
    assert ocisti_kredit("(Image credit: AMD)") == "AMD"
    assert ocisti_kredit("Photo: Jane Doe") == "Jane Doe"


def _tema_s_obrazkami() -> dict:
    return {
        "titulok": "T", "pocet_zdrojov": 1, "signal_hn": 0,
        "spravy": [{
            "zdroj": "a", "zdroj_nazov": "Tom's Hardware", "titulok": "T", "url": "https://a.example/1",
            "publikovane": "2026-11-11T10:00:00+00:00", "zhrnutie": "", "text": "AMD MEXT 145 95",
            "obrazky": [
                {"url": "https://a.example/getty.jpg", "kredit": "Getty Images"},
                {"url": "https://a.example/amd.jpg?w=800", "kredit": "(Image credit: AMD)", "popisok": "AMD slide"},
                {"url": "https://a.example/amd.jpg?w=1200", "kredit": "(Image credit: AMD)"},
                {"url": "https://a.example/nic.jpg"},
            ],
        }],
    }


def test_posudenie_zoradi_a_odstrani_duplicity():
    posudene = posud_obrazky(_tema_s_obrazkami(), {"AMD"})
    assert [p.zaradenie for p in posudene] == ["tlacove", "nejasne", "chranene"]


def test_odporucanie_nikdy_nenavrhne_chraneny_obrazok():
    posudene = posud_obrazky(_tema_s_obrazkami(), {"AMD"})
    assert odporucanie(posudene, [])["url"] == "https://a.example/amd.jpg?w=800"

    len_chranene = [p for p in posudene if p.zaradenie in ("chranene", "nejasne")]
    alt = Alternativa(url="https://commons.example/x.jpg", licencia="CC BY-SA 4.0", stranka="https://commons.example/x", povod="wikimedia")
    assert odporucanie(len_chranene, [alt]) == {
        "typ": "alternativa", "url": alt.url, "poznamka": "Voľná náhrada. Editor musí overiť licenciu na stránke pôvodu.",
    }
    assert odporucanie(len_chranene, [])["typ"] == "ilustracia"


# ---------- celý graf ----------


def test_cely_graf_s_falosnymi_modelmi():
    hladane = []

    def hladac(dopyty):
        hladane.extend(dopyty)
        return [Alternativa(url="https://commons.example/x.jpg", licencia="CC0", stranka="https://commons.example/x", povod="wikimedia")]

    graf = zostav_graf(
        model_autorky=RunnableLambda(lambda _: _koncept(TELO + " " + "slovo " * 300)),
        model_factchecku=RunnableLambda(lambda _: Factcheck(tvrdenia=[], celkove_hodnotenie="V poriadku.")),
        model_korektury=RunnableLambda(lambda _: Korektura(upravy=[
            _u("V virtualizovanom prostredí", "Vo virtualizovanom prostredí"),
            _u("na 145 serveroch", "na 541 serveroch"),
        ])),
        model_fotoeditora=RunnableLambda(lambda _: Dopyty(dopyty=["AMD Epyc server", "server rack"])),
        hladac_obrazkov=hladac,
    )
    v = graf.invoke({"tema": _tema_s_obrazkami()})
    assert v["koncept"].telo.startswith("Vo virtualizovanom") and "145 serveroch" in v["koncept"].telo
    assert [u["stav"] for u in v["korektura"]["upravy"]] == ["vykonana", "zamietnuta"]
    assert hladane == ["AMD Epyc server", "server rack"]
    assert v["obrazky"]["odporucanie"]["typ"] == "povodny"  # tlačový obrázok AMD má prednosť pred náhradou
    assert len(v["obrazky"]["alternativy"]) == 1


def test_vypadok_korektorky_nezahodi_clanok():
    def spadne(_):
        raise RuntimeError("limit")

    graf = zostav_graf(
        model_autorky=RunnableLambda(lambda _: _koncept(TELO + " " + "slovo " * 300)),
        model_factchecku=RunnableLambda(lambda _: Factcheck(tvrdenia=[], celkove_hodnotenie="")),
        model_korektury=RunnableLambda(spadne),
        model_fotoeditora=RunnableLambda(spadne),
        hladac_obrazkov=lambda d: [],
    )
    v = graf.invoke({"tema": _tema_s_obrazkami()})
    assert "neprebehla" in v["korektura"]["chyba"]
    assert v["koncept"].telo.startswith("V virtualizovanom")  # text ostal nedotknutý
    assert v["obrazky"]["dopyty"] == ["AMD", "MEXT"]  # bez modelu sa hľadá podľa tagov
