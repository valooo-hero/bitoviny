---
title: Microsoft pripísal výpadok Exchange Online chybe v júlovej aktualizácii
perex: Chyba v sieťových bránach sa prejavila až pri súbehu zvýšenej záťaže a výpadku časti kapacity. Podľa predbežnej správy sa v najhoršej chvíli stalo neodpovedajúcimi viac než 80 percent serverov.
sekcia: softver
tagy:
  - Microsoft
  - Exchange Online
  - výpadok
  - cloudové služby
publikovane: 2026-11-17T10:06:39Z
obrazok:
  src: /obrazky/microsoft-pripisal-vypadok-exchange-online-chybe-v-julovej-aktualizacii-mwkj2965.jpg
  alt: Ilustračný obrázok.
  popisok: Ilustračný obrázok.
  kredit: Bitoviny / FLUX.1-schnell
  licencia: vygenerované AI
  ai: true
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
  schvalil: sefredaktor
zdroje:
  - nazov: "The Register: Microsoft blames monster email outage on software defect introduced in July fix"
    url: https://www.theregister.com/saas/2026/11/16/microsoft-blames-monster-email-outage-on-software-defect-introduced-in-july-fix/5310026
---

Microsoft v predbežnej správe pripísal rozsiahly výpadok Exchange Online a ďalších služieb chybe v softvéri sieťových brán. Závada sa do nich dostala v júli 2026, no prejavila sa až v novembri, keď sa stretla zvýšená záťaž so zníženou dostupnou kapacitou. V najhoršej chvíli neodpovedalo viac než 80 percent serverov.

Ako informoval portál The Register, Microsoft správu zverejnil 15. novembra. Firma uviedla, že júlová zmena pri vtedajšom testovaní záťažou nevyvolala problémy. Testy však podľa nej viac zohľadňovali menej výkonný hardvér s menším počtom jadier. Chyba sa naopak zhoršovala na novších serveroch s väčším počtom jadier.

## Záťaž odkryla skrytú chybu

Závada spôsobovala súperenie procesov o prístup k systémovým prostriedkom v internom procese Windows. Následkom bolo nadmerné využitie procesora a pamäte a napokon prestali servery správne odpovedať. Microsoft upozornil, že samotný nárast prevádzky ani dočasný výpadok časti kapacity by za bežných okolností nemali stačiť na vyvolanie takého problému.

Kľúčová kombinácia nastala 12. novembra o 0107 UTC, keď Teams prešli na primárnu sieťovú bránu podporujúcu Exchange Online. Súčasne bolo mimo prevádzky takmer 14 percent kapacity brán. Microsoft podľa správy považoval rezervu za dostatočnú a odstavené servery sa mali vracať do služby. Zvýšená prevádzka však aktivovala skrytú chybu.

Keď jeden server stratil spojenie, prevádzka sa presmerovala na ďalší dostupný server, ktorý narazil na rovnaký problém. Takéto presmerovania následne rozširovali poruchu naprieč infraštruktúrou. O 1603 UTC systém na sledovanie pripojenia zaznamenal nárast problémov a o pol hodiny neskôr prišla prvá zákaznícka požiadavka na podporu.

## Obnova si vyžiadala opravu opravy

Obnovené servery boli podľa Microsoftu okamžite znovu preťažené. Automatické postupy obnovy neboli pripravené na taký rozsiahly stav, pričom jednoduchý návrat k predchádzajúcej verzii nebol možný, keďže chybná zmena bola nasadená už pred niekoľkými mesiacmi. Inžinieri preto pripravili aktualizáciu, ktorá vrátila chybnú časť kódu do predtým funkčného stavu, a nasadzovali ju postupne na skupiny serverov.

Microsoft o 0030 UTC 13. novembra identifikoval vyjednávanie spojenia ako hlavnú príčinu problémov s prístupom. O 0720 UTC už podľa správy našiel a nasadil zmierňujúcu opravu. Spoločnosť o 1610 UTC potvrdila, že služby opäť fungujú stabilne; poslednú zákaznícku aktualizáciu vydala 14. novembra o 0415 UTC.

## Nie všetky služby mohli obísť bránu

Niektoré služby, medzi nimi Teams, OneDrive, SharePoint a aplikácie Office, sa dokázali presmerovať mimo chybnej infraštruktúry. Exchange Online takú možnosť podľa Microsoftu nemal z kapacitných dôvodov, čo prispelo k dlhému výpadku e-mailov. Aj preto sa problém výrazne dotkol používateľov Outlooku.

Microsoft pozastavil prebiehajúce aj plánované nasadzovania a zmeny konfigurácie, pridával kapacitu a presmerúval prevádzku, no tieto kroky samy osebe nestačili. Záverečnú správu o incidente má zverejniť 20. novembra. Predbežné zistenia zároveň ukazujú, že testovanie júlovej zmeny nezachytilo podmienky, v ktorých sa neskôr prejavila.
