// Štatistiky redakcie počítané pri zostavení webu z repozitára: zverejnené články
// v content/clanky a redakčné správy v redakcia/spravy. Žiadne externé API.
import { getCollection, type CollectionEntry } from 'astro:content';

type Sprava = {
  slug: string;
  factcheck?: { kola?: { kolo: number; tvrdeni: number; potvrdenych: number; chyb: number }[]; otvorene_nalezy?: { zavaznost: string }[] } | null;
  korektura?: { upravy?: { stav: string }[]; chyba?: string } | null;
  obrazky?: { povodne?: { zaradenie: string; automaticke_zaradenie?: string }[] } | null;
  text_agentov?: { titulok: string; perex: string; telo: string };
};

const spravy = import.meta.glob<Sprava>('/redakcia/spravy/*.json', { eager: true, import: 'default' });

export function spravaClanku(slug: string): Sprava | undefined {
  return spravy[`/redakcia/spravy/${slug}.json`];
}

const slova = (text: string) => text.replace(/[#*_>`[\]()|-]/g, ' ').split(/\s+/).filter(Boolean);

/** Podiel slov, ktoré editor zmenil, pridal alebo vypustil (0 až 1). Počíta sa cez najdlhšiu spoločnú podpostupnosť slov. */
export function podielZmien(pred: string, po: string): number {
  const a = slova(pred);
  const b = slova(po);
  if (!a.length && !b.length) return 0;
  let predosly = new Array(b.length + 1).fill(0);
  for (let i = 1; i <= a.length; i++) {
    const riadok = new Array(b.length + 1).fill(0);
    for (let j = 1; j <= b.length; j++) {
      riadok[j] = a[i - 1] === b[j - 1] ? predosly[j - 1] + 1 : Math.max(predosly[j], riadok[j - 1]);
    }
    predosly = riadok;
  }
  const spolocne = predosly[b.length];
  return 1 - (2 * spolocne) / (a.length + b.length);
}

type TypObrazka = 'ai' | 'volny' | 'vlastny';
function typObrazka(o: CollectionEntry<'clanky'>['data']['obrazok']): TypObrazka {
  if (o.ai) return 'ai';
  if (/Wikimedia|Openverse/i.test(o.kredit) || /CC|public domain/i.test(o.licencia)) return 'volny';
  return 'vlastny';
}

export interface StatClanku {
  slug: string;
  titulok: string;
  slovAgentov: number | null;
  slovZverejnenych: number;
  zasahEditora: number | null; // podiel zmenených slov v tele
  zmenenyTitulok: boolean | null;
  zmenenyPerex: boolean | null;
  tvrdeni: number | null;
  kolFactchecku: number | null;
  chybVPrvomKole: number | null;
  otvorenychNalezov: number | null;
  upravVykonanych: number;
  upravZamietnutych: number;
  obrazkovZoZdrojov: number;
  obrazkovZmenilEditor: number;
  obrazkovChranenych: number;
  typTitulnehoObrazka: TypObrazka;
  obrazkovSpolu: number;
  zdrojov: number;
  oprav: number;
}

/** Štatistika jedného článku. Vzorové články nemajú redakčnú správu, preto časť polí ostane prázdna. */
export function statistikaClanku(c: CollectionEntry<'clanky'>): StatClanku {
  const d = c.data;
  const s = spravaClanku(c.id);
  const telo = c.body ?? '';
  const kola = s?.factcheck?.kola ?? [];
  const upravy = s?.korektura?.upravy ?? [];
  const povodne = s?.obrazky?.povodne ?? [];
  const agenti = s?.text_agentov;
  return {
    slug: c.id,
    titulok: d.title,
    slovAgentov: agenti ? slova(agenti.telo).length : null,
    slovZverejnenych: slova(telo).length,
    zasahEditora: agenti ? podielZmien(agenti.telo, telo) : null,
    zmenenyTitulok: agenti ? agenti.titulok.trim() !== d.title.trim() : null,
    zmenenyPerex: agenti ? agenti.perex.trim() !== d.perex.trim() : null,
    tvrdeni: kola.length ? kola[kola.length - 1].tvrdeni : null,
    kolFactchecku: s?.factcheck ? kola.length : null,
    chybVPrvomKole: kola.length ? kola[0].chyb : null,
    otvorenychNalezov: s?.factcheck ? (s.factcheck.otvorene_nalezy ?? []).filter((n) => n.zavaznost === 'chyba').length : null,
    upravVykonanych: upravy.filter((u) => u.stav === 'vykonana').length,
    upravZamietnutych: upravy.filter((u) => u.stav !== 'vykonana').length,
    obrazkovZoZdrojov: povodne.length,
    obrazkovZmenilEditor: povodne.filter((p) => p.automaticke_zaradenie && p.automaticke_zaradenie !== p.zaradenie).length,
    obrazkovChranenych: povodne.filter((p) => (p.automaticke_zaradenie ?? p.zaradenie) === 'chranene' || (p.automaticke_zaradenie ?? p.zaradenie) === 'nejasne').length,
    typTitulnehoObrazka: typObrazka(d.obrazok),
    obrazkovSpolu: 1 + d.galeria.length,
    zdrojov: d.zdroje.length,
    oprav: d.opravy.length,
  };
}

const priemer = (cisla: number[]) => (cisla.length ? cisla.reduce((a, b) => a + b, 0) / cisla.length : null);
const sucet = (cisla: number[]) => cisla.reduce((a, b) => a + b, 0);

/** Súhrn za celú redakciu: len články, ktoré pripravili agenti a schválil človek. */
export async function statistikyRedakcie() {
  const vsetky = await getCollection('clanky');
  const agentove = vsetky.filter((c) => !c.data.vzorovy && c.data.redaktori?.schvalil && spravaClanku(c.id));
  const zverejnene = agentove.filter((c) => !c.data.stiahnute);
  const st = zverejnene.map(statistikaClanku);
  const sTextom = st.filter((x) => x.zasahEditora !== null);

  return {
    clankov: st.length,
    stiahnutych: agentove.length - zverejnene.length,
    // Autorka
    priemerSlovAgentov: priemer(sTextom.map((x) => x.slovAgentov!)),
    priemerSlovZverejnenych: priemer(st.map((x) => x.slovZverejnenych)),
    // Editor
    priemernyZasah: priemer(sTextom.map((x) => x.zasahEditora!)),
    bezZasahu: sTextom.filter((x) => x.zasahEditora! < 0.01).length,
    zmenenychTitulkov: sTextom.filter((x) => x.zmenenyTitulok).length,
    clankovSTextom: sTextom.length,
    oprav: sucet(st.map((x) => x.oprav)),
    // Factchecker
    tvrdeni: sucet(st.map((x) => x.tvrdeni ?? 0)),
    vratenych: st.filter((x) => (x.kolFactchecku ?? 0) > 1).length,
    chybVPrvomKole: sucet(st.map((x) => x.chybVPrvomKole ?? 0)),
    neuzavretych: st.filter((x) => (x.otvorenychNalezov ?? 0) > 0).length,
    // Korektorka
    upravVykonanych: sucet(st.map((x) => x.upravVykonanych)),
    upravZamietnutych: sucet(st.map((x) => x.upravZamietnutych)),
    // Zberač
    priemerZdrojov: priemer(st.map((x) => x.zdrojov)),
    jednozdrojovych: st.filter((x) => x.zdrojov < 2).length,
    // Fotoeditor a ilustrátorka
    obrazkovZoZdrojov: sucet(st.map((x) => x.obrazkovZoZdrojov)),
    obrazkovChranenych: sucet(st.map((x) => x.obrazkovChranenych)),
    obrazkovZmenilEditor: sucet(st.map((x) => x.obrazkovZmenilEditor)),
    titulnychAi: st.filter((x) => x.typTitulnehoObrazka === 'ai').length,
    titulnychVolnych: st.filter((x) => x.typTitulnehoObrazka === 'volny').length,
    titulnychVlastnych: st.filter((x) => x.typTitulnehoObrazka === 'vlastny').length,
    obrazkovSpolu: sucet(st.map((x) => x.obrazkovSpolu)),
    clanky: st,
  };
}

export const percento = (x: number | null) => (x === null ? '–' : `${Math.round(x * 100)} %`);
export const cislo = (x: number | null, desatinne = 0) => (x === null ? '–' : x.toLocaleString('sk-SK', { maximumFractionDigits: desatinne }));

/** Slovenský tvar podľa čísla: 1 chyba, 2 až 4 chyby, 0 a 5 a viac chýb. */
export const sklon = (n: number, jeden: string, dva: string, pat: string) => `${n} ${n === 1 ? jeden : n >= 2 && n <= 4 ? dva : pat}`;
