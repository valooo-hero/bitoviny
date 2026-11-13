import { bezHtml, rozdel, zloz } from '../../../functions-lib/clanok.js';
import { GitHub } from '../../../functions-lib/github.js';
import { chyba } from '../../../functions-lib/pristup.js';
import { cestaClanku, spracujVstup, teraz, zapisDoHlavicky } from '../../../functions-lib/uprava.js';

// Zverejnený článok z vetvy main.
export async function onRequestGet({ env, params, data }) {
  const gh = new GitHub(env, data.token);
  const { slug, cesta } = cestaClanku(params);
  const { hlavicka, telo } = rozdel((await gh.subor(cesta, 'main')).text);
  let sprava = null;
  try {
    sprava = JSON.parse((await gh.subor(`redakcia/spravy/${slug}.json`, 'main')).text);
  } catch {
    // vzorové a ručne písané články redakčnú správu nemajú
  }
  return Response.json({ slug, hlavicka, telo, sprava, obrazokUrl: hlavicka.obrazok?.src, zverejneny: true });
}

// Úprava zverejneného článku. Zapisuje sa priamo do main, web sa potom sám znovu zostaví.
// Zmena je na webe viditeľná ako „Aktualizované“; poznámka k oprave sa zobrazí pod článkom
// a na stránke Opravy.
export async function onRequestPut({ env, params, request, data }) {
  const vstup = await request.json();
  const vysledok = spracujVstup(vstup);
  if (vysledok.chyby) return chyba(400, vysledok.chyby.join(' '));

  const gh = new GitHub(env, data.token);
  const { slug, cesta } = cestaClanku(params);
  const subor = await gh.subor(cesta, 'main');
  const { hlavicka } = rozdel(subor.text);
  zapisDoHlavicky(hlavicka, vysledok.polia);
  hlavicka.aktualizovane = teraz();

  const oprava = bezHtml(vstup.oprava || '').trim();
  if (oprava) {
    if (oprava.length < 10) return chyba(400, 'Poznámka k oprave musí mať aspoň 10 znakov.');
    hlavicka.opravy = [...(hlavicka.opravy || []), { datum: hlavicka.aktualizovane, text: oprava.slice(0, 500) }];
  }

  await gh.zapisText(cesta, 'main', zloz(hlavicka, vysledok.polia.telo), `Úprava článku: ${hlavicka.title}`, subor.sha);
  return Response.json({ ok: true, clanok: `/clanok/${slug}/` });
}
