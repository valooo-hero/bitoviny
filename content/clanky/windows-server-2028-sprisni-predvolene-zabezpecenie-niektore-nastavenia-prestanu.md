---
title: Windows Server 2028 sprísni predvolené zabezpečenie, niektoré nastavenia prestanú fungovať
perex: Microsoft sprístupnil verejnú ukážku novej verzie serverového systému. Zabezpečený režim sa týka Server Core a môže vyžadovať úpravy starších protokolov, prihlasovania či administrátorských nástrojov.
sekcia: softver
tagy:
- Windows Server
- Microsoft
- kybernetická bezpečnosť
publikovane: '2026-11-19T04:39:02+00:00'
obrazok:
  src: /obrazky/zastupny.jpg
  alt: Zástupný obrázok, čaká na výber editora
  popisok: Obrázok čaká na výber editora.
  kredit: Bitoviny
  licencia: vlastná ilustrácia
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
zdroje:
- nazov: 'The Register: Windows Server 2028 won''t be compatible by default'
  url: https://www.theregister.com/os-platforms/2026/11/18/windows-server-2028-wont-be-compatible-by-default/5310766
- nazov: 'BleepingComputer: Microsoft announces Windows Server 2028 with hardened security'
  url: https://www.bleepingcomputer.com/news/microsoft/microsoft-announces-windows-server-2028-with-hardened-security/
- nazov: 'Ars Technica: Windows Server 2028 trades compatibility for out-of-the-box security'
  url: https://arstechnica.com/gadgets/2026/11/windows-server-2028-public-preview-bets-on-a-security-first-approach/
---

Microsoft predstavil verejnú ukážku systému Windows Server 2028 na konferencii Ignite 2026. Hlavnou zmenou je prísnejšie zabezpečenie zapnuté už pri inštalácii edície Server Core. Pre správcov to znamená menej práce s úvodným spevňovaním systému, ale aj riziko, že niektoré doteraz používané nastavenia či nástroje budú treba upraviť.

Ako upozornil The Register, Microsoft varuje pred možnými problémami so staršími protokolmi, zastaraným prihlasovaním a niektorými nástrojmi a skriptmi na správu. To, že konfigurácia funguje na Windows Server 2025, preto podľa portálu nezaručuje bezproblémový prechod na novú verziu.

## Zabezpečenie bude súčasťou východiskového nastavenia

Zmena sa týka edície Server Core, nie inštalácie Windows Servera s grafickým prostredím Desktop Experience. Ako píše Ars Technica, Microsoft označuje novú konfiguráciu ako Hardened Server Core a uvádza, že jej bezpečnostný rámec vychádza aj z odporúčaní DISA STIG, teda bezpečnostných pravidiel americkej vládnej agentúry.

BleepingComputer uvádza, že od prvého spustenia bude aktívnych niekoľko stoviek bezpečnostných nastavení. Patrí medzi ne uprednostnenie Kerberosu pred NTLM, ochrana procesu LSASS, obmedzenie TLS na moderné šifrovacie súpravy a prísnejšie overovanie pri vzdialenom prístupe. Výmena kľúčov má využívať hybridný postkvantový mechanizmus ML-KEM. Nová bezpečnostná základňa má správcom umožniť jednotlivé nastavenia podľa potreby uvoľniť.

Nie všetky plánované ochrany sú už hotové. Podľa BleepingComputer Microsoft ešte pracuje napríklad na blokovaní NTLM a ďalšom zabezpečení tlače či RPC. Trusted Launch má rozšíriť ochranu virtuálnych strojov a podpora Confidential VM je určená pre kompatibilný hardvér.

## Prechod si vyžiada testovanie

Zdroje sa zhodujú, že nové predvolené nastavenia môžu narušiť kompatibilitu, no rozsah ich použitia treba rozlišovať. The Register uvádza, že bezpečnostné spevnenie sa podľa informácie, ktorú Microsoft poskytol odborníkovi z Lansweeper, týka iba nových inštalácií. Ak to zostane aj vo finálnej verzii, aktualizácie existujúcich serverov by mohli byť jednoduchšie, no nemuseli by získať nové predvolené ochrany. Ars Technica potvrdzuje obmedzenie na Server Core, nie však túto podmienku pri aktualizáciách.

Esben Dochy z Lansweeperu pre The Register uviedol, že spevnenie je správny smer, ale pre tímy pridá prácu. Podľa údajov spoločnosti tvoril Windows Server 2019 v októbri 2026 tretinu sledovaného používania, kým Windows Server 2025 dosiahol 7 percent. Dochy očakáva, že nasadzovanie bude závisieť najmä od konca podpory starších verzií. Windows Server 2025 má podľa The Register rozšírenú podporu do roku 2034.

## Novinky pre úložiská, správu a AI

Windows Server 2028 má predvolene zapnúť natívne NVMe úložisko a podporiť NVMe over TCP aj RDMA. Microsoft plánuje tiež zavádzanie systému z ReFS. Správcovia budú môcť využiť správu serverov cez Intune, ktorá prináša postupy známe zo správy koncových zariadení; naďalej zostáva dostupný aj Azure Arc.

Nová verzia má podporovať aj lokálne inferovanie modelov a akcelerovaný hardvér vrátane AMD Instinct MI350P. BleepingComputer spomína nástroje a prostredia Windows ML, Foundry Local, vLLM a Llama.cpp. Záujemcovia môžu skúšať ukážku cez Windows Insider Program for Windows Server alebo požiadať o prístup v programe Technology Adoption Program.
