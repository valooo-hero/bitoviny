export interface Redaktor {
  id: string;
  meno: string;
  rola: string;
  bio: string;
  motto: string;
  model: string;
  farba: string;
  clovek?: boolean;
}

// Avatary sú v public/avatary/<id>.webp (FLUX.1-schnell). Bez súboru sa zobrazia iniciály.
export const REDAKCIA: Redaktor[] = [
  {
    id: 'robert',
    meno: 'Róbert S. Sliedič',
    rola: 'Zberač správ',
    bio: 'Vstáva o piatej a kým si ostatní varia kávu, má prečítaných jedenásť portálov. Iniciály R. S. S. sú vraj náhoda. Neznáša, keď niekto zverejní tú istú správu trikrát pod iným titulkom.',
    motto: 'Kto skôr číta, ten skôr vie.',
    model: 'Groq, malý model + lokálne embeddingy',
    farba: '#2563eb',
  },
  {
    id: 'klara',
    meno: 'Klára Vesnicová',
    rola: 'Autorka',
    bio: 'Píše rýchlejšie, než stíhate čítať, a nikdy jej nevychladne čaj, lebo žiadny nepije. Z troch anglických článkov spraví jeden slovenský a tvrdí, že to nie je preklad, ale remeslo.',
    motto: 'Titulok má povedať, čo sa stalo. Nič viac.',
    model: 'Gemini Flash',
    farba: '#db2777',
  },
  {
    id: 'tomas',
    meno: 'Tomáš Neverný',
    rola: 'Factchecker',
    bio: 'Neverí nikomu, najmenej Kláre. Každé číslo si dohľadá v zdroji a ak ho nenájde, článok vráti. Robí to najviac dvakrát, potom to s povzdychom odovzdá šéfredaktorovi.',
    motto: 'Ukáž mi, kde to je napísané.',
    model: 'Gemini Flash-Lite',
    farba: '#d97706',
  },
  {
    id: 'ciarka',
    meno: 'Čiarka Ypsilonová',
    rola: 'Korektorka',
    bio: 'Vie, kde sa píše čiarka pred „a“, a nebojí sa to použiť. Vybrané slová ovláda naspamäť, lebo inak ani nevie. Čísla a mená v texte nechá na pokoji, to má od Tomáša zakázané.',
    motto: 'Rytmus vety pozná ten, kto ju prečíta nahlas.',
    model: 'Gemini Flash-Lite',
    farba: '#7c3aed',
  },
  {
    id: 'cyril',
    meno: 'Cyril Kopirajt',
    rola: 'Fotoeditor',
    bio: 'Každú fotku považuje za chránenú, kým mu niekto neukáže licenciu. Na večierkoch ho nikto nemá rád, na súdoch ho nikto nepozná. Tak to má byť.',
    motto: 'Bez kreditu ani pixel.',
    model: 'Pravidlá + Groq, malý model',
    farba: '#dc2626',
  },
  {
    id: 'fluxana',
    meno: 'Fluxana Štetcová',
    rola: 'Ilustrátorka',
    bio: 'Maľuje na počkanie, štyri kroky a hotovo. Čo jej editor napíše do zadania, to dostane, takže za šesť prstov na ruke nemôže len ona.',
    motto: 'Dobrý prompt je polovica obrazu.',
    model: 'FLUX.1-schnell, Cloudflare Workers AI',
    farba: '#0d9488',
  },
  {
    id: 'sefredaktor',
    meno: 'Šéfredaktor',
    rola: 'Jediný človek v redakcii',
    bio: 'Číta všetko, čo ostatní napíšu, a ako jediný smie stlačiť Zverejniť. Keď je v článku chyba, je to jeho chyba. Na rozdiel od kolegov potrebuje spať.',
    motto: 'Stroj navrhuje, človek zodpovedá.',
    model: 'Žiadny',
    farba: '#475569',
    clovek: true,
  },
];

export function redaktor(id: string) {
  return REDAKCIA.find((r) => r.id === id);
}
