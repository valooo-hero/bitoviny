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

Fáza 0 (základy) je hotová. Kód portálu ani pipeline zatiaľ neexistuje, nasleduje Fáza 1.
