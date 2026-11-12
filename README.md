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

## Stav

Hotová je Fáza 0 (základy) a Fáza 1 (portál). Redakčná pipeline zatiaľ neexistuje, články na webe sú vzorové. Nasleduje Fáza 2 (Zberač).

## Lokálny vývoj

Potrebný je Node 24.

```bash
npm install
npm run dev      # vývojový server na http://localhost:4321
npm run build    # statický web do dist/ a vyhľadávací index
npm run preview  # náhľad zostaveného webu
```

Vyhľadávanie funguje až po `npm run build`, vo vývojovom serveri index neexistuje.

## Nasadenie

Cloudflare Pages napojené na tento repozitár: príkaz `npm run build`, výstupný priečinok `dist`.

## Štruktúra

| Cesta | Obsah |
|---|---|
| `content/clanky/` | Články v Markdowne, schéma v `src/content.config.ts` |
| `src/data/` | Sekcie a redaktori |
| `src/pages/` | Stránky portálu |
| `public/obrazky/` | Obrázky k článkom |
| `config/sources.yaml` | Zdroje pre Zberača |
| `docs/` | Plán, zásady, zdroje, LLM limity |
