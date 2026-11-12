import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://bitoviny.pages.dev',
  trailingSlash: 'always',
  integrations: [sitemap({ filter: (stranka) => !stranka.includes('/admin/') })],
});
