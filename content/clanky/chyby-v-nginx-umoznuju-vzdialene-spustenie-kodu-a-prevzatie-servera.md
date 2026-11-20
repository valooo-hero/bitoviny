---
title: Chyby v NGINX umožňujú vzdialené spustenie kódu a prevzatie servera
perex: Dve zraniteľnosti HTTP/2 môžu útočníkom otvoriť cestu k vykonaniu kódu bez prihlásenia. Výskumníci zároveň ukázali, že jedna z nich sa dá spojiť s chybou jadra Linuxu a získať prístup root.
sekcia: bezpecnost
tagy:
  - NGINX
  - HTTP/2
  - kybernetická bezpečnosť
publikovane: 2026-11-20T04:25:21+00:00
obrazok:
  src: /obrazky/chyby-v-nginx-umoznuju-vzdialene-spustenie-kodu-a-prevzatie-servera-mwp2i291.webp
  alt: Ilustračný obrázok.
  popisok: Ilustračný obrázok.
  kredit: Bitoviny / FLUX.1-schnell
  licencia: vygenerované AI
  ai: true
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
zdroje:
  - nazov: "BleepingComputer: Critical NGINX ‘NGINX2Root’ bugs let attackers hijack servers"
    url: https://www.bleepingcomputer.com/news/security/critical-nginx-nginx2root-bugs-let-attackers-hijack-servers/
---

Dve kritické chyby v NGINX môžu umožniť neautentifikovaným útočníkom spustiť na zraniteľnom serveri vlastný kód. Bezpečnostní výskumníci ich označili spoločným názvom „nginx2root“ a pri jednej zraniteľnosti predviedli aj cestu k oprávneniam root, keď ju spojili s ďalšou chybou v jadre Linuxu. Opravy sú dostupné; prevádzkovatelia majú aktualizovať bez odkladu.

Ako uviedol portál BleepingComputer, chyby súvisia s obsluhou HTTP/2. Zraniteľnosti nezávisle objavili tímy z Xint, Wiz, Ikotas Labs, Metnir a Rapid7. Xint navyše našiel ďalšie tri chyby umožňujúce vzdialené spustenie kódu.

## Dve chyby v obsluhe HTTP/2

Prvá chyba, CVE-2026-123007, vzniká pri spracovaní riadenia toku a môže poškodiť pamäť procesu NGINX. Podľa zistení zasahuje verzie od 1.9.5 po 1.31.8. Výskumníci z Wiz predviedli vzdialené spustenie kódu na serveri, ktorý cez HTTP/2 s TLS poskytoval obyčajné statické súbory.

Xint ukázal, že zraniteľnosť možno spojiť s osobitnou chybou v podsystéme SCTP jadra Linuxu. Takýto reťazec útoku môže umožniť únik z kontajnera NGINX a získanie oprávnení root na hostiteľskom systéme. Nejde teda o tvrdenie, že samotná chyba NGINX automaticky poskytuje prístup root.

Druhá zraniteľnosť, CVE-2026-123633, je chyba typu use-after-free. Týka sa verzií od 1.19.7 po 1.31.8 a prichádza do úvahy, keď NGINX prijíma spojenia HTTP/2 a preposiela požiadavky na backend. Pri nedostatku voľných miest pre spojenia môže proces uvoľniť pamäť, ktorú ešte používa požiadavka. Wiz aj tu demonštroval vzdialené spustenie kódu, no svoj dôkaz konceptu zatiaľ nezverejnil.

## Opravy a dočasné opatrenie

F5 chyby opravil vo vydaniach NGINX Open Source 1.30.7 (stabilná vetva) a 1.31.9 (mainline). Používatelia NGINX Plus majú prejsť na verziu 37.0.8.1 alebo 37.3.0.1. Aktualizácia F5 zahŕňa aj ďalších päť bezpečnostných chýb. Medzi nimi je CVE-2026-118899, ktorá môže pri spracovaní tela požiadavky cez TLS 1.3 dostať proces do nekonečnej slučky a spôsobiť odmietnutie služby.

Ak správca nemôže aktualizovať okamžite, môže dočasne vypnúť HTTP/2. Toto opatrenie však podľa BleepingComputer pokrýva iba dve chyby „nginx2root“, nie ostatné problémy uvedené v bezpečnostnej aktualizácii. Ďalšie tri chyby nájdené Xint sa týkajú HTTP/3 reverse proxy, DNS pri podpožiadavkách a overovania v mail proxy.

## Riziko závisí od konfigurácie

Samotné číslo verzie nestačí na potvrdenie, že server možno napadnúť. Útočník potrebuje dosiahnuteľný, neopravený server s povoleným HTTP/2; druhá chyba navyše predpokladá preposielanie požiadaviek na backend. Opravy mohli byť do niektorých distribúcií spätne prenesené bez zmeny čísla verzie.

Bezpečnostný výskumník Florian Roth podľa BleepingComputer upozornil, že tvrdenia o plošnom ohrození založené len na odhalených verziách môžu byť zavádzajúce. Censys k 19. novembru odhadoval približne 8,8 milióna služieb potenciálne zraniteľných voči CVE-2026-123007. Viac než 511 000 predtým vystavených služieb už podľa spoločnosti opravili alebo zmiernili ich riziko. Pri ďalších 104 miliónoch služieb nebola verzia zverejnená, takže ich stav sa nedá spoľahlivo určiť. Tieto čísla preto neznamenajú, že všetky uvedené servery sú skutočne napadnuteľné.
