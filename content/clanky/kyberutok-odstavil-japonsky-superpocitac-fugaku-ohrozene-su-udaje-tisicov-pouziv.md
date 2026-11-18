---
title: Kyberútok odstavil japonský superpočítač Fugaku, ohrozené sú údaje tisícov používateľov
perex: RIKEN vyšetruje prienik cez verejný panel so stavom systému. Útočník sa podľa zistení dostal na interné servery a nainštaloval škodlivý softvér; rozsah odcudzených údajov zatiaľ nie je jasný.
sekcia: bezpecnost
tagy:
  - Fugaku
  - RIKEN
  - kyberútok
  - superpočítače
publikovane: 2026-11-18T05:01:00+00:00
obrazok:
  src: /obrazky/kyberutok-odstavil-japonsky-superpocitac-fugaku-ohrozene-su-udaje-tisicov-pouziv-mwm4600g.jpg
  alt: RIKEN R-CCS Fugaku
  popisok: RIKEN R-CCS Fugaku
  kredit: Barsaka2 / Wikimedia Commons
  licencia: CC0
  ai: false
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
zdroje:
  - nazov: "Tom's Hardware: Japan’s most powerful supercomputer may have been hacked, over 4,000 users’ personal data stolen"
    url: https://www.tomshardware.com/tech-industry/supercomputers/japans-most-powerful-supercomputer-may-have-been-hacked-over-4-000-users-personal-data-stolen-investigation-opened-into-fugaku-breach-after-unauthorized-software-installed
  - nazov: "BleepingComputer: Japan takes Fugaku supercomputer offlline after cyberattack"
    url: https://www.bleepingcomputer.com/news/security/japan-takes-fugaku-supercomputer-offlline-after-cyberattack/
  - nazov: "The Register: Japan's Fugaku supercomputer has decidedly un-super security"
    url: https://www.theregister.com/security/2026/11/17/japans-fugaku-supercomputer-has-decidedly-un-super-security/5310333
---

Japonský superpočítač Fugaku je po kybernetickom útoku odstavený. Jeho prevádzkovateľ, výskumné centrum RIKEN, uviedol, že neznámy útočník v období od 10. do 13. novembra zneužil verejne dostupný panel zobrazujúci prevádzkový stav systému. Cez neho sa dostal na viaceré interné servery a nainštaloval na ne škodlivý softvér.

Pri incidente mohli byť ohrozené osobné údaje 4 222 používateľov Fugaku a 375 používateľov menšieho superpočítača Rikyu. RIKEN však podľa správ zatiaľ nevie s istotou určiť, ktoré informácie útočník skutočne získal. K útoku sa nikto neprihlásil a jeho pôvod nebol zistený.

## Aké údaje mohli byť zasiahnuté

Medzi údajmi spojenými s používateľmi sú mená, e-mailové adresy a identifikátory účtov. BleepingComputer uvádza aj súkromné SSH kľúče a prístupové kľúče uložené na počítačoch používateľov, ako aj výskumné súbory. Podľa The Registeru servery obsahovali prihlasovacie údaje na superpočítače a služby, ktoré neprevádzkuje RIKEN.

Rozsah úniku výskumných dát zostáva nejasný. The Register píše, že vyšetrovatelia zatiaľ nenašli dôkaz o ich úniku, no nevedia potvrdiť, aké informácie opustili sieť. BleepingComputer zasa medzi potenciálne zasiahnutými údajmi uvádza výskumné súbory uložené na počítačoch používateľov. To samo osebe nepotvrdzuje, že ich útočník odcudzil.

RIKEN podľa BleepingComputeru zistil, že útočník skúšal použiť niektoré získané prístupové kľúče na pripojenie k ďalším systémom. Vyšetrovanie však zatiaľ nepotvrdilo ďalší neoprávnený prístup ani krádež výsledkov výskumu. Organizácia spolupracuje s prevádzkovateľmi dotknutých systémov na preverení týchto pokusov.

## Vyšetrovanie a obmedzenie škôd

Panel, ktorý mal slúžiť na zobrazovanie prevádzkového stavu Fugaku, RIKEN odstavil. Centrum tiež zablokovalo prístupové kľúče používateľov a vyzvalo ich, aby zneplatnili a vymenili prihlasovacie údaje uložené na superpočítači. Používateľom odporúča obozretnosť aj pri e-mailoch, ktoré sa môžu vydávať za správy od RIKEN.

Správy sa nezhodujú v presnom čase odstavenia systému. BleepingComputer uvádza, že RIKEN vypol Fugaku 14. novembra, kým The Register píše, že ho prevádzkovateľ odstavil po pokuse o prihlásenie zaznamenanom 13. novembra. Tom’s Hardware uvádza, že podozrivú komunikáciu zaznamenali 12. novembra a prístup zablokovali 14. novembra.

RIKEN podľa BleepingComputeru plánuje preveriť zneužitú softvérovú zraniteľnosť, obnoviť napadnuté servery a skontrolovať nastavenie siete. Prevádzka Fugaku sa má obnoviť až po tom, ako centrum vyhodnotí systém ako bezpečný. Japonská vláda sa do vyšetrovania zapojila prostredníctvom ministerstva školstva, kultúry, športu, vedy a technológií. Hlavný tajomník kabinetu Minoru Kihara zdôraznil, že ochrana systému je dôležitá, no zároveň treba obmedziť dosah incidentu na výskum.

Fugaku slúži akademickým aj priemyselným výskumníkom a využíva sa napríklad pri vývoji liekov, predpovediach extrémneho počasia či simuláciách šírenia vírusov vzduchom. Podľa BleepingComputeru dosahuje výkon 537 petaflopsov; menší Rikyu je určený na výskum umelej inteligencie a má výkon 64 petaflopsov. Odstávka preto obmedzuje prístup výskumníkov k výpočtovým kapacitám, kým RIKEN dokončuje vyšetrovanie.
