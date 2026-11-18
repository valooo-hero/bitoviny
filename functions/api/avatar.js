import { GitHub, naBase64 } from '../../functions-lib/github.js';
import { jeJpeg } from '../../functions-lib/jpeg.js';
import { chyba } from '../../functions-lib/pristup.js';

// Redaktori zo src/data/redakcia.ts. Iné mená súborov sa zapísať nedajú.
const REDAKTORI = ['robert', 'klara', 'tomas', 'ciarka', 'cyril', 'fluxana', 'sefredaktor'];
const MAX_BAJTOV = 400 * 1024;

// Uloží avatar redaktora do public/avatary/<id>.jpg vo vetve main.
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
  if (bajty.length > MAX_BAJTOV) return chyba(400, 'Obrázok je väčší než 400 kB.');
  if (!jeJpeg(bajty)) return chyba(400, 'Avatar musí byť vo formáte JPG.');

  const gh = new GitHub(env, data.token);
  const src = `/avatary/${id}.jpg`;
  const cesta = `public${src}`;
  await gh.zapis(cesta, 'main', naBase64(bajty), `Avatar redaktora: ${id}`, await gh.shaSuboru(cesta, 'main'));
  return Response.json({ ok: true, src });
}
