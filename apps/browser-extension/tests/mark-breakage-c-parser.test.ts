import { afterEach, describe, expect, it } from 'vitest';
import { flattenText, paintRange } from '@/entrypoints/content';
import {
  JSDOM_LOADS,
  type Fixture,
  joinedWrapText,
  loadCatalog,
  rangeFromSelection,
  restoreFresh,
} from './mark-breakage-helpers';

const PATH_UNUSABLE = new Set(['C05', 'C10', 'C13', 'C16', 'C17']);

const rows = loadCatalog().fixtures.filter(
  (fixture) => fixture.family === 'C_parser_x',
);

function skipReason(fixture: Fixture): string | null {
  if (fixture.browserOnly) return 'browserOnly';
  if (!JSDOM_LOADS.has(fixture.load)) return `unsupported load: ${fixture.load}`;
  if (PATH_UNUSABLE.has(fixture.id)) {
    return 'recovered-path-unusable in jsdom';
  }
  return null;
}

afterEach(() => {
  document.body.innerHTML = '';
});

describe('C_parser_x recovered-tree harness', () => {
  it('classifies jsdom-capable C rows without inventing authored paths', () => {
    expect(rows).toHaveLength(22);
    expect(rows.filter((fixture) => fixture.browserOnly).map((f) => f.id)).toEqual([
      'C14',
      'C15',
      'C21',
    ]);
    expect(rows.filter((fixture) => PATH_UNUSABLE.has(fixture.id)).map((f) => f.id)).toEqual([
      'C05',
      'C10',
      'C13',
      'C16',
      'C17',
    ]);
    const runnable = rows.filter((fixture) => skipReason(fixture) === null);
    expect(runnable.filter((f) => f.expect.paint === 'first-mark' || f.expect.restore === 'ok').map((f) => f.id)).toEqual([
      'C01',
      'C02',
      'C03',
      'C04',
      'C06',
      'C08',
      'C09',
      'C11',
      'C12',
      'C18',
      'C19',
      'C20',
      'C22',
    ]);
    expect(runnable.filter((f) => f.expect.restore === 'null').map((f) => f.id)).toEqual([
      'C07',
    ]);
  });

  for (const fixture of rows) {
    const reason = skipReason(fixture);
    const run = reason ? it.skip : it;
    run(`${fixture.id} ${fixture.title}${reason ? ` — skipped (${reason})` : ''}`, () => {
      const container = document.createElement('div');
      container.innerHTML = fixture.html;
      document.body.append(container);

      if (fixture.ops.includes('restore') || fixture.record) {
        const last = restoreFresh(container, fixture.record!);
        if (fixture.expect.restore === 'null') {
          expect(last, fixture.id).toBeNull();
        } else {
          expect(last, fixture.id).toBeInstanceOf(HTMLElement);
        }
        if (fixture.expect.markCount !== null) {
          expect(container.querySelectorAll('mark').length, fixture.id).toBe(
            fixture.expect.markCount,
          );
        }
        for (const check of fixture.oracle.checks) {
          if (check.flatten !== undefined) {
            expect(flattenText(container).text).toBe(check.flatten);
          }
          if (check.paintedText !== undefined) {
            expect(last?.textContent).toBe(check.paintedText);
          }
          if (check.fn === 'resolveAndPaint' && check.returns === null) {
            expect(last).toBeNull();
          }
        }
        return;
      }

      const selection =
        fixture.selection ?? fixture.parserRecovery?.afterParseSelection;
      expect(selection, fixture.id).toBeTruthy();
      let built = rangeFromSelection(container, selection!);
      if (!built.range && fixture.parserRecovery?.afterParseSelection) {
        built = rangeFromSelection(
          container,
          fixture.parserRecovery.afterParseSelection,
        );
      }
      expect(built.range, `${fixture.id} ${built.error}`).not.toBeNull();

      const mark = paintRange(built.range!, '#FFF3B0');
      if (fixture.expect.paint === 'first-mark') {
        expect(mark, fixture.id).toBeInstanceOf(HTMLElement);
      } else if (fixture.expect.paint === 'null') {
        expect(mark, fixture.id).toBeNull();
      }
      if (fixture.expect.markCount !== null) {
        expect(container.querySelectorAll('mark').length, fixture.id).toBe(
          fixture.expect.markCount,
        );
      }
      for (const check of fixture.oracle.checks) {
        if (check.joinedMarkText !== undefined) {
          expect(joinedWrapText(container)).toBe(check.joinedMarkText);
        }
        if (check.query && check.count !== undefined) {
          expect(container.querySelectorAll(check.query).length).toBe(check.count);
        }
      }
    });
  }
});
