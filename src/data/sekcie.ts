export const SEKCIE = [
  { id: 'ai', nazov: 'AI', popis: 'Umelá inteligencia, jazykové modely a ich dôsledky.' },
  { id: 'bezpecnost', nazov: 'Bezpečnosť', popis: 'Zraniteľnosti, útoky, ochrana údajov.' },
  { id: 'hardver', nazov: 'Hardvér', popis: 'Čipy, počítače, komponenty.' },
  { id: 'mobil', nazov: 'Mobil', popis: 'Telefóny, tablety, nositeľná elektronika.' },
  { id: 'softver', nazov: 'Softvér a vývoj', popis: 'Operačné systémy, nástroje, programovanie.' },
  { id: 'veda', nazov: 'Veda a vesmír', popis: 'Výskum, kozmonautika, energetika.' },
  { id: 'biznis', nazov: 'Biznis', popis: 'Firmy, akvizície, trh a regulácia.' },
  { id: 'slovensko-eu', nazov: 'Slovensko a EÚ', popis: 'Technológie doma a v Európe.' },
] as const;

export type SekciaId = (typeof SEKCIE)[number]['id'];

export const SEKCIA_IDS = SEKCIE.map((s) => s.id) as [SekciaId, ...SekciaId[]];

export function sekcia(id: string) {
  return SEKCIE.find((s) => s.id === id)!;
}
