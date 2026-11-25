---
title: AI agenty a bežné nástroje našli kľúč od finančnej firmy za necelých šesť minút
perex: Bezpečnostní experti varujú pred novou vlnou útokov, pri ktorých hackeri využívajú voľne dostupné open-source AI agenty na automatizáciu prienikov do kritických sietí.
sekcia: bezpecnost
tagy:
  - AI
  - Jesta
  - OpenCode
  - Cairn
  - bezpecnost
publikovane: 2026-11-25T11:24:55Z
obrazok:
  src: /obrazky/ai-agenty-a-bezne-nastroje-nasli-kluc-od-financnej-firmy-za-necelych-sest-minut-mww1dpq0.webp
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
  - nazov: "The Register: An AI coding agent, a browser, and a Mac tool found a financial firm's access key in under 6 minutes"
    url: https://www.theregister.com/security/2026/11/24/an-ai-coding-agent-a-browser-and-a-mac-tool-found-a-financial-firms-access-key-in-under-6-minutes/5311922
  - nazov: "Ars Technica: Amazon says hackers' AI agents found and exploited 0-day with little human input"
    url: https://arstechnica.com/security/2026/11/amazon-says-hackers-ai-agents-found-and-exploited-0-day-with-little-human-input/
---

Bezpečnostný start-up Jesta so sídlom v Tel Avive zdokumentoval pokus o kybernetický útok, pri ktorom útočník z Bukurešti využil voľne dostupný open-source programovací agent s názvom OpenCode. Útok, ktorý mieril na poprednú finančnú inštitúciu, trval menej ako šesť minút a vyžiadal si minimálne úsilie zo strany človeka. 

## Priebeh incidentu

Podľa zistení spoločnosti Jesta sa útok začal 16. novembra o 4:24:57 ráno východného času. Útočník použil prehliadač Chrome bežiaci na zariadení Mac a nástroj na príkazovom riadku curl verzie 8.7.1, pričom agent prenášal informácie medzi týmito nástrojmi. Nástroj OpenCode nebol navrhnutý na hackerské účely, no umožňuje pripojenie k viac ako dvom stovkám modelov vrátane modelov od spoločností Anthropic, OpenAI, Google či DeepSeek. 

Agent najprv neúspešne žiadal o prístup k hlavnej stránke systému a následne testoval rôzne požiadavky. Keď systém odmietol vydať API definíciu, agent o niekoľko sekúnd neskôr vyskúšal inú adresu. Táto adresa však bola vopred pripravenou pascou, takzvaným decoy prostredím, ktoré vytvorila firma Jesta na oklamanie votrelcov. V tomto falošnom prostredí agent objavil prístupový kľúč a následne otestoval niekoľko scenárov vrátane použitia falošného kľúča, žiadneho kľúča a vlastného vymysleného kľúča. 

Spoluzakladateľ a technologický riaditeľ spoločnosti Jesta Lior Finkelshtein uviedol, že agent pracoval presne tak, ako by pracoval bežný vývojár. Prečítal si dokumentáciu k rozhraniu API, našiel kľúč a následne overil, či je zámok reálny. Celá operácia trvala päť minút a štridsaťštyri sekúnd, po ktorých útočník prestal vyvíjať aktivitu. 

## Problémy pre obranu sietí

Bezpečnostní experti upozorňujú, že bežné obranné mechanizmy založené na zoznamoch blokovaných adries, takzvaných blocklistoch, by v tomto prípade nedokázali útok zastaviť. Adresa útočníka totiž dovtedy nebola evidovaná ako škodlivá. Finkelshtein odporúča, aby sa obranné tímy namiesto IP adries zameriavali na správanie návštevníkov, keďže kombinácia netradičných krokov v priebehu niekoľkých minút môže odhaliť prítomnosť autonómneho agenta.

Tento incident nie je ojedinelým prípadom využitia umelej inteligencie pri útokoch. Spoločnosť Amazon nedávno informovala o tom, že hackeri využili open-source framework s názvom Cairn na vyhľadanie a zneužitie zero-day zraniteľnosti. Útočníci poskytli agentom bežiacim na tomto frameworku zoznam IP adries a jednoduchý pokyn v zjednodušenej čínštine na získanie prístupu k serveru Východoázijskej univerzity. 

## Súvislosti a ďalší vývoj

Framework Cairn bol pôvodne vytvorený ako nástroj pre obrancov na autonómne penetračné testovanie. Výskumníci zo spoločnosti Palo Alto Networks však zaznamenali jeho využitie útočníkmi pri dvadsiatich piatich autonómnych operáciách cielených na organizácie v oblasti polovodičov, obrany a občianskej spoločnosti, pričom najmenej desať organizácií bolo úspešne napadnutých. 

Odborníci zdôrazňujú, že tieto incidenty ukazujú rýchlosť a vytrvalosť, akú ponúkajú moderné nástroje ponúkajú, a bezpečnostné tímy by sa mali pripraviť na nárast podobne vedených automatizovaných operácií.
