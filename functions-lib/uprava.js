// Spoločné overenie a zápis polí článku, ktoré editor mení v rozhraní.
import { bezHtml, overTexty } from './clanok.js';

export const SEKCIE = ['ai', 'bezpecnost', 'hardver', 'mobil', 'softver', 'veda', 'biznis', 'slovensko-eu'];

/**
 * Očistí a overí vstup z formulára. Vráti { polia } alebo { chyby }.
 * Zdroje, tagy a sekcia sú nepovinné: čo vo vstupe nie je, to sa nemení.
 */
export function spracujVstup(vstup) {
  const polia = {
    titulok: bezHtml(vstup.titulok).trim(),
    perex: bezHtml(vstup.perex).trim(),
    telo: bezHtml(vstup.telo).trim(),
  };
  const chyby = overTexty(polia);

  if (vstup.sekcia !== undefined) {
    if (!SEKCIE.includes(vstup.sekcia)) chyby.push('Neznáma sekcia.');
    polia.sekcia = vstup.sekcia;
  }
  if (vstup.tagy !== undefined) {
    if (!Array.isArray(vstup.tagy)) chyby.push('Tagy majú byť zoznam.');
    else polia.tagy = [...new Set(vstup.tagy.map((t) => bezHtml(t).trim()).filter(Boolean))].slice(0, 8);
  }
  if (vstup.zdroje !== undefined) {
    if (!Array.isArray(vstup.zdroje)) chyby.push('Zdroje majú byť zoznam.');
    else {
      polia.zdroje = vstup.zdroje.map((z) => ({ nazov: bezHtml(z?.nazov).trim().slice(0, 200), url: String(z?.url ?? '').trim() }));
      if (!polia.zdroje.length) chyby.push('Článok musí mať aspoň jeden zdroj.');
      for (const z of polia.zdroje) {
        if (z.nazov.length < 2) chyby.push('Každý zdroj musí mať názov.');
        let adresa;
        try { adresa = new URL(z.url); } catch { adresa = null; }
        if (!adresa || !['http:', 'https:'].includes(adresa.protocol)) chyby.push(`Neplatná adresa zdroja: ${z.url.slice(0, 80) || '(prázdna)'}`);
      }
    }
  }
  return chyby.length ? { chyby } : { polia };
}

export function zapisDoHlavicky(hlavicka, polia) {
  hlavicka.title = polia.titulok;
  hlavicka.perex = polia.perex;
  if (polia.sekcia) hlavicka.sekcia = polia.sekcia;
  if (polia.tagy) hlavicka.tagy = polia.tagy;
  if (polia.zdroje) hlavicka.zdroje = polia.zdroje;
  return hlavicka;
}

export const teraz = () => new Date().toISOString().replace(/\.\d+Z$/, 'Z');

/** Overí identifikátor článku z adresy a vráti cestu k súboru v repozitári. */
export function cestaClanku(params) {
  const slug = String(params.slug || '');
  if (!/^[a-z0-9][a-z0-9-]{2,120}$/.test(slug)) throw new Error('Neplatný identifikátor článku.');
  return { slug, cesta: `content/clanky/${slug}.md` };
}
