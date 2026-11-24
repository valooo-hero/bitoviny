---
title: Útočníci zneužívajú kritickú chybu v Cisco Expressway na získanie práv root
perex: CISA označila zraniteľnosť za aktívne zneužívanú a vyzvala na rýchlu opravu. Bezpečnostná firma F6 opisuje prienik cez internetovo dostupné zariadenia aj prípravu na ďalší pohyb v napadnutej sieti.
sekcia: bezpecnost
tagy:
- Cisco
- CISA
- kybernetická bezpečnosť
- zraniteľnosti
publikovane: '2026-11-24T07:16:44+00:00'
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
- nazov: 'BleepingComputer: CISA flags critical Cisco RCE flaw as actively exploited in attacks'
  url: https://www.bleepingcomputer.com/news/security/cisa-flags-critical-cisco-expressway-rce-flaw-as-actively-exploited/
- nazov: 'The Register: Critical Cisco remote code execution bug under attack'
  url: https://www.theregister.com/security/2026/11/23/critical-cisco-remote-code-execution-bug-under-attack/5311722
---

Americká agentúra CISA upozornila, že útočníci aktívne zneužívajú kritickú chybu v zariadeniach Cisco Expressway. Zraniteľnosť CVE-2026-76466 umožňuje bez prihlásenia spúšťať príkazy na diaľku s najvyššími oprávneniami root. Týka sa zariadení Expressway-C a Expressway-E nakonfigurovaných v klastri, či už ide o virtuálne stroje alebo fyzické zariadenia.

Cisco vydalo opravu ešte v októbri, keď chybu zverejnilo. Ako uviedli BleepingComputer a The Register, výrobca vtedy nepoznal prípady jej zneužitia. Cisco však podľa The Register ani po upozornení CISA nemá priame dôkazy o aktívnych útokoch. Bezpečnostná firma F6 naopak opisuje konkrétny incident, pri ktorom útočníci chybu využili.

## Chyba v overovaní zariadení v klastri

Problém súvisí s pevne zakódovanými prihlasovacími údajmi a nedostatočným overovaním klientskych certifikátov v klastrovej konfigurácii. Podľa upozornenia Cisco môže útočník, ktorý získa potrebné cookies, pristupovať k databázovej službe a vyvolať konkrétne príkazy RPC. Úspešné zneužitie mu umožní vykonávať príkazy v operačnom systéme napadnutého zariadenia ako root.

Expressway slúži ako brána pre firemnú hlasovú a videokomunikáciu. Prepája interné systémy s externými sieťami a používateľmi pracujúcimi na diaľku. Kompromitovanie zariadenia tak môže útočníkovi poskytnúť vstupný bod do ďalších častí podnikovej infraštruktúry.

## F6 opisuje pohyb do internej siete

F6 uviedla, že útočníci najprv napadli dve zariadenia Cisco Expressway dostupné z internetu. Cez jedno z nich sa podľa firmy dostali k ďalším dvom uzlom klastra v internej sieti organizácie. Po získaní prístupu root pripravovali nástroje na ďalší pohyb po sieti.

Išlo o vlastné skripty v jazyku Python, ktoré mali vyhľadávať dostupné zdieľané súbory cez SMB, komunikovať so SQL Serverom a WinRM a prehľadávať úložiská GitLab. Cieľom malo byť nájdenie prihlasovacích údajov a ďalších citlivých informácií. F6 podľa analýzy skriptov usudzuje, že operátor používal AI asistenta. The Register zároveň uvádza, že krátko pred zaznamenaným útokom sa objavil verejný proof-of-concept, teda ukážkový kód na zneužitie chyby.

F6 zverejnila aj možný indikátor kompromitácie: záznam „wombat@127.0.0.1“ v systémovom logu Erlang na zariadeniach Expressway. CISA podrobnosti o útokoch nezverejnila.

## Výzva na opravu, no nejednotné termíny

CISA zaradila chybu do katalógu Known Exploited Vulnerabilities a nariadila federálnym úradom v USA, aby systémy zabezpečili v krátkom termíne. BleepingComputer uvádza lehotu troch dní podľa smernice BOD 26-04; The Register píše, že úrady mali opraviť systémy do pondelka. Agentúra vyzvala aj súkromné organizácie a ďalších správcov sietí, aby opravu uprednostnili.
