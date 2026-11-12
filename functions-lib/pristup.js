// Prihlásenie do redakčného rozhrania cez GitHub (OAuth).
//
// Editor sa prihlási svojím GitHub účtom. Rozhranie pustí len účet uvedený v
// ADMIN_GITHUB_LOGIN a s repozitárom potom pracuje jeho oprávnením, takže
// netreba žiadny trvalý token uložený na serveri.
//
// Relácia je šifrovaný cookie (AES-GCM). Kľúč sa odvodzuje z tajomstva OAuth
// aplikácie, ktoré pozná len server. Cookie je HttpOnly, skript na stránke ho
// neprečíta, a SameSite=Strict, cudzia stránka ho neodošle.

export const COOKIE_RELACIE = 'bitoviny_relacia';
export const COOKIE_STAVU = 'bitoviny_oauth_stav';
const PLATNOST_S = 8 * 3600;

export function chyba(stav, sprava, navyse = {}) {
  return Response.json({ chyba: sprava, ...navyse }, { status: stav });
}

const naB64url = (bajty) => btoa(String.fromCharCode(...bajty)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const zB64url = (text) => {
  const b64 = text.replace(/-/g, '+').replace(/_/g, '/');
  return Uint8Array.from(atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4)), (c) => c.charCodeAt(0));
};

async function kluc(env) {
  const material = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`bitoviny-relacia:${env.GITHUB_CLIENT_SECRET}`));
  return crypto.subtle.importKey('raw', material, 'AES-GCM', false, ['encrypt', 'decrypt']);
}

export async function zasifruj(env, data) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const sifra = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, await kluc(env), new TextEncoder().encode(JSON.stringify(data)));
  return `${naB64url(iv)}.${naB64url(new Uint8Array(sifra))}`;
}

export async function odsifruj(env, text) {
  const [iv, sifra] = String(text).split('.');
  if (!iv || !sifra) throw new Error('Poškodená relácia');
  const cisty = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: zB64url(iv) }, await kluc(env), zB64url(sifra));
  return JSON.parse(new TextDecoder().decode(cisty));
}

export function cookie(request, nazov) {
  const hlavicka = request.headers.get('Cookie') || '';
  for (const cast of hlavicka.split(';')) {
    const [k, ...v] = cast.trim().split('=');
    if (k === nazov) return v.join('=');
  }
  return null;
}

export function nastavCookie(nazov, hodnota, { maxAge, sameSite = 'Strict', lokalne = false } = {}) {
  const casti = [`${nazov}=${hodnota}`, 'Path=/', 'HttpOnly', `SameSite=${sameSite}`];
  if (!lokalne) casti.push('Secure');
  if (maxAge !== undefined) casti.push(`Max-Age=${maxAge}`);
  return casti.join('; ');
}

export function jeLokalne(request) {
  const host = new URL(request.url).hostname;
  return host === 'localhost' || host === '127.0.0.1';
}

/** Prihlásenie funguje len na produkčnej adrese (a lokálne), nie na náhľadových nasadeniach. */
export function povolenyPovod(request, env) {
  const povod = new URL(request.url).origin;
  return jeLokalne(request) || povod === (env.ADMIN_ORIGIN || 'https://bitoviny.pages.dev');
}

export function nakonfigurovane(env) {
  return Boolean(env.GITHUB_CLIENT_ID && env.GITHUB_CLIENT_SECRET && env.ADMIN_GITHUB_LOGIN);
}

export async function vytvorRelaciu(env, token, login) {
  return zasifruj(env, { token, login, exp: Math.floor(Date.now() / 1000) + PLATNOST_S });
}

export const PLATNOST_RELACIE_S = PLATNOST_S;

/**
 * Overí požiadavku na API. Vráti { token, login }, alebo { odmietnutie: Response }.
 * Bez konfigurácie API neodpovedá vôbec, takže nenastavené rozhranie nie je otvorené.
 */
export async function overPoziadavku(request, env) {
  // Lokálny vývoj: obídenie platí len na localhoste a len s výslovným nastavením.
  if (env.ADMIN_DEV_BYPASS === '1' && jeLokalne(request)) {
    if (!env.GITHUB_TOKEN) return { odmietnutie: chyba(503, 'Lokálny vývoj: v .dev.vars chýba GITHUB_TOKEN.') };
    return { token: env.GITHUB_TOKEN, login: 'lokalny-vyvoj' };
  }
  if (!nakonfigurovane(env)) {
    return { odmietnutie: chyba(503, 'Redakčné rozhranie nie je nakonfigurované (chýba OAuth aplikácia GitHubu).') };
  }
  if (!povolenyPovod(request, env)) return { odmietnutie: chyba(403, 'Redakčné rozhranie funguje len na produkčnej adrese.') };

  // Zápisy len z vlastnej stránky.
  if (request.method !== 'GET') {
    const povod = request.headers.get('Origin');
    if (!povod || povod !== new URL(request.url).origin) return { odmietnutie: chyba(403, 'Požiadavka z cudzej stránky.') };
  }

  const hodnota = cookie(request, COOKIE_RELACIE);
  if (!hodnota) return { odmietnutie: chyba(401, 'Neprihlásený.', { prihlasenie: '/api/auth/login' }) };
  let relacia;
  try {
    relacia = await odsifruj(env, hodnota);
  } catch {
    return { odmietnutie: chyba(401, 'Neplatná relácia.', { prihlasenie: '/api/auth/login' }) };
  }
  if (!relacia.exp || relacia.exp < Date.now() / 1000) return { odmietnutie: chyba(401, 'Relácia vypršala.', { prihlasenie: '/api/auth/login' }) };
  if (String(relacia.login).toLowerCase() !== String(env.ADMIN_GITHUB_LOGIN).toLowerCase()) {
    return { odmietnutie: chyba(403, 'Tento účet nemá prístup do redakcie.') };
  }
  return { token: relacia.token, login: relacia.login };
}
