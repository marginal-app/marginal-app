import { afterEach, describe, expect, it } from 'vitest';
import {
  extractContext,
  quoteOffsetInBlock,
} from '@/entrypoints/content';
import {
  JSDOM_LOADS,
  type Fixture,
  joinedWrapText,
  loadCatalog,
  nodeAt,
  paintQuoteFromFlatten,
  rangeFromSelection,
  recordsFor,
  restoreFresh,
} from './mark-breakage-helpers';

const rows = loadCatalog().fixtures.filter(
  (fixture) => fixture.family === 'B_live_split',
);

function skipReason(fixture: Fixture): string | null {
  if (fixture.browserOnly) return 'browserOnly';
  if (!JSDOM_LOADS.has(fixture.load)) return `unsupported load: ${fixture.load}`;
  return null;
}

function runProductPath(fixture: Fixture, container: HTMLElement): HTMLElement | null {
  const recs = recordsFor(fixture);
  let last: HTMLElement | null = null;

  if (fixture.id === 'B02' || fixture.id === 'B11') {
    last = restoreFresh(container, recs[0] ?? fixture.record!);
    const quote =
      fixture.overlapSelectionAfterFirstPaint?.quote ??
      (fixture.id === 'B11' ? 'ck bro' : 'brown fox');
    last = paintQuoteFromFlatten(container, quote) ?? last;
    return last;
  }

  if (fixture.id === 'B04') {
    restoreFresh(container, fixture.record!);
    container.innerHTML = container.innerHTML;
    last = restoreFresh(container, fixture.record!);
    return last;
  }

  if (fixture.id === 'B05' || fixture.id === 'B12') {
    last = restoreFresh(container, fixture.record!);
    if (fixture.id === 'B12') {
      container.querySelectorAll('mark').forEach((mark) => {
        mark.replaceWith(...mark.childNodes);
      });
      container.normalize();
    }
    last = restoreFresh(container, fixture.record!);
    return last;
  }

  if (fixture.id === 'B08') {
    restoreFresh(container, recs[0]!);
    container.normalize();
    last = restoreFresh(container, recs[1]!);
    return last;
  }

  if (fixture.id === 'B09') {
    restoreFresh(container, recs[0]!);
    const target = nodeAt(container, fixture.mutation!.path!) as Text;
    target.insertData(fixture.mutation!.offset!, fixture.mutation!.text!);
    last = restoreFresh(container, recs[1]!);
    return last;
  }

  if (fixture.id === 'B10' || fixture.id === 'B14') {
    container.innerHTML = fixture.mutation!.html!;
    last = restoreFresh(container, fixture.record!);
    return last;
  }

  if (fixture.id === 'B13') {
    const built = rangeFromSelection(container, fixture.selection!);
    if (!built.range) throw new Error(`${fixture.id}: selection path failed`);
    const block = container.querySelector('p')!;
    const ctx = extractContext(
      block,
      fixture.selection!.quote ?? 'red fox',
      6,
      quoteOffsetInBlock(block, built.range),
    );
    last = restoreFresh(container, {
      quote: fixture.selection!.quote ?? 'red fox',
      prefix: ctx.prefix,
      suffix: ctx.suffix,
    });
    return last;
  }

  for (const rec of recs) {
    last = restoreFresh(container, rec);
  }
  return last;
}

afterEach(() => {
  document.body.innerHTML = '';
});

describe('B_live_split product-path harness', () => {
  it('runs every B row on the live content-script path (fresh flatten / wrap / scored restore)', () => {
    expect(rows).toHaveLength(14);
    expect(rows.filter((fixture) => skipReason(fixture))).toHaveLength(0);
    expect(rows.filter((fixture) => fixture.expect.restore === 'ok')).toHaveLength(14);
    expect(rows.filter((fixture) => fixture.expect.wrongSpan)).toHaveLength(0);
  });

  for (const fixture of rows) {
    const reason = skipReason(fixture);
    const run = reason ? it.skip : it;
    run(`${fixture.id} ${fixture.title}${reason ? ` — skipped (${reason})` : ''}`, () => {
      const container = document.createElement('div');
      container.innerHTML = fixture.html;
      document.body.append(container);

      const last = runProductPath(fixture, container);

      expect(last, fixture.id).toBeInstanceOf(HTMLElement);
      expect(fixture.expect.restore, fixture.id).toBe('ok');
      expect(fixture.expect.wrongSpan, fixture.id).toBe(false);
      if (fixture.expect.markCount !== null) {
        expect(container.querySelectorAll('mark').length, fixture.id).toBe(
          fixture.expect.markCount,
        );
      }
      if (fixture.id === 'B13') {
        expect(last?.previousSibling?.textContent, 'second red fox').toMatch(/and\s$/);
      }
      for (const check of fixture.oracle.checks) {
        if (check.joinedMarkText !== undefined) {
          expect(joinedWrapText(container)).toBe(check.joinedMarkText);
        }
        if (check.paintedText !== undefined) {
          expect(last?.textContent).toBe(check.paintedText);
        }
        if (check.query && check.count !== undefined) {
          expect(container.querySelectorAll(check.query).length).toBe(check.count);
        }
        if (check.query && check.minCount !== undefined) {
          expect(
            container.querySelectorAll(check.query).length,
          ).toBeGreaterThanOrEqual(check.minCount);
        }
      }
    });
  }
});
