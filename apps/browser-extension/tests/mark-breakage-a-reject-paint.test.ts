import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, describe, expect, it } from 'vitest';
import { paintRange } from '@/entrypoints/content';

const catalogPath = join(
  dirname(fileURLToPath(import.meta.url)),
  'fixtures/mark-breakage/phase1-break-fixtures.json',
);

const DEFAULT_COLOR = '#FFF3B0';
const JSDOM_LOADS = new Set(['container-innerHTML']);

type PathPoint = { path: number[]; offset: number };

type Selection = {
  api: string;
  pathFrom: string;
  start: PathPoint;
  end: PathPoint;
  quote?: string | null;
};

type OracleCheck = {
  query?: string;
  count?: number;
  minCount?: number;
  fn?: string;
  returns?: unknown;
  joinedMarkText?: string;
  any?: OracleCheck[];
};

type Fixture = {
  id: string;
  family: string;
  title: string;
  html: string;
  load: string;
  selection: Selection | null;
  record: { color?: string } | null;
  expect: {
    paint: string;
    exceptionName: string | null;
    markCount: number | null;
    notes: string;
  };
  oracle: {
    kind: string;
    via?: string;
    checks: OracleCheck[];
  };
  browserOnly: boolean;
  harnessNotes?: string;
};

type Catalog = { fixtures: Fixture[] };

function nodeAt(root: Node, path: number[]): Node | null {
  let current: Node = root;
  for (const index of path) {
    const next = current.childNodes[index];
    if (!next) return null;
    current = next;
  }
  return current;
}

function skipReason(fixture: Fixture): string | null {
  if (fixture.browserOnly) return 'browserOnly';
  if (!JSDOM_LOADS.has(fixture.load)) return `unsupported load: ${fixture.load}`;
  if (!fixture.selection) return 'no selection';
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
    mark: HTMLElement | null;
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

  if (check.fn === 'paintRange') {
    if (check.returns === null) {
      expect(ctx.mark).toBeNull();
    } else if (check.returns === 'first-mark') {
      expect(ctx.mark).toBeInstanceOf(HTMLElement);
      expect(ctx.mark?.tagName).toBe('MARK');
      const pieces = wrapMarks(ctx.container);
      expect(ctx.mark).toBe(pieces[0] ?? null);
    }
  }
}

function assertPaintOutcome(
  fixture: Fixture,
  mark: HTMLElement | null,
  container: HTMLElement,
): void {
  if (fixture.expect.paint === 'first-mark') {
    expect(mark, fixture.id).toBeInstanceOf(HTMLElement);
    expect(mark?.tagName, fixture.id).toBe('MARK');
  } else if (fixture.expect.paint === 'null') {
    expect(mark, fixture.id).toBeNull();
  } else if (fixture.expect.paint === 'nested-or-null') {
    const nested = container.querySelectorAll('mark mark').length > 0;
    expect(mark === null || nested, fixture.id).toBe(true);
  } else {
    throw new Error(`${fixture.id}: unknown expect.paint ${fixture.expect.paint}`);
  }

  if (fixture.expect.markCount !== null) {
    expect(container.querySelectorAll('mark').length, fixture.id).toBe(
      fixture.expect.markCount,
    );
  }
}

const catalog = JSON.parse(readFileSync(catalogPath, 'utf8')) as Catalog;
const rows = catalog.fixtures.filter((fixture) => fixture.family === 'A_reject');

afterEach(() => {
  document.body.innerHTML = '';
});

describe('A_reject paintRange harness (wrap)', () => {
  it('has A_reject rows and a live expect for every jsdom-capable fixture', () => {
    expect(rows).toHaveLength(38);

    const skippedBrowserOnly = rows.filter((fixture) => fixture.browserOnly);
    const skippedUnsupportedLoad = rows.filter(
      (fixture) => !fixture.browserOnly && !JSDOM_LOADS.has(fixture.load),
    );
    const runnable = rows.filter((fixture) => skipReason(fixture) === null);
    const paints = runnable.filter((fixture) => fixture.expect.paint === 'first-mark');
    const stillFails = runnable.filter((fixture) => fixture.expect.paint === 'null');

    expect(skippedBrowserOnly.map((fixture) => fixture.id)).toEqual([
      'A31',
      'A32',
      'A35',
      'A36',
      'A38',
    ]);
    expect(skippedUnsupportedLoad).toHaveLength(0);
    expect(paints).toHaveLength(runnable.length);
    expect(stillFails).toHaveLength(0);
  });

  for (const fixture of rows) {
    const reason = skipReason(fixture);
    const run = reason ? it.skip : it;
    const suffix = reason ? ` — skipped (${reason})` : '';

    run(`${fixture.id} ${fixture.title}${suffix}`, () => {
      const selection = fixture.selection;
      if (!selection) {
        throw new Error(`${fixture.id}: skipped rows must not run`);
      }

      const container = document.createElement('div');
      container.innerHTML = fixture.html;
      document.body.append(container);

      const startNode = nodeAt(container, selection.start.path);
      const endNode = nodeAt(container, selection.end.path);
      expect(startNode, `${fixture.id} start path`).not.toBeNull();
      expect(endNode, `${fixture.id} end path`).not.toBeNull();

      const range = document.createRange();
      try {
        range.setStart(startNode!, selection.start.offset);
        range.setEnd(endNode!, selection.end.offset);
      } catch (error) {
        if (fixture.harnessNotes) {
          return;
        }
        throw error;
      }

      const color = fixture.record?.color ?? DEFAULT_COLOR;
      const mark = paintRange(range, color);

      assertPaintOutcome(fixture, mark, container);
      for (const check of fixture.oracle.checks) {
        assertOracleCheck(check, { container, mark });
      }
    });
  }
});
