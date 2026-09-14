# mark-breakage fixtures

Phase 1 is **break-only counterexamples** (`schemaVersion` 2).

Every row in `phase1-break-fixtures.json` is a case the current content script is expected to lose: `Range.surroundContents` reject, stale flatten after a live split, HTML-parser recovery that moves nodes, restore that returns null or paints the wrong span, or a mouseup path that never reaches `paintRange`.

Happy paths (single text node inside `p | li | h*`, unique `prefix+quote+suffix` restore, fresh `flattenText` per record) are **deferred**. Do not add them here.

Each row also has founder-facing fields so a path/offset pair is not the only way to see the drag:

- `story`, `selectHow`, `expectHuman`, `repro` — plain language
- `selectionAnnotated` — short snippet with `⟦` (mouse down) and `⟧` (mouse up). Restore-only rows use `‹quote›` and say `no mouse`. Markers are documentation only; they must not appear in `html`.

See [PHASE1.md](./PHASE1.md) for families, schema, the `⟦⟧` convention, and harness hints. Do not wire a fuzzy matcher or Playwright runner in the same change as this pack.
