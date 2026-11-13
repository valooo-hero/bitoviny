import { GitHub } from '../../../../functions-lib/github.js';
import { cielKonceptu, zmenPrava, sChybami } from '../../../../functions-lib/obrazky.js';

// Editor mení zaradenie obrázka zo zdroja podľa vlastného úsudku. Cieľ: koncept.
export async function onRequestPost({ env, params, request, data }) {
  return sChybami(async () => {
    const gh = new GitHub(env, data.token);
    const vysledok = await zmenPrava(gh, await cielKonceptu(gh, params), await request.json(), data.login);
    return Response.json({ ok: true, ...(vysledok && typeof vysledok === 'object' ? { vysledok } : {}) });
  });
}
