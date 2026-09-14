import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, describe, expect, it } from 'vitest';
import { flattenText, resolveAndPaint } from '@/entrypoints/content';
import type { HighlightRecord } from '@/utils/highlight-messages';

const catalogPath = join(
  dirname(fileURLToPath(import.meta.url)),
  'fixtures/mark-breakage/phase1-break-fixtures.json',
);

const DEFAULT_COLOR = '#FFF3B0';
const JSDOM_LOADS = new Set(['container-innerHTML']);

type PartialRecord = {
  id?: string;
  quote?: string;
  prefix?: string;
  suffix?: string;
  color?: string;
};

type OracleCheck = {
  query?: string;
  count?: number;
  minCount?: number;
  fn?: string;
  returns?: unknown;
  joinedMarkText?: string;
  paintedText?: string;
  flatten?: string;
  firstMark?: string;
  secondMark?: string;
  any?: OracleCheck[];
};

type Fixture = {
  id: string;
  family: string;
  title: string;
  html: string;
  load: string;
  record: PartialRecord | null;
  records?: PartialRecord[];
  expect: {
    paint: string | null;
    markCount: number | null;
    restore: string | null;
    wrongSpan: boolean;
  };
  oracle: {
    kind: string;
    checks: OracleCheck[];
  };
  browserOnly: boolean;
};

type Catalog = { fixtures: Fixture[] };

function asRecord(partial: PartialRecord): HighlightRecord {
  return {
    id: partial.id ?? 'id',
    pageKey: '',
    origin: '',
    path: '',
    query: '',
    quote: partial.quote ?? '',
    prefix: partial.prefix ?? '',
    suffix: partial.suffix ?? '',
    color: partial.color ?? DEFAULT_COLOR,
    createdAt: 0,
    updatedAt: 0,
  };
}

function recordsFor(fixture: Fixture): PartialRecord[] {
  if (fixture.records?.length) return fixture.records;
  if (fixture.record) return [fixture.record];
  return [];
}

function skipReason(fixture: Fixture): string | null {
  if (fixture.browserOnly) return 'browserOnly';
  if (!JSDOM_LOADS.has(fixture.load)) return `unsupported load: ${fixture.load}`;
  if (recordsFor(fixture).length === 0) return 'no record';
  return null;
}

function wrapMarks(root: ParentNode): HTMLElement[] {
  return [...root.querySelectorAll<HTMLElement>('mark[data-paint-group]')];
}

function joinedWrapText(root: ParentNode): string {
  return wrapMarks(root)
    .map((mark) => mark.textContent ?? '')
    .join('');
}

function assertOracleCheck(
  check: OracleCheck,
  ctx: {
    container: HTMLElement;
    lastMark: HTMLElement | null;
    flatten: string;
  },
): void {
  if (check.any) {
    const passed = check.any.some((inner) => {
      try {
        assertOracleCheck(inner, ctx);
        return true;
      } catch {
        return false;
      }
    });
    expect(passed, 'oracle.any').toBe(true);
    return;
  }

  if (check.joinedMarkText !== undefined) {
    expect(joinedWrapText(ctx.container)).toBe(check.joinedMarkText);
  }

  if (check.paintedText !== undefined) {
    const pieces = wrapMarks(ctx.container);
    const lastGroup = ctx.lastMark?.dataset.paintGroup;
    const lastText = pieces
      .filter((mark) => mark.dataset.paintGroup === lastGroup)
      .map((mark) => mark.textContent ?? '')
      .join('');
    expect(lastText).toBe(check.paintedText);
  }

  if (check.flatten !== undefined) {
    expect(ctx.flatten).toBe(check.flatten);
  }

  if (check.firstMark !== undefined) {
    const marks = [...ctx.container.querySelectorAll('mark')];
    expect(marks[0]?.textContent).toBe(check.firstMark);
  }

  if (check.secondMark !== undefined) {
    const marks = [...ctx.container.querySelectorAll('mark')];
    expect(marks[1]?.textContent).toBe(check.secondMark);
  }

  if (check.query) {
    const found = ctx.container.querySelectorAll(check.query);
    if (check.count !== undefined) {
      expect(found.length, `query ${check.query}`).toBe(check.count);
    }
    if (check.minCount !== undefined) {
      expect(found.length, `query ${check.query} minCount`).toBeGreaterThanOrEqual(
        check.minCount,
      );
    }
  }

  if (check.fn === 'resolveAndPaint') {
    if (check.returns === null) {
      expect(ctx.lastMark).toBeNull();
    } else if (check.returns === 'first-mark') {
      expect(ctx.lastMark).toBeInstanceOf(HTMLElement);
      expect(ctx.lastMark?.tagName).toBe('MARK');
    }
  }
}

const catalog = JSON.parse(readFileSync(catalogPath, 'utf8')) as Catalog;
const rows = catalog.fixtures.filter((fixture) => fixture.family === 'D_restore_orphan');

afterEach(() => {
  document.body.innerHTML = '';
});

describe('D_restore_orphan resolveAndPaint harness', () => {
  it('has D rows and a live expect for every jsdom-capable fixture', () => {
    expect(rows).toHaveLength(10);

    const skipped = rows.filter((fixture) => skipReason(fixture) !== null);
    const runnable = rows.filter((fixture) => skipReason(fixture) === null);
    const restored = runnable.filter((fixture) => fixture.expect.restore === 'ok');
    const correctNull = runnable.filter((fixture) => fixture.expect.restore === 'null');
    const wrongSpan = runnable.filter((fixture) => fixture.expect.wrongSpan);

    expect(skipped).toHaveLength(0);
    expect(restored.map((fixture) => fixture.id)).toEqual([
      'D04',
      'D05',
      'D06',
      'D08',
      'D10',
    ]);
    expect(correctNull.map((fixture) => fixture.id)).toEqual([
      'D01',
      'D02',
      'D03',
      'D07',
      'D09',
    ]);
    expect(wrongSpan).toHaveLength(0);
  });

  for (const fixture of rows) {
    const reason = skipReason(fixture);
    const run = reason ? it.skip : it;
    const suffix = reason ? ` — skipped (${reason})` : '';

    run(`${fixture.id} ${fixture.title}${suffix}`, () => {
      const container = document.createElement('div');
      container.innerHTML = fixture.html;
      document.body.append(container);

      let lastMark: HTMLElement | null = null;
      let lastFlatten = '';
      for (const partial of recordsFor(fixture)) {
        const { text, spans } = flattenText(container);
        lastFlatten = text;
        lastMark = resolveAndPaint(asRecord(partial), spans, text);
      }

      if (fixture.expect.restore === 'ok') {
        expect(lastMark, fixture.id).toBeInstanceOf(HTMLElement);
        expect(lastMark?.tagName, fixture.id).toBe('MARK');
      } else if (fixture.expect.restore === 'null') {
        expect(lastMark, fixture.id).toBeNull();
      } else {
        throw new Error(`${fixture.id}: unknown expect.restore ${fixture.expect.restore}`);
      }

      expect(fixture.expect.wrongSpan, fixture.id).toBe(false);

      if (fixture.expect.markCount !== null) {
        expect(container.querySelectorAll('mark').length, fixture.id).toBe(
          fixture.expect.markCount,
        );
      }

      if (fixture.expect.paint === 'first-mark') {
        expect(lastMark, fixture.id).toBeInstanceOf(HTMLElement);
      } else if (fixture.expect.paint === 'null' || fixture.expect.paint === null) {
        expect(lastMark, fixture.id).toBeNull();
      }

      for (const check of fixture.oracle.checks) {
        assertOracleCheck(check, {
          container,
          lastMark,
          flatten: lastFlatten,
        });
      }
    });
  }
});
