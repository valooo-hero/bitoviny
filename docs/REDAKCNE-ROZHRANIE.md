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

**Výmena obrázka.** Použiť sa dá len obrázok, ktorý ponúkla redakčná správa a nie je chránený. Server to overuje, nestačí poslať ľubovoľnú adresu. Obrázok sa stiahne a uloží do vetvy konceptu ako `public/obrazky/<slug>.<prípona>` spolu s popiskom, kreditom a licenciou.

**Generovanie obrázka** má dva kroky. Prvé tlačidlo ukáže prompt, ktorý pripravila autorka, a dá sa upraviť. Až druhé tlačidlo ho odošle modelu FLUX.1-schnell na Cloudflare Workers AI. Výsledok sa zobrazí na náhľad s voľbami Použiť, Skúsiť znova a Zahodiť. Použitý obrázok je na webe označený ako vytvorený AI.

**Zverejnenie** je zablokované, kým článok nemá obrázok, kým sú v texte neuložené zmeny a kým editor nezaškrtne potvrdenie. Neuzavreté nálezy factchecku sa zobrazia ako upozornenie, nezablokujú.

## Bezpečnosť

- `/admin/` a `/api/*` chráni **Cloudflare Access**.
- Každá požiadavka na API navyše overuje podpis tokenu Access (`functions-lib/pristup.js`). Bez nakonfigurovaného Access API neodpovedá vôbec (stav 503), takže nenastavené rozhranie nie je otvorené.
- Zápisy sa prijímajú len z vlastnej stránky.
- Text od modelov a z cudzích webov sa nikde nevkladá ako HTML. Značky a odkazy s inou schémou než `http`, `https` a `mailto` sa odstraňujú v pipeline, v API aj v náhľade.
- Token pre GitHub je uložený ako tajomstvo v Cloudflare a má prístup len k tomuto repozitáru.

## Nastavenie (jednorazovo)

### GitHub

1. **Tajomstvá pre denný beh.** V priečinku repozitára:

   ```bash
   gh secret set -f .env
   ```

2. **Povoliť Actions vytvárať pull requesty.** Settings > Actions > General > Workflow permissions > „Allow GitHub Actions to create and approve pull requests“.
3. **Token pre rozhranie.** Settings > Developer settings > Fine-grained tokens: prístup len k repozitáru `bitoviny`, oprávnenia Contents a Pull requests na čítanie aj zápis.

### Cloudflare

1. **Zero Trust > Access > Applications:** aplikácia typu Self-hosted pre `bitoviny.pages.dev` s cestami `/admin` a `/api`, pravidlo povoľujúce e-mail editora.
2. Z aplikácie skopírovať **Application Audience (AUD) tag** a názov tímu. Oba údaje patria do `wrangler.toml` ako `ACCESS_AUD` a `ACCESS_TEAM_DOMAIN`.
3. **Pages > bitoviny > Settings > Variables and Secrets:** tajomstvo `GITHUB_TOKEN` s tokenom z GitHubu.

Workers AI je pripojené cez `wrangler.toml` (`[ai] binding = "AI"`), nič ďalšie netreba.

### Lokálny vývoj

```bash
npm run build
npx wrangler pages dev dist
```

Do súboru `.dev.vars` (je v `.gitignore`) patrí `ADMIN_DEV_BYPASS=1` a `GITHUB_TOKEN=...`. Obídenie prihlásenia platí len na `localhost`.

## Čo zatiaľ chýba

- Vrátiť článok agentom s komentárom. Editor zatiaľ môže text upraviť sám alebo koncept zahodiť.
- Nahranie vlastného obrázka z disku.
- Úprava tagov a sekcie v rozhraní.
