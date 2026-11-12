# Implementačný plán

Cieľ: verejný portál `bitoviny.pages.dev`, ktorý denne zverejní niekoľko pôvodných slovenských článkov o technológiách. Projekt slúži ako ukážka agentových AI systémov, nie ako komerčné médium.

## Zásady projektu

- **Nulové náklady.** Všetko beží na bezplatných tarifách, pozri [LLM-PROVIDERY.md](LLM-PROVIDERY.md).
- **Človek zverejňuje.** Žiadny článok nejde von bez schválenia editorom.
- **Fotka je chránená, kým sa nepreukáže opak.**
- **Otvorený obsah.** Portál nie je chránený pred AI crawlermi ani tréningom.
- **Priehľadnosť.** Každý článok je označený ako pripravený AI a odkazuje na zdroje aj na záznam behu v Langfuse.

## Architektúra

| Vrstva | Riešenie |
|---|---|
| Web | Astro, statický výstup, Cloudflare Pages |
| Redakčné rozhranie | `/admin` v tom istom projekte, Pages Functions, prístup cez Cloudflare Access |
| Úložisko konceptov | GitHub: jeden pull request na článok, admin ho číta a upravuje cez GitHub API |
| Články | Markdown s frontmatterom v `content/clanky/` |
| Obrázky | Repozitár, pri väčšom objeme Cloudflare R2 |
| Pipeline | Python, LangGraph (stavový graf), LangChain (modely, štruktúrované výstupy) |
| Plánovač | GitHub Actions cron, denne okolo 5:00 |
| Sledovanie | Langfuse Cloud (EU): trace, verzie promptov, evaly |
| Generovanie obrázkov | Cloudflare Workers AI, FLUX.1-schnell |

## Agenti

Každý agent je uzol grafu a zároveň „redaktor“ na stránke Redakcia.

| Redaktor | Rola | Čo robí |
|---|---|---|
| Róbert S. Sliedič | Zberač | Číta RSS, vyberie včerajšie správy, zoskupí rovnaké témy, vyberie 5 najdôležitejších, stiahne plné texty a obrázky s popismi a kreditmi |
| Klára Vesnicová | Autorka | Z aspoň dvoch zdrojov napíše pôvodný článok: titulok, perex, telo, sekcia, tagy, zdroje. Navrhne aj prompt na ilustráciu |
| Tomáš Neverný | Factchecker | Rozloží článok na tvrdenia, každé overí voči zdrojom, chyby vráti autorke (najviac dve kolá), zvyšok zapíše do správy |
| Čiarka Ypsilonová | Korektorka | Opraví gramatiku a štýl, výstup ako diff. Automatická kontrola overí, že sa nezmenili čísla ani mená |
| Cyril Kopirajt | Fotoeditor | Zaradí každý obrázok: voľná licencia, nejasné, chránené. Vyhľadá náhrady |
| Fluxana Štetcová | Ilustrátorka | Na pokyn editora vygeneruje ilustračný obrázok |
| Šéfredaktor | Človek | Skontroluje, upraví, zverejní |

Avatary redaktorov sa vygenerujú jednorazovo cez FLUX v jednotnom štýle. Profil obsahuje bio, použitý model a štatistiky z Langfuse.

## Práva k obrázkom

1. Agent hľadá kredit v popisku, v RSS (`media:credit`), v schema.org a IPTC metadátach.
2. Signály ochrany: Getty, Reuters, AP, AFP, Shutterstock, „©“, meno fotografa bez licencie.
3. Chránené a nejasné obrázky sa do článku nevložia. V admine sú označené červeno s dôvodom.
4. Náhrady v tomto poradí: press kit výrobcu, Wikimedia Commons, Openverse alebo Unsplash, AI ilustrácia.
5. Každý obrázok má povinne popisok, kredit a licenciu, inak build zlyhá.

## Redakčné rozhranie a release

Zoznam konceptov, po otvorení náhľad článku a redakčná správa: zdroje, tabuľka tvrdení s verdiktmi, diff korektúry, stav práv k obrázkom, odkaz na Langfuse trace.

Akcie pri obrázku:

- **Vymeniť obrázok**: galéria vopred pripravených alternatív s licenciou a kreditom. Popisok a kredit sa doplnia automaticky.
- **Vygenerovať obrázok**, dvojkrokovo:
  1. Prvé tlačidlo zobrazí prompt navrhnutý agentom v upraviteľnom poli.
  2. Druhé tlačidlo „Odoslať“ zavolá Workers AI.
  3. Náhľad s voľbami Použiť, Skúsiť znova, Zahodiť. Použitý obrázok dostane popisok „Ilustračný obrázok, vytvorené AI“.
- **Odstrániť obrázok**, úprava popisku.

Akcie pri článku: upraviť text, vrátiť agentom s komentárom, zahodiť, **Zverejniť**.

Zverejnenie je zablokované, kým je v článku chránený obrázok bez výslovného potvrdenia editora. Zverejnenie zlúči pull request, Cloudflare Pages web znovu zostaví a zapíše sa, kto článok schválil. Opravy po zverejnení idú rovnakou cestou a pod článkom pribudne poznámka „Aktualizované“.

## Portál

**Sekcie:** AI, Bezpečnosť, Hardvér, Mobil, Softvér a vývoj, Veda a vesmír, Biznis, Slovensko a EÚ.

**Titulka:** hlavná správa, najnovšie, bloky podľa sekcií.

**Článok:** titulok, perex, hlavný obrázok s popiskom a kreditom, dátum a aktualizácia, podpis redaktorov, označenie AI, zdroje, tagy, súvisiace články, odkaz na trace.

**Stránky:** Redakcia, Ako to funguje, Redakčné zásady, Opravy, Kontakt, Ochrana súkromia.

**Technické prvky:** tmavý režim (podľa systému, prepínač, pamätá si voľbu), RSS, sitemap a news sitemap, schema.org `NewsArticle`, Open Graph, vyhľadávanie (Pagefind), archív, 404, Cloudflare Web Analytics bez cookies, `robots.txt` povoľujúci všetko, `llms.txt`.

## Fázy

| Fáza | Obsah | Hotovo, keď |
|---|---|---|
| 0. Základy | Repozitár, plán, zdroje, zásady, overenie limitov | Hotové |
| 1. Portál | Astro šablóny, sekcie, schéma článku, tmavý režim, stránka Redakcia s avatarmi, 3 ručné vzorové články, nasadenie | Hotové, beží na bitoviny.pages.dev. Avatary sú zástupné, news sitemap chýba |
| 2. Zberač | RSS, sťahovanie textov a obrázkov, zoskupovanie tém, výber | Hotové: `python -m bitoviny.zber` vytvorí denný JSON s témami. Alternatívne obrázky sa presunuli do Fázy 5, výber tém cez LLM do Fázy 3 |
| 3. Autorka a Langfuse | Graf v LangGraphe, výber tém modelom, prompty, záložné modely, trasovanie | Hotové: `python -m bitoviny.redakcia` napíše koncepty do `data/koncepty/` s odkazom na trace. Prompty sú v repozitári, nie v Langfuse |
| 4. Factcheck | Extrakcia tvrdení, overenie, slučka opráv | Správa s verdiktmi, test na zámerne chybných článkoch |
| 5. Korektúra a fotky | Korektorka, klasifikácia práv | Diff korektúry a varovania k obrázkom |
| 6. Redakčné rozhranie | Admin za Cloudflare Access, výmena a generovanie obrázkov, Zverejniť, cron | Prvý článok zverejnený celým procesom |
| 7. Kvalita | Evaly, ladenie modelov, štatistiky redaktorov, stránka Ako to funguje | Známa miera zásahov editora |
| 8. Rozšírenia | Newsletter, sociálne siete, vlastná doména | Podľa priorít |

## Účty, ktoré treba založiť ručne

Zakladá ich majiteľ projektu, kľúče patria do GitHub Secrets a Cloudflare, nikdy do repozitára.

| Služba | Kedy | Na čo |
|---|---|---|
| Cloudflare | Fáza 1 | Pages, neskôr Access a Workers AI |
| Google AI Studio | Fáza 3 | Kľúč pre Gemini API |
| Groq | Fáza 3 | Kľúč pre rýchle pomocné úlohy |
| OpenRouter | Fáza 3 | Záložné bezplatné modely |
| Langfuse Cloud (EU) | Fáza 3 | Trasovanie |

## Otvorené body

- Právna stránka: podmienky použitia zdrojov, povinnosti prevádzkovateľa spravodajského webu na Slovensku, označovanie AI obsahu podľa EU AI Act. Pri demonštračnom projekte nízke riziko, pri komerčnom použití treba konzultáciu.
- Claude Pro: voliteľný pokus vo Fáze 7 (naplánovaná úloha Claude Code ako nezávislý druhý názor). Nie je súčasťou produkčnej pipeline.
