---
title: PHP Foundation pripravuje na štvrtok ďalšiu kritickú bezpečnostnú aktualizáciu
perex: Vydanie má obsahovať opravy chýb označených ako kritické, hoci podľa nadácie vyžadujú nezvyčajné nastavenia alebo konfiguráciu. Jedna z nich umožňuje vzdialené spustenie kódu.
sekcia: bezpecnost
tagy:
  - PHP
  - kyberbezpečnosť
  - zraniteľnosti
publikovane: 2026-11-19T09:20:03Z
obrazok:
  src: /obrazky/php-foundation-pripravuje-na-stvrtok-dalsiu-kriticku-bezpecnostnu-aktualizaciu-mwnca28f.jpg
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
  - nazov: "The Register: Get ready for another critical PHP security release to drop"
    url: https://www.theregister.com/patches/2026/11/18/get-ready-for-another-critical-php-security-release-to-drop/5310911
---

PHP Foundation plánuje vydať ďalšiu bezpečnostnú aktualizáciu vo štvrtok medzi 14:00 a 14:30 UTC. Nadácia v upozornení zverejnenom v stredu označila najzávažnejšie chyby v pripravovanom vydaní za kritické a vyzvala používateľov PHP, aby boli pripravení aktualizovať bez zbytočného odkladu. Podrobnosti o väčšine zraniteľností zatiaľ nezverejnila.

## Jedna chyba umožňuje vzdialené spustenie kódu

Známe je, že medzi opravovanými problémami bude zraniteľnosť CVE-2026-115560, ktorá umožňuje vzdialené spustenie kódu (RCE). Ako uviedol portál The Register, PHP Foundation už v októbri potvrdila, že toto označenie pridelila ďalšej chybe tohto typu. Vtedy však vysvetlila, že nejde o prípad, ktorý by si vyžadoval mimoriadnu opravu.

Výkonná riaditeľka nadácie Elizabeth Barron v októbri uviedla, že problém si vyžaduje veľmi nepravdepodobnú kombináciu nastavení a konkrétneho kódu aplikácie. Podľa nej sa takáto konfigurácia v bežnej praxi PHP pravdepodobne nevyskytuje. Nadácia zároveň upozornila, že riziko možno obmedziť zmenou nastavenia.

## Riziko závisí od konfigurácie aplikácie

Na zneužitie chyby musí aplikácia najprv používať hodnotu `php_binary` alebo `php_serialize` v nastavení `session.serialize_handler` a neskôr ju za behu zmeniť na `php` pomocou `ini_set()` ešte pred volaním `session_start()`. Súčasne musí byť zapnutá funkcia sledovania priebehu nahrávania súborov v relácii.

PHP Foundation označila takúto zostavu za veľmi neobvyklú. Jej predchádzajúce informačné upozornenie odporúčalo dočasne nastaviť `session.upload_progress.enabled=0`, čo má podľa nadácie používateľov chrániť pred týmto nepravdepodobným spôsobom vzdialeného spustenia kódu. Nová aktualizácia má priniesť riadnu opravu; presný rozsah ostatných chýb zatiaľ zverejnený nebol.

## Po októbrových núdzových opravách

Nové vydanie prichádza po rušnom októbri, keď bezpečnostné tímy nasadzovali núdzové opravy dvoch zraniteľností známych ako PHP2Shell: CVE-2026-109618 a CVE-2026-109619. The Register uvádza, že tieto chyby súviseli s bezpečnosťou pamäte a PHP podľa článku používa približne 70 percent webových stránok.

Americká agentúra CISA zaradila obe zraniteľnosti do katalógu známych zneužívaných chýb 26. októbra. Výskumníci zo spoločnosti Dream neskôr informovali, že podozriví čínski útočníci spojili PHP2Shell s chybou umožňujúcou zvýšenie oprávnení v jadre Linuxu. Takto podľa nich získali najvyššie oprávnenia na 25 serveroch vrátane firewallov Palo Alto Networks napojených na organizácie spojené s vládou USA.

Dream uviedol, že cieľmi boli organizácie v USA, Japonsku, na Taiwane a v Južnej Kórei a, že útočníci si podľa odhadu výskumníkov pravdepodobne zachovali vzdialený prístup do časti napadnutých sietí. Tieto zistenia sa týkajú októbrových zraniteľností PHP2Shell, nie chyby CVE-2026-115560. Správcovia PHP by preto mali sledovať oznámenie nadácie a po sprístupnení vydania preveriť, či sa ich systémy týkajú opravované problémy.
