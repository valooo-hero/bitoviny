// Práca s obrázkami článku. Tá istá logika slúži konceptu (vetva pull requestu)
// aj zverejnenému či stiahnutému článku (vetva main). Líši sa len „cieľ“.
import { bezHtml, rozdel, zloz } from './clanok.js';
import { ZASTUPNY_OBRAZOK, naBase64 } from './github.js';
import { cestaClanku, teraz } from './uprava.js';

const MAX_BAJTOV = 6 * 1024 * 1024;
const MAX_OBRAZKOV = 8;
const PRIPONY = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp' };
const ZARADENIA = ['volne', 'tlacove', 'chranene', 'nejasne'];
const ZASTUPNY = {
  src: ZASTUPNY_OBRAZOK,
  alt: 'Zástupný obrázok, čaká na výber editora',
  popisok: 'Obrázok čaká na výber editora.',
  kredit: 'Bitoviny',
  licencia: 'vlastná ilustrácia',
};

export class ChybaVstupu extends Error {}

/** Cieľ pre koncept: súbory vo vetve pull requestu. */
export async function cielKonceptu(gh, params) {
  const k = await gh.koncept(Number(params.pr));
  return { vetva: k.vetva, clanok: k.clanok, sprava: k.sprava ?? null, slug: k.slug, zverejneny: false, pr: k.pr };
}

/** Cieľ pre zverejnený alebo stiahnutý článok: súbory vo vetve main. */
export async function cielClanku(gh, params) {
  const { slug, cesta } = cestaClanku(params);
  const sprava = `redakcia/spravy/${slug}.json`;
  return { vetva: 'main', clanok: cesta, sprava: (await gh.shaSuboru(sprava, 'main')) ? sprava : null, slug, zverejneny: true };
}

/** Adresa, z ktorej rozhranie načíta obrázok hneď po zápise, ešte pred zostavením webu. */
export function nahladObrazka(gh, vetva, src) {
  return src.startsWith('/obrazky/') && src !== ZASTUPNY_OBRAZOK
    ? `https://raw.githubusercontent.com/${gh.repo}/${encodeURIComponent(vetva).replace(/%2F/g, '/')}/public${src}`
    : src;
}

/** Všetky obrázky článku v poradí: titulný, potom galéria. */
export function zoznamObrazkov(gh, vetva, hlavicka) {
  return [
    { ...hlavicka.obrazok, titulny: true, nahlad: nahladObrazka(gh, vetva, hlavicka.obrazok.src) },
    ...(hlavicka.galeria ?? []).map((o) => ({ ...o, titulny: false, nahlad: nahladObrazka(gh, vetva, o.src) })),
  ];
}

/** Súbor patrí článku, ak leží v /obrazky/ a začína jeho slugom. Len také sa smú mazať. */
function patriClanku(src, slug) {
  return typeof src === 'string' && src.startsWith(`/obrazky/${slug}`) && /^\/obrazky\/[a-z0-9-]+\.(jpg|png|webp)$/.test(src);
}

async function nacitajSpravu(gh, ciel) {
  if (!ciel.sprava) return { sprava: null, sha: null };
  const subor = await gh.subor(ciel.sprava, ciel.vetva);
  return { sprava: JSON.parse(subor.text), sha: subor.sha };
}

/** Adresy, ktoré smie editor použiť: voľné náhrady a obrázky zo zdrojov v stave voľné alebo tlačové. */
function povoleneObrazky(sprava) {
  const povolene = new Map();
  for (const a of sprava?.obrazky?.alternativy ?? []) {
    povolene.set(a.url, { kredit: [a.autor, a.povod === 'wikimedia' ? 'Wikimedia Commons' : 'Openverse'].filter(Boolean).join(' / '), licencia: a.licencia, popisok: a.nazov });
  }
  for (const p of sprava?.obrazky?.povodne ?? []) {
    if (p.zaradenie === 'volne' || p.zaradenie === 'tlacove') {
      // Zaradenie mohol zmeniť editor, potom platí kredit a licencia, ktoré zadal.
      povolene.set(p.url, { kredit: p.kredit || p.zdroj_clanku, licencia: p.licencia || (p.zaradenie === 'volne' ? 'voľná licencia' : 'tlačový materiál'), popisok: p.popisok || p.alt });
    }
  }
  return povolene;
}

async function stiahni(url) {
  const r = await fetch(url, { headers: { 'User-Agent': 'BitovinyBot/0.1 (+https://bitoviny.pages.dev/ako-to-funguje/)' } });
  if (!r.ok) throw new ChybaVstupu(`Obrázok sa nepodarilo stiahnuť (${r.status}).`);
  const typ = (r.headers.get('Content-Type') || '').split(';')[0].trim();
  if (!PRIPONY[typ]) throw new ChybaVstupu(`Nepodporovaný typ obrázka: ${typ || 'neznámy'}.`);
  const bajty = new Uint8Array(await r.arrayBuffer());
  if (bajty.length > MAX_BAJTOV) throw new ChybaVstupu('Obrázok je väčší než 6 MB.');
  return { bajty, pripona: PRIPONY[typ] };
}

/** Typ súboru sa určuje z jeho prvých bajtov, nie z názvu ani z toho, čo tvrdí prehliadač. */
export function priponaZBajtov(b) {
  if (b[0] === 0xff && b[1] === 0xd8) return 'jpg';
  if (b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47) return 'png';
  if (b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 && b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50) return 'webp';
  return null;
}

function zBase64(text) {
  if (typeof text !== 'string' || !text.length) throw new ChybaVstupu('Chýbajú dáta obrázka.');
  if (text.length > MAX_BAJTOV * 1.4) throw new ChybaVstupu('Obrázok je väčší než 6 MB.');
  let bajty;
  try {
    bajty = Uint8Array.from(atob(text), (c) => c.charCodeAt(0));
  } catch {
    throw new ChybaVstupu('Dáta obrázka sú poškodené.');
  }
  const pripona = priponaZBajtov(bajty);
  if (!pripona) throw new ChybaVstupu('Súbor nie je obrázok JPEG, PNG ani WebP.');
  return { bajty, pripona };
}

/**
 * Pridá obrázok do článku. vstup.typ:
 *   url         voľná náhrada alebo obrázok zo zdroja z redakčnej správy
 *   generovany  ilustrácia z Workers AI
 *   vlastny     súbor nahraný editorom
 * vstup.umiestnenie „titulny“ nahradí titulný obrázok, „galeria“ pridá ďalší pod text.
 */
export async function pridajObrazok(gh, ciel, vstup) {
  const umiestnenie = vstup.umiestnenie === 'galeria' ? 'galeria' : 'titulny';
  let obrazok, meta;

  if (vstup.typ === 'url') {
    const { sprava } = await nacitajSpravu(gh, ciel);
    const info = povoleneObrazky(sprava).get(vstup.url);
    if (!info) throw new ChybaVstupu('Tento obrázok nie je v ponuke redakčnej správy alebo je v stave chránené či nejasné. Najprv zmeňte jeho stav.');
    obrazok = await stiahni(vstup.url);
    meta = { kredit: info.kredit, licencia: info.licencia, popisok: bezHtml(vstup.popisok || info.popisok || ''), ai: false };
  } else if (vstup.typ === 'generovany') {
    obrazok = zBase64(vstup.obrazokB64);
    meta = { kredit: 'Bitoviny / FLUX.1-schnell', licencia: 'vygenerované AI', popisok: bezHtml(vstup.popisok || 'Ilustračný obrázok.'), ai: true };
  } else if (vstup.typ === 'vlastny') {
    obrazok = zBase64(vstup.obrazokB64);
    // Pri vlastnom obrázku za pôvod a práva ručí editor, preto ich musí výslovne uviesť.
    meta = { kredit: bezHtml(vstup.kredit || '').trim(), licencia: bezHtml(vstup.licencia || '').trim(), popisok: bezHtml(vstup.popisok || ''), ai: vstup.ai === true };
    if (meta.kredit.length < 2) throw new ChybaVstupu('Uveďte autora alebo zdroj obrázka.');
    if (meta.licencia.length < 2) throw new ChybaVstupu('Uveďte licenciu alebo právny základ použitia.');
  } else {
    throw new ChybaVstupu('Neznámy typ obrázka.');
  }
  meta.popisok = meta.popisok.trim();
  if (meta.popisok.length < 5) throw new ChybaVstupu('Popisok obrázka musí mať aspoň 5 znakov.');

  const pred = rozdel((await gh.subor(ciel.clanok, ciel.vetva)).text);
  if (umiestnenie === 'galeria' && (pred.hlavicka.galeria ?? []).length >= MAX_OBRAZKOV - 1) throw new ChybaVstupu(`Článok môže mať najviac ${MAX_OBRAZKOV} obrázkov.`);

  // Každý obrázok má vlastný súbor, aby sa obrázky neprepisovali navzájom.
  const src = `/obrazky/${ciel.slug}-${Date.now().toString(36)}.${obrazok.pripona}`;
  await gh.zapis(`public${src}`, ciel.vetva, naBase64(obrazok.bajty), 'Obrázok k článku');

  const novy = {
    src,
    alt: bezHtml(vstup.alt || meta.popisok).slice(0, 200),
    popisok: meta.popisok.slice(0, 300),
    kredit: meta.kredit.slice(0, 150),
    licencia: meta.licencia.slice(0, 80),
    ai: meta.ai,
  };

  // Čerstvé načítanie: zápis obrázka medzitým posunul vetvu.
  const subor = await gh.subor(ciel.clanok, ciel.vetva);
  const { hlavicka, telo } = rozdel(subor.text);
  let nahradeny = null;
  if (umiestnenie === 'galeria') {
    hlavicka.galeria = [...(hlavicka.galeria ?? []), novy];
  } else {
    nahradeny = hlavicka.obrazok?.src;
    hlavicka.obrazok = novy;
  }
  if (ciel.zverejneny) hlavicka.aktualizovane = teraz();
  await gh.zapisText(ciel.clanok, ciel.vetva, zloz(hlavicka, telo), umiestnenie === 'galeria' ? 'Ďalší obrázok v článku' : 'Výber titulného obrázka', subor.sha);

  // Súbor nahradeného titulného obrázka už nič nepoužíva.
  if (nahradeny && patriClanku(nahradeny, ciel.slug)) await gh.zmazSubor(`public${nahradeny}`, ciel.vetva, 'Nepoužitý obrázok');
  return { obrazok: novy, umiestnenie };
}

/**
 * Správa obrázkov, ktoré už v článku sú:
 *   titulny    urobí z obrázka v galérii titulný, doterajší titulný sa presunie do galérie
 *   odstranit  odstráni obrázok z článku a zmaže jeho súbor
 *   popisok    zmení popisok obrázka
 */
export async function upravGaleriu(gh, ciel, { akcia, src, popisok }) {
  const subor = await gh.subor(ciel.clanok, ciel.vetva);
  const { hlavicka, telo } = rozdel(subor.text);
  const galeria = hlavicka.galeria ?? [];
  const jeTitulny = hlavicka.obrazok?.src === src;
  const index = galeria.findIndex((o) => o.src === src);
  if (!jeTitulny && index < 0) throw new ChybaVstupu('Tento obrázok v článku nie je.');

  let sprava;
  let naZmazanie = null;
  if (akcia === 'titulny') {
    if (jeTitulny) return;
    const [novy] = galeria.splice(index, 1);
    if (hlavicka.obrazok && hlavicka.obrazok.src !== ZASTUPNY_OBRAZOK) galeria.unshift(hlavicka.obrazok);
    hlavicka.obrazok = novy;
    sprava = 'Zmena titulného obrázka';
  } else if (akcia === 'odstranit') {
    if (jeTitulny) {
      if (src === ZASTUPNY_OBRAZOK) throw new ChybaVstupu('Zástupný obrázok sa odstrániť nedá.');
      // Zverejnený článok musí mať skutočný titulný obrázok, inak by z webu zmizol.
      if (ciel.zverejneny && !hlavicka.stiahnute && !galeria.length) throw new ChybaVstupu('Zverejnený článok musí mať titulný obrázok. Najprv pridajte iný, alebo článok stiahnite.');
      // Titulným sa stane prvý obrázok z galérie; ak žiadny nie je, vráti sa zástupný.
      hlavicka.obrazok = galeria.shift() ?? ZASTUPNY;
    } else {
      galeria.splice(index, 1);
    }
    naZmazanie = src;
    sprava = 'Odstránený obrázok';
  } else if (akcia === 'popisok') {
    const novy = bezHtml(popisok || '').trim();
    if (novy.length < 5) throw new ChybaVstupu('Popisok obrázka musí mať aspoň 5 znakov.');
    const obrazok = jeTitulny ? hlavicka.obrazok : galeria[index];
    obrazok.popisok = novy.slice(0, 300);
    obrazok.alt = novy.slice(0, 200);
    sprava = 'Zmena popisku obrázka';
  } else {
    throw new ChybaVstupu('Neznáma akcia.');
  }

  if (galeria.length) hlavicka.galeria = galeria;
  else delete hlavicka.galeria;
  if (ciel.zverejneny) hlavicka.aktualizovane = teraz();
  await gh.zapisText(ciel.clanok, ciel.vetva, zloz(hlavicka, telo), sprava, subor.sha);
  if (naZmazanie && patriClanku(naZmazanie, ciel.slug)) await gh.zmazSubor(`public${naZmazanie}`, ciel.vetva, 'Nepoužitý obrázok');
}

/**
 * Editor mení zaradenie obrázka zo zdroja podľa vlastného úsudku. Automatické
 * pravidlá sú len odporúčanie. Zmena sa zapíše do redakčnej správy aj s dôvodom,
 * pôvodným zaradením a menom editora.
 */
export async function zmenPrava(gh, ciel, vstup, login) {
  const zaradenie = String(vstup.zaradenie || '');
  const dovod = bezHtml(vstup.dovod || '').trim();
  const kredit = bezHtml(vstup.kredit || '').trim();
  const licencia = bezHtml(vstup.licencia || '').trim();

  if (!ZARADENIA.includes(zaradenie)) throw new ChybaVstupu('Neznáme zaradenie.');
  if (zaradenie === 'volne' || zaradenie === 'tlacove') {
    if (dovod.length < 10) throw new ChybaVstupu('Uveďte dôvod, prečo sa obrázok smie použiť (aspoň 10 znakov).');
    if (kredit.length < 2) throw new ChybaVstupu('Uveďte autora alebo zdroj obrázka.');
    if (licencia.length < 2) throw new ChybaVstupu('Uveďte licenciu alebo právny základ použitia.');
  }

  const { sprava, sha } = await nacitajSpravu(gh, ciel);
  if (!sprava) throw new ChybaVstupu('Článok nemá redakčnú správu.');
  const obrazok = (sprava.obrazky?.povodne ?? []).find((p) => p.url === vstup.url);
  if (!obrazok) throw new ChybaVstupu('Tento obrázok nie je medzi obrázkami zo zdrojov.');

  // Pôvodné automatické zaradenie sa uchová pri prvej zmene.
  obrazok.automaticke_zaradenie ??= obrazok.zaradenie;
  obrazok.automaticky_dovod ??= obrazok.dovod;
  obrazok.zaradenie = zaradenie;
  obrazok.dovod = `Rozhodnutie editora: ${dovod || 'bez udania dôvodu'}`;
  if (kredit) obrazok.kredit = kredit.slice(0, 150);
  if (licencia) obrazok.licencia = licencia.slice(0, 80);
  obrazok.rozhodol_editor = { kto: login, kedy: teraz() };

  await gh.zapisText(ciel.sprava, ciel.vetva, JSON.stringify(sprava, null, 2) + '\n', `Práva k obrázku: ${zaradenie} (rozhodnutie editora)`, sha);
  return obrazok;
}

/** Obalí obsluhu tak, aby chyba vstupu skončila ako 400 so zrozumiteľnou správou. */
export async function sChybami(fn) {
  try {
    return await fn();
  } catch (e) {
    if (e instanceof ChybaVstupu) return Response.json({ chyba: e.message }, { status: 400 });
    throw e;
  }
}
