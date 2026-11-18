import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { jeJpeg } from './functions-lib/jpeg.js';

// Stiahnuté články majú na svojej adrese len oznam a do sitemap nepatria.
const stiahnute = readdirSync('./content/clanky')
  .filter((f) => f.endsWith('.md') && /^stiahnute:\s*true\s*$/m.test(readFileSync(`./content/clanky/${f}`, 'utf8').split(/^---\s*$/m)[1] ?? ''))
  .map((f) => `/clanok/${f.replace(/\.md$/, '')}/`);

export default defineConfig({
  site: 'https://bitoviny.pages.dev',
  trailingSlash: 'always',
  integrations: [
    {
      name: 'kontrola-jpg',
      hooks: {
        'astro:build:start': () => {
          for (const subor of readdirSync('public', { recursive: true, withFileTypes: true })) {
            if (subor.isDirectory() || !/\.(jpe?g|png|webp|gif|avif|svg|ico|bmp|tiff?|heic)$/i.test(subor.name)) continue;
            const cesta = join(subor.parentPath, subor.name);
            if (!subor.name.endsWith('.jpg') || !jeJpeg(readFileSync(cesta))) {
              throw new Error(`Obrázok musí byť vo formáte JPG: ${cesta}`);
            }
          }
        },
      },
    },
    sitemap({ filter: (stranka) => !stranka.includes('/admin/') && !stiahnute.some((cesta) => stranka.endsWith(cesta)) }),
  ],
});
