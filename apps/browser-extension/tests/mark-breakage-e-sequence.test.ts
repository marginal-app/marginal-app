import { afterEach, describe, expect, it } from 'vitest';
import {
  findToolbarBlock,
  paintRange,
  shouldPersistHighlight,
} from '@/entrypoints/content';
import {
  DEFAULT_COLOR,
  JSDOM_LOADS,
  type Fixture,
  loadCatalog,
  rangeFromSelection,
} from './mark-breakage-helpers';

const rows = loadCatalog().fixtures.filter(
  (fixture) => fixture.family === 'E_sequence',
);

function skipReason(fixture: Fixture): string | null {
  if (fixture.browserOnly) return 'browserOnly';
  if (!JSDOM_LOADS.has(fixture.load)) return `unsupported load: ${fixture.load}`;
  if (!fixture.selection) return 'no selection';
  return null;
}

afterEach(() => {
  document.body.innerHTML = '';
});

describe('E_sequence toolbar + persist harness', () => {
  it('has live expects for every E row', () => {
    expect(rows).toHaveLength(5);
    expect(rows.filter((fixture) => skipReason(fixture))).toHaveLength(0);
    expect(rows.filter((fixture) => fixture.expect.toolbar === 'shown')).toHaveLength(5);
    expect(rows.filter((fixture) => fixture.expect.ghostRecord)).toHaveLength(0);
  });

  for (const fixture of rows) {
    const reason = skipReason(fixture);
    const run = reason ? it.skip : it;
    run(`${fixture.id} ${fixture.title}${reason ? ` — skipped (${reason})` : ''}`, () => {
      const container = document.createElement('div');
      container.innerHTML = fixture.html;
      document.body.append(container);

      const built = rangeFromSelection(container, fixture.selection!);
      expect(built.range, `${fixture.id} ${built.error}`).not.toBeNull();

      const block = findToolbarBlock(built.range!);
      if (fixture.expect.toolbar === 'shown') {
        expect(block, fixture.id).not.toBeNull();
      } else if (fixture.expect.toolbar === 'hidden') {
        expect(block, fixture.id).toBeNull();
      }

      const mark = paintRange(built.range!.cloneRange(), DEFAULT_COLOR);
      if (fixture.expect.paint === 'first-mark') {
        expect(mark, fixture.id).toBeInstanceOf(HTMLElement);
        expect(shouldPersistHighlight(mark)).toBe(true);
      } else if (fixture.expect.paint === 'null') {
        expect(mark, fixture.id).toBeNull();
        expect(shouldPersistHighlight(mark)).toBe(false);
      }

      expect(fixture.expect.ghostRecord, fixture.id).toBe(false);
      if (fixture.expect.markCount !== null) {
        expect(container.querySelectorAll('mark').length, fixture.id).toBe(
          fixture.expect.markCount,
        );
      }
    });
  }

  it('does not persist SAVE when paint returns null', () => {
    expect(shouldPersistHighlight(null)).toBe(false);
  });
});
