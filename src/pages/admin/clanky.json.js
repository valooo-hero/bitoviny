import { getCollection } from 'astro:content';

// Zoznam všetkých článkov v repozitári pre redakčné rozhranie, vrátane stiahnutých.
// Vzniká pri zostavení webu, takže po zmene sa aktualizuje zhruba o minútu.
export async function GET() {
  const clanky = (await getCollection('clanky'))
    .sort((a, b) => b.data.publikovane.getTime() - a.data.publikovane.getTime())
    .map((c) => ({
      slug: c.id,
      titulok: c.data.title,
      sekcia: c.data.sekcia,
      publikovane: c.data.publikovane.toISOString(),
      aktualizovane: c.data.aktualizovane?.toISOString() ?? null,
      stiahnute: c.data.stiahnute,
      vzorovy: c.data.vzorovy,
    }));
  return new Response(JSON.stringify({ clanky }), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
}
