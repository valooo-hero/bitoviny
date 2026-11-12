// Overenie, že požiadavku pustil Cloudflare Access. Bez platného tokenu API neodpovie.
//
// Access posiela v hlavičke Cf-Access-Jwt-Assertion podpísaný token. Podpis sa
// overuje verejnými kľúčmi tímu, takže hlavičku nemožno podvrhnúť ani na adrese
// náhľadového nasadenia, ktorú Access nemusí chrániť.

const certifikaty = new Map(); // tím -> { kluce, nacitane }

function b64urlNaBajty(text) {
  const b64 = text.replace(/-/g, '+').replace(/_/g, '/');
  const bin = atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4));
  return Uint8Array.from(bin, (c) => c.charCodeAt(0));
}

async function kluceTimu(tim) {
  const ulozene = certifikaty.get(tim);
  if (ulozene && Date.now() - ulozene.nacitane < 3600_000) return ulozene.kluce;
  const r = await fetch(`https://${tim}/cdn-cgi/access/certs`);
  if (!r.ok) throw new Error(`Certifikáty Access sa nepodarilo načítať (${r.status})`);
  const { keys } = await r.json();
  certifikaty.set(tim, { kluce: keys, nacitane: Date.now() });
  return keys;
}

export async function overToken(token, tim, aud) {
  const casti = token.split('.');
  if (casti.length !== 3) throw new Error('Token nemá tri časti');
  const hlavicka = JSON.parse(new TextDecoder().decode(b64urlNaBajty(casti[0])));
  const obsah = JSON.parse(new TextDecoder().decode(b64urlNaBajty(casti[1])));
  if (hlavicka.alg !== 'RS256') throw new Error('Nepodporovaný algoritmus');

  const jwk = (await kluceTimu(tim)).find((k) => k.kid === hlavicka.kid);
  if (!jwk) throw new Error('Neznámy podpisový kľúč');
  const kluc = await crypto.subtle.importKey('jwk', jwk, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['verify']);
  const platny = await crypto.subtle.verify(
    'RSASSA-PKCS1-v1_5',
    kluc,
    b64urlNaBajty(casti[2]),
    new TextEncoder().encode(`${casti[0]}.${casti[1]}`),
  );
  if (!platny) throw new Error('Neplatný podpis');

  const teraz = Math.floor(Date.now() / 1000);
  if (!obsah.exp || obsah.exp < teraz) throw new Error('Token vypršal');
  if (obsah.iss !== `https://${tim}`) throw new Error('Nesprávny vydavateľ');
  const publikum = Array.isArray(obsah.aud) ? obsah.aud : [obsah.aud];
  if (!publikum.includes(aud)) throw new Error('Token je pre inú aplikáciu');
  return obsah;
}

export function chyba(stav, sprava) {
  return Response.json({ chyba: sprava }, { status: stav });
}

/** Vráti null, ak je prístup v poriadku, inak odpoveď s chybou. */
export async function skontrolujPristup(request, env) {
  const host = new URL(request.url).hostname;
  // Lokálny vývoj: obídenie platí len na localhoste a len s výslovným nastavením.
  if (env.ADMIN_DEV_BYPASS === '1' && (host === 'localhost' || host === '127.0.0.1')) return null;

  if (!env.ACCESS_TEAM_DOMAIN || !env.ACCESS_AUD) {
    return chyba(503, 'Redakčné rozhranie nie je nakonfigurované (chýba ACCESS_TEAM_DOMAIN alebo ACCESS_AUD).');
  }
  const token = request.headers.get('Cf-Access-Jwt-Assertion');
  if (!token) return chyba(401, 'Chýba prihlásenie cez Cloudflare Access.');
  try {
    await overToken(token, env.ACCESS_TEAM_DOMAIN, env.ACCESS_AUD);
  } catch (e) {
    return chyba(401, `Prihlásenie sa nepodarilo overiť: ${e.message}`);
  }
  // Zápisy len z vlastnej stránky, nie z cudzieho webu cez prehliadač prihláseného editora.
  if (request.method !== 'GET') {
    const povod = request.headers.get('Origin');
    if (povod && new URL(povod).host !== new URL(request.url).host) return chyba(403, 'Požiadavka z cudzej stránky.');
  }
  return null;
}
