---
title: Anthropic spúšťa Claude Ship na kontrolu a schvaľovanie zmien v kóde
perex: Nová sada agentov dokáže kontrolovať návrhy zmien, opravovať problémy a schváliť tie, ktoré spĺňajú pravidlá tímu. Funkcia automatického schvaľovania je zatiaľ v beta verzii.
sekcia: ai
tagy:
  - Anthropic
  - Claude
  - AI agenti
  - vývoj softvéru
publikovane: 2026-11-24T13:22:07Z
obrazok:
  src: /obrazky/anthropic-spusta-claude-ship-na-kontrolu-a-schvalovanie-zmien-v-kode-mwuq4muu.webp
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
  - nazov: "TechCrunch: Anthropic launches Claude Ship, letting AI agents review, fix, and approve code changes"
    url: https://techcrunch.com/2026/11/23/anthropic-launches-claude-ship-letting-ai-agents-review-fix-and-approve-code-changes/
  - nazov: "9to5Mac: Anthropic launches new Claude Ship feature for builders"
    url: https://9to5mac.com/2026/11/23/anthropic-launches-new-claude-ship-feature-for-builders/
---

Anthropic predstavil Claude Ship, sadu AI agentov, ktorá má automatizovať kontrolu, opravy aj schvaľovanie zmien v kóde. Kým viaceré nástroje už dokážu navrhovaný kód kontrolovať, novinkou je možnosť zveriť agentovi aj rozhodnutie, či konkrétna zmena spĺňa pravidlá tímu a môže pokračovať k zlúčeniu do projektu.

Ako uvádza TechCrunch, Anthropic ponúka Claude Ship v beta verzii pre tímy používajúce plány Claude Team a Enterprise a repozitáre na GitHube. Samotný Code Review je už všeobecne dostupný; PR Steward a Claude Approvals zostávajú v beta verzii.

## Od kontroly k schváleniu

Claude Ship tvoria tri nástroje: Code Review, PR Steward a Claude Approvals. Spoločne majú pokrývať viac krokov práce s pull requestom, teda návrhom na začlenenie zmien do kódu. Anthropic podľa 9to5Mac tvrdí, že cieľom je obmedziť potrebu manuálne riadiť každý krok tohto procesu.

Code Review kontroluje navrhované zmeny a hľadá v nich problémy. PR Steward sa zameriava na ich následné riešenie: môže reagovať na neúspešné kontroly CI, konflikty pri zlučovaní kódu aj pripomienky od Code Review. Po každom nahratí novej verzie má zanechať komentár s opisom vykonaných úprav a návodom, ako ich v prípade potreby vrátiť späť.

## Pravidlá určuje vývojový tím

Najvýraznejšou súčasťou novinky je Claude Approvals. Tím mu môže zadať schvaľovacie pravidlá v súbore uloženom priamo v repozitári. Podľa TechCrunch môžu byť napísané prirodzeným jazykom a zohľadňovať napríklad zistenia Code Review či vlastné klasifikátory firmy.

Automatické schválenie teda nemá byť bezpodmienečné: agent posudzuje zmeny podľa pravidiel nastavených tímom. Anthropic zároveň uvádza, že ľudia si ponechajú kontrolu nad tým, kde sa Claude Ship spúšťa, aký režim kontroly sa používa a, ktoré zmeny musí posúdiť človek. Dostupné režimy kontroly sú Quick, Standard a Deep.

## Opatrný štart v beta verzii

Keďže schvaľovanie agentom je stále v beta verzii, Anthropic odporúča najskôr používať režim, v ktorom systém rozhodnutia iba zaznamenáva a nemení stav návrhov. Tímy môžu začať aj s jediným repozitárom a nastaviť mesačné limity výdavkov.

Podľa TechCrunch nástroj reaguje na situáciu, keď AI agenti dokážu vytvárať čoraz viac kódu, no jeho kontrola a schvaľovanie môžu vývoj spomaľovať. Claude Ship má automatizovať aj časť práce po vytvorení kódu, pričom rozhodnutie o tom, ktoré zmeny potrebujú ľudský dohľad, zostáva na tíme.

9to5Mac uvádza, že vývojári môžu Claude Ship skúsiť na vlastných pull requestoch pomocou príkazu `/ship` v Claude Code.
