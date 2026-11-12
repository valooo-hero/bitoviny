import {
  COOKIE_RELACIE,
  COOKIE_STAVU,
  PLATNOST_RELACIE_S,
  cookie,
  jeLokalne,
  nakonfigurovane,
  nastavCookie,
  povolenyPovod,
  vytvorRelaciu,
} from '../../../functions-lib/pristup.js';

function stranka(stav, sprava) {
  const html = `<!doctype html><html lang="sk"><meta charset="utf-8"><meta name="robots" content="noindex"><title>Prihlásenie</title>
<body style="font-family:system-ui;max-width:40rem;margin:4rem auto;padding:0 1rem"><h1>Prihlásenie sa nepodarilo</h1><p>${sprava}</p><p><a href="/admin/">Späť do redakcie</a></p></body></html>`;
  return new Response(html, { status: stav, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' } });
}

// Návrat z GitHubu: vymení kód za token, overí účet a založí reláciu.
export async function onRequestGet({ request, env }) {
  if (!nakonfigurovane(env)) return stranka(503, 'Redakčné rozhranie nie je nakonfigurované.');
  if (!povolenyPovod(request, env)) return stranka(403, 'Prihlásenie funguje len na produkčnej adrese.');

  const url = new URL(request.url);
  const kod = url.searchParams.get('code');
  const stav = url.searchParams.get('state');
  const ocakavany = cookie(request, COOKIE_STAVU);
  if (!kod || !stav || !ocakavany || stav !== ocakavany) return stranka(400, 'Neplatný alebo vypršaný pokus o prihlásenie. Skúste to znova.');

  const vymena = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'bitoviny-admin' },
    body: JSON.stringify({
      client_id: env.GITHUB_CLIENT_ID,
      client_secret: env.GITHUB_CLIENT_SECRET,
      code: kod,
      redirect_uri: `${url.origin}/api/auth/callback`,
    }),
  });
  const { access_token: token } = await vymena.json().catch(() => ({}));
  if (!token) return stranka(502, 'GitHub nevydal prístupový token.');

  const ja = await fetch('https://api.github.com/user', {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'User-Agent': 'bitoviny-admin' },
  });
  const { login } = await ja.json().catch(() => ({}));
  if (!login) return stranka(502, 'Nepodarilo sa zistiť prihlásený účet.');
  if (login.toLowerCase() !== String(env.ADMIN_GITHUB_LOGIN).toLowerCase()) {
    return stranka(403, 'Tento účet GitHubu nemá prístup do redakcie.');
  }

  const lokalne = jeLokalne(request);
  const hlavicky = new Headers({ Location: '/admin/', 'Cache-Control': 'no-store' });
  hlavicky.append('Set-Cookie', nastavCookie(COOKIE_RELACIE, await vytvorRelaciu(env, token, login), { maxAge: PLATNOST_RELACIE_S, lokalne }));
  hlavicky.append('Set-Cookie', nastavCookie(COOKIE_STAVU, '', { maxAge: 0, sameSite: 'Lax', lokalne }));
  return new Response(null, { status: 302, headers: hlavicky });
}
