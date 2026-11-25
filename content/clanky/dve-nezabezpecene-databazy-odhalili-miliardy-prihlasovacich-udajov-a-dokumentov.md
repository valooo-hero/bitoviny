---
title: Dve nezabezpečené databázy odhalili miliardy prihlasovacích údajov a dokumentov
perex: Dva nezabezpečené databázové servery odhalili viac než 3,6 miliardy záznamov. Podľa výskumníkov ide o zmes zloženú z viacerých zdrojov vrátane dát ukradnutých infostealer softvérom.
sekcia: bezpecnost
tagy:
- UpGuard
- Black Hills Information Security
- databázy
- infostealer malware
- multi-factor authentication
publikovane: '2026-11-25T06:51:35+00:00'
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
- nazov: 'Wired: Database Leaks Expose 3.5 Billion Usernames, Passwords, and Documents'
  url: https://www.wired.com/story/3-billion-usernames-passwords-and-documents-leaked-online/
- nazov: 'Engadget: Researchers find 3.6 billion usernames, passwords and documents in unsecured databases'
  url: https://www.engadget.com/2326647/researchers-find-3-6-billion-usernames-passwords-and-documents-in-unsecured-database/
- nazov: '9to5Mac: Two billion credentials publicly exposed, including everything needed for identity theft'
  url: https://9to5mac.com/2026/11/24/two-billion-credentials-publicly-exposed-including-everything-needed-for-identity-theft/
---

## Dva nezabezpečené servery

Bez ochrany heslom aj bez šifrovania sa na verejnom internete ocitli dve databázy, ktoré obsahovali viac než 3,6 miliardy záznamov. Ako prvý o tom informoval portál Wired, ktorý spresnil, že ide o súčet 3,5 miliardy záznamov. V prípade oboch ide o údaje ľudí z desiatok krajín.

Databázy našli nepozorovane dvaja rôzni výskumníci približne v rovnakom čase. Podľa Wired spolu nijako nesúvisia.

## Dve miliardy prihlasovacích údajov

Väčšia z nich obsahovala približne dve miliardy prihlasovacích údajov. Našiel ju Jeremiah Fowler zo spoločnosti Black Hills Information Security.

Opisuje ju ako najrozsiahlejšie odhalenie prihlasovacích údajov, aké doteraz v otvorenej databáze našiel. Sú v nej e-mailové adresy, používateľské mená, heslá, cookies, session tokeny a informácie o zariadeniach.

Databáza mala 8 471 priečinkov s heslami a údajmi o účtoch v nešifrovanej podobe. Niektoré boli pomenované podľa krajín, vrátane USA, Spojeného kráľovstva, Francúzska a Nemecka.

Fowler v nej našiel stovky miliónov bežných e-mailových účtov, desiatky miliónov adries .gov, .edu a .org, viac než 100 miliónov účtov sociálnych sietí a desiatky miliónov účtov e-shopov. Engadget uvádza odhad 114 miliónov účtov prepojených so službami Google, 88 miliónov účtov Facebook, takmer 33 miliónov X, takmer 42 miliónov Roblox a 36,6 milióna Amazon, s tým, že medzi službami môže byť prekrývanie.

Fowler hovorí, že nič nenasvedčuje tomu, že by na zozbieranie údajov bolo treba prelomiť konkrétne firmy či inštitúcie. Súčasťou boli aj tisíce Tor.onion adries spojených s účtami. Sám upozorňuje, že.onion služby prevádzkujú aj legitímne organizácie, novinári či whistleblower platformy.

## Profily jednotlivých obetí

Najzávažnejšou časťou databázy bolo podľa Fowlera približne 400 000 dokumentov, ktoré pochádzali z pokročilejšieho škodlivého softvéru. Ten vytváral samostatné priečinky pre jednotlivé obete.

Obsahovali priečinky pomenované applications, cookies, edge, important files a operating systems, ako aj textové dokumenty označené system, process, clipboard, brute force či passwords.

Podľa Fowlera to dáva detailný profil obete, jej zariadení a účtov a odkrýva širšie možnosti útoku než samotné meno a heslo. „Ak to máte, vlastníte toho človeka,“ povedal pre Wired.

## Čínsky zväzok s číslami občianskych preukazov

Druhá databáza, ktorú našiel Greg Pollock, riaditeľ výskumu vo firme UpGuard, obsahovala 1,64 miliardy dokumentov. Väčšina sa týkala ľudí a firiem v Číne.

Pollock v nej našiel najmenej 840 miliónov rôznych čísel občianskych preukazov, 300 miliónov telefónnych čísel, približne 11 miliónov záznamov o zápisoch študentov a takmer 8 miliónov firemných registrácií. Engadget uvádza 7,8 milióna registrácií a dodáva, že mnohé študentské záznamy sa týkali maloletých. Pollock hovorí aj o prípadoch detí a zosnulých.

Podľa Pollocka dáta pochádzali z viacerých zdrojov pod rôznou správou: registrácií občianskych preukazov, dát platobných aplikácií, školského systému a firemných registrov. „Žiadny zákonný držiteľ by nemohol mať všetko,“ napísal na blogu.

Databáza ležala otvorená na zjavnej šedej či kriminálnej infraštruktúre. Pollock nenašiel vlastníka a počas jeho kontroly prestala byť dostupná, zrejme po ransomvérovom útoku. Aktualizovaná bola ešte týždeň pred objavením.

## Čo s tým

Obaja výskumníci upozorňujú, že rokmi overenou ochranou sú správcovia hesiel a viacfaktorové overenie. Podľa Engadgetu sú užitočné aj passkeys, VPN a opatrnosť pri zdieľaní údajov. Podľa 9to5Mac je pri 2FA lepšia autentifikačná aplikácia než SMS, a to kvôli SIM-swap útokom.
