// Ochrana pri ručnom schvaľovaní konceptov vrátane tých zo starších behov.
import { rozdel } from './clanok.js';
import { jeZastupnyObrazok } from './github.js';

const OKNO_MS = 7 * 24 * 60 * 60 * 1000;
const SLEDOVANIE = new Set(['fbclid', 'gclid', 'dclid', 'msclkid', 'mc_cid', 'mc_eid', 'igshid']);

function normalizujUrl(hodnota) {
  let url;
  try {
    url = new URL(hodnota);
  } catch {
    return '';
  }
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) return '';
  for (const kluc of [...url.searchParams.keys()]) {
    const male = kluc.toLowerCase();
    if (male.startsWith('utm_') || SLEDOVANIE.has(male)) url.searchParams.delete(kluc);
  }
  const parametre = [...url.searchParams].sort(([klucA, hodnotaA], [klucB, hodnotaB]) =>
    (klucA > klucB) - (klucA < klucB) || (hodnotaA > hodnotaB) - (hodnotaA < hodnotaB)
  );
  const query = new URLSearchParams(parametre).toString();
  const host = url.host.replace(/^www\./, '');
  return host + url.pathname.replace(/\/+$/, '') + (query ? '?' + query : '');
}

function zdroje(hlavicka) {
  return new Set((hlavicka.zdroje ?? []).map((zdroj) => normalizujUrl(zdroj.url)).filter(Boolean));
}

export async function prekazkaZverejnenia(gh, cesta, hlavicka, teraz) {
  const clanky = await gh.suboryClankov();
  teraz ??= Date.now();
  if (clanky.some((clanok) => clanok.path === cesta)) return 'Na tejto adrese už existuje článok.';
  const kandidatskeZdroje = zdroje(hlavicka);
  if (!kandidatskeZdroje.size) return null;

  for await (const { path, text } of gh.textyClankov(clanky)) {
    const { hlavicka: stare } = rozdel(text);
    if (jeZastupnyObrazok(stare.obrazok?.src) || (stare.redaktori && !stare.redaktori.schvalil)) continue;
    const publikovane = Date.parse(stare.publikovane);
    if (!Number.isFinite(publikovane)) throw new Error('V archíve je článok bez platného dátumu zverejnenia.');
    if (publikovane > teraz || publikovane < teraz - OKNO_MS) continue;
    const povodneZdroje = zdroje(stare);
    if ([...kandidatskeZdroje].every((url) => povodneZdroje.has(url))) {
      const slug = path.slice('content/clanky/'.length, -'.md'.length);
      return 'Všetky zdroje už použil článok „' + stare.title + '“ (/clanok/' + slug + '/).';
    }
  }
  return null;
}
