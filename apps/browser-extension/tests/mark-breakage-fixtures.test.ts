import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const catalogPath = join(
  dirname(fileURLToPath(import.meta.url)),
  'fixtures/mark-breakage/phase1-break-fixtures.json',
);

const REQUIRED = [
  'id',
  'family',
  'title',
  'why_breaks',
  'html',
  'load',
  'selection',
  'record',
  'ops',
  'expect',
  'oracle',
  'browserOnly',
  'tags',
] as const;

const FAMILIES = [
  'A_reject',
  'B_live_split',
  'C_parser_x',
  'D_restore_orphan',
  'E_sequence',
] as const;

type Fixture = {
  id: string;
  family: (typeof FAMILIES)[number];
  html: string;
  ops: unknown;
  tags: unknown;
  browserOnly: boolean;
};

type Catalog = {
  meta: {
    phase: number;
    policy: string;
    count: number;
    families: Record<(typeof FAMILIES)[number], number>;
  };
  fixtures: Fixture[];
};

describe('phase-1 mark-breakage fixture pack', () => {
  const catalog = JSON.parse(readFileSync(catalogPath, 'utf8')) as Catalog;

  it('is a break-only catalog whose counts match meta', () => {
    expect(catalog.meta.phase).toBe(1);
    expect(catalog.meta.policy).toMatch(/break-only/i);
    expect(catalog.fixtures).toHaveLength(catalog.meta.count);
    expect(catalog.meta.count).toBeGreaterThanOrEqual(80);

    const counts = Object.fromEntries(FAMILIES.map((family) => [family, 0])) as Record<
      (typeof FAMILIES)[number],
      number
    >;
    for (const fixture of catalog.fixtures) {
      counts[fixture.family] += 1;
    }
    expect(counts).toEqual(catalog.meta.families);
  });

  it('gives every row the schema fields and a unique id', () => {
    const ids = catalog.fixtures.map((fixture) => fixture.id);
    expect(new Set(ids).size).toBe(ids.length);

    for (const fixture of catalog.fixtures) {
      for (const key of REQUIRED) {
        expect(fixture, fixture.id).toHaveProperty(key);
      }
      expect(FAMILIES, fixture.id).toContain(fixture.family);
      expect(fixture.html.length, fixture.id).toBeGreaterThan(0);
      expect(Array.isArray(fixture.ops), fixture.id).toBe(true);
      expect(Array.isArray(fixture.tags), fixture.id).toBe(true);
      expect(typeof fixture.browserOnly, fixture.id).toBe('boolean');
    }
  });
});
