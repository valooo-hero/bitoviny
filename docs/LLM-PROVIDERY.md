# Bezplatné jazykové modely redakcie

Poradie modelov pre každú rolu určuje [konfigurácia](../config/modely.yaml). Výber tém a výrazy pre fotobanky začínajú na GPT-OSS 120B cez Groq. Klára píše a opravuje články cez Gemini 3.8 Flash. Tomáš overuje tvrdenia a Čiarka robí korektúru cez Gemini 3.5 Flash-Lite.

## Kľúče a tarify

Lokálne sa kľúče načítajú zo súboru `.env` v koreni projektu. Nočná redakcia ich dostáva z GitHub Actions Secrets. Stačí jeden z týchto kľúčov.

| Premenná | Podmienka použitia |
|---|---|
| `GOOGLE_API_KEY` | Projekt Gemini Developer API na bezplatnej tarife. Tarifu skontroluj v Google AI Studio. |
| `GROQ_API_KEY` | Organizácia na pláne Free v konzole Groq. |
| `OPENROUTER_API_KEY` | Konkrétny model s príponou `:free`. Požiadavka obmedzuje cenu vstupu aj výstupu na nulu. |

Pri zmene účtu alebo kľúča skontroluj tarifu Google a Groq. Cenu pri týchto službách určuje fakturácia účtu. Pred použitím kľúča z plateného účtu ho odober z nastavení redakcie. [Cenník Gemini](https://ai.google.dev/gemini-api/docs/pricing) · [Limity Groq](https://console.groq.com/docs/rate-limits)

## Zálohy a denné limity

Redakcia preskočí poskytovateľov bez kľúča. Pri výpadku, limite alebo chybnom štruktúrovanom výstupe skúsi ďalší model pre danú rolu. Na OpenRouteri používa ERNIE Flash Preview s výstupom podľa JSON schémy. Pri dlhých zdrojových textoch je Groq až posledná možnosť, lebo jeho tokenový limit môže odmietnuť celý vstup. [Bezplatný model ERNIE](https://openrouter.ai/baidu/ernie-5.5-flash-preview%3Afree) · [Limity OpenRouter](https://openrouter.ai/docs/api/reference/limits)

Nočný beh cieli na osem článkov. Ak zlyhá výber tém, beh skončí pred písaním. Ak zlyhajú všetky možnosti povinného factchecku, v logu zostane dôvod, koncept sa neuloží a redakcia pokračuje ďalšou témou. Pri výpadku samotnej korektúry zostávajú dostupné pevné pravidlá a LanguageTool.

Generovanie obrázkov má vlastných poskytovateľov a účtovanie. [Redakčné rozhranie](REDAKCNE-ROZHRANIE.md)
