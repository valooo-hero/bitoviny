// Čítanie a zápis článku v Markdowne s YAML hlavičkou.
import { parse, stringify } from 'yaml';

export function rozdel(markdown) {
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(markdown);
  if (!m) throw new Error('Článok nemá hlavičku.');
  return { hlavicka: parse(m[1]), telo: m[2].trim() };
}

export function zloz(hlavicka, telo) {
  return `---\n${stringify(hlavicka, { lineWidth: 0 })}---\n\n${telo.trim()}\n`;
}

/** Markdown na webe vykresľuje aj surové HTML, preto ho z textu od editora aj modelu odstraňujeme. */
export function bezHtml(text) {
  return String(text ?? '')
    .replace(/<\/?[a-zA-Z!][^>]{0,500}>/g, '')
    // Odkazy smú viesť len na web, e-mail alebo v rámci stránky (žiadne javascript: a podobne).
    .replace(/\]\(\s*(?!https?:|mailto:|\/|#)(?:[^()]|\([^()]*\))*\)/gi, ']()');
}

export function overTexty({ titulok, perex, telo }) {
  const chyby = [];
  if (titulok.length < 10 || titulok.length > 110) chyby.push(`Titulok má ${titulok.length} znakov, povolených je 10 až 110.`);
  if (perex.length < 40 || perex.length > 320) chyby.push(`Perex má ${perex.length} znakov, povolených je 40 až 320.`);
  if (telo.length < 200) chyby.push('Telo článku je príliš krátke.');
  return chyby;
}
