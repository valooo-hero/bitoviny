import { rozdel, zloz } from '../../../../functions-lib/clanok.js';
import { GitHub } from '../../../../functions-lib/github.js';
import { cestaClanku, teraz } from '../../../../functions-lib/uprava.js';

// Stiahnutie článku zo zverejnenia a jeho vrátenie. Súbor ostáva v repozitári
// s príznakom stiahnute, web ho po zostavení prestane zobrazovať. História
// repozitára aj obrázok v priečinku public ostávajú verejne dostupné.
export async function onRequestPost({ env, params, request, data }) {
  const { stiahnut } = await request.json();
  const gh = new GitHub(env, data.token);
  const { slug, cesta } = cestaClanku(params);
  const subor = await gh.subor(cesta, 'main');
  const { hlavicka, telo } = rozdel(subor.text);

  if (stiahnut === true) {
    hlavicka.stiahnute = true;
    hlavicka.stiahnute_kedy = teraz();
  } else if (stiahnut === false) {
    delete hlavicka.stiahnute;
    delete hlavicka.stiahnute_kedy;
  } else {
    return Response.json({ chyba: 'Chýba voľba stiahnut (true alebo false).' }, { status: 400 });
  }

  const sprava = stiahnut ? `Stiahnuté zo zverejnenia: ${hlavicka.title}` : `Vrátené na web: ${hlavicka.title}`;
  await gh.zapisText(cesta, 'main', zloz(hlavicka, telo), sprava, subor.sha);
  return Response.json({ ok: true, stiahnute: stiahnut, slug });
}
