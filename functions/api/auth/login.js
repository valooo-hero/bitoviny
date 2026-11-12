import { COOKIE_STAVU, chyba, jeLokalne, nakonfigurovane, nastavCookie, povolenyPovod } from '../../../functions-lib/pristup.js';

// Začiatok prihlásenia: presmeruje na GitHub. Náhodný „stav“ v cookie chráni
// pred podvrhnutým návratom z prihlásenia.
export async function onRequestGet({ request, env }) {
  if (!nakonfigurovane(env)) return chyba(503, 'Redakčné rozhranie nie je nakonfigurované (chýba OAuth aplikácia GitHubu).');
  if (!povolenyPovod(request, env)) return chyba(403, 'Prihlásenie funguje len na produkčnej adrese.');

  const stav = [...crypto.getRandomValues(new Uint8Array(24))].map((b) => b.toString(16).padStart(2, '0')).join('');
  const ciel = new URL('https://github.com/login/oauth/authorize');
  ciel.searchParams.set('client_id', env.GITHUB_CLIENT_ID);
  ciel.searchParams.set('redirect_uri', `${new URL(request.url).origin}/api/auth/callback`);
  // Repozitár je verejný, preto stačí najužší rozsah, ktorý dovoľuje zápis.
  ciel.searchParams.set('scope', 'public_repo');
  ciel.searchParams.set('state', stav);
  ciel.searchParams.set('allow_signup', 'false');

  return new Response(null, {
    status: 302,
    headers: {
      Location: ciel.toString(),
      // Lax, lebo cookie sa musí odoslať pri návrate z github.com.
      'Set-Cookie': nastavCookie(COOKIE_STAVU, stav, { maxAge: 600, sameSite: 'Lax', lokalne: jeLokalne(request) }),
      'Cache-Control': 'no-store',
    },
  });
}
