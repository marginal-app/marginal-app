import { beforeEach, describe, expect, it } from 'vitest';
import { IDBFactory } from 'fake-indexeddb';
import {
  getCatalog,
  getHighlights,
  saveHighlight,
  updateComment,
} from '@/entrypoints/background';

beforeEach(() => {
  // Fresh, empty IndexedDB per test so records from one test can't leak
  // into another.
  globalThis.indexedDB = new IDBFactory();
});

describe('saveHighlight / getHighlights', () => {
  it('saves a highlight and retrieves it by pageKey', async () => {
    const draft = {
      pageKey: 'https://example.com/',
      quote: 'q',
      prefix: 'p',
      suffix: 's',
      color: '#fff',
    };

    const record = await saveHighlight(draft);
    expect(record.id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
    );
    expect(record.updatedAt).toBe(record.createdAt);
    expect(record.pageKey).toBe(draft.pageKey);

    const results = await getHighlights('https://example.com/');
    expect(results).toHaveLength(1);
    expect(results[0]?.id).toBe(record.id);
  });

  it('only returns highlights matching the given pageKey', async () => {
    await saveHighlight({
      pageKey: 'a',
      quote: 'q1',
      prefix: '',
      suffix: '',
      color: '#fff',
    });
    await saveHighlight({
      pageKey: 'b',
      quote: 'q2',
      prefix: '',
      suffix: '',
      color: '#fff',
    });

    const results = await getHighlights('a');
    expect(results).toHaveLength(1);
    expect(results[0]?.quote).toBe('q1');
  });

  it('stores origin, path, and query and keeps query in the pageKey', async () => {
    const record = await saveHighlight({
      pageKey: 'https://example.com/item?id=321#comments',
      quote: 'q',
      prefix: '',
      suffix: '',
      color: '#fff',
    });

    expect(record.pageKey).toBe('https://example.com/item?id=321');
    expect(record.origin).toBe('https://example.com');
    expect(record.path).toBe('/item');
    expect(record.query).toBe('?id=321');

    const same = await getHighlights('https://example.com/item?id=321');
    const other = await getHighlights('https://example.com/item?id=322');
    expect(same).toHaveLength(1);
    expect(other).toHaveLength(0);
  });

  it('migrates v1 records that only had pageKey', async () => {
    await new Promise<void>((resolve, reject) => {
      const request = indexedDB.open('marginal-highlights', 1);
      request.onupgradeneeded = () => {
        const store = request.result.createObjectStore('highlights', {
          keyPath: 'id',
        });
        store.createIndex('by_pageKey', 'pageKey', { unique: false });
        store.createIndex('by_createdAt', 'createdAt', { unique: false });
      };
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction('highlights', 'readwrite');
        tx.objectStore('highlights').add({
          id: 'old-1',
          pageKey: 'https://example.com/item',
          quote: 'q',
          prefix: '',
          suffix: '',
          color: '#fff',
          createdAt: 1,
        });
        tx.oncomplete = () => {
          db.close();
          resolve();
        };
        tx.onerror = () => reject(tx.error);
      };
      request.onerror = () => reject(request.error);
    });

    const results = await getHighlights('https://example.com/item');
    expect(results).toHaveLength(1);
    expect(results[0]?.origin).toBe('https://example.com');
    expect(results[0]?.path).toBe('/item');
    expect(results[0]?.query).toBe('');
    expect(results[0]?.id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
    );
    expect(results[0]?.updatedAt).toBe(1);
  });

  it('upserts catalog title and description with the highlight', async () => {
    await saveHighlight({
      pageKey: 'https://example.com/item?id=321',
      quote: 'q',
      prefix: '',
      suffix: '',
      color: '#fff',
      catalog: { title: 'The item', description: 'A page about the item.' },
    });

    const row = await getCatalog('https://example.com/item?id=321');
    expect(row?.title).toBe('The item');
    expect(row?.description).toBe('A page about the item.');
    expect(row?.origin).toBe('https://example.com');
    expect(row?.query).toBe('?id=321');
    expect(row?.bookmarked).toBe(false);
  });

  it('keeps catalog meta when a later highlight omits it', async () => {
    await saveHighlight({
      pageKey: 'https://example.com/item?id=321',
      quote: 'one',
      prefix: '',
      suffix: '',
      color: '#fff',
      catalog: { title: 'The item', description: 'Kept.' },
    });
    const first = await getCatalog('https://example.com/item?id=321');
    await saveHighlight({
      pageKey: 'https://example.com/item?id=321',
      quote: 'two',
      prefix: '',
      suffix: '',
      color: '#fff',
    });

    const row = await getCatalog('https://example.com/item?id=321');
    expect(row?.title).toBe('The item');
    expect(row?.description).toBe('Kept.');
    expect(row?.updatedAt).toBe(first?.updatedAt);
  });
});

describe('updateComment', () => {
  it('updates a comment on an existing highlight', async () => {
    const record = await saveHighlight({
      pageKey: 'a',
      quote: 'q',
      prefix: '',
      suffix: '',
      color: '#fff',
    });

    const updated = await updateComment(record.id, 'nice highlight');
    expect(updated.comment).toBe('nice highlight');
    expect(updated.updatedAt).toBeGreaterThan(record.updatedAt);

    const [fetched] = await getHighlights('a');
    expect(fetched?.comment).toBe('nice highlight');
    expect(fetched?.updatedAt).toBe(updated.updatedAt);
  });

  it('rejects when updating a comment for a non-existent highlight', async () => {
    await expect(updateComment('missing-id', 'x')).rejects.toThrow();
  });
});
