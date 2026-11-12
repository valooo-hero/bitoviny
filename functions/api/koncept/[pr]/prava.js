import { bezHtml } from '../../../../functions-lib/clanok.js';
import { GitHub } from '../../../../functions-lib/github.js';
import { chyba } from '../../../../functions-lib/pristup.js';

const ZARADENIA = ['volne', 'tlacove', 'chranene', 'nejasne'];

// Editor mení zaradenie obrázka zo zdroja podľa vlastného úsudku. Automatické
// pravidlá sú len odporúčanie: posledné slovo o právach má človek. Zmena sa
// zapíše do redakčnej správy aj s dôvodom a pôvodným zaradením, aby bolo
// dohľadateľné, kto a prečo rozhodol.
export async function onRequestPost({ env, params, request, data }) {
  const vstup = await request.json();
  const zaradenie = String(vstup.zaradenie || '');
  const dovod = bezHtml(vstup.dovod || '').trim();
  const kredit = bezHtml(vstup.kredit || '').trim();
  const licencia = bezHtml(vstup.licencia || '').trim();

  if (!ZARADENIA.includes(zaradenie)) return chyba(400, 'Neznáme zaradenie.');
  const pouzitelne = zaradenie === 'volne' || zaradenie === 'tlacove';
  if (pouzitelne) {
    if (dovod.length < 10) return chyba(400, 'Uveďte dôvod, prečo sa obrázok smie použiť (aspoň 10 znakov).');
    if (kredit.length < 2) return chyba(400, 'Uveďte autora alebo zdroj obrázka.');
    if (licencia.length < 2) return chyba(400, 'Uveďte licenciu alebo právny základ použitia.');
  }

  const gh = new GitHub(env, data.token);
  const k = await gh.koncept(Number(params.pr));
  if (!k.sprava) return chyba(400, 'Koncept nemá redakčnú správu.');
  const subor = await gh.subor(k.sprava, k.vetva);
  const sprava = JSON.parse(subor.text);
  const obrazok = (sprava.obrazky?.povodne ?? []).find((p) => p.url === vstup.url);
  if (!obrazok) return chyba(400, 'Tento obrázok nie je medzi obrázkami zo zdrojov.');

  // Pôvodné automatické zaradenie sa uchová pri prvej zmene.
  obrazok.automaticke_zaradenie ??= obrazok.zaradenie;
  obrazok.automaticky_dovod ??= obrazok.dovod;
  obrazok.zaradenie = zaradenie;
  obrazok.dovod = `Rozhodnutie editora: ${dovod || 'bez udania dôvodu'}`;
  if (kredit) obrazok.kredit = kredit.slice(0, 150);
  if (licencia) obrazok.licencia = licencia.slice(0, 80);
  obrazok.rozhodol_editor = { kto: data.login, kedy: new Date().toISOString().replace(/\.\d+Z$/, 'Z') };

  await gh.zapisText(k.sprava, k.vetva, JSON.stringify(sprava, null, 2) + '\n', `Práva k obrázku: ${zaradenie} (rozhodnutie editora)`, subor.sha);
  return Response.json({ ok: true, obrazok });
}
