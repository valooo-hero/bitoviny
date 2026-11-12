import { chyba, overPoziadavku } from '../../functions-lib/pristup.js';

// Každá požiadavka na /api/* okrem prihlasovania musí mať platnú reláciu.
// Chyby sa vracajú ako JSON a odpovede sa neukladajú do vyrovnávacej pamäte.
export async function onRequest(context) {
  const cesta = new URL(context.request.url).pathname;
  try {
    if (!cesta.startsWith('/api/auth/')) {
      const overenie = await overPoziadavku(context.request, context.env);
      if (overenie.odmietnutie) return overenie.odmietnutie;
      context.data.token = overenie.token;
      context.data.login = overenie.login;
    }
    const odpoved = await context.next();
    const kopia = new Response(odpoved.body, odpoved);
    kopia.headers.set('Cache-Control', 'no-store');
    return kopia;
  } catch (e) {
    return chyba(500, e.message || 'Neznáma chyba');
  }
}
