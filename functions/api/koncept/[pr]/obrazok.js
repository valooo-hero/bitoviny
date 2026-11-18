import { GitHub } from '../../../../functions-lib/github.js';
import { cielKonceptu, nahladZdroja, pridajObrazok, sChybami } from '../../../../functions-lib/obrazky.js';

// Pridá obrázok: voľnú náhradu, obrázok zo zdroja, vygenerovanú ilustráciu alebo vlastný súbor. Cieľ: koncept.
export async function onRequestPost({ env, params, request, data }) {
  return sChybami(async () => {
    const gh = new GitHub(env, data.token);
    const ciel = await cielKonceptu(gh, params);
    const vstup = await request.json();
    if (vstup.typ === 'nahlad-zdroja') return nahladZdroja(gh, ciel, vstup.url);
    const vysledok = await pridajObrazok(gh, ciel, vstup);
    return Response.json({ ok: true, ...(vysledok && typeof vysledok === 'object' ? { vysledok } : {}) });
  });
}
