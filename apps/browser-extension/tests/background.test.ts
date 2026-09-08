import { beforeEach, describe, expect, it } from 'vitest';
import { IDBFactory } from 'fake-indexeddb';
import { getHighlights, saveHighlight, updateComment } from '@/entrypoints/background';

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
    expect(record.id).toBeTruthy();
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

    const [fetched] = await getHighlights('a');
    expect(fetched?.comment).toBe('nice highlight');
  });

  it('rejects when updating a comment for a non-existent highlight', async () => {
    await expect(updateComment('missing-id', 'x')).rejects.toThrow();
  });
});
