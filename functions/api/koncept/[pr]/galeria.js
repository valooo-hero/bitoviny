import { bezHtml, rozdel, zloz } from '../../../../functions-lib/clanok.js';
import { GitHub, ZASTUPNY_OBRAZOK } from '../../../../functions-lib/github.js';
import { chyba } from '../../../../functions-lib/pristup.js';
import { patriKonceptu } from './obrazok.js';

const ZASTUPNY = {
  src: ZASTUPNY_OBRAZOK,
  alt: 'Zástupný obrázok, čaká na výber editora',
  popisok: 'Obrázok čaká na výber editora.',
  kredit: 'Bitoviny',
  licencia: 'vlastná ilustrácia',
};

// Správa obrázkov, ktoré už v článku sú:
//   titulny    urobí z obrázka v galérii titulný, doterajší titulný sa presunie do galérie
//   odstranit  odstráni obrázok z článku a zmaže jeho súbor
//   popisok    zmení popisok obrázka
export async function onRequestPost({ env, params, request, data }) {
  const { akcia, src, popisok } = await request.json();
  const gh = new GitHub(env, data.token);
  const k = await gh.koncept(Number(params.pr));
  const subor = await gh.subor(k.clanok, k.vetva);
  const { hlavicka, telo } = rozdel(subor.text);
  const galeria = hlavicka.galeria ?? [];
  const jeTitulny = hlavicka.obrazok?.src === src;
  const index = galeria.findIndex((o) => o.src === src);
  if (!jeTitulny && index < 0) return chyba(400, 'Tento obrázok v článku nie je.');

  let sprava;
  let naZmazanie = null;
  if (akcia === 'titulny') {
    if (jeTitulny) return Response.json({ ok: true });
    const [novy] = galeria.splice(index, 1);
    if (hlavicka.obrazok && hlavicka.obrazok.src !== ZASTUPNY_OBRAZOK) galeria.unshift(hlavicka.obrazok);
    hlavicka.obrazok = novy;
    sprava = 'Zmena titulného obrázka';
  } else if (akcia === 'odstranit') {
    if (jeTitulny) {
      if (src === ZASTUPNY_OBRAZOK) return chyba(400, 'Zástupný obrázok sa odstrániť nedá.');
      // Titulným sa stane prvý obrázok z galérie; ak žiadny nie je, vráti sa zástupný.
      hlavicka.obrazok = galeria.shift() ?? ZASTUPNY;
    } else {
      galeria.splice(index, 1);
    }
    naZmazanie = src;
    sprava = 'Odstránený obrázok';
  } else if (akcia === 'popisok') {
    const novy = bezHtml(popisok || '').trim();
    if (novy.length < 5) return chyba(400, 'Popisok obrázka musí mať aspoň 5 znakov.');
    const ciel = jeTitulny ? hlavicka.obrazok : galeria[index];
    ciel.popisok = novy.slice(0, 300);
    ciel.alt = novy.slice(0, 200);
    sprava = 'Zmena popisku obrázka';
  } else {
    return chyba(400, 'Neznáma akcia.');
  }

  if (galeria.length) hlavicka.galeria = galeria;
  else delete hlavicka.galeria;
  await gh.zapisText(k.clanok, k.vetva, zloz(hlavicka, telo), sprava, subor.sha);
  if (naZmazanie && patriKonceptu(naZmazanie, k.slug)) await gh.zmazSubor(`public${naZmazanie}`, k.vetva, 'Nepoužitý obrázok');
  return Response.json({ ok: true });
}
