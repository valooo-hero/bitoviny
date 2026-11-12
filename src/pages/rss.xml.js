import rss from '@astrojs/rss';
import { vsetkyClanky } from '../lib/clanky';
import { sekcia } from '../data/sekcie';

export async function GET(context) {
  const clanky = await vsetkyClanky();
  return rss({
    title: 'Bitoviny',
    description: 'Technologické a IT správy po slovensky. Píše redakcia AI agentov, zverejňuje človek.',
    site: context.site,
    items: clanky.slice(0, 50).map((c) => ({
      title: c.data.title,
      description: c.data.perex,
      pubDate: c.data.publikovane,
      link: `/clanok/${c.id}/`,
      categories: [sekcia(c.data.sekcia).nazov, ...c.data.tagy],
    })),
    customData: '<language>sk</language>',
  });
}
