---
title: Populárny správca hesiel 1Password čelil kybernetickému útoku
perex: Neznámy útočník prenikol do interných systémov spoločnosti 1Password cez napadnutý firemný účet na Gitufe. Zlodeji získali zdrojový kód a údaje o časti používateľov, avšak samotné trezory s heslami údajne zostali v bezpečí.
sekcia: bezpecnost
tagy:
- 1Password
- GitHub
- kyberneticka-bezpecnost
- unik-dat
publikovane: '2026-11-27T05:18:19+00:00'
obrazok:
  src: /obrazky/popularny-spravca-hesiel-1password-celil-kybernetickemu-utoku.webp
  alt: 'Ilustrácia k článku: Populárny správca hesiel 1Password čelil kybernetickému útoku'
  popisok: Ilustračný obrázok.
  kredit: Bitoviny / FLUX.1-schnell
  licencia: vygenerované AI
  ai: true
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
zdroje:
- nazov: 'The Register: Hackers help themselves to 1Password''s source code and customer data'
  url: https://www.theregister.com/security/2026/11/26/hackers-help-themselves-to-1passwords-source-code-and-customer-data/5312317
- nazov: '9to5Mac: 1Password confirms security incident, here’s what you need to know'
  url: https://9to5mac.com/2026/11/25/1password-confirms-security-incident-heres-what-you-need-to-know/
- nazov: 'Engadget: 1Password says it was hacked but users'' vaults are safe'
  url: https://www.engadget.com/2329013/1password-hacked-but-users-vaults-are-safe/
---

Kanadská spoločnosť zaoberajúca sa digitálnou bezpečnosťou a správou prihlasovacích údajov tento týždeň oficiálne potvrdila bezpečnostný incident. Vyšetrovanie útokov spustila ešte 19. novembra po tom, čo odhalila podozrivú aktivitu na firemnom účte jedného zo svojich zamestnancov na platforme GitHub. Ako uviedol portál The Register, útočníkovi sa podarilo získať prístup k súkromnému zdrojovému kódu a nasadiť škodlivý kód do backendových služieb platformy.

## Údaje zákazníkov a zabezpečenie trezorov

Podľa informácií, ktoré zverejnili weby 9to5Mac a Engadget, útočník skopíroval obmedzené množstvo informácií od bližšie nešpecifikovanej časti používateľov. Medzi kompromitované dáta patria mená a e-mailové adresy používané na prihlásenie, identifikátory účtov, časové značky vytvorenia konta a posledného prístupu, verejné kľúče, protokoly Secure Remote Password a rôzne necitlivé metadáta. Útočník sa dostal aj k tokenom v e-mailových správach pre pozvánky či obnovenie kont.

Firma však rázne odmieta, že by boli ohrozené samotné citlivé dáta používateľov. „V žiadnom momente neboli obsahy zákazníckych trezorov prístupné útočníkovi alebo pre neho dostupné,“ uviedla spoločnosť 1Password. Keďže platforma neukladá hlavné heslá, tajné kľúče ani kľúče na obnovenie kont, tieto položky zostali nedotknuté. Aplikácie a rozšírenia pre internetové prehliadače taktiež podľa vyjadrení firmy neboli ovplyvnené.

## Ohrozená infraštruktúra a prijaté opatrenia

Omnoho vážnejším problémom bol fakt, že narušiteľ prenikol aj do infraštruktúry pre nepretržitú integráciu a doručovanie softvéru známej ako CI/CD, ktorá slúži na vývoj a testovanie produktov. V tejto súvislosti 1Password potvrdil, že preventívne obmenil alebo zrušil všetky interné prihlasovacie údaje a tajné kľúče, ktoré sa v systéme nachádzali a mohli byť potenciálne vystavené riziku.

Spoločnosť útočníka z prostredia Gitubu vyblokovala, obnovila postihnuté backendové služby na čisté verzie kódu a najala externých bezpečnostných špecialistov na audit vývojovej infraštruktúry. Okrem toho firma sprísnila overovacie kódy v e-mailoch na obnovenie kont a pozvánky, kde pôvodné šesťmiestne číselné kódy nahradila desaťmiestnymi alfanumerickými reťazcami s cieľom sťažiť prípadné útoky hrubou silou.

## Riziko phishingu a ďalší vývoj

Napriek tomu, že dáta v trezoroch sú bezpečné, odborníci varujú pred zvýšeným rizikom podvodov. Získaný zoznam e-mailových adries a uniknuté tokeny môžu útočníci využiť na presvedčivejšie phishingové útoky, najmä v podobe falošných správ o obnove účtu či pozvánok do služieb. Spoločnosť preto odporúča všetkým používateľom zvýšiť pozornosť a sledovať možné pokusy o podvod.

Táto udalosť pripomína prvú fázu bezpečnostného incidentu spoločnosti LastPass z roku 2022, kde útok na vývojové prostredie taktiež viedol ku krádeži zdrojového kódu a neskoršiemu ohrozeniu záloh trezorov. Britský úrad pre ochranu údajov neskôr LastPass udelil pokutu vo výške 1,2 milióna libier za nedodržanie vysokých štandardov bezpečnosti. V prípade platformy 1Password zatiaľ nie je nutné meniť hlavné heslá ani tajné kľúče, keďže ich spoločnosť vôbec neuchováva.
