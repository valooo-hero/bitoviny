---
title: Chatbot inšpirovaný ChatGPT beží na Super Nintende
perex: Experiment Benja Edwardsa prináša na starú konzolu malý jazykový model s 2,2 milióna parametrov. Odpovede sú obmedzené, no projekt možno spustiť aj na skutočnom SNES-e.
sekcia: hardver
tagy:
  - Super Nintendo
  - SNES
  - ChatGPT
  - umelá inteligencia
publikovane: 2026-11-22T03:34:04+00:00
obrazok:
  src: /obrazky/chatbot-inspirovany-chatgpt-bezi-na-super-nintende-mwsfqa9p.jpg
  alt: Nintendo-Super-NES-Console-101-FL
  popisok: Nintendo-Super-NES-Console-101-FL
  kredit: Evan-Amos / Wikimedia Commons
  licencia: Public domain
  ai: false
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
zdroje:
  - nazov: "The Register: ChatGPT shrunk down to run on a Super Nintendo"
    url: https://www.theregister.com/offbeat/2026/11/21/chatgpt-shrunk-down-to-run-on-a-super-nintendo/5311418
  - nazov: "Tom's Hardware: 35-year-old SNES runs ChatGPT, accelerated with a Super FX 2 chip — 21 MHz of RISC muscle speeds 2.2M parameter chatbot replies"
    url: https://www.tomshardware.com/tech-industry/artificial-intelligence/35-year-old-snes-runs-chatgpt-accelerated-with-a-super-fx-2-chip-21-mhz-of-risc-muscle-speeds-2-2m-parameter-chatbot-replies
---

Benj Edwards vytvoril chatbot pre konzolu Super Nintendo, ktorý využíva jazykový model s 2,2 milióna parametrov. Projekt ChatGPT for SNES si možno vyskúšať v emulátore aj stiahnuť ako ROM pre skutočný hardvér. Nejde však o zmenšenú verziu dnešného asistenta s porovnateľnými schopnosťami: tvorca ho opisuje ako experiment, ktorý často odpovedá nesprávne.

Ako informovali The Register a Tom’s Hardware, model vznikol destiláciou veľkého modelu GPT-OSS-120b. Pri tomto postupe sa z väčšieho modelu pripravili tréningové rozhovory pre menší systém. Výsledkom je chatbot, ktorý sa zmestí do možností hernej konzoly, no jeho vedomosti aj kvalita odpovedí sú výrazne obmedzené.

## Dve verzie s odlišnými možnosťami

Projekt ponúka základnú verziu s veľkosťou približne 4 MB a rozšírenú verziu s veľkosťou 19 MB. Druhá obsahuje aj zbierku úvodných viet z približne 150-tisíc článkov anglickej Wikipédie v jednoduchej angličtine. Táto doplnková databáza má modelu poskytnúť viac faktických informácií; podľa testu Tom’s Hardware môže pomôcť aj pri výpočtoch.

Pri porovnaní oboch variantov sa rozdiel podľa The Register prejaví výrazne. Edwards upozorňuje, že model pozná asi 8 000 slov a môže sa mýliť, niekedy aj s veľkou istotou. Chyby sa môžu nachádzať aj v samotnej faktografickej databáze. Tvorca preto projekt neprezentuje ako užitočného asistenta, ale skôr ako ukážku toho, čo sa dá na starom hernom zariadení vytvoriť.

Rozhranie zachováva atmosféru konzoly: pri písaní zaznievajú dobové zvukové efekty a aplikáciu sprevádza chiptune hudba. V emulátore možno zadávať text z počítačovej klávesnice, takže na komunikáciu netreba ovládač.

## Čo robí koprocesor a čo potrebuje konzola

Tom’s Hardware uvádza, že výpočty zrýchľuje čip Super FX 2, ktorý pracuje na frekvencii 21,47 MHz. Pôvodne pomáhal hrám s pokročilejšou 2D grafikou a 3D polygónmi. Hlavný procesor SNES-u podľa toho istého zdroja pracuje na frekvencii 2,68 MHz. Super FX 2 tak poskytuje projektu dodatočný výkon, hoci z neho nerobí moderný chatbot.

Na spustenie na skutočnej konzole treba flashovaciu kazetu, ktorá podporuje príslušný koprocesor. The Register spomína modely FXPak Pro a SD2SNES. Rozšírená verzia s encyklopedickou databázou navyše potrebuje podporu MSU-1, rozšírenia umožňujúceho ukladať doplnkové dáta na kazete.

The Register zároveň uvádza, že existuje aj základná verzia upravená tak, aby fungovala bez čipu Super FX. Odpovede sú podľa Edwardsa v takom prípade slabšie. V tomto bode sa zdroje nezhodujú priamo: Tom’s Hardware zdôrazňuje zrýchlenie pomocou Super FX 2, zatiaľ čo The Register opisuje aj variant bez koprocesora.

## Kód napísala AI, návrh určil človek

Edwards pre The Register povedal, že samotné programovanie zabezpečili AI nástroje, no človek určil rozsah projektu, spôsob fungovania aj podobu rozhrania. Tvorca sa podľa vlastných slov už dlhšie zaujíma o malé „hovoriace stroje“ a chce skúmať, či sa dajú takéto modely ešte zlepšiť.

Chatbot pre SNES je súčasťou širšieho experimentovania: Edwards vytvoril aj ROM pre pôvodný Nintendo Entertainment System, v ktorej menší model simuluje rozhovor s duchom. Pri SNES projekte však AI agenti zapojení do programovania odhadli, že možnosti modelu na danom hardvéri sa už vyčerpali. Edwards s tým nesúhlasí a tvrdí, že hľadá ďalšie spôsoby, ako zlepšiť jeho súdržnosť.
