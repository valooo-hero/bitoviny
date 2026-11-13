# Bitoviny

Slovenský spravodajský portál o technológiách a IT, ktorý pripravuje redakcia AI agentov a zverejňuje ľudský editor.

Projekt je **demonštrácia agentových AI systémov** (LangChain, LangGraph, Langfuse) a beží s nulovými nákladmi na bezplatných tarifách.

## Ako to funguje

1. **Zberač** každé ráno prejde RSS kanály desiatich technologických portálov a vyberie najdôležitejšie včerajšie témy.
2. **Autorka** napíše z viacerých zdrojov pôvodný slovenský článok.
3. **Factchecker** overí každé tvrdenie voči zdrojom a vráti článok na opravu.
4. **Korektorka** opraví gramatiku a štýl.
5. **Fotoeditor** posúdi práva k obrázkom a navrhne náhrady.
6. **Ľudský editor** článok v redakčnom rozhraní skontroluje, prípadne vymení alebo vygeneruje obrázok, a zverejní.

## Dokumentácia

- [Implementačný plán a fázy](docs/PLAN.md)
- [Zdroje správ](docs/ZDROJE.md)
- [LLM poskytovatelia a limity](docs/LLM-PROVIDERY.md)
- [Redakčné zásady](docs/REDAKCNE-ZASADY.md)
- [Factcheck](docs/FACTCHECK.md)
- [Korektúra a obrázky](docs/KOREKTURA-A-OBRAZKY.md)
- [Redakčné rozhranie a zverejňovanie](docs/REDAKCNE-ROZHRANIE.md)
- [Kvalita, štatistiky a evaly](docs/KVALITA.md)

## Stav

Hotové sú Fázy 0 až 7: portál na https://bitoviny.pages.dev, celá redakčná pipeline s trasovaním v Langfuse, redakčné rozhranie, denný beh a štatistiky kvality. Ostáva voliteľná Fáza 8 (newsletter, sociálne siete, vlastná doména).
s trasovaním v Langfuse, redakčné rozhranie a denný beh. Prvé články od agentov schválil a zverejnil editor 12. 11. 2026. 
Nasleduje Fáza 7 (kvalita a štatistiky).

## Lokálny vývoj

Potrebný je Node 24.

```bash
npm install
npm run dev      # vývojový server na http://localhost:4321
npm run build    # statický web do dist/ a vyhľadávací index
npm run preview  # náhľad zostaveného webu
```

Vyhľadávanie funguje až po `npm run build`, vo vývojovom serveri index neexistuje.

## Pipeline

Potrebný je Python 3.12 alebo novší.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e "pipeline[dev]"   # na Linuxe .venv/bin/python
cd pipeline
../.venv/Scripts/python -m pytest
../.venv/Scripts/python -m bitoviny.zber --pocet 12      # včerajšie správy do data/raw/
../.venv/Scripts/python -m bitoviny.redakcia --max-clankov 1   # koncept do data/koncepty/
```

Redakcia potrebuje kľúče v súbore `.env` podľa vzoru `.env.example`. Modely a ich zálohy sú v `config/modely.yaml`, prompty v `pipeline/bitoviny/redakcia/prompty/`.

## Nasadenie

Cloudflare Pages napojené na tento repozitár: príkaz `npm run build`, výstupný priečinok `dist`.

## Štruktúra

| Cesta | Obsah |
|---|---|
| `content/clanky/` | Články v Markdowne, schéma v `src/content.config.ts` |
| `src/data/` | Sekcie a redaktori |
| `src/pages/` | Stránky portálu |
| `public/obrazky/` | Obrázky k článkom |
| `pipeline/bitoviny/` | Redakčná pipeline v Pythone |
| `functions/api/` | API redakčného rozhrania (Cloudflare Pages Functions) |
| `src/pages/admin/` | Redakčné rozhranie |
| `config/sources.yaml` | Zdroje pre Zberača |
| `docs/` | Plán, zásady, zdroje, LLM limity |
