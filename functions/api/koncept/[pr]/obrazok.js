import { GitHub } from '../../../../functions-lib/github.js';
import { cielKonceptu, pridajObrazok, sChybami } from '../../../../functions-lib/obrazky.js';

// Pridá obrázok: voľnú náhradu, obrázok zo zdroja, vygenerovanú ilustráciu alebo vlastný súbor. Cieľ: koncept.
export async function onRequestPost({ env, params, request, data }) {
  return sChybami(async () => {
    const gh = new GitHub(env, data.token);
    const vysledok = await pridajObrazok(gh, await cielKonceptu(gh, params), await request.json());
    return Response.json({ ok: true, ...(vysledok && typeof vysledok === 'object' ? { vysledok } : {}) });
  });
}
