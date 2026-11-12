import { COOKIE_RELACIE, jeLokalne, nastavCookie } from '../../../functions-lib/pristup.js';

// Odhlásenie: zmaže reláciu v prehliadači. Oprávnenie aplikácie sa dá navyše
// odvolať na GitHube v Settings > Applications.
export async function onRequestPost({ request }) {
  const povod = request.headers.get('Origin');
  if (!povod || povod !== new URL(request.url).origin) return Response.json({ chyba: 'Požiadavka z cudzej stránky.' }, { status: 403 });
  return Response.json(
    { ok: true },
    { headers: { 'Set-Cookie': nastavCookie(COOKIE_RELACIE, '', { maxAge: 0, lokalne: jeLokalne(request) }), 'Cache-Control': 'no-store' } },
  );
}
