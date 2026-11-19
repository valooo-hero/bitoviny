import { FLUX, GPT_IMAGE, MUSE } from '../../functions-lib/modely-obrazkov.js';
import { chyba } from '../../functions-lib/pristup.js';

const MAX_BASE64 = 8 * 1024 * 1024; // 6 MiB obrázka pred zakódovaním.

async function generujFal(kluc, model, prompt) {
  if (!kluc) return chyba(503, 'V Cloudflare Pages chýba tajomstvo FAL_KEY.');

  const gpt = model === GPT_IMAGE;
  const format = gpt ? 'webp' : 'jpeg';
  const nastavenia = gpt
    ? {
        image_size: { width: GPT_IMAGE.vstupnaSirka, height: GPT_IMAGE.generovanaVyska },
        quality: 'low',
        background: 'opaque',
        output_compression: 100,
      }
    : { aspect_ratio: '16:9' };
  let odpoved, vysledok;
  try {
    odpoved = await fetch(`https://fal.run/${model.id}`, {
      method: 'POST',
      headers: {
        Authorization: `Key ${kluc}`,
        'Content-Type': 'application/json',
        'X-Fal-Request-Start-Timeout': '30',
      },
      redirect: 'error',
      signal: AbortSignal.timeout(85_000),
      body: JSON.stringify({
        prompt,
        ...nastavenia,
        num_images: 1,
        output_format: format,
        sync_mode: true,
      }),
    });
    if (odpoved.ok) vysledok = await odpoved.json();
  } catch (e) {
    if (e?.name === 'TimeoutError') return chyba(504, 'Generovanie na fal.ai trvalo príliš dlho.');
    return chyba(502, 'Výsledok generovania sa nepodarilo načítať z fal.ai.');
  }

  if (odpoved.status === 401 || odpoved.status === 403) {
    return chyba(502, 'fal.ai odmietol prístup. Skontrolujte kľúč FAL_KEY a kredit účtu.');
  }
  if (odpoved.status === 504) return chyba(504, 'Generovanie na fal.ai trvalo príliš dlho.');
  if (!odpoved.ok) return chyba(502, `fal.ai nevygeneroval obrázok (HTTP ${odpoved.status}).`);

  const prefix = `data:image/${format};base64,`;
  const url = vysledok?.images?.[0]?.url;
  if (typeof url !== 'string' || !url.startsWith(prefix) || url.length === prefix.length) {
    return chyba(502, `Model ${model.nazov} nevrátil obrázok ${format.toUpperCase()}.`);
  }
  const obrazokB64 = url.slice(prefix.length);
  if (obrazokB64.length > MAX_BASE64) return chyba(502, 'Vygenerovaný obrázok je väčší než 6 MB.');
  return Response.json({ obrazokB64, model: model.id });
}

// Obrázok sa vráti na náhľad. Do článku sa uloží až po potvrdení editorom.
export async function onRequestPost({ env, request }) {
  const vstup = await request.json().catch(() => null);
  const { prompt, model = FLUX.id } = vstup ?? {};
  if (typeof prompt !== 'string' || prompt.trim().length < 10) return chyba(400, 'Prompt musí mať aspoň 10 znakov.');
  if (prompt.length > 1500) return chyba(400, 'Prompt je dlhší než 1 500 znakov.');

  if (model === MUSE.id) return generujFal(env.FAL_KEY, MUSE, prompt.trim());
  if (model === GPT_IMAGE.id) return generujFal(env.FAL_KEY, GPT_IMAGE, prompt.trim());
  if (model !== FLUX.id) return chyba(400, 'Neznámy model na generovanie obrázka.');
  if (!env.AI) return chyba(503, 'Workers AI nie je k projektu pripojené (chýba binding AI).');

  const vysledok = await env.AI.run(FLUX.id, { prompt: prompt.trim(), steps: 4 });
  if (!vysledok?.image) return chyba(502, 'Model nevrátil obrázok.');
  return Response.json({ obrazokB64: vysledok.image, model: FLUX.id });
}
