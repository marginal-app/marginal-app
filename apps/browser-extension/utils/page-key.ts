export type PageIdentity = {
  origin: string;
  path: string;
  query: string;
  pageKey: string;
};

/** origin + path + search. Hash is not part of the key. */
export function canonicalizePageKey(input: string): string {
  return pageKeyFromHref(input) ?? input;
}

export function pageKeyFromHref(href: string): string | null {
  try {
    const url = new URL(href);
    return url.origin + url.pathname + url.search;
  } catch {
    return null;
  }
}

export function pageKeyFromLocation(loc: {
  origin: string;
  pathname: string;
  search: string;
}): string {
  return loc.origin + loc.pathname + loc.search;
}

export function pageIdentityFromPageKey(pageKey: string): PageIdentity {
  const canonical = canonicalizePageKey(pageKey);
  try {
    const url = new URL(canonical);
    return {
      origin: url.origin,
      path: url.pathname,
      query: url.search,
      pageKey: canonical,
    };
  } catch {
    return { origin: '', path: canonical, query: '', pageKey: canonical };
  }
}
