---
title: "Bitoviny štartujú: redakcia, v ktorej píšu AI agenti a zverejňuje človek"
perex: "Nový slovenský portál o technológiách skúša, či šesť špecializovaných AI agentov dokáže pripraviť článok, pod ktorý sa človek neváha podpísať."
sekcia: ai
tagy: ["Bitoviny", "AI agenti", "LangGraph"]
publikovane: 2026-11-12T09:00:00+01:00
obrazok:
  src: /obrazky/vzor-redakcia.svg
  alt: "Šesť farebných kruhov spojených čiarou, ktorá vedie k siedmemu, sivému kruhu"
  popisok: "Šesť agentov a jeden človek na konci reťaze."
  kredit: "Bitoviny"
  licencia: "vlastná ilustrácia"
zdroje:
  - nazov: "Implementačný plán projektu Bitoviny"
    url: "https://github.com/valooo-hero/bitoviny/blob/main/docs/PLAN.md"
  - nazov: "Redakčné zásady"
    url: "https://bitoviny.pages.dev/redakcne-zasady/"
vzorovy: true
---

Bitoviny nie sú bežný spravodajský web. Sú to pokus a ukážka zároveň: redakciu tvorí šesť AI agentov, z ktorých každý vie jednu vec, a jeden človek, ktorý má posledné slovo.

## Prečo šesť agentov a nie jeden

Jeden veľký jazykový model by článok napísal aj sám. Lenže ten istý model, ktorý text napísal, zle hľadá vlastné chyby. Preto je práca rozdelená tak, ako v skutočnej redakcii.

- **Zberač** číta RSS kanály technologických portálov a vyberá témy.
- **Autorka** z viacerých zdrojov skladá pôvodný slovenský text.
- **Factchecker** každé tvrdenie hľadá v zdrojoch a čo nenájde, vráti.
- **Korektorka** opraví gramatiku, ale nesmie siahnuť na čísla a mená.
- **Fotoeditor** stráži autorské práva k obrázkom.
- **Ilustrátorka** nakreslí obrázok, keď sa žiadny použiteľný nenájde.

Každý agent dostane len to, čo potrebuje, a jeho výstup kontroluje ďalší v poradí.

## Kde je človek

Na konci. Editor vidí hotový článok spolu so správou od agentov: ktoré tvrdenia sa podarilo overiť, čo zmenila korektúra a ktoré obrázky sú podozrivé. Až potom rozhodne, či text vyjde.

Fotku, pri ktorej agent našiel znaky autorskej ochrany, systém do článku vôbec nevloží. Editor ju musí vymeniť alebo výslovne potvrdiť.

## Čo je na tom verejné

Všetko. Zdrojový kód, pokyny pre agentov aj zoznam zdrojov sú na GitHube. Pri článkoch pribudne odkaz na záznam, v ktorom je vidieť, čo ktorý agent dostal a čo vrátil.

Projekt beží výhradne na bezplatných tarifách. Aj to je súčasť pokusu: zistiť, koľko redakčnej práce sa dá urobiť bez rozpočtu.

## Čo zatiaľ chýba

Agenti ešte nepíšu. Hotový je portál, pipeline sa stavia po fázach. Články, ktoré tu teraz nájdete, sú vzorové a sú tak aj označené.
