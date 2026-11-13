import { GitHub, naBase64 } from '../../functions-lib/github.js';
import { priponaZBajtov } from '../../functions-lib/obrazky.js';
import { chyba } from '../../functions-lib/pristup.js';

// Redaktori zo src/data/redakcia.ts. Iné mená súborov sa zapísať nedajú.
const REDAKTORI = ['robert', 'klara', 'tomas', 'ciarka', 'cyril', 'fluxana', 'sefredaktor'];
const MAX_BAJTOV = 400 * 1024;

// Uloží avatar redaktora do public/avatary/<id>.<prípona> vo vetve main.
// Obrázok pripraví rozhranie: vygeneruje ho cez /api/generuj a zmenší.
export async function onRequestPost({ env, request, data }) {
  const { id, obrazokB64 } = await request.json();
  if (!REDAKTORI.includes(id)) return chyba(400, 'Neznámy redaktor.');
  if (typeof obrazokB64 !== 'string' || obrazokB64.length > MAX_BAJTOV * 1.4) return chyba(400, 'Chýba obrázok alebo je väčší než 400 kB.');

  let bajty;
  try {
    bajty = Uint8Array.from(atob(obrazokB64), (c) => c.charCodeAt(0));
  } catch {
    return chyba(400, 'Dáta obrázka sú poškodené.');
  }
  const pripona = priponaZBajtov(bajty);
  if (!pripona) return chyba(400, 'Súbor nie je obrázok JPEG, PNG ani WebP.');

  const gh = new GitHub(env, data.token);
  // Starý avatar s inou príponou by ostal visieť, preto sa zmaže.
  for (const ina of ['jpg', 'png', 'webp'].filter((p) => p !== pripona)) {
    await gh.zmazSubor(`public/avatary/${id}.${ina}`, 'main', `Avatar redaktora: ${id} (stará verzia)`);
  }
  const cesta = `public/avatary/${id}.${pripona}`;
  await gh.zapis(cesta, 'main', naBase64(bajty), `Avatar redaktora: ${id}`, await gh.shaSuboru(cesta, 'main'));
  return Response.json({ ok: true, src: `/avatary/${id}.${pripona}` });
}
