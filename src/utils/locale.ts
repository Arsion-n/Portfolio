/** Locale segment for URL prefix: `/zh` only on zh pages; otherwise English is default. */
export function getLocalePrefix(pathname: string): '/en' | '/zh' {
  return pathname.startsWith('/zh/') || pathname === '/zh' ? '/zh' : '/en';
}

export function localizeHref(pathname: string, href: string): string {
  if (href.startsWith('#') || /^(https?:|mailto:|tel:)/.test(href)) return href;
  if (href.startsWith('/en/') || href.startsWith('/zh/')) return href;
  const prefix = getLocalePrefix(pathname);
  if (href === '/') return `${prefix}/`;
  return `${prefix}${href}`;
}

export function homeHrefFromPath(pathname: string): string {
  return `${getLocalePrefix(pathname)}/`;
}

/** Same path in English (for language switcher). */
export function enSwitchHref(pathname: string): string {
  if (pathname.startsWith('/zh/')) return pathname.replace('/zh/', '/en/');
  if (pathname === '/zh') return '/en/';
  if (pathname.startsWith('/en/') || pathname === '/en') {
    return pathname === '/en' ? '/en/' : pathname;
  }
  return '/en/';
}

/** Same path in Traditional Chinese (for language switcher). */
export function zhSwitchHref(pathname: string): string {
  if (pathname.startsWith('/en/')) return pathname.replace('/en/', '/zh/');
  if (pathname === '/en') return '/zh/';
  if (pathname.startsWith('/zh/') || pathname === '/zh') {
    return pathname === '/zh' ? '/zh/' : pathname;
  }
  return '/zh/';
}

/** Full URL for hreflang alternates (same path, other locale). */
export function alternatePageUrl(siteOrigin: string, pathname: string, lang: 'en' | 'zh'): string {
  if (pathname.startsWith('/zh/')) {
    return `${siteOrigin}${pathname.replace('/zh/', `/${lang}/`)}`;
  }
  if (pathname.startsWith('/en/')) {
    return `${siteOrigin}${pathname.replace('/en/', `/${lang}/`)}`;
  }
  if (pathname === '/zh' || pathname === '/zh/') {
    return `${siteOrigin}/${lang}/`;
  }
  return `${siteOrigin}/${lang}/`;
}
