import { readdirSync, readFileSync } from 'node:fs';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Stiahnuté články majú na svojej adrese len oznam a do sitemap nepatria.
const stiahnute = readdirSync('./content/clanky')
  .filter((f) => f.endsWith('.md') && /^stiahnute:\s*true\s*$/m.test(readFileSync(`./content/clanky/${f}`, 'utf8').split(/^---\s*$/m)[1] ?? ''))
  .map((f) => `/clanok/${f.replace(/\.md$/, '')}/`);

export default defineConfig({
  site: 'https://bitoviny.pages.dev',
  trailingSlash: 'always',
  integrations: [
    sitemap({ filter: (stranka) => !stranka.includes('/admin/') && !stiahnute.some((cesta) => stranka.endsWith(cesta)) }),
  ],
});
