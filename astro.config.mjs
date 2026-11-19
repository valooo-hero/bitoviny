import { readdirSync, readFileSync } from 'node:fs';
import { join, sep } from 'node:path';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { jeJpeg, jeWebp } from './functions-lib/format-obrazka.js';

// Stiahnuté články majú na svojej adrese len oznam a do sitemap nepatria.
const stiahnute = readdirSync('./content/clanky')
  .filter((f) => f.endsWith('.md') && /^stiahnute:\s*true\s*$/m.test(readFileSync(`./content/clanky/${f}`, 'utf8').split(/^---\s*$/m)[1] ?? ''))
  .map((f) => `/clanok/${f.replace(/\.md$/, '')}/`);

export default defineConfig({
  site: 'https://bitoviny.pages.dev',
  trailingSlash: 'always',
  integrations: [
    {
      name: 'kontrola-formatu-obrazkov',
      hooks: {
        'astro:build:start': () => {
          for (const subor of readdirSync('public', { recursive: true, withFileTypes: true })) {
            if (subor.isDirectory() || !/\.(jpe?g|png|webp|gif|avif|svg|ico|bmp|tiff?|heic)$/i.test(subor.name)) continue;
            const cesta = join(subor.parentPath, subor.name);
            const bajty = readFileSync(cesta);
            const jeClankovyWebp = cesta.startsWith(join('public', 'obrazky') + sep) && subor.name.endsWith('.webp') && jeWebp(bajty);
            if (!jeClankovyWebp && !(subor.name.endsWith('.jpg') && jeJpeg(bajty))) {
              throw new Error(`Nepodporovaný formát obrázka: ${cesta}`);
            }
          }
        },
      },
    },
    sitemap({ filter: (stranka) => !stranka.includes('/admin/') && !stiahnute.some((cesta) => stranka.endsWith(cesta)) }),
  ],
});
