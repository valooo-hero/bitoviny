---
title: AMD obhajuje natívny FP64 v akcelerátore Instinct MI430X
perex: Na konferencii SC26 firma spochybnila, či emulácia dvojitej presnosti dokáže nahradiť špecializovaný hardvér vo vedeckých výpočtoch. Nvidia zároveň predstavila nový variant Rubin určený pre HPC.
sekcia: hardver
tagy:
- AMD
- Instinct MI430X
- Nvidia
- HPC
- FP64
publikovane: '2026-11-18T05:01:11+00:00'
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
- nazov: 'Tom''s Hardware: AMD attacks Nvidia''s FP64 emulation at SC26, touts native double-precision on Instinct MI430X'
  url: https://www.tomshardware.com/pc-components/gpus/amd-attacks-nvidias-fp64-emulation-at-sc26-touts-native-double-precision-on-instinct-mi430x-says-ozaki-schemes-fit-less-than-10-percent-of-hpc-workloads-and-triple-memory-use-and-emulated-fp64-is-a-poor-fit-for-many-hpc-workloads
- nazov: 'The Register: GPU giants throw HPC users some tasty crumbs'
  url: https://www.theregister.com/hpc/2026/11/17/gpu-giants-throw-hpc-users-some-tasty-crumbs/5310611
---

AMD na konferencii Supercomputing 2026 (SC26) obhajuje natívne výpočty s dvojitou presnosťou FP64 v akcelerátore Instinct MI430X. Firma tvrdí, že emulácia FP64, ktorú využíva Nvidia pri niektorých maticových úlohách, sa nehodí na veľkú časť výpočtov používaných vo vede a technike.

FP64 je dôležitý napríklad pri simuláciách, modelovaní a vedeckých výpočtoch. Podľa portálu Tom’s Hardware AMD pri profilovaní aplikácií zistilo, že husté násobenie matíc, teda typ úlohy, pre, ktorý je emulácia Ozakiho schémou vhodná, tvorí menej než 10 percent HPC pracovných záťaží. Ide o tvrdenie výrobcu, nie o nezávislé meranie.

## Kde emulácia naráža na limity

Ozakiho schéma rozkladá výpočty FP64 na sériu operácií s nižšou presnosťou. Nvidia ju využíva na maticové výpočty, ktoré možno efektívne spracovať na tensorových jadrách. AMD namieta, že najlepšie výsledky takýto prístup dosahuje pri dostatočne veľkých maticiach a vhodne zvolených vstupných hodnotách. Ak úloha tieto podmienky nespĺňa, výkon môže klesnúť.

Podľa AMD mnohé HPC aplikácie namiesto hustých matíc využívajú napríklad riedku lineárnu algebru, hydrodynamické simulácie, konečné prvky vyššieho rádu, Monte Carlo výpočty, transport častíc či klasickú molekulárnu dynamiku. Pri nich firma považuje za dôležitý vysoký výkon vektorových výpočtov FP64.

Ďalšou výhradou je pamäť. AMD tvrdí, že emulácia môže v niektorých prípadoch zvýšiť jej spotrebu až trojnásobne oproti natívnemu FP64. Keďže kapacita pamäte ovplyvňuje, koľko akcelerátorov a výpočtových uzlov treba na úlohu nasadiť, môže to podľa firmy zvýšiť nároky na sieťové prepojenie, napájanie aj chladenie.

## MI430X cieli na vedecké výpočty

Podľa The Register má MI430X 432 GB pamäte HBM4, priepustnosť 23 TB/s a špičkový výkon 288 TFLOPS pri FP64. AMD tak stavia na odlišnom prístupe než pri akcelerátoroch, ktoré uprednostňujú výpočty pre umelú inteligenciu. Tom’s Hardware uvádza, že štyri MI430X spolu ponúkajú 1,72 TB pamäte HBM4 a priepustnosť 93,2 TB/s.

AMD spomína aj využitie akcelerátora na inferenciu AI modelov popri vedeckých výpočtoch. MI430X má podľa firmy teoretický výkon 9,2 PFLOPS pri FP4. Pre porovnanie, AI akcelerátor MI455X dosahuje podľa rovnakého zdroja 40,3 PFLOPS. Štyri MI430X sú pritom prepojené do menšej skupiny než 72 akcelerátorov MI455X v rackovom systéme Helios.

## Nvidia predstavila variant Rubin HPC

Debata sa odohráva v čase, keď Nvidia predstavila aj Rubin HPC, variant GPU určený pre simulácie, inžinierske úlohy a vedecké výpočty. The Register uvádza, že má ponúknuť viac než 50-tisíc jadier CUDA a doraziť v roku 2028. Nvidia podľa portálu hovorí o výkone až 200 TFLOPS pri emulovaných maticových výpočtoch FP64. Podrobnosti o maximálnom výkone a pamäti zatiaľ nezverejnila.

Nvidia zároveň podľa The Register tvrdí, že zákazníci pri Rubin HPC nebudú odkázaní iba na emuláciu a čip ponúkne aj natívny maticový výkon FP64. To čiastočne odlišuje jej vyjadrenie od kritiky AMD, ktorá sa sústreďuje na obmedzenia emulácie a potrebu natívneho výkonu v rôznych typoch úloh.

MI430X si AMD spája s pripravovanými systémami Discovery v americkom Oak Ridge National Laboratory, Alice Recoque vo Francúzsku, LUMI-AI vo Fínsku a Herder v Nemecku. Ide o projekty v Európe aj v USA; dostupnosť akcelerátora pre bežných zákazníkov zdroje neuvádzajú.
