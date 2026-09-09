import { beforeEach, describe, expect, it, vi } from 'vitest';
import { IDBFactory } from 'fake-indexeddb';
import { saveHighlight, getHighlights, getCatalog } from '@/utils/highlight-store';
import { runSync } from '@/utils/sync';

const UUID =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

beforeEach(async () => {
  globalThis.indexedDB = new IDBFactory();
  await browser.storage.local.clear();
  vi.unstubAllGlobals();
});

describe('runSync', () => {
  it('pulls remote rows then pushes local-only highlights and stores server stamps', async () => {
    await browser.storage.local.set({
      settings: { serverUrl: 'http://sync.test', apiToken: 'token' },
    });
    const local = await saveHighlight({
      pageKey: 'https://example.com/item',
      quote: 'local',
      prefix: '',
      suffix: '',
      color: '#fff',
      catalog: { title: 'Item', description: '' },
    });

    const remoteHighlight = {
      id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
      pageKey: 'https://example.com/other',
      quote: 'remote',
      prefix: '',
      suffix: '',
      color: '#fff',
      comment: '',
      createdAt: 10,
      updatedAt: 20,
    };
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes('/api/sync/pull')) {
        return new Response(
          JSON.stringify({ cursor: 20, highlights: [remoteHighlight], memberships: [] }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.includes('/api/sync/push')) {
        const body = JSON.parse(String(init?.body)) as {
          highlights: Array<{ id: string }>;
          memberships: Array<{ pageKey: string }>;
        };
        expect(body.highlights.map((row) => row.id)).toEqual([local.id]);
        return new Response(
          JSON.stringify({
            highlights: [
              {
                id: local.id,
                pageKey: local.pageKey,
                quote: local.quote,
                prefix: '',
                suffix: '',
                color: '#fff',
                comment: '',
                createdAt: local.createdAt,
                updatedAt: 50,
              },
            ],
            memberships: [
              {
                pageKey: 'https://example.com/item',
                bookmarked: false,
                title: 'Item',
                description: '',
                createdAt: 40,
                updatedAt: 50,
              },
            ],
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      throw new Error(`unexpected fetch ${url}`);
    });
    vi.stubGlobal('fetch', fetchMock);

    await runSync();

    const other = await getHighlights('https://example.com/other');
    expect(other).toHaveLength(1);
    expect(other[0]?.quote).toBe('remote');

    const [pushed] = await getHighlights('https://example.com/item');
    expect(pushed?.id).toMatch(UUID);
    expect(pushed?.updatedAt).toBe(50);

    const catalog = await getCatalog('https://example.com/item');
    expect(catalog?.updatedAt).toBe(50);
    expect(catalog?.title).toBe('Item');
  });
});
