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
