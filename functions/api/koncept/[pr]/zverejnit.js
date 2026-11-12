import { overTexty, rozdel, zloz } from '../../../../functions-lib/clanok.js';
import { GitHub, ZASTUPNY_OBRAZOK } from '../../../../functions-lib/github.js';
import { chyba } from '../../../../functions-lib/pristup.js';

// Zverejnenie: doplní schválenie a čas, zlúči pull request do main a zmaže vetvu.
export async function onRequestPost({ env, params, request, data }) {
  const vstup = await request.json().catch(() => ({}));
  const gh = new GitHub(env, data.token);
  const k = await gh.koncept(Number(params.pr));
  const subor = await gh.subor(k.clanok, k.vetva);
  const { hlavicka, telo } = rozdel(subor.text);

  const prekazky = overTexty({ titulok: hlavicka.title, perex: hlavicka.perex, telo });
  if (hlavicka.obrazok.src === ZASTUPNY_OBRAZOK) prekazky.push('Článok nemá vybraný obrázok.');
  if (!hlavicka.obrazok.popisok || !hlavicka.obrazok.kredit || !hlavicka.obrazok.licencia) prekazky.push('Obrázku chýba popisok, kredit alebo licencia.');
  if (vstup.potvrdenie !== true) prekazky.push('Chýba potvrdenie, že editor článok skontroloval.');
  if (prekazky.length) return chyba(400, prekazky.join(' '));

  hlavicka.publikovane = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  hlavicka.redaktori = { ...(hlavicka.redaktori || {}), schvalil: 'sefredaktor' };
  const zapis = await gh.zapisText(k.clanok, k.vetva, zloz(hlavicka, telo), 'Schválenie editorom', subor.sha);

  await gh.zluc(k.pr.number, `Článok: ${hlavicka.title}`, zapis?.commit?.sha);
  await gh.zmazVetvu(k.vetva);
  return Response.json({ ok: true, clanok: `/clanok/${k.slug}/` });
}
