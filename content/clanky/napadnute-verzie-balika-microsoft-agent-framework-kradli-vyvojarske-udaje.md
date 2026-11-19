---
title: Napadnuté verzie balíka Microsoft Agent Framework kradli vývojárske údaje
perex: Z PyPI sa šírili verzie 1.26.1 a 1.26.2 s kódom, ktorý sa spúšťal pri štarte Pythonu aj bez importovania balíka. Útočníci cielili na cloudové a vývojárske prístupové údaje.
sekcia: bezpecnost
tagy:
- Microsoft
- PyPI
- Python
- krádež údajov
publikovane: '2026-11-19T04:39:22+00:00'
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
- nazov: 'BleepingComputer: Microsoft’s Agent Framework PyPI package compromised to steal credentials'
  url: https://www.bleepingcomputer.com/news/security/microsofts-agent-framework-pypi-package-compromised-to-steal-credentials/
- nazov: 'The Register: Microsoft''s official Python agent framework hijacked to distribute malware'
  url: https://www.theregister.com/security/2026/11/18/microsofts-official-python-agent-framework-hijacked-to-distribute-malware/5310858
---

Dve napadnuté verzie oficiálneho balíka Microsoft Agent Framework pre Python obsahovali škodlivý kód na krádež prihlasovacích údajov a ďalších tajomstiev z vývojárskych systémov. Verzie 1.26.1 a 1.26.2 sa objavili na PyPI 17. novembra 2026. Podľa portálov BleepingComputer a The Register má balík približne 200-tisíc stiahnutí mesačne.

Riziko sa týkalo aj prostredí, v ktorých vývojár balík priamo nepoužil. Škodlivý kód sa spustil pri štarte interpretera Python, ak bol balík nainštalovaný. Obe napadnuté vydania pritom zachovali závislosť od legitímnej verzie agent-framework-core 1.26.0, takže mohli pôsobiť funkčne a dôveryhodne.

## Kód sa spúšťal na pozadí

Podľa bezpečnostných firiem Socket a Step Security využila prvá napadnutá verzia súbor `agent_framework_meta.pth`, ktorý pri spustení Pythonu aktivoval kód v `agent_framework_meta/_telemetry.py`. Vydanie 1.26.2 presunulo škodlivú časť do súborov `af_runtime_diag.pth` a `af_runtime_diag.py`.

Malvér vyhľadával tajomstvá v premenných prostredia, konfiguračných súboroch a ďalších procesoch, ku ktorým mal prístup. Záujem mal o údaje pre služby Azure, AWS, GitHub, Docker, Hugging Face a OpenAI, ako aj ďalšie nástroje. Okrem už uložených údajov sa pokúšal vyžiadať nové tokeny spravovaných identít Azure a tokeny OIDC pre Azure DevOps. Druhá verzia pridala aj požiadavky na tokeny OIDC pre GitHub Actions a prehľadávanie adresárov GitHub runnerov.

Zozbierané informácie smerovali na rovnakú adresu služby webhook.site, ktorú mali obe vydania pevne zapísanú v kóde. The Register uvádza, že údaje boli odosielané v zakódovanom bloku JSON. Podľa výskumníkov OpenSourceMalware je kombinácia krádeže existujúcich údajov a aktívneho získavania tokenov obzvlášť nebezpečná v cloudových zostavovacích prostrediach, pretože aj krátkodobé tokeny môžu útočníci zneužiť, ak ich získajú rýchlo.

## Čo zatiaľ vieme o zásahu

BleepingComputer píše, že PyPI prvé škodlivé vydanie umiestnil do karantény, no približne o dve a pol minúty sa objavila verzia 1.26.2, ktorú platforma podľa článku zablokovala asi o osem minút neskôr. The Register opisuje prvú verziu ako vrátenú na bezpečný stav a uvádza, že útočník neskôr nahral ďalšiu cez oficiálny publikačný účet Microsoftu. Obe správy teda naznačujú pokračujúci prístup k publikovaniu, presný priebeh zásahu však opisujú odlišne.

Microsoft podľa The Register uviedol, že niektoré repozitáre sprístupnil iba súkromne, kým preveruje škodlivý obsah. Repozitár Agent Framework bol v čase publikovania článku nedostupný. Aj repozitár ONNX Runtime bol vtedy offline, no Microsoft ani bezpečnostní výskumníci ho s touto kampaňou nespájali. Príčina získania prístupu k vydávaniu balíka nebola známa.

Vývojárom, ktorí nainštalovali niektorú z napadnutých verzií, BleepingComputer odporúča izolovať dotknuté prostredie, nespúšťať v ňom Python ani pip, kým nebude zabezpečené, a obnoviť ho z dôveryhodného základu. Odporúča tiež okamžite zmeniť všetky potenciálne odhalené prístupové údaje a v odchádzajúcich sieťových záznamoch hľadať konkrétnu cestu webhooku. Ako bezpečnú alternatívu uvádza verziu 1.26.0.
