---
title: Chyba v Azure API Management umožnila krádež zákazníckych prístupových údajov
perex: Microsoft opravil zraniteľnosť v starších úrovniach služby, no samotná oprava nezneplatnila tajomstvá, ku ktorým mohli útočníci získať prístup. Nórske úrady incident spájajú s útokmi na energetické firmy.
sekcia: bezpecnost
tagy:
- Microsoft Azure
- Azure API Management
- kybernetická bezpečnosť
- cloud
publikovane: '2026-11-24T07:16:54+00:00'
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
- nazov: 'BleepingComputer: Microsoft Azure flaw exploited to steal customers'' API credentials'
  url: https://www.bleepingcomputer.com/news/security/microsoft-azure-flaw-exploited-to-steal-customers-api-credentials/
- nazov: 'The Register: Norway links energy firm cyberattacks to critical Azure API Management flaw'
  url: https://www.theregister.com/security/2026/11/23/norway-links-energy-firm-cyberattacks-to-critical-azure-api-management-flaw/5311598
---

Microsoft upozornil zákazníkov na zraniteľnosť v službe Azure API Management (APIM), ktorú útočníci mohli využiť na prístup k uloženým tajomstvám a vykonávanie administrátorských operácií. Podľa spoločnosti boli ohrozené iba inštancie APIM Classic. Microsoft problém identifikoval 18. novembra 2026 a nasledujúci deň nasadil opravu.

Zraniteľnosť sa týkala úrovní Developer, Basic, Standard a Premium. Úroveň Consumption v APIM Classic ani novšie úrovne APIM v2 zasiahnuté neboli. Microsoft uviedol, že k problému dochádzalo pri inštanciách, ktoré neboli nastavené podľa odporúčaných bezpečnostných postupov.

## Aké údaje mohli byť ohrozené

Ako píše BleepingComputer, medzi potenciálne dostupné údaje patrili tajomstvá uložené v položkách Named Values, prihlasovacie tajomstvá poskytovateľov identity a OpenID Connect, predplatiteľské kľúče aj tokeny na volanie priamych rozhraní na správu služby.

Tieto údaje môžu podľa svojich oprávnení otvárať prístup aj k ďalším aplikáciám, službám či systémom napojeným na APIM. Bezpečnostný expert Anders Kristiansen upozornil, že získané prihlasovacie údaje môžu v niektorých prípadoch fungovať priamo voči chránenej službe, teda aj mimo APIM. Rozsah prístupu závisí od oprávnení a od toho, či sú údaje stále platné.

The Register uvádza, že riziko sa mohlo týkať aj organizácií, ktoré zabudli na staršie testovacie alebo vývojové inštancie. Zdroje však neuvádzajú, koľko zákazníkov bolo skutočne napadnutých.

## Nórske energetické firmy medzi zasiahnutými

Nórsky Národný bezpečnostný úrad (NSM) uviedol, že nórsky energetický sektor zraniteľnosť odhalil ako prvý a že útoky zasiahli aj organizácie v ďalších krajinách a odvetviach. Menoval energetickú spoločnosť Equinor a spoločnosť Skagerak Energi zaoberajúcu sa vodnou energiou. Equinor oznámil kybernetický útok 17. novembra, no neskôr uviedol, že ho zastavil a nenašiel známky odcudzenia alebo zmeny dát. Skagerak Energi informovala o pokuse o útok, ktorý podľa firmy neovplyvnil prevádzku; dôkazy o úniku informácií nenašla.

NSM odporúča predpokladať, že tajomstvá a položky Named Values mohli byť sprístupnené, a vymeniť všetky príslušné tokeny a tajomstvá. Zákazníkom tiež radí zmapovať, ku ktorým systémom mali jednotlivé APIM inštancie prístup.

## Oprava neznamená výmenu zákazníckych hesiel

Microsoft tvrdí, že uzavrel cestu k neoprávnenému prístupu a opravu automaticky nasadil na inštancie hostované Microsoftom. Zároveň upozorňuje, že tým nezneplatnil zákaznícke údaje, ku ktorým sa útočníci mohli dostať pred opravou. Zákazníci majú preto vymeniť potenciálne odhalené údaje, preveriť podozrivú aktivitu v nadväzujúcich systémoch a skontrolovať dostupné záznamy.

Medzi odporúčaniami je rozdiel: Microsoft podľa BleepingComputer tvrdí, že jeho oprava bola plne nasadená a nevyžaduje zásah zákazníka. NSM však organizáciám radí overiť verziu prostredia a kontaktovať poskytovateľa, ak inštancia nedostala aktualizáciu. The Register tiež informuje o upozornení NSM na neopravené verzie. Zdroje neuvádzajú konkrétne hranice verzií.

Pre firmy na Slovensku či inde v EÚ ide o pripomienku, že tajomstvá uložené v cloudovej službe treba po bezpečnostnom incidente vymeniť aj po nasadení opravy; zdroje však neuvádzajú zasiahnutú slovenskú organizáciu.
