import { rozdel, zloz } from '../../../functions-lib/clanok.js';
import { GitHub, ZASTUPNY_OBRAZOK } from '../../../functions-lib/github.js';
import { chyba } from '../../../functions-lib/pristup.js';
import { spracujVstup, zapisDoHlavicky } from '../../../functions-lib/uprava.js';

function cisloPr(params) {
  const n = Number(params.pr);
  if (!Number.isInteger(n) || n <= 0) throw new Error('Neplatné číslo konceptu.');
  return n;
}

// Detail konceptu: článok, redakčná správa a adresa náhľadu.
export async function onRequestGet({ env, params, data }) {
  const gh = new GitHub(env, data.token);
  const k = await gh.koncept(cisloPr(params));
  const { hlavicka, telo } = rozdel((await gh.subor(k.clanok, k.vetva)).text);
  let sprava = null;
  if (k.sprava) sprava = JSON.parse((await gh.subor(k.sprava, k.vetva)).text);
  // Obrázky sú zatiaľ len vo vetve konceptu, preto ich rozhranie číta priamo z GitHubu.
  const nahlad = (src) =>
    src.startsWith('/obrazky/') && src !== ZASTUPNY_OBRAZOK
      ? `https://raw.githubusercontent.com/${gh.repo}/${encodeURIComponent(k.vetva).replace(/%2F/g, '/')}/public${src}`
      : src;
  const obrazokUrl = nahlad(hlavicka.obrazok.src);
  // Všetky obrázky článku v poradí: titulný, potom galéria.
  const obrazky = [
    { ...hlavicka.obrazok, titulny: true, nahlad: obrazokUrl },
    ...(hlavicka.galeria ?? []).map((o) => ({ ...o, titulny: false, nahlad: nahlad(o.src) })),
  ];
  return Response.json({
    pr: k.pr.number,
    slug: k.slug,
    vetva: k.vetva,
    prUrl: k.pr.html_url,
    hlavicka,
    telo,
    sprava,
    obrazokUrl,
    obrazky,
    cakaNaObrazok: hlavicka.obrazok.src === ZASTUPNY_OBRAZOK,
  });
}

// Úprava textu editorom.
export async function onRequestPut({ env, params, request, data }) {
  const vysledok = spracujVstup(await request.json());
  if (vysledok.chyby) return chyba(400, vysledok.chyby.join(' '));

  const gh = new GitHub(env, data.token);
  const k = await gh.koncept(cisloPr(params));
  const subor = await gh.subor(k.clanok, k.vetva);
  const { hlavicka } = rozdel(subor.text);
  zapisDoHlavicky(hlavicka, vysledok.polia);
  await gh.zapisText(k.clanok, k.vetva, zloz(hlavicka, vysledok.polia.telo), 'Úprava konceptu editorom', subor.sha);
  return Response.json({ ok: true });
}
