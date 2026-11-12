# Zdroje správ

Strojovo čitateľný zoznam je v [`config/sources.yaml`](../config/sources.yaml). Všetky kanály boli 12. 11. 2026 overené, odpovedajú kódom 200.

| Zdroj | Zameranie | Položiek v kanáli | Plný text v RSS | Obrázky v RSS |
|---|---|---|---|---|
| The Verge | Všeobecné tech | 10 | áno | nie |
| Ars Technica | Tech, veda, politika | 20 | áno | áno |
| TechCrunch | Startupy, biznis | 20 | nie | nie |
| Wired | Tech, spoločnosť | 50 | nie | čiastočne |
| Engadget | Spotrebná elektronika | 20 | áno | áno |
| The Register | Enterprise IT | 50 | áno | áno |
| BleepingComputer | Bezpečnosť | 15 | nie | nie |
| Tom's Hardware | Hardvér | 50 | áno | áno |
| MIT Technology Review | Veda, AI | 10 | áno | nie |
| 9to5Mac | Apple | 100 | nie | nie |
| Hacker News | Signál dôležitosti | 30 | nie | nie |

„Plný text“ je odhad podľa prítomnosti značiek s obsahom, môže ísť aj o dlhší výňatok. Skutočný rozsah overí Fáza 2.

## Pravidlá zberu

- Hlavný vstup je RSS. Stránku článku sťahujeme len tam, kde kanál neobsahuje text alebo obrázky.
- Rešpektujeme `robots.txt`, jedna požiadavka na doménu za niekoľko sekúnd, vlastný User-Agent.
- Zdrojové texty slúžia len ako podklad pre agentov. Nezverejňujú sa a do repozitára sa neukladajú.
- Článok vznikne len z témy, ktorú pokrývajú aspoň dva zdroje. Výnimkou je exkluzívna správa, kde jasne uvedieme pôvodný zdroj.
- Hacker News neslúži ako zdroj textu, iba ako váha pri výbere tém.

## Možné rozšírenia

Android Authority (mobil), The Hacker News (bezpečnosť), IEEE Spectrum (veda), slovenské a české portály na porovnanie, čo už vyšlo lokálne.

## Ako Zberač pracuje

Kód je v `pipeline/bitoviny/zber/`, spúšťa sa príkazom `python -m bitoviny.zber`.

1. Stiahne všetky kanály a ponechá správy publikované včera podľa slovenského času.
2. Titulok a úvod každej správy prevedie lokálnym modelom (`bge-small-en-v1.5`, bez API) na vektor a správy o tej istej udalosti zoskupí.
3. Témy zoradí podľa počtu nezávislých zdrojov. Zhoda s Hacker News a dostupný plný text pridávajú váhu.
4. Pri vybraných témach stiahne stránku článku tam, kde RSS obsahuje len výňatok alebo chýbajú obrázky.
5. Zapíše `data/raw/temy-RRRR-MM-DD.json`. Priečinok je v `.gitignore`.

Pri obrázkoch zbiera adresu, alt text, popisok, kredit a licenciu z RSS, zo schema.org metadát a z prvkov `figure`. Práva neposudzuje, to je úloha fotoeditora vo Fáze 5.

## Známe obmedzenia

- **Krátke kanály.** The Verge a MIT Technology Review majú v kanáli len 10 položiek. Pri rannom behu z nich včerajšie správy často vypadnú. Riešením je spúšťať zber krátko po polnoci.
- **robots.txt.** The Register zakazuje nášmu robotovi stránky článkov, takže z neho máme len text z RSS.
- **Príbuzné správy v jednej téme.** Viac rôznych článkov o tej istej osobe alebo firme sa môže spojiť do jednej témy. Autorka a factchecker s tým musia rátať.
- **Výber bez úsudku.** Poradie tém je čisto počtové. Redakčný úsudok (čo je zaujímavé pre slovenského čitateľa) doplní jazykový model vo Fáze 3.
