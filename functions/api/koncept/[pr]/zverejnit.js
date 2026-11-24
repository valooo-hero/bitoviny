import { overTexty, rozdel, zloz } from '../../../../functions-lib/clanok.js';
import { prekazkaZverejnenia } from '../../../../functions-lib/duplicity.js';
import { GitHub, jeZastupnyObrazok } from '../../../../functions-lib/github.js';
import { chyba } from '../../../../functions-lib/pristup.js';

// Zverejnenie: doplní schválenie a čas, zlúči pull request do main a zmaže vetvu.
export async function onRequestPost({ env, params, request, data }) {
  const vstup = await request.json().catch(() => ({}));
  const gh = new GitHub(env, data.token);
  const k = await gh.koncept(Number(params.pr));
  const subor = await gh.subor(k.clanok, k.vetva);
  const { hlavicka, telo } = rozdel(subor.text);

  const prekazky = overTexty({ titulok: hlavicka.title, perex: hlavicka.perex, telo });
  if (jeZastupnyObrazok(hlavicka.obrazok.src)) prekazky.push('Článok nemá vybraný obrázok.');
  if (!hlavicka.obrazok.popisok || !hlavicka.obrazok.kredit || !hlavicka.obrazok.licencia) prekazky.push('Obrázku chýba popisok, kredit alebo licencia.');
  for (const o of hlavicka.galeria ?? []) {
    if (!o.popisok || !o.kredit || !o.licencia) prekazky.push('Niektorému obrázku v článku chýba popisok, kredit alebo licencia.');
  }
  if ([hlavicka.obrazok, ...(hlavicka.galeria ?? [])].some((o) => !jeZastupnyObrazok(o.src) && !/\.(jpg|webp)$/.test(o.src))) {
    prekazky.push('Článok obsahuje obrázok v nepodporovanom formáte. Nahrajte ho znova, aby sa previedol na JPG.');
  }
  if (vstup.potvrdenie !== true) prekazky.push('Chýba potvrdenie, že editor článok skontroloval.');
  if (prekazky.length) return chyba(400, prekazky.join(' '));

  const duplicita = await prekazkaZverejnenia(gh, k.clanok, hlavicka);
  if (duplicita) return chyba(409, duplicita);

  hlavicka.publikovane = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  hlavicka.redaktori = { ...(hlavicka.redaktori || {}), schvalil: 'sefredaktor' };
  const zapis = await gh.zapisText(k.clanok, k.vetva, zloz(hlavicka, telo), 'Schválenie editorom', subor.sha);

  await gh.zluc(k.pr.number, `Článok: ${hlavicka.title}`, zapis?.commit?.sha);
  await gh.zmazVetvu(k.vetva);
  return Response.json({ ok: true, clanok: `/clanok/${k.slug}/` });
}
