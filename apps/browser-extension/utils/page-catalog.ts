export type PageCatalogDraft = {
  title: string;
  description: string;
};

function metaContent(doc: Document, selectors: string[]): string {
  for (const selector of selectors) {
    const value = doc.querySelector(selector)?.getAttribute('content')?.trim();
    if (value) return value;
  }
  return '';
}

export function pageCatalogFromDocument(doc: Document): PageCatalogDraft {
  const title =
    doc.title.trim() || metaContent(doc, ['meta[property="og:title"]']);
  const description = metaContent(doc, [
    'meta[name="description"]',
    'meta[property="og:description"]',
  ]);
  return { title, description };
}
