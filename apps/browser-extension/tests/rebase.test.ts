import { describe, expect, it } from 'vitest';
import { rebaseRows, rowsToPush } from '@/utils/rebase';

describe('rebaseRows', () => {
  it('inserts remote-only rows and keeps local-only rows', () => {
    const merged = rebaseRows(
      [{ id: 'local', updatedAt: 1, value: 'L' }],
      [{ id: 'remote', updatedAt: 2, value: 'R' }],
      (row) => row.id,
    );
    expect(merged).toEqual(
      expect.arrayContaining([
        { id: 'local', updatedAt: 1, value: 'L' },
        { id: 'remote', updatedAt: 2, value: 'R' },
      ]),
    );
  });

  it('takes remote when it is newer', () => {
    const merged = rebaseRows(
      [{ id: 'a', updatedAt: 1, value: 'old' }],
      [{ id: 'a', updatedAt: 2, value: 'new' }],
      (row) => row.id,
    );
    expect(merged).toEqual([{ id: 'a', updatedAt: 2, value: 'new' }]);
  });

  it('keeps local when it is newer or equal', () => {
    const merged = rebaseRows(
      [{ id: 'a', updatedAt: 5, value: 'mine' }],
      [{ id: 'a', updatedAt: 5, value: 'theirs' }],
      (row) => row.id,
    );
    expect(merged).toEqual([{ id: 'a', updatedAt: 5, value: 'mine' }]);
  });
});

describe('rowsToPush', () => {
  it('sends never-acked rows and rows newer than the last server stamp', () => {
    const local = [
      { id: 'new', updatedAt: 1 },
      { id: 'dirty', updatedAt: 4 },
      { id: 'clean', updatedAt: 3 },
    ];
    const push = rowsToPush(local, { dirty: 3, clean: 3 }, (row) => row.id);
    expect(push.map((row) => row.id)).toEqual(['new', 'dirty']);
  });
});
