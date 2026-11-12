# Factcheck

Kód je v `pipeline/bitoviny/redakcia/factcheck.py` a `graf.py`, pokyny modelu v `prompty/factcheck.md` a `prompty/oprava.md`.

## Priebeh

```
START -> autorka -> factcheck -+-> koniec (správa pre editora)
                        ^      |
                        +-- oprava   (najviac 2 opravy)
```

1. **Factchecker** dostane koncept a tie isté zdroje ako autorka. Vypíše každé overiteľné tvrdenie s verdiktom (`potvrdene`, `nepresne`, `nepodlozene`, `v_rozpore`), doslovným úryvkom zo zdroja a návrhom opravy.
2. **Mechanické kontroly** bez jazykového modelu overia aj samotného factcheckera:
   - Každé viacciferné číslo z konceptu sa hľadá v zdrojoch. Zohľadňuje sa rozdielny zápis (`2,000` a `2 000`, `1.5` a `1,5`).
   - Každý úryvok, ktorý factchecker cituje ako dôkaz, sa musí v zdroji nachádzať doslova. Ak nie, verdiktu sa nedá veriť a editor dostane upozornenie.
3. Ak ostali chyby, **autorka** dostane nálezy a koncept opraví. Meniť smie len to, čo bolo namietnuté.
4. Po najviac dvoch opravách ide článok editorovi aj s neuzavretými nálezmi.

Factcheck má v `config/modely.yaml` iné poradie modelov než autorka, aby text podľa možnosti nekontroloval ten istý model, ktorý ho napísal. Pri výpadkoch sa to však nedá zaručiť.

## Čo dostane editor

Vo frontmatteri konceptu je `koncept.factcheck`: celkové hodnotenie, priebeh kôl, neuzavreté nálezy a tabuľka všetkých tvrdení s verdiktmi a úryvkami.

## Skúška na pokazenom článku

```bash
cd pipeline
../.venv/Scripts/python evaly/factcheck_chyby.py ../data/koncepty/RRRR-MM-DD/nazov.md
```

Skript vloží do hotového konceptu päť chýb (zmenené percento, počet, mesiac, obrátený význam a vymyslený výrok) a spustí jedno kolo factchecku. Zámeny sú napísané pre článok o AMD MEXT z 11. 11. 2026; pre iný článok ich treba upraviť.

Výsledok z 12. 11. 2026: zachytených 5 z 5, všetky jazykovým modelom. Navyše namietol vetu o európskych firmách, ktorú autorka sama označila ako nepodloženú. Je to jediný beh na jednom článku, nie meranie spoľahlivosti.

## Známe slabiny

- **Factchecker nie je stabilný.** V ostrom behu našiel v každom z troch kôl inú drobnosť, hoci predošlé kolá ju neuviedli. Slučka preto často vyčerpá obe opravy a posledný nález ostane editorovi.
- **Číselná kontrola nepozná čísla napísané slovom** ani prepočty. Jednociferné čísla preto preskakuje a prepočet nahlási ako číslo bez opory.
- **Overuje sa len voči dodaným zdrojom.** Ak sa mýli zdroj, chyba prejde.
- **Až päť volaní modelu na článok** (písanie, tri factchecky, dve opravy). Pri výpadkoch Gemini to všetko padá na OpenRouter s limitom 50 požiadaviek denne.
