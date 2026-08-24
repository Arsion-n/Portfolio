// @ts-check
import { defineConfig } from 'astro/config';

import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://arison.me',
  integrations: [sitemap()],
  // Production (Cloudflare) uses public/_redirects for a fast edge-level
  // HTTP 301 on '/'. This config-level redirect is a fallback so the route
  // still works (via meta refresh) in `astro dev`/`astro preview`, where
  // Cloudflare's _redirects file isn't processed.
  redirects: {
    '/': '/en/',
  },
});