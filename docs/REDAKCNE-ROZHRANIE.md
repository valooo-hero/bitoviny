# Redakčné rozhranie a zverejňovanie

## Cesta článku

1. **Denný beh** (`.github/workflows/redakcia.yml`, krátko po polnoci) spustí zber a redakčný graf.
2. Z každého konceptu vznikne **pull request** z vetvy `koncept/<dátum>-<slug>` s dvoma súbormi:
   - `content/clanky/<slug>.md`: článok so zástupným obrázkom,
   - `redakcia/spravy/<slug>.json`: redakčná správa (factcheck, korektúra, obrázky, poznámky).
3. Editor otvorí **`/admin/`**, koncept si prečíta, upraví text, vyberie alebo vygeneruje obrázok.
4. **Zverejniť** doplní čas a schválenie, zlúči pull request do `main` a Cloudflare Pages web znovu zostaví.

Pull requesty konceptov sa nezlučujú ručne na GitHube. Ak by sa to stalo, web článok bez schválenia a s zástupným obrázkom na produkcii nezobrazí (`src/lib/clanky.ts`).

## Rozhranie

| Karta | Čo na nej je |
|---|---|
| Článok | Úprava titulku, perexu a tela s živým náhľadom, poznámky od agentov, zdroje |
| Obrázok | Aktuálny obrázok, obrázky zo zdrojov so zaradením, voľné náhrady, generovanie |
| Factcheck | Hodnotenie, priebeh kôl, neuzavreté nálezy, tabuľka tvrdení s úryvkami |
| Korektúra | Vykonané a zamietnuté úpravy, diff |

**Výmena obrázka.** Použiť sa dá voľná náhrada alebo obrázok zo zdroja v stave `volne` či `tlacove`. Server to overuje, nestačí poslať ľubovoľnú adresu. Redakcia pripraví obrázok vo formáte JPG a uloží ho do vetvy konceptu spolu s popiskom, kreditom a licenciou. Pri prevode sa priehľadné časti vyplnia bielou.

**Zmena stavu obrázka zo zdroja.** Automatické zaradenie je len odporúčanie, posledné slovo má editor. Tlačidlo „Zmeniť stav“ otvorí formulár so stavom, autorom, licenciou a dôvodom. Ak editor obrázok označí za použiteľný, dôvod, autor aj licencia sú povinné. Zmena sa zapíše do redakčnej správy spolu s pôvodným automatickým zaradením, menom editora a časom, takže je dohľadateľné, kto a prečo rozhodol.

**Generovanie obrázka** má dva kroky. Prvé tlačidlo ukáže prompt, ktorý pripravila autorka, a dá sa upraviť. Editor vyberie model a tlačidlom **Odoslať** spustí generovanie. Predvolený FLUX.1-schnell na Cloudflare Workers AI vytvára obrázky 1024 × 1024 px. Druhý model, Meta Muse Image cez fal.ai, generuje JPEG v pomere 16 : 9 pri natívnom rozlíšení približne 2,5 Mpx. Tretí model, ChatGPT Images 2.0 cez fal.ai, generuje s kvalitou `low` v najbližšom podporovanom rozlíšení 1 152 × 656 px. Redakcia oreže 4 px zhora aj zdola na 1 152 × 648 px, zväčší filtrom Lanczos3 na 1 280 × 720 px. Štvrtý model, FLUX.2 [klein] 4B cez DeepInfra, generuje v rozlíšení 1 280 × 720 px. Výstup každého modelu sa pred uložením zakóduje ako WebP s kvalitou 75. Výsledok sa zobrazí na náhľad s voľbami Použiť, Skúsiť znova a Zahodiť. Použitý obrázok je na webe označený ako vytvorený AI.

**Zverejnenie** je zablokované, kým článok nemá obrázok, kým sú v texte neuložené zmeny a kým editor nezaškrtne potvrdenie. Neuzavreté nálezy factchecku sa zobrazia ako upozornenie, nezablokujú.

## Bezpečnosť

- Do rozhrania sa prihlasuje **účtom GitHub** (OAuth). Pustí len účet uvedený v `ADMIN_GITHUB_LOGIN`.
- S repozitárom pracuje rozhranie oprávnením prihláseného editora. Na serveri nie je uložený žiadny trvalý token k repozitáru.
- Relácia je šifrovaný cookie (AES-GCM, kľúč odvodený z tajomstva OAuth aplikácie), označený `HttpOnly`, `Secure` a `SameSite=Strict`. Platí 8 hodín.
- Každá požiadavka na API reláciu overuje (`functions-lib/pristup.js`). Bez nakonfigurovanej OAuth aplikácie API neodpovedá vôbec (stav 503), takže nenastavené rozhranie nie je otvorené.
- Prihlásenie funguje len na produkčnej adrese, nie na náhľadových nasadeniach pull requestov.
- Zápisy sa prijímajú len z vlastnej stránky (kontrola hlavičky `Origin`).
- Text od modelov a z cudzích webov sa nikde nevkladá ako HTML. Značky a odkazy s inou schémou než `http`, `https` a `mailto` sa odstraňujú v pipeline, v API aj v náhľade.

Pôvodný návrh počítal s Cloudflare Access. Ten vyžaduje aktiváciu Zero Trust s platobnou metódou aj pri bezplatnom pláne, preto ho nahradilo prihlásenie cez GitHub.

**Kompromis:** OAuth rozsah `public_repo` dáva prihlásenej relácii zápis do všetkých verejných repozitárov editora, nie len do tohto. GitHub užší rozsah pre OAuth aplikácie neponúka. Oprávnenie sa dá kedykoľvek odvolať v Settings > Applications > Authorized OAuth Apps.

## Nastavenie (jednorazovo)

### GitHub

1. **Tajomstvá pre denný beh.** V priečinku repozitára:

   ```bash
   gh secret set -f .env
   ```

2. **Povoliť Actions vytvárať pull requesty.** Settings > Actions > General > Workflow permissions > „Allow GitHub Actions to create and approve pull requests“.
3. **OAuth aplikácia pre rozhranie.** Settings > Developer settings > OAuth Apps > New OAuth App:
   - Homepage URL: `https://bitoviny.pages.dev`
   - Authorization callback URL: `https://bitoviny.pages.dev/api/auth/callback`

   Po vytvorení skopírovať **Client ID** do `wrangler.toml` (`GITHUB_CLIENT_ID`) a vygenerovať **Client secret**.

### Cloudflare

**Pages > bitoviny > Settings > Variables and Secrets:** tajomstvo `GITHUB_CLIENT_SECRET` s hodnotou Client secret z GitHubu.

Workers AI je pripojené cez `wrangler.toml` (`[ai] binding = "AI"`), nič ďalšie netreba.

1. Pre Meta Muse Image a ChatGPT Images 2.0 vytvorte kľúč s oprávnením **API**. [fal.ai API Keys](https://fal.ai/dashboard/keys)
2. V Cloudflare vyberte **bitoviny → Settings → Production → Variables and Secrets → Add**. Vytvorte šifrované tajomstvo s názvom `FAL_KEY` a hodnotou skopírovaného kľúča. Uložte ho pred produkčným nasadením, ktoré ho použije. [Cloudflare Workers & Pages](https://dash.cloudflare.com/?to=/:account/workers-and-pages)

3. Pre FLUX.2 [klein] 4B nastavte v rovnakých produkčných nastaveniach šifrované tajomstvo `DEEPINFRA_API_KEY`. [DeepInfra API Keys](https://deepinfra.com/dash/keys)

### Lokálny vývoj

```bash
npm run build
npx wrangler pages dev dist
```

Do súboru `.dev.vars` (je v `.gitignore`) patrí `ADMIN_DEV_BYPASS=1` a `GITHUB_TOKEN=...`. Obídenie prihlásenia platí len na `localhost`.

## Viac obrázkov v článku

Článok má jeden **titulný obrázok** (`obrazok`, hore v článku a na titulke webu) a ľubovoľne ďalších v `galeria`, ktoré sa zobrazia pod textom. Spolu najviac 8.

- Pri použití voľnej náhrady, obrázka zo zdroja alebo vygenerovanej ilustrácie editor zvolí umiestnenie: titulný (nahradí doterajší) alebo ďalší obrázok pod textom.
- Na karte Obrázok je zoznam obrázkov článku. Pri každom sa dá zmeniť popisok, odstrániť ho alebo ho nastaviť ako titulný. Doterajší titulný sa vtedy presunie medzi ostatné.
- Po odstránení titulného sa titulným stane prvý z ostatných. Ak žiadny nie je, článok sa vráti k zástupnému obrázku a nedá sa zverejniť.
- **Vlastný obrázok** sa dá nahrať vždy, pri koncepte aj pri zverejnenom článku: JPEG, PNG alebo WebP do 6 MB. Typ súboru sa overuje podľa jeho obsahu, nie podľa názvu. Autor a licencia sú povinné, lebo za pôvod a práva ručí editor.
- Každý obrázok má vlastný súbor `public/obrazky/<slug>-<kód>.jpg`. Vygenerované obrázky majú príponu `webp`. Súbor odstráneného alebo nahradeného obrázka sa z vetvy zmaže.

## Zverejnené články

Pod zoznamom konceptov je zoznam všetkých článkov na webe. Po otvorení sa dá meniť titulok, perex, telo, sekcia, tagy a zdroje.

- **Úprava** sa zapíše priamo do vetvy `main` a web sa znovu zostaví. Článok dostane označenie „Aktualizované“ s časom. Nepovinná poznámka k oprave sa zobrazí pod článkom a na stránke Opravy.
- **Stiahnutie zo zverejnenia** nastaví v článku príznak `stiahnute`. Web ho prestane zobrazovať na všetkých stránkach vrátane RSS a vyhľadávania. Súbor ostáva v repozitári a článok sa dá tlačidlom vrátiť.
- Stiahnutý článok nie je vymazaný: text, obrázok aj história úprav ostávajú verejne dostupné v repozitári na GitHube. Súbory obrázkov ostávajú dostupné aj na webe pod svojou priamou adresou.
- **Obrázky** sa dajú meniť rovnako ako pri koncepte, aj keď je článok zverejnený alebo stiahnutý. Redakčná správa s voľnými náhradami, obrázkami zo zdrojov a promptom autorky sa pri zverejnení ukladá do `redakcia/spravy/<slug>.json` a ostáva k článku natrvalo.
- **Stiahnutý článok má na svojej adrese oznam** „Článok bol stiahnutý“. Samotné odstránenie stránky nestačí: Cloudflare Pages podáva zmazané stránky z vyrovnávacej pamäte ešte až týždeň. Nová stránka na tej istej adrese starú kópiu nahradí.

Zoznam zverejnených článkov je statický súbor `/admin/clanky.json`, ktorý vzniká pri zostavení webu. Po zmene sa preto aktualizuje až o minútu.

## Čo zatiaľ chýba

- Vrátiť článok agentom s komentárom. Editor zatiaľ môže text upraviť sám alebo koncept zahodiť.
- Zmenšovanie a orezávanie nahraných obrázkov. Ukladajú sa v pôvodnej veľkosti.
