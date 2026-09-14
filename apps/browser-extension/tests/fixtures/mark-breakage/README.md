# mark-breakage fixtures

Phase 1 is **break-only counterexamples** (`schemaVersion` 2).

Every row in `phase1-break-fixtures.json` started as a case the content script was expected to lose. Step 2 runs `A_reject` through wrap `paintRange` and keeps those `expect` fields live; B/C/D/E still describe older counterexamples (stale flatten, parser recovery, restore orphans, mouseup / ghost SAVE).

Happy paths (single text node inside `p | li | h*`, unique `prefix+quote+suffix` restore, fresh `flattenText` per record) are **deferred**. Do not add them here.

Each row also has founder-facing fields so a path/offset pair is not the only way to see the drag:

- `story`, `selectHow`, `expectHuman`, `repro` — plain language
- `selectionAnnotated` — short snippet with `⟦` (mouse down) and `⟧` (mouse up). Restore-only rows use `‹quote›` and say `no mouse`. Markers are documentation only; they must not appear in `html`.

See [PHASE1.md](./PHASE1.md) for families, schema, the `⟦⟧` convention, and harness hints. Do not wire a fuzzy matcher or Playwright runner in the same change as this pack.
