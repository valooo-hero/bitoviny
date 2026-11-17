---
title: Júlová chyba ochromila viac než 80 percent serverov Microsoft 365
perex: Microsoft pripísal novembrový výpadok kombinácii chyby v sieťovom softvéri, presmerovanej prevádzky a zníženej kapacity. Problém podľa firmy zasiahol služby na celom svete a vyšetrovanie pokračuje.
sekcia: softver
tagy:
- Microsoft 365
- Microsoft
- výpadok
- cloudové služby
publikovane: '2026-11-17T05:36:36+00:00'
obrazok:
  src: /obrazky/zastupny.svg
  alt: Zástupný obrázok, čaká na výber editora
  popisok: Obrázok čaká na výber editora.
  kredit: Bitoviny
  licencia: vlastná ilustrácia
redaktori:
  autor: klara
  factcheck: tomas
  korektura: ciarka
zdroje:
- nazov: 'BleepingComputer: Microsoft says months-old bug caused global Microsoft 365 outage'
  url: https://www.bleepingcomputer.com/news/microsoft/microsoft-says-months-old-bug-caused-global-microsoft-365-outage/
- nazov: '9to5Mac: Microsoft outage saw 80% of servers fail – here’s what happened'
  url: https://9to5mac.com/2026/11/16/microsoft-outage-saw-80-of-servers-fail-heres-what-happened/
---

Microsoft tvrdí, že za novembrovým celosvetovým výpadkom Microsoft 365 stála chyba v aktualizácii sieťových brán, ktorú firma zaviedla už v júli. Pri najhoršom priebehu prestalo reagovať viac než 80 percent týchto serverov. Výpadok zasiahol napríklad Outlook, Exchange Online, Teams a Copilot a trval takmer 24 hodín.

Podľa predbežnej správy v Microsoft 365 Admin Center sa spojili tri okolnosti: skrytá chyba v softvéri, nárast prevádzky po presmerovaní Teams na inú sieťovú infraštruktúru a dočasne znížená kapacita serverov. Ako uvádza BleepingComputer, Microsoft stále pripravuje záverečnú správu o incidente.

## Chyba zostala skrytá celé mesiace

Aktualizácia určená pre sieťové brány Microsoft 365 sa začala nasadzovať v júli. Podľa Microsoftu sa počas rozšírenia na celú infraštruktúru ani v nasledujúcich mesiacoch neprejavili problémy. Chyba sa však mohla aktivovať pri určitých podmienkach záťaže a spôsobiť, že servery prestali odpovedať.

Testy ju neodhalili, pretože laboratórne prostredie používalo iný typ prevádzky a menej výkonné servery s menším počtom jadier než produkčná infraštruktúra. Microsoft v správe vysvetlil, že problém sa zhoršuje na novšom a výkonnejšom hardvéri. Portál 9to5Mac opisuje príčinu ako súťaž o prístup k internému procesu, ktorá mohla server zablokovať.

## Prevádzka spustila kaskádový výpadok

Približne 15 hodín pred začiatkom incidentu sa Teams automaticky presunul na sieťovú infraštruktúru, ktorú využíva Exchange Online. Tým sa zvýšila záťaž na príslušné brány. Zároveň bolo pre nesúvisiaci problém mimo prevádzky takmer 14 percent ich kapacity. Microsoft uviedol, že samotné zníženie kapacity by infraštruktúra zvládla, no v kombinácii s vyššou prevádzkou sa prejavila softvérová chyba.

Keď prvé servery prestali reagovať, systém presmeroval používateľov na ďalšie dostupné servery. Tie však dostali dodatočnú záťaž a zlyhávali tiež. Do dvoch hodín sa problém rozšíril naprieč serverovou flotilou; v najhoršom bode bolo nefunkčných viac než 80 percent serverov. Ochranné mechanizmy, ktoré mali brániť šíreniu problémov medzi regiónmi, podľa Microsoftu kaskádu nezastavili.

## Obnova trvala do nasledujúceho dňa

Incident sa začal 12. novembra o 11:20 východného času a Microsoft potvrdil obnovenie služieb 13. novembra o 11:10. Teams, OneDrive a SharePoint mohli prejsť na alternatívnu infraštruktúru a obnovili sa skôr. Exchange Online takú možnosť nemal, takže používatelia sa nevedeli dostať k pošte. Obnovu komplikovalo aj to, že reštartované servery opäť zahltila nahromadená prevádzka.

Microsoft po identifikovaní chyby pripravil opravu a nasadil ju na zasiahnuté servery. Firma následne zvýšila kapacitu, vylepšila monitorovanie a pridala ochrany proti podobnému presmerovaniu prevádzky. Charles Lamanna, výkonný viceprezident Microsoftu pre Copilot, Agents a Platform, sa zákazníkom ospravedlnil za vplyv výpadku na ich bežnú prevádzku.

BleepingComputer uvádza, že Microsoft vyšetrovanie ešte neuzavrel. 9to5Mac zhrňuje príčinu najmä ako súhru zlyhania jednej brány a chyby v aktualizácii, zatiaľ čo predbežná správa citovaná BleepingComputer osobitne uvádza aj zníženú kapacitu serverov.
