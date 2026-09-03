// @ts-check
import { defineConfig } from 'astro/config';

import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://arison.me',
  integrations: [sitemap()],
  devToolbar: {
    enabled: false,
  },
  // The About page is the landing page, so the locale roots only redirect to
  // it. Production (Cloudflare) uses public/_redirects for a fast edge-level
  // HTTP 301. These config-level redirects are a fallback so the routes still
  // work (via meta refresh) in `astro dev`/`astro preview`, where Cloudflare's
  // _redirects file isn't processed.
  redirects: {
    '/': '/en/about/',
    '/en/': '/en/about/',
    '/zh/': '/zh/about/',
  },
});