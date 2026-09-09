import { beforeEach, describe, expect, it } from 'vitest';
import { pageCatalogFromDocument } from '@/utils/page-catalog';

describe('pageCatalogFromDocument', () => {
  beforeEach(() => {
    document.title = '';
    document.head.innerHTML = '';
  });

  it('reads title and meta description', () => {
    document.head.innerHTML =
      '<title>The item</title><meta name="description" content="A page about the item.">';
    document.title = 'The item';

    expect(pageCatalogFromDocument(document)).toEqual({
      title: 'The item',
      description: 'A page about the item.',
    });
  });

  it('falls back to og tags', () => {
    document.title = '';
    document.head.innerHTML = [
      '<meta property="og:title" content="OG title">',
      '<meta property="og:description" content="OG description">',
    ].join('');

    expect(pageCatalogFromDocument(document)).toEqual({
      title: 'OG title',
      description: 'OG description',
    });
  });
});
