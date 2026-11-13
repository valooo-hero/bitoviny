import { getCollection } from 'astro:content';

// Koncept z pipeline má zástupný obrázok, kým editor nevyberie skutočný.
export const ZASTUPNY_OBRAZOK = '/obrazky/zastupny.svg';

// Na produkčnej vetve sa nezverejní článok, ktorý neschválil človek alebo má
// zástupný obrázok, ani keby sa omylom dostal do main. V náhľadoch pull
// requestov a lokálne ho vidno.
const SKRY_KONCEPTY = process.env.CF_PAGES_BRANCH === 'main';

export async function vsetkyClanky() {
  const clanky = (await getCollection('clanky')).filter((c) => {
    const jeKoncept =
      c.data.obrazok.src === ZASTUPNY_OBRAZOK || (c.data.redaktori !== undefined && !c.data.redaktori.schvalil);
    // Stiahnutý článok sa nezobrazí nikde, ani v náhľadoch.
    return !c.data.stiahnute && !(SKRY_KONCEPTY && jeKoncept);
  });
  return clanky.sort((a, b) => b.data.publikovane.getTime() - a.data.publikovane.getTime());
}

const fmtDatum = new Intl.DateTimeFormat('sk-SK', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'Europe/Bratislava',
});
const fmtCas = new Intl.DateTimeFormat('sk-SK', {
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'Europe/Bratislava',
});

export function datum(d: Date) {
  return fmtDatum.format(d);
}

export function datumCas(d: Date) {
  return `${fmtDatum.format(d)}, ${fmtCas.format(d)}`;
}

export function slug(text: string) {
  return text
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}
