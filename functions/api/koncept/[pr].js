import { bezHtml, overTexty, rozdel, zloz } from '../../../functions-lib/clanok.js';
import { GitHub, ZASTUPNY_OBRAZOK } from '../../../functions-lib/github.js';
import { chyba } from '../../../functions-lib/pristup.js';

function cisloPr(params) {
  const n = Number(params.pr);
  if (!Number.isInteger(n) || n <= 0) throw new Error('Neplatné číslo konceptu.');
  return n;
}

// Detail konceptu: článok, redakčná správa a adresa náhľadu.
export async function onRequestGet({ env, params }) {
  const gh = new GitHub(env);
  const k = await gh.koncept(cisloPr(params));
  const { hlavicka, telo } = rozdel((await gh.subor(k.clanok, k.vetva)).text);
  let sprava = null;
  if (k.sprava) sprava = JSON.parse((await gh.subor(k.sprava, k.vetva)).text);
  // Obrázok je zatiaľ len vo vetve konceptu, preto ho rozhranie číta priamo z GitHubu.
  const obrazokUrl = hlavicka.obrazok.src.startsWith('/obrazky/') && hlavicka.obrazok.src !== ZASTUPNY_OBRAZOK
    ? `https://raw.githubusercontent.com/${gh.repo}/${encodeURIComponent(k.vetva).replace(/%2F/g, '/')}/public${hlavicka.obrazok.src}`
    : hlavicka.obrazok.src;
  return Response.json({
    pr: k.pr.number,
    slug: k.slug,
    vetva: k.vetva,
    prUrl: k.pr.html_url,
    hlavicka,
    telo,
    sprava,
    obrazokUrl,
    cakaNaObrazok: hlavicka.obrazok.src === ZASTUPNY_OBRAZOK,
  });
}

// Úprava textu editorom.
export async function onRequestPut({ env, params, request }) {
  const vstup = await request.json();
  const texty = {
    titulok: bezHtml(vstup.titulok).trim(),
    perex: bezHtml(vstup.perex).trim(),
    telo: bezHtml(vstup.telo).trim(),
  };
  const chyby = overTexty(texty);
  if (chyby.length) return chyba(400, chyby.join(' '));

  const gh = new GitHub(env);
  const k = await gh.koncept(cisloPr(params));
  const subor = await gh.subor(k.clanok, k.vetva);
  const { hlavicka } = rozdel(subor.text);
  hlavicka.title = texty.titulok;
  hlavicka.perex = texty.perex;
  await gh.zapisText(k.clanok, k.vetva, zloz(hlavicka, texty.telo), 'Úprava textu editorom', subor.sha);
  return Response.json({ ok: true });
}
