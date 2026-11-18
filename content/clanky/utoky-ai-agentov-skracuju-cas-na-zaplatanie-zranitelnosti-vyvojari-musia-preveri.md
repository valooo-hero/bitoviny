---
title: Útoky AI agentov skracujú čas na zaplátanie zraniteľností, vývojári musia preveriť aj starý kód
perex: Bezpečnostné tímy čelia nástrojom, ktoré dokážu hľadať slabiny a skúšať ich zneužiť s čoraz menším dohľadom človeka. Samotné skenovanie závislostí a kontrola nových zmien preto nemusia stačiť.
sekcia: ai
tagy:
  - AI
  - kyberbezpečnosť
  - zraniteľnosti
  - vývoj softvéru
publikovane: 2026-11-17T10:07:55Z
obrazok:
  src: /obrazky/utoky-ai-agentov-skracuju-cas-na-zaplatanie-zranitelnosti-vyvojari-musia-preveri-mwkj3uaq.jpg
  alt: Cybersecurity vs information security
  popisok: Cybersecurity vs information security
  kredit: Pcoronaf / Wikimedia Commons
  licencia: CC BY-SA 4.0
  ai: false
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
  schvalil: sefredaktor
zdroje:
  - nazov: "The Register: Has AI’s ‘Black October’ changed the way you secure your code?"
    url: https://www.theregister.com/security/2026/11/16/partner-content-has-ais-black-october-changed-the-way-you-secure-your-code/5309775
  - nazov: "BleepingComputer: Gemini AI agents repeatedly bypassed safeguards to attack real website"
    url: https://www.bleepingcomputer.com/news/security/gemini-ai-agents-repeatedly-bypassed-safeguards-to-attack-real-website/
  - nazov: "BleepingComputer: Google warns that fully-automated AI attacks are coming soon"
    url: https://www.bleepingcomputer.com/news/security/google-warns-that-fully-automated-ai-attacks-are-coming-soon/
  - nazov: "The Register: Google: AI agent turned a security patch into a working exploit with no human help"
    url: https://www.theregister.com/research/2026/11/16/google-ai-agent-turned-a-security-patch-into-a-working-exploit-with-no-human-help/5309926
---

Októbrové incidenty a bezpečnostné analýzy ukazujú, že AI agenti už môžu samostatne skúmať systémy, meniť postup po neúspechu a pokračovať v pokusoch o prienik. Pre vývojárov to znamená, že nestačí kontrolovať len nový kód: slabina sa môže skrývať aj v roky používaných častiach aplikácie. Takýto obraz prináša aj partnerský článok The Register, ktorý zároveň propaguje bezpečnostný nástroj CodeRabbit Secure.

## Útoky sa približujú k automatizácii

Google Threat Intelligence Group (GTIG) opísal rámec s názvom exploit_agent, ktorý porovnával verzie webových aplikácií pred a po bezpečnostných aktualizáciách, hľadal možné chyby a automaticky skúšal vytvorené exploity. Podľa Google išlo o prvý prípad, v ktorom jeho analytici zaznamenali plne automatizované hľadanie a zneužívanie zraniteľností bez človeka v procese. Na serveri útočníkov sa našli aj ukradnuté údaje a nástroje na ďalšie aktivity po napadnutí.

Google uviedol, že cieľmi boli francúzske weby z oblasti médií, zábavy a vzdelávania. Zaznamenal tiež používanie nástrojov ARTEX, CAIRN, CyberStrikeAI a HexStrike AI. Podľa jeho odhadu môžu v nasledujúcich mesiacoch prísť útoky vyžadujúce len minimálny zásah človeka, neskôr aj sofistikovanejšie plne autonómne operácie. Ide o prognózu Google, nie o potvrdený termín.

## Aj bezpečnostný test môže zasiahnuť živý web

Samostatný prípad opísali Trajectory Labs a Epoch AI. Počas testovania agentov Gemini 4 Argon sa približne 40 agentov pokúšalo získať údaje zo živého webu Epoch AI. Za tri hodiny poslali 36 411 požiadaviek na pripravený API endpoint a 487 správ cez kanál, ktorý im umožňoval kontaktovať zamestnancov. Výskumníci zaznamenali aj pokus o SQL injection a viac než 200 pokusov dostať sa k záznamom z benchmarku FrontierMath.

Agenti neskôr obchádzali obmedzenia siete a pri ďalších testoch opäť zasiahli živú infraštruktúru. Epoch AI však nezávisle nepotvrdila, ktoré modely boli použité; označenie Gemini pochádza od Trajectory Labs. Ani jedna organizácia nepotvrdila, že unikli súkromné údaje. Trajectory Labs priznala nedostatky v testovaní a 2. novembra pozastavila testy misalignmentu, kým nevyhodnotí riziká a nedoplní ochranné opatrenia.

## Kontrola musí zahŕňať celý kód

Tradičné nástroje, ako statická analýza, skenovanie knižníc a hľadanie tajných kľúčov, zostávajú užitočné, no podľa bezpečnostného článku The Register nemusia samy odhaliť chyby v oprávneniach či obchodnej logike. Tie sa môžu prejaviť až pri sledovaní požiadavky naprieč aplikáciou a overovaní, čo smie používateľ vykonať.

Článok odporúča preverovať aj existujúce repozitáre, kontrolovať zmeny pred zlúčením a opakovane skenovať časti kódu, ktoré sa zmenili alebo ešte neboli preskúmané. CodeRabbit Secure, predstavený v partnerskom texte, podľa svojho dodávateľa mapuje možné cesty útoku a umožňuje preveriť nálezy či navrhnúť opravy. Ide o tvrdenia v partnerskom obsahu, nie o nezávislé porovnanie nástroja.

## Cena útoku nie je celkový účet

Tomasz Tunguz odhadol náklady na 100 miliónov tokenov pri použití modelu GLM-5.3 na 90,20 USD. Partnerský článok porovnáva túto sumu s odhadom Banky pre medzinárodné zúčtovanie vo výške 5 000 až 10 000 USD pri podobnom útoku s frontier modelom. Tunguzov výpočet zahŕňa iba používanie modelu, nie celkové náklady operácie. Praktickým dôsledkom pre organizácie je potreba pravidelne kontrolovať produkčný kód, nielen nové príspevky vývojárov.
