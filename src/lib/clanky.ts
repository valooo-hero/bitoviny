import { getCollection } from 'astro:content';

export async function vsetkyClanky() {
  const clanky = await getCollection('clanky');
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
