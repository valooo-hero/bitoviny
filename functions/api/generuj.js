import { chyba } from '../../functions-lib/pristup.js';

const MODEL = '@cf/black-forest-labs/flux-1-schnell';

// Vygeneruje ilustráciu z promptu, ktorý editor videl a potvrdil. Obrázok sa len
// vráti na náhľad: do článku ho uloží až /api/koncept/<pr>/obrazok.
export async function onRequestPost({ env, request }) {
  if (!env.AI) return chyba(503, 'Workers AI nie je k projektu pripojené (chýba binding AI).');
  const { prompt } = await request.json();
  if (typeof prompt !== 'string' || prompt.trim().length < 10) return chyba(400, 'Prompt musí mať aspoň 10 znakov.');
  if (prompt.length > 1500) return chyba(400, 'Prompt je dlhší než 1 500 znakov.');

  // Model vracia štvorec 1024×1024 (1 megapixel). Štyri kroky sú pre schnell obvyklé.
  const vysledok = await env.AI.run(MODEL, { prompt: prompt.trim(), steps: 4 });
  if (!vysledok?.image) return chyba(502, 'Model nevrátil obrázok.');
  return Response.json({ obrazokB64: vysledok.image, model: MODEL });
}
