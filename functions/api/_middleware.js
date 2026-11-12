import { chyba, skontrolujPristup } from '../../functions-lib/pristup.js';

// Každá požiadavka na /api/* musí prejsť overením prístupu. Chyby sa vracajú ako JSON.
export async function onRequest(context) {
  const odmietnutie = await skontrolujPristup(context.request, context.env);
  if (odmietnutie) return odmietnutie;
  try {
    const odpoved = await context.next();
    odpoved.headers.set('Cache-Control', 'no-store');
    return odpoved;
  } catch (e) {
    return chyba(500, e.message || 'Neznáma chyba');
  }
}
