import { bezHtml, rozdel, zloz } from '../../../../functions-lib/clanok.js';
import { GitHub, ZASTUPNY_OBRAZOK, naBase64 } from '../../../../functions-lib/github.js';
import { chyba } from '../../../../functions-lib/pristup.js';

const MAX_BAJTOV = 6 * 1024 * 1024;
const MAX_OBRAZKOV = 8;
const PRIPONY = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp' };

/** Adresy, ktoré smie editor použiť: voľné náhrady a obrázky zo zdrojov v stave voľné alebo tlačové. */
function povoleneObrazky(sprava) {
  const povolene = new Map();
  for (const a of sprava?.obrazky?.alternativy ?? []) {
    povolene.set(a.url, { kredit: [a.autor, a.povod === 'wikimedia' ? 'Wikimedia Commons' : 'Openverse'].filter(Boolean).join(' / '), licencia: a.licencia, popisok: a.nazov, stranka: a.stranka });
  }
  for (const p of sprava?.obrazky?.povodne ?? []) {
    if (p.zaradenie === 'volne' || p.zaradenie === 'tlacove') {
      // Zaradenie mohol zmeniť editor (/prava), potom platí kredit a licencia, ktoré zadal.
      povolene.set(p.url, { kredit: p.kredit || p.zdroj_clanku, licencia: p.licencia || (p.zaradenie === 'volne' ? 'voľná licencia' : 'tlačový materiál'), popisok: p.popisok || p.alt });
    }
  }
  return povolene;
}

async function stiahni(url) {
  const r = await fetch(url, { headers: { 'User-Agent': 'BitovinyBot/0.1 (+https://bitoviny.pages.dev/ako-to-funguje/)' } });
  if (!r.ok) throw new Error(`Obrázok sa nepodarilo stiahnuť (${r.status}).`);
  const typ = (r.headers.get('Content-Type') || '').split(';')[0].trim();
  if (!PRIPONY[typ]) throw new Error(`Nepodporovaný typ obrázka: ${typ || 'neznámy'}.`);
  const bajty = new Uint8Array(await r.arrayBuffer());
  if (bajty.length > MAX_BAJTOV) throw new Error('Obrázok je väčší než 6 MB.');
  return { bajty, pripona: PRIPONY[typ] };
}

/** Súbor obrázka patrí konceptu, ak leží v /obrazky/ a začína jeho slugom. Len také sa smú mazať. */
export function patriKonceptu(src, slug) {
  return typeof src === 'string' && src.startsWith(`/obrazky/${slug}`) && /^\/obrazky\/[a-z0-9-]+\.(jpg|png|webp)$/.test(src);
}

// Pridá obrázok do článku: voľnú náhradu, obrázok zo zdroja alebo vygenerovanú ilustráciu.
// umiestnenie „titulny“ nahradí titulný obrázok, „galeria“ pridá ďalší obrázok pod text.
export async function onRequestPost({ env, params, request, data }) {
  const vstup = await request.json();
  const umiestnenie = vstup.umiestnenie === 'galeria' ? 'galeria' : 'titulny';
  const gh = new GitHub(env, data.token);
  const k = await gh.koncept(Number(params.pr));
  const sprava = k.sprava ? JSON.parse((await gh.subor(k.sprava, k.vetva)).text) : null;

  let obrazok, meta;
  if (vstup.typ === 'url') {
    const info = povoleneObrazky(sprava).get(vstup.url);
    if (!info) return chyba(400, 'Tento obrázok nie je v ponuke redakčnej správy alebo je v stave chránené či nejasné. Najprv zmeňte jeho stav.');
    obrazok = await stiahni(vstup.url);
    meta = { kredit: info.kredit, licencia: info.licencia, popisok: bezHtml(vstup.popisok || info.popisok || ''), ai: false };
  } else if (vstup.typ === 'generovany') {
    if (typeof vstup.obrazokB64 !== 'string' || vstup.obrazokB64.length > MAX_BAJTOV * 1.4) return chyba(400, 'Chýba alebo je príliš veľký vygenerovaný obrázok.');
    const bajty = Uint8Array.from(atob(vstup.obrazokB64), (c) => c.charCodeAt(0));
    // JPEG začína bajtami FF D8, PNG bajtami 89 50.
    const pripona = bajty[0] === 0xff && bajty[1] === 0xd8 ? 'jpg' : bajty[0] === 0x89 && bajty[1] === 0x50 ? 'png' : null;
    if (!pripona) return chyba(400, 'Dáta nie sú obrázok JPEG ani PNG.');
    obrazok = { bajty, pripona };
    meta = { kredit: 'Bitoviny / FLUX.1-schnell', licencia: 'vygenerované AI', popisok: bezHtml(vstup.popisok || 'Ilustračný obrázok.'), ai: true };
  } else {
    return chyba(400, 'Neznámy typ obrázka.');
  }
  if (meta.popisok.length < 5) return chyba(400, 'Popisok obrázka musí mať aspoň 5 znakov.');

  const subor = await gh.subor(k.clanok, k.vetva);
  const { hlavicka, telo } = rozdel(subor.text);
  const galeria = hlavicka.galeria ?? [];
  if (umiestnenie === 'galeria' && galeria.length >= MAX_OBRAZKOV - 1) return chyba(400, `Článok môže mať najviac ${MAX_OBRAZKOV} obrázkov.`);

  // Každý obrázok má vlastný súbor, aby sa obrázky neprepisovali navzájom.
  const src = `/obrazky/${k.slug}-${Date.now().toString(36)}.${obrazok.pripona}`;
  await gh.zapis(`public${src}`, k.vetva, naBase64(obrazok.bajty), 'Obrázok k článku');

  const novy = {
    src,
    alt: bezHtml(vstup.alt || meta.popisok).slice(0, 200),
    popisok: meta.popisok.slice(0, 300),
    kredit: meta.kredit.slice(0, 150),
    licencia: meta.licencia.slice(0, 80),
    ai: meta.ai,
  };

  let nahradeny = null;
  if (umiestnenie === 'galeria') {
    hlavicka.galeria = [...galeria, novy];
  } else {
    nahradeny = hlavicka.obrazok?.src;
    hlavicka.obrazok = novy;
  }
  // Čerstvé sha: zápis obrázka medzitým posunul vetvu.
  const aktualny = await gh.subor(k.clanok, k.vetva);
  await gh.zapisText(k.clanok, k.vetva, zloz(hlavicka, telo), umiestnenie === 'galeria' ? 'Ďalší obrázok v článku' : 'Výber titulného obrázka', aktualny.sha);

  // Súbor nahradeného titulného obrázka už nič nepoužíva.
  if (nahradeny && nahradeny !== ZASTUPNY_OBRAZOK && patriKonceptu(nahradeny, k.slug)) await gh.zmazSubor(`public${nahradeny}`, k.vetva, 'Nepoužitý obrázok');
  return Response.json({ ok: true, obrazok: novy, umiestnenie });
}
