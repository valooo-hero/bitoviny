---
title: Útočníci zneužili chybu v cloude GL.iNet na napadnutie routerov a zariadení KVM
perex: Výrobca opravil cestu, ktorou útočníci prenikali do zariadení cez službu GoodCloud, no už nainštalovaný malvér tým neodstránil. Rozsah napadnutia zatiaľ nevyčíslil.
sekcia: bezpecnost
tagy:
- GL.iNet
- GoodCloud
- routery
- malvér
- kybernetická bezpečnosť
publikovane: '2026-11-23T04:03:50+00:00'
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
- nazov: 'BleepingComputer: Hackers exploit GL.iNet cloud flaw to infect routers, KVM devices'
  url: https://www.bleepingcomputer.com/news/security/hackers-exploit-glinet-cloud-flaw-to-infect-routers-kvm-devices/
---

Spoločnosť GL.iNet potvrdila, že útočníci zneužili chybu v jej cloudových službách na vzdialenú správu a do niektorých routerov a zariadení KVM nainštalovali malvér. Firma tvrdí, že napadnutú cestu zablokovala a chybu opravila. Oprava však neodstráni škodlivý softvér zo zariadení, ktoré už boli napadnuté.

Zariadenia KVM umožňujú vzdialený prístup k počítačom a ich ovládanie. Služba GoodCloud slúži na ich správu aj na správu podporovaných routerov. Ako uvádza BleepingComputer, GL.iNet zatiaľ nezverejnil, ako presne útočníci chybu využili, koľko zákazníkov zasiahli ani či z napadnutých zariadení odcudzili údaje. Firma skúma aj možnosť, že útočníci prenikli do počítačov pripojených k zariadeniam KVM.

## Na zariadeniach našli zadné vrátka aj vzdialené príkazy

Zákazníci a bezpečnostní výskumníci po zverejnení incidentu hlásili malvér vytvorený pre zariadenia GL.iNet aj reverzné shelly s oprávneniami root. Tie umožňovali vzdialené vykonávanie príkazov a pripájali napadnuté routery na adresu 170.39.226[.]219.

Výskumníci z RemoteToHome Consulting analyzovali 183 routerov, ktoré vlastnia alebo spravujú. Podozrivú aktivitu zaznamenali na 152 z nich: 24 malo reverzné shelly s oprávneniami root, 47 staršie pretrvávajúce zadné vrátka a na 81 zariadeniach našli známky vykonania príkazov dodaných útočníkom. Výskumníci upozornili, že ich vzorka nemusí zodpovedať situácii u ostatných zákazníkov a staršie zadné vrátka nemusia súvisieť s novembrovým útokom.

Tím zároveň opísal možnú chybu v klientovi GoodCloud: handler pre funkcie AstroWarp a SD-WAN podľa neho odovzdával hodnoty z cloudu do shellových príkazov spúšťaných s oprávneniami root bez dostatočnej kontroly. GL.iNet však nepotvrdil, že práve táto chyba bola pri útoku zneužitá.

## Malvér sa snažil zostať skrytý

Majiteľ napadnutého zariadenia GL-RM1 KVM zverejnil záznamy, podľa ktorých zariadenie 19. novembra stiahlo škodlivý skript ni.sh a ďalšie súbory z adresy 66.245.219[.]252. Následne komunikovalo približne s 1 800 rezidenčnými IP adresami denne a opakovane kontaktovalo rozhranie blockchainu TRON. Účel tejto komunikácie nie je známy; nie je potvrdené, že zariadenia slúžili ako rezidenčné proxy alebo súčasť botnetu.

Analýza skriptu ni.sh podľa BleepingComputer ukázala, že rozpoznáva viacero modelov GL.iNet, sťahuje programy gl-helper a gb a nastavuje ich automatické spúšťanie. Dokázal sa tiež maskovať ako proces `crond -i /tmp/.log`, ktorý GL.iNet uviedol ako jeden z indikátorov napadnutia. Skript upravoval nástroj netstat tak, aby filtroval spojenia na jednu z útočníckych adries, a mohol inštalovať SSH kľúče na vzdialený prístup.

## Aktualizácia nemusí stačiť

GL.iNet zákazníkom odporúča skontrolovať zariadenia a nainštalovať najnovší bezpečnostný firmvér. Pre modely KVM RM10, RM1, RM1V2, RM1PE a RM4PE uviedol verziu 1.10.3 alebo novšiu; pre RM10RC verziu 1.10.3 beta alebo novšiu a pre RMQ1 verziu 1.8.7 alebo novšiu. Majitelia routerov majú použiť najnovší bezpečnostný firmvér určený pre konkrétny model.

Firma vo svojich pokynoch odkazuje aj na komunitný nástroj na kontrolu a čistenie. Ten hľadá známe škodlivé súbory, podozrivé procesy a zmeny v konfigurácii, ale jeho autori upozorňujú, že nezachytí každú infekciu. V niektorých prípadoch môže byť potrebné firmvér preinštalovať bez obnovenia pôvodných nastavení, pretože škodlivé súbory môžu v konfigurácii prežiť bežnú aktualizáciu. Pred resetovaním sa odporúča zachovať dôkazy, neobnovovať potenciálne napadnutú konfiguráciu a zmeniť heslá aj prístupové kľúče. Pri KVM treba preveriť aj pripojené počítače.
