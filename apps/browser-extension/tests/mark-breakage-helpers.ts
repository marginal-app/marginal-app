import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { flattenText, paintRange, resolveAndPaint } from '@/entrypoints/content';
import type { HighlightRecord } from '@/utils/highlight-messages';

export const catalogPath = join(
  dirname(fileURLToPath(import.meta.url)),
  'fixtures/mark-breakage/phase1-break-fixtures.json',
);

export const DEFAULT_COLOR = '#FFF3B0';
export const JSDOM_LOADS = new Set(['container-innerHTML']);

export type PartialRecord = {
  id?: string;
  quote?: string;
  prefix?: string;
  suffix?: string;
  color?: string;
};

export type PathPoint = { path: number[]; offset: number };

export type Selection = {
  api?: string;
  pathFrom?: string;
  start: PathPoint;
  end: PathPoint;
  quote?: string | null;
};

export type OracleCheck = {
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
  toolbar?: string;
  closest?: string | null;
  persist?: boolean;
  any?: OracleCheck[];
};

export type Fixture = {
  id: string;
  family: string;
  title: string;
  html: string;
  load: string;
  selection: Selection | null;
  record: PartialRecord | null;
  records?: PartialRecord[];
  ops: string[];
  expect: {
    paint: string | null;
    markCount: number | null;
    restore: string | null;
    toolbar: string | null;
    wrongSpan: boolean;
    ghostRecord: boolean;
  };
  oracle: {
    kind: string;
    checks: OracleCheck[];
  };
  browserOnly: boolean;
  parserRecovery?: { afterParseSelection?: Selection };
  overlapSelectionAfterFirstPaint?: { quote?: string };
  mutation?: {
    op?: string;
    html?: string;
    path?: number[];
    offset?: number;
    text?: string;
  };
};

export type Catalog = { fixtures: Fixture[] };

export function loadCatalog(): Catalog {
  return JSON.parse(readFileSync(catalogPath, 'utf8')) as Catalog;
}

export function asRecord(partial: PartialRecord): HighlightRecord {
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

export function recordsFor(fixture: Fixture): PartialRecord[] {
  if (fixture.records?.length) return fixture.records;
  if (fixture.record) return [fixture.record];
  return [];
}

export function nodeAt(root: Node, path: number[]): Node | null {
  let current: Node = root;
  for (const index of path) {
    const next = current.childNodes[index];
    if (!next) return null;
    current = next;
  }
  return current;
}

export function rangeFromSelection(
  container: HTMLElement,
  selection: Selection,
): { range: Range | null; error: string | null } {
  const startNode = nodeAt(container, selection.start.path);
  const endNode = nodeAt(container, selection.end.path);
  if (!startNode || !endNode) {
    return { range: null, error: 'path-missing' };
  }
  const range = document.createRange();
  try {
    range.setStart(startNode, selection.start.offset);
    range.setEnd(endNode, selection.end.offset);
    return { range, error: null };
  } catch (error) {
    const name = error instanceof Error ? error.name : 'Error';
    return { range: null, error: name };
  }
}

export function restoreFresh(
  container: HTMLElement,
  partial: PartialRecord,
): HTMLElement | null {
  const { text, spans } = flattenText(container);
  return resolveAndPaint(asRecord(partial), spans, text);
}

export function wrapMarks(root: ParentNode): HTMLElement[] {
  return [...root.querySelectorAll<HTMLElement>('mark[data-paint-group]')];
}

export function joinedWrapText(root: ParentNode): string {
  return wrapMarks(root)
    .map((mark) => mark.textContent ?? '')
    .join('');
}

export function paintQuoteFromFlatten(
  container: HTMLElement,
  quote: string,
  color = DEFAULT_COLOR,
): HTMLElement | null {
  const { text, spans } = flattenText(container);
  const idx = text.indexOf(quote);
  if (idx === -1) return null;
  const endAt = idx + quote.length;
  const start = spans.find((span) => idx >= span.start && idx < span.end);
  const end =
    spans.find((span) => endAt > span.start && endAt <= span.end) ??
    spans[spans.length - 1];
  if (!start || !end) return null;
  const range = document.createRange();
  range.setStart(start.node, idx - start.start);
  range.setEnd(end.node, endAt - end.start);
  return paintRange(range, color);
}
