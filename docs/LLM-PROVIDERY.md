# LLM poskytovatelia a limity

Stav k 12. 11. 2026. Čísla okrem Cloudflare, OpenRouter a Langfuse pochádzajú z blogov tretích strán, nie z oficiálnych stránok, a navzájom si odporujú. **Záväzné sú až hodnoty v konzole každého poskytovateľa po založení kľúča.**

## Zistené limity bezplatných taríf

| Služba | Limit | Spoľahlivosť údaju |
|---|---|---|
| Gemini Flash | Novšie zdroje: 5 požiadaviek za minútu, 20 denne. Staršie uvádzajú až 1 500 denne | Nízka, zdroje si odporujú |
| Gemini Flash-Lite | 15 za minútu, 500 denne | Stredná |
| Gemini Pro | Bez bezplatného prístupu | Stredná |
| Groq, malé modely (trieda Llama 8B) | 30 za minútu, 14 400 denne | Stredná |
| Groq, veľké modely (trieda 70B a viac) | 30 za minútu, približne 1 000 denne | Stredná |
| OpenRouter `:free` | 20 za minútu, 50 denne. Po jednorazovom nákupe kreditu za 10 USD 1 000 denne | Vysoká, oficiálna stránka |
| Workers AI | 10 000 neurónov denne, spoločné pre všetky modely | Vysoká, oficiálna dokumentácia |
| Langfuse Hobby | 50 000 jednotiek mesačne, 30 dní histórie, 2 používatelia | Vysoká, oficiálny cenník |

FLUX.1-schnell na Workers AI stojí 4,80 neurónu za dlaždicu 512×512 a 9,60 za krok. Obrázok 1024×1024 (4 dlaždice) na 4 kroky vychádza približne na 58 neurónov, teda zhruba 170 obrázkov denne v bezplatnom limite. Je to vlastný prepočet z cenníka, treba ho potvrdiť meraním.

## Dôsledok pre návrh

Pôvodný predpoklad „všetko slovenské na Gemini Flash“ nemusí vyjsť. Pri 5 článkoch denne potrebuje pipeline približne 5 volaní autorky, 10 až 15 volaní factcheckera a 5 volaní korektorky. Ak platí limit 20 denne, Flash stačí len autorke.

## Priradenie modelov

| Agent | Hlavný model | Záloha |
|---|---|---|
| Zberač: triedenie a výber tém | Groq, malý model | Gemini Flash-Lite |
| Zoskupovanie tém | Lokálny embedding model v GitHub Actions | žiadna |
| Autorka | Gemini Flash | Gemini Flash-Lite, potom OpenRouter `:free` |
| Factchecker | Gemini Flash-Lite | Groq, veľký model |
| Korektorka | Gemini Flash-Lite | OpenRouter `:free` |
| Prompt na ilustráciu | Groq, malý model | Gemini Flash-Lite |
| Ilustrácia | Workers AI, FLUX.1-schnell | žiadna |

Zálohy rieši LangChain cez `with_fallbacks`. Názvy konkrétnych modelov budú v konfigurácii, nie v kóde, lebo ponuka sa mení.

Keď všetky modely narazia na denný limit, pipeline článok odloží na ďalší beh a nezlyhá.

## Čo overiť vo Fáze 3

- Skutočné limity Gemini Flash a Flash-Lite v Google AI Studio.
- Kvalitu slovenčiny Flash-Lite pri korektúre. Ak nestačí, korektúra prejde na Flash a počet článkov klesne na 3 až 4 denne.
- Či bezplatná tarifa Gemini platí aj pre účty z EÚ.

## Zdroje

- https://developers.cloudflare.com/workers-ai/platform/pricing/
- https://openrouter.ai/pricing
- https://langfuse.com/pricing
- https://imisofts.com/blog/gemini-api-free-tier-limits/
- https://www.aifreeapi.com/en/posts/google-gemini-api-free-tier
- https://tokenmix.ai/blog/gemini-api-free-tier-limits
- https://benchlm.ai/free-tier/groq

## Overené s vlastnými kľúčmi (12. 11. 2026)

Všetky štyri kľúče sa úspešne prihlásili.

| Služba | Zistenie |
|---|---|
| Gemini | Dostupné sú `gemini-3.8-flash` a `gemini-3.5-flash-lite`. Flash-Lite opravil slovenskú vetu správne. Flash pri teste vrátil 503 (preťaženie), takže záloha je nutná |
| Groq | Modely Llama v ponuke už nie sú. Použiteľné sú `qwen/qwen3.8-27b`, `openai/gpt-oss-20b` a `openai/gpt-oss-120b`. Limit 1 000 požiadaviek denne a 8 000 tokenov za minútu na model. Qwen opravil slovenskú vetu správne |
| OpenRouter | Bezplatná tarifa, 50 požiadaviek denne na modely `:free` |
| Langfuse | Kľúče platia pre projekt „My Project“ |

Limit 8 000 tokenov za minútu na Groq znamená, že dlhé zdrojové texty sa doň nezmestia. Groq sa preto hodí na krátke úlohy, factcheck s celými zdrojmi musí bežať na Gemini.

Denné limity Gemini API nevracia, treba ich pozrieť v Google AI Studio.

## Skúsenosti z prvých ostrých behov (12. 11. 2026)

Platné priradenie modelov je v `config/modely.yaml`, tabuľka „Priradenie modelov“ vyššie je pôvodný návrh.

- **Gemini je nespoľahlivé.** `gemini-3.8-flash` aj `gemini-3.5-flash` a Flash-Lite pri dlhom vstupe opakovane vracali 503 a 504. Prvý koncept nakoniec napísal až štvrtý model v poradí, `baidu/ernie-5.5-flash-preview:free` cez OpenRouter, v použiteľnej slovenčine.
- **Modely Gemini 2.5 už nie sú dostupné** novým používateľom.
- **Groq Qwen kazí volanie nástrojov** (skomolí názov schémy). Funguje so štruktúrovaným výstupom cez JSON schému. Výber tém preto robí `openai/gpt-oss-120b`, ktorý lepšie triafal aj sekcie.
- **Gemma na OpenRouter** bola v bezplatnej tarife dočasne obmedzená (429).
- **Bezplatné modely na OpenRouter sa menia.** Zoznam treba občas skontrolovať, inak záloha potichu prestane existovať.

Pri výpadku všetkých modelov pipeline článok preskočí a pokračuje ďalším.
