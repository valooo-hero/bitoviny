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

**Výmena obrázka.** Použiť sa dá voľná náhrada alebo obrázok zo zdroja v stave `volne` či `tlacove`. Server to overuje, nestačí poslať ľubovoľnú adresu. Obrázok sa stiahne a uloží do vetvy konceptu ako `public/obrazky/<slug>.<prípona>` spolu s popiskom, kreditom a licenciou.

**Zmena stavu obrázka zo zdroja.** Automatické zaradenie je len odporúčanie, posledné slovo má editor. Tlačidlo „Zmeniť stav“ otvorí formulár so stavom, autorom, licenciou a dôvodom. Ak editor obrázok označí za použiteľný, dôvod, autor aj licencia sú povinné. Zmena sa zapíše do redakčnej správy spolu s pôvodným automatickým zaradením, menom editora a časom, takže je dohľadateľné, kto a prečo rozhodol.

**Generovanie obrázka** má dva kroky. Prvé tlačidlo ukáže prompt, ktorý pripravila autorka, a dá sa upraviť. Až druhé tlačidlo ho odošle modelu FLUX.1-schnell na Cloudflare Workers AI. Výsledok sa zobrazí na náhľad s voľbami Použiť, Skúsiť znova a Zahodiť. Použitý obrázok je na webe označený ako vytvorený AI.

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
- Každý obrázok má vlastný súbor `public/obrazky/<slug>-<kód>.<prípona>`. Súbor odstráneného alebo nahradeného obrázka sa z vetvy zmaže.

## Zverejnené články

Pod zoznamom konceptov je zoznam všetkých článkov na webe. Po otvorení sa dá meniť titulok, perex, telo, sekcia, tagy a zdroje.

- **Úprava** sa zapíše priamo do vetvy `main` a web sa znovu zostaví. Článok dostane označenie „Aktualizované“ s časom. Nepovinná poznámka k oprave sa zobrazí pod článkom a na stránke Opravy.
- **Stiahnutie zo zverejnenia** nastaví v článku príznak `stiahnute`. Web ho prestane zobrazovať na všetkých stránkach vrátane RSS a vyhľadávania. Súbor ostáva v repozitári a článok sa dá tlačidlom vrátiť.
- Stiahnutý článok nie je vymazaný: text, obrázok aj história úprav ostávajú verejne dostupné v repozitári na GitHube.
- Obrázky zverejneného článku sa v rozhraní zatiaľ meniť nedajú.

Zoznam zverejnených článkov je statický súbor `/admin/clanky.json`, ktorý vzniká pri zostavení webu. Po zmene sa preto aktualizuje až o minútu.

## Čo zatiaľ chýba

- Vrátiť článok agentom s komentárom. Editor zatiaľ môže text upraviť sám alebo koncept zahodiť.
- Nahranie vlastného obrázka z disku.
- Zmena obrázkov pri už zverejnenom článku.
