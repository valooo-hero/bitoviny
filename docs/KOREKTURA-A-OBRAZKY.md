# Korektúra a obrázky

Oba kroky bežia po factchecku: `factcheck -> korektura -> fotoeditor -> koniec`.

## Korektúra

Kód: `pipeline/bitoviny/redakcia/korektura.py`, pokyny: `prompty/korektura.md`.

Jazykový model článok neprepisuje. Vráti zoznam úprav v tvare „pôvodný úryvok, opravený úryvok, dôvod“ a vykoná ich až kód, ak prejdú kontrolou:

| Kontrola | Čo zamietne |
|---|---|
| Čísla | Úpravu, po ktorej sa líši množina čísel v úryvku |
| Vlastné mená | Úpravu, ktorá pridá alebo odstráni slovo s veľkým písmenom. Zmena pádovej koncovky prejde |
| Rozsah | Úryvok dlhší než 400 znakov alebo zmenu, ktorá text mení z viac než polovice |
| Štruktúra | Zmenu nadpisov a zalomení |
| Jednoznačnosť | Úryvok, ktorý v texte nie je alebo je v ňom viackrát |

Editor dostane v `koncept.korektura` každú úpravu so stavom (`vykonana`, `zamietnuta`, `nenajdena`) a diff. Ak korektorka zlyhá, článok pokračuje s pôvodným textom a správa to uvedie.

### Slabiny

- **Bezplatné modely korigujú slabo.** Na texte so známymi chybami („V virtualizovanom“, „klastéri“) našiel Gemini Flash-Lite jednu z dvoch, Qwen na Groq žiadnu a ďalší model vrátil prázdnu úpravu s dôvodom „text je bez chýb“. Mechanizmus a ochrany fungujú, kvalita opráv závisí od modelu. Jazykovú kontrolu musí zatiaľ robiť editor.
- **Kontrola mien pozná len kmeň slova** (prvé štyri písmená). Preklep v koncovke mena preto prejde.

## Práva k obrázkom

Kód: `pipeline/bitoviny/redakcia/obrazky.py`.

Zaradenie robia pravidlá v kóde, nie jazykový model, aby bolo predvídateľné a dalo sa skontrolovať. Východisko: obrázok je chránený, kým sa nepreukáže opak.

| Zaradenie | Kedy | Čo s ním |
|---|---|---|
| `chranene` | Agentúra alebo fotobanka (Getty, Reuters, AP, AFP, Shutterstock a ďalšie), znak ©, výhrada práv, uvedený autor bez voľnej licencie, vlastný obrázok vydavateľa, licencia CC so zákazom komerčného použitia alebo úprav | Nikdy sa nenavrhne |
| `nejasne` | Bez kreditu a licencie, alebo licencia, ktorú nevieme posúdiť | Nikdy sa nenavrhne |
| `tlacove` | Kredit uvádza firmu, o ktorej je článok | Navrhne sa, editor musí potvrdiť pôvod |
| `volne` | Uvedená licencia CC BY, CC BY-SA, CC0 alebo public domain | Navrhne sa |

Agentúra má prednosť aj pred uvedenou voľnou licenciou.

Tabuľka opisuje, čo pipeline navrhne sama. Editor môže stav ktoréhokoľvek obrázka v redakčnom rozhraní zmeniť podľa vlastného úsudku a zodpovedá za to, pozri `docs/REDAKCNE-ROZHRANIE.md`.

## Voľné náhrady

Model navrhne dva až tri anglické hľadané výrazy a kód nimi prehľadá Wikimedia Commons a Openverse. Berú sa len licencie CC0, public domain, CC BY a CC BY-SA. Výsledky sa striedajú medzi výrazmi a fotobankami, aby ponuku nezaplnil prvý výraz.

Pri každej náhrade je autor, licencia a odkaz na stránku pôvodu. Editor ju má pred použitím otvoriť: údaje z fotobánk môžu byť nesprávne a logá bývajú voľné z hľadiska autorského práva, no chránené ako ochranná známka.

## Odporúčanie pre editora

V `koncept.obrazky.odporucanie` je jeden návrh v tomto poradí: voľný obrázok zo zdrojov, tlačový obrázok, voľná náhrada, a ak nič z toho nie je, ilustrácia z promptu, ktorý pripravila autorka. Rozhoduje editor v redakčnom rozhraní (Fáza 6). Obrázky sa zatiaľ nesťahujú, uchováva sa len adresa.

### Slabiny

- **Relevancia náhrad je premenlivá.** Hľadanie podľa výrazu „Gemini“ vráti aj autobus toho mena.
- **Pravidlá nepoznajú tlačové materiály s menom fotografa** a zaradia ich ako chránené. Je to bezpečná chyba.
- **Zdrojové weby často kredit neuvádzajú** v strojovo čitateľnej podobe. Také obrázky končia ako `nejasne`.
