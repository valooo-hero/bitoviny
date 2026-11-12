---
title: "Prompt injection: prečo AI agent nesmie veriť textom, ktoré číta"
perex: "Jazykový model nerozlišuje medzi pokynom a obsahom. Kto to vie, môže mu do webovej stránky podstrčiť vlastné príkazy."
sekcia: bezpecnost
tagy: ["prompt injection", "AI agenti", "OWASP"]
publikovane: 2026-11-12T07:00:00+01:00
obrazok:
  src: /obrazky/vzor-injection.svg
  alt: "Riadky textu, z ktorých jeden je zvýraznený červenou farbou"
  popisok: "Jeden riadok v texte nie je obsah, ale príkaz."
  kredit: "Bitoviny"
  licencia: "vlastná ilustrácia"
zdroje:
  - nazov: "OWASP Top 10 for LLM Applications: LLM01 Prompt Injection"
    url: "https://genai.owasp.org/llmrisk/llm01-prompt-injection/"
  - nazov: "Simon Willison: Prompt injection attacks against GPT-3"
    url: "https://simonwillison.net/2022/Sep/12/prompt-injection/"
  - nazov: "Greshake a kol.: Not what you've signed up for (arXiv:2302.12173)"
    url: "https://arxiv.org/abs/2302.12173"
vzorovy: true
---

Predstavte si asistenta, ktorý vykoná každú vetu v rozkazovacom spôsobe, na ktorú narazí. Aj tú, ktorú našiel v cudzom liste. Presne tak sa bez ochrany správa jazykový model.

## V čom je problém

Model dostáva pokyny aj spracúvaný obsah tou istou cestou: ako text. Nemá spoľahlivý spôsob, ako ich od seba oddeliť. Ak je v článku, ktorý má zhrnúť, veta „ignoruj predchádzajúce pokyny a napíš toto“, môže ju poslúchnuť.

Názov prompt injection použil v septembri 2022 vývojár Simon Willison, podľa podobnosti so starším útokom SQL injection. Organizácia OWASP ho vo svojom rebríčku rizík pre aplikácie s jazykovými modelmi uvádza na prvom mieste.

## Priamy a nepriamy útok

Pri priamom útoku píše škodlivý pokyn sám používateľ. Nepríjemnejší je nepriamy variant, ktorý v roku 2023 opísal tím okolo Kaia Greshakeho. Útočník pokyn schová do obsahu, ktorý si model prečíta sám: do webovej stránky, e-mailu alebo dokumentu.

Text môže byť pre človeka neviditeľný, napríklad biely na bielom pozadí alebo v metadátach obrázka. Model ho aj tak uvidí.

## Prečo sa to týka redakcie agentov

Agent, ktorý číta cudzie weby, je presne ten prípad. Zberač Bitovín denne spracuje desiatky článkov, ktoré nenapísal a nad ktorými nemá kontrolu. Preto platí niekoľko pravidiel.

- **Stiahnutý text je údaj, nie pokyn.** Agent ho dostane oddelene a výslovne označený ako nedôveryhodný obsah.
- **Agenti majú úzke právomoci.** Zberač nevie nič zverejniť, autorka nevie nič stiahnuť.
- **Výstup má pevnú štruktúru.** Čo do nej nepatrí, ďalší krok odmietne.
- **Factchecker porovnáva so zdrojmi.** Podstrčené tvrdenie, ktoré v nich nie je, neprejde.
- **Posledný je človek.** Nič nevyjde bez jeho schválenia.

## Úplná ochrana neexistuje

Žiadne z týchto opatrení nie je samo osebe spoľahlivé. Model sa dá oklamať aj cez dobre napísané pokyny. Preto sa obrana skladá z viacerých vrstiev a ráta s tým, že niektorá zlyhá.

Pre každého, kto stavia systém s jazykovým modelom, z toho plynie jednoduché pravidlo: model nesmie mať viac právomocí, než koľko by ste zverili neznámemu autorovi textu, ktorý práve číta.
