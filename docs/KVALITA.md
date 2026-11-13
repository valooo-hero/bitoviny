# Kvalita a štatistiky (Fáza 7)

## Čo sa meria

Štatistiky počíta web pri každom zostavení z repozitára (`src/lib/statistiky.ts`), bez externého API. Rátajú sa len zverejnené články, ktoré pripravili agenti a schválil človek. Vzorové a stiahnuté články sa nerátajú.

| Metrika | Odkiaľ |
|---|---|
| Miera zásahov editora | Podiel slov tela článku, ktoré editor zmenil, pridal alebo vypustil. Porovnáva sa `text_agentov` v redakčnej správe so zverejneným textom (najdlhšia spoločná podpostupnosť slov) |
| Overené tvrdenia, kolá factchecku, chyby v 1. kole | `factcheck` v redakčnej správe |
| Jazykové opravy | `korektura.upravy` so stavom `vykonana` |
| Nepoužiteľné obrázky zo zdrojov | Automatické zaradenie `chranene` alebo `nejasne` |
| Rozhodnutia o obrázkoch zmenené editorom | Obrázky s iným zaradením, než navrhli pravidlá |

Pipeline ukladá text agentov do redakčnej správy pri vytvorení pull requestu. Pre prvých šesť článkov bol doplnený spätne z prvého commitu ich pull requestu.

Čísla sa zobrazujú na stránke Redakcia pri každom redaktorovi, na stránke Ako to funguje v súhrne a pri každom článku v boxe „Ako vznikol tento článok“.

## Stav k 13. 11. 2026 (5 článkov)

| | |
|---|---|
| Overených tvrdení | 84 |
| Článkov vrátených factcheckom na opravu | 4 z 5 |
| Text zmenený editorom | 0 % (editor nezmenil ani jedno slovo) |
| Jazykových opráv | 1 |
| Nepoužiteľných obrázkov zo zdrojov | 29 z 30 |
| Priemerná dĺžka | 272 slov (cieľ 350 až 600) |

**Čo z toho vyplýva:** factcheck je najužitočnejší agent, editor do textu nezasahoval a korektúra na bezplatných modeloch takmer nepracovala. Články sú sústavne kratšie, než žiada zadanie autorky.

## Korektúra: tri vrstvy

Korektúra má od Fázy 7 tri vrstvy. Každá úprava z ktorejkoľvek vrstvy prejde tou istou kontrolou (nemení čísla, mená, štruktúru ani zmysel):

1. **Jazykový model** navrhne úpravy.
2. **Pevné pravidlá** v kóde: vokalizácia predložiek (v vo, s so, z zo, k ku) a medzera pred znakom percenta.
3. **LanguageTool** (verejné bezplatné API): automaticky sa vykonajú len spoľahlivé gramatické pravidlá, najmä čiarky pred „že“, „ktorý“, „čo“. Návrhy pri preklepoch sa nevykonajú, lebo bývajú zlé („virtualizovanom“ na „aktualizovanom“, „Gary“ na „Gaby“). Idú editorovi do karty Korektúra ako podozrivé slová.

Výpadok ktorejkoľvek vrstvy článok nezastaví.

## Evaly

Oba skripty používajú skutočné modely a služby, spúšťajú sa ručne:

```bash
cd pipeline
../.venv/Scripts/python evaly/factcheck_chyby.py ../data/koncepty/2026-11-11/<koncept>.md
../.venv/Scripts/python evaly/korektura_chyby.py
```

| Eval | Čo robí | Výsledok 13. 11. 2026 |
|---|---|---|
| `factcheck_chyby.py` | Vloží do hotového konceptu 5 vecných chýb a spustí jedno kolo factchecku | 5 z 5 zachytených |
| `korektura_chyby.py` | Spustí korektúru na texte s 8 známymi jazykovými chybami a 5 výrazmi, ktoré sa meniť nesmú | 6 z 8 opravených, 0 pokazených; „klastéri“ označené ako podozrivé, „svojim“ na „svojím“ neopravené |

Sú to jednotlivé behy na malých vzorkách, nie štatistické meranie. Modely na bezplatných tarifách sa správajú premenlivo: pri skoršom behe korektúry jazykový model navrhol úryvok, ktorý v texte nebol, a čiarku pred „že“ doplnil až LanguageTool.

## Čo by pomohlo ďalej

- **Dlhšie články:** autorka sústavne píše okolo 270 slov. Treba sprísniť pokyn alebo kontrolu dĺžky premeniť na dôvod na prepísanie.
- **Zaznamenávať, ktorý model text naozaj napísal.** Pri zálohách to dnes vie len Langfuse, redakčná správa nie.
- **Väčšia sada evalov** zo skutočných opráv editora, keď ich bude dosť.
