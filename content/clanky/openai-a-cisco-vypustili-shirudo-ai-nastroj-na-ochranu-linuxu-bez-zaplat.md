---
title: OpenAI a Cisco vypustili Shirudo, AI nástroj na ochranu Linuxu bez záplat
perex: Otvorený nástroj využíva eBPF a AI agentov na blokovanie zneužitia zraniteľností ešte predtým, než administrátori stihnú nasadiť záplaty. Ľudia však majú nad každou ochranou finálne slovo.
sekcia: softver
tagy:
- OpenAI
- Cisco
- Linux
- eBPF
- bezpecnost
publikovane: '2026-11-25T07:05:50+00:00'
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
- nazov: 'BleepingComputer: New Shirudo tool uses AI to shield unpatched Linux systems from exploits'
  url: https://www.bleepingcomputer.com/news/security/new-shirudo-tool-uses-ai-to-shield-unpatched-linux-systems-from-exploits/
- nazov: 'The Register: Cisco and OpenAI pitch eBPF kernel plugins as the way to tame the patchpocalypse'
  url: https://www.theregister.com/security/2026/11/24/cisco-and-openai-pitch-ebpf-kernel-plugins-as-the-way-to-tame-the-patchpocalypse/5311795
---

OpenAI a Cisco spoločne vydali otvorený nástroj Shirudo, ktorý má chrániť linuxové systémy pred zneužitím zraniteľností v čase, keď administrátori ešte nestihli nasadiť záplaty. Nástroj nasadzuje dočasné ochrany za behu, a to bez nutnosti reštartu služieb.

## Ochrana bez reštartu

Podstatou Shirudo je technológia eBPF (extended Berkeley Packet Filter), ktorá umožňuje spúšťať programy v riadenom prostredí priamo v jadre (kernel) operačného systému, bez zásahu do jeho zdrojového kódu a bez reštartu. eBPF sa už dlhšie používa napríklad na sledovanie siete a výkonu; Cisco a OpenAI ho teraz chcú využiť na bezpečnosť.

Nástroj vytvára takzvané „shields“ (anglicky štíty) – cielené ochrany, ktoré blokujú konkrétne nebezpečné správanie, no bežné fungowanie aplikácií nechávajú nedotknuté. Ako uviedol portál BleepingComputer, OpenAI vypichol štyri hlavné vlastnosti: ochranu za behu bez reštartu, AI podporu pri vyšetrovaní zraniteľností a tvorbe štítov, dôveryhodné nasadenie cez kryptografické podpisy a overovacie mechanizmy jadra a hardvérové overenie pomocou čipov TPM.

Kľúčové je, že samotné nasadenie ostáva pod kontrolou ľudí. Výskumníci oboch firiem predviedli, že vygenerovaný štít dokázal zablokovať pokus o zneužitie Java4Shell proti bežiacej službe Elasticsearch bez prerušenia jej prevádzky.

## Prečo prichádza práve teraz

Podľa The Register Cisco a OpenAI reagujú na obrovský počet zraniteľností – tento rok ich bolo nahlásených viac než 100 000, pričom mnohé boli pridané nástrojmi na hľadanie chýb poháňanými umelou inteligenciou. Organizácie, ktoré už dnes zápasia s testovaním a nasadzovaním opráv, tak čelia záplave, ktorú nestíhajú záplatovať.

Riešením sú takzvané kompenzačné kontroly – úpravy aplikácií či infraštruktúry, ktoré ich utužia proti zraniteľnosti bez záplaty. Nejde o novinku: spoločnosť Rimini Street ich používa roky, VMware zaviedlo „virtuálne záplaty“ a podobný prístup ponúkajú aj Palo Alto Networks či Rapid7. Cisco a OpenAI sa odlišujú tým, že Shirudo sprístupnili ako open-source a chcú, aby ho ďalší hráči rozvíjali.

Podľa odporúčaní by AI agenti mali skenovať infraštruktúru, nájsť zraniteľnosti a pomocou nástrojov ako OpenAI Codex písať kompenzačné kontroly v podobe eBPF programov „strojovou rýchlosťou“. Firmy plánujú dodávať aj pripravené, otestované štíty spolu so zverejnením zraniteľností, a to až kým nebude dostupná záplata. Štíty sa šíria ako kryptograficky podpísané balíčky „.bee“ cez OCI registry.

## Tetragon, Codex a byznys

Shirudo nie je úplne nový základ. Výskumníci z Isovalentu – cloudovej bezpečnostnej firmy, ktorú Cisco kúpil v roku 2024 – vysvetlili, že „Shirudo is a rewrite of Tetragon“, otvoreného eBPF nástroja z roku 2022, na ktorom stojí aj Cisco Live Protect. Nástroj sa okrem eBPF dokáže podľa Isovalentu zásahom do bajtkódu chrániť aj samotné aplikácie a po nasadení štítu ukazuje počet zásahov, teda kde sa útočníci pokúšali preniknúť.

The Register upozorňuje, že krok firiem nie je úplne nezištný: ak sa Shirudo ujme, môže to zvýšiť dopyt po OpenAI Codex. Cisco zase vlastní Isovalent, ktorý stál pri zrode eBPF.

## Výhrady a ďalšie kroky

Nie všetci sú nadšení. Marcus Hutchins, hlavný výskumník hrozieb vo firme Expel, pripúšťa, že eBPF má v zmierňovaní zneužití obrovský potenciál – „genuinely so much runtime exploit mitigation potential“ – no nechať AI agentov písať pravidlá, ktoré zasahujú do jadra, nemusí byť dobrý nápad. Upozornil tiež, že nástroj je obmedzený na Linux, pretože macOS a Windows nemajú potrebné komponenty.

OpenAI chystá na 15. decembra technický webinár o tom, ako nástroj kombinuje eBPF a umelú inteligenciu. Shirudo je dostupný ako open-source (BSD + GPL), takže si ho vývojári hneď môžu vyskúšať.
