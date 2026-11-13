import { GitHub } from '../../../../functions-lib/github.js';
import { cielClanku, upravGaleriu, sChybami } from '../../../../functions-lib/obrazky.js';

// Obrázky, ktoré už v článku sú: nastaviť ako titulný, zmeniť popisok, odstrániť. Cieľ: zverejnený alebo stiahnutý článok.
export async function onRequestPost({ env, params, request, data }) {
  return sChybami(async () => {
    const gh = new GitHub(env, data.token);
    const vysledok = await upravGaleriu(gh, await cielClanku(gh, params), await request.json());
    return Response.json({ ok: true, ...(vysledok && typeof vysledok === 'object' ? { vysledok } : {}) });
  });
}
