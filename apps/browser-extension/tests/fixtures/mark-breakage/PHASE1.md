# Phase 1 — mark-breakage fixtures (break-only)

`phase1-break-fixtures.json` is the committed source of truth (`schemaVersion` 2). This note is the reading guide.

**Step 2:** `tests/mark-breakage-a-reject-paint.test.ts` executes every jsdom-capable `A_reject` row against current wrap `paintRange`. A-family `expect` / `oracle` / `expectHuman` / `why_breaks` are live for those rows. `browserOnly` and unsupported `load` values are skipped (no Playwright in this step). Schema smoke in `mark-breakage-fixtures.test.ts` is unchanged.

## Human fields (read these first)

Machine paths (`selection.start.path`, UTF-16 offsets) are not a founder-readable way to see a mouse drag. Every row also has five documentation fields. They do not change harness behavior.

| Field | What to write |
| --- | --- |
| `story` | 2–3 sentences: what is on the page, and what the user (or a restore) tries to do. |
| `selectHow` | Plain language of the drag (“from the last syllable of the bold run into the following plain text”). Restore-only rows start with `no mouse; restore looks for …`. |
| `selectionAnnotated` | A **short** HTML or text snippet of the relevant region with visible markers (below). |
| `expectHuman` | Plain-language outcome (wrap paint, or a remaining reject). |
| `repro` | Three short steps to reproduce in DevTools or mentally. |

### `⟦` `⟧` and `‹` `›` convention

These characters are documentation only. **Never** put them in the harness `html` field (or in `shadow.innerHTML`).

| Marker | Meaning |
| --- | --- |
| `⟦` | Selection start (mouse down). |
| `⟧` | Selection end (mouse up). |
| `‹quote›` | On restore-only rows (`selection` is `null`): the quote occurrence restore would target. Say `no mouse` in `selectHow` / the snippet. |

Example (A02): the user starts inside bold “text” and ends in the following “now”:

```text
See <strong>bold ⟦text</strong> now⟧
```

A row that has a `selection` must show a clear `⟦`…`⟧` pair. A restore-only row annotates the quote (or explains that restore looks for a string that is not on the page). Hybrid rows (restore, then a later drag) may use both.

## Policy

Phase 1 **maximizes counterexamples**. Rows were added because today's implementation lost on:

- `paintRange` used `range.surroundContents(mark)` and returned `null` on `InvalidStateError` (A; Step 2 now records wrap outcomes instead of deleting the rows)
- `flattenText` / `resolveOffset` go stale after a paint splits text nodes
- `resolveAndPaint` uses `indexOf` (first match, then quote-only fallback)
- mouseup requires `closest('p, li, h1, h2, h3, h4, h5, h6')`
- `savePendingHighlight` still sends `SAVE_HIGHLIGHT` when paint returned `null`

Happy-path coverage is a later pack. Do not add fresh single-text-node-in-`p` rows here.

Product `paintRange` wraps intersecting text nodes (`splitText` + one `<mark>` per segment, grouped by `data-paint-group`) and does not use `surroundContents` on the success path. Step 2 refreshed **A_reject** `expect` / `oracle` so they match that wrap (most jsdom rows now paint). B / C / D / E rows still describe the older counterexamples until a later commit on the same review PR. Do not delete fixtures.

## Families

| Family | Count | What it attacks |
| --- | --- | --- |
| `A_reject` | 38 | Partial-boundary selections that used to reject `surroundContents`. After wrap, jsdom-capable rows paint; `expect` records mark count + joined wrap text. `browserOnly` rows stay skipped. |
| `B_live_split` | 14 | Live DOM after a successful mark: stale flatten, overlaps, innerHTML roundtrip, double restore, `normalize`, mutations |
| `C_parser_x` | 22 | Dirty HTML. Parser recovery (adoption agency, foster parenting, nested `a`/`button`/`form`, `p` closed by `div`/`ul`) so authored paths and flatten intersections are wrong |
| `D_restore_orphan` | 10 | `resolveAndPaint` returns `null` or paints the wrong span (missing quote, duplicates, flatten concatenation, NBSP, substring, script-only, empty quote, soft hyphen) |
| `E_sequence` | 5 | Product-path divergences: mouseup without `p\|li\|h*`, and toolbar-shown + ghost `SAVE_HIGHLIGHT` |

Total: **89**. Counts also live on `meta.families`.

## Schema

Every fixture has these fields:

| Field | Role |
| --- | --- |
| `id` | Stable id (`A01`…`E05`, plus `A38`) |
| `family` | One of the five families above |
| `title` | Short name |
| `story` / `selectHow` / `selectionAnnotated` / `expectHuman` / `repro` | Founder-facing; see [Human fields](#human-fields-read-these-first) |
| `why_breaks` | Why this loses against the current content script |
| `html` | Compact snippet (no interstitial whitespace between blocks). No `⟦⟧` / `‹›` |
| `load` | How to mount it (see below) |
| `selection` | `null` for restore-only rows; otherwise a range spec |
| `record` | `null`, or `{id,quote,prefix,suffix,color}` (`#FFF3B0`). Multi-restore rows use `extra.records` |
| `ops` | Ordered harness steps |
| `expect` | `{paint, exceptionName, markCount, toolbar, restore, wrongSpan, ghostRecord, notes}` |
| `oracle` | `{kind, checks[]}` — exact asserts, not a fuzzy scorer |
| `browserOnly` | Skip jsdom; run under Playwright Chromium |
| `tags` | Searchable facets |

Optional sibling fields (not required by the schema smoke test): `parserRecovery`, `records`, `mutation`, `shadow`, `harnessNotes`, `quoteNotes`, `overlapSelectionAfterFirstPaint`.

### `load`

| Value | Meaning |
| --- | --- |
| `container-innerHTML` | Default. `container.innerHTML = html` (a `<div>` you own, or `document.body`) |
| `open-shadow` | Attach `{mode:'open'}` on the host from `html`; put `extra.shadow.innerHTML` in the shadow root. **Selection paths are relative to `shadowRoot`.** |
| `closed-shadow` | Same, `{mode:'closed'}` — noted on A38, not a second row |
| `iframe-srcdoc` | Reserved for a document *inside* the iframe (A35 is the parent-range reject) |
| `domparser-body` | `new DOMParser().parseFromString(html, 'text/html').body` when you need a detached parse |

### `selection`

```json
{
  "api": "range",
  "pathFrom": "container",
  "start": { "path": [0, 0], "offset": 3 },
  "end": { "path": [0, 1, 0], "offset": 3 },
  "quote": "lo wor"
}
```

- `path` is `childNode` indices **after** the HTML parser, not the authored source string.
- `offset` is a UTF-16 code unit index into that text node.
- Compact `html` keeps paths stable (a newline between `</p><p>` would insert a text node).
- Tables in `A_*` include an explicit `<tbody>`. `C_*` foster cases do **not** — re-read `innerHTML` / `childNodes` before applying paths (`parserRecovery.typical` is a hint, not a golden).
- `quote` is the expected `range.toString()` when it is stable. Some unicode / `<br>` / form-control rows tell you not to assert it (`quoteNotes`).

### `ops` (vocabulary)

A_reject Step 2 executes `load`, `select`, `paint`. The rest (`flatten`, `flattenOnce`, `restore`, `restoreStale`, `restore-again`, `mouseup`, `color-pick`, `save`, `normalize`, `innerHTML-roundtrip`, `unwrapMark`, plus the `restore:quote` / `select-overlap` aliases) stay catalog vocabulary for later slices.

## Mapping onto `content.ts`

```
paintRange        → wrap intersecting text nodes (splitText + <mark> per segment, data-paint-group); null only when nothing paintable
flattenText       → TreeWalker SHOW_TEXT; reject SCRIPT / STYLE / NOSCRIPT
resolveOffset     → first span with start <= offset < end (or last.end)
resolveAndPaint   → indexOf(prefix+quote+suffix) else indexOf(quote)
mouseup           → closest('p, li, h1…h6') or hide toolbar
savePendingHighlight → SAVE_HIGHLIGHT even when mark is null (E05)
```

The Step 2 A harness calls `paintRange` (not `surroundContents`). Live A oracles use `kind: wrap-paints` / `via: paintRange-returns-first-mark` and `joinedMarkText` (new `mark[data-paint-group]` textContent joined).

## Harness hints

### jsdom (Vitest, already on this package)

**Implemented for A_reject:** `tests/mark-breakage-a-reject-paint.test.ts` — `container-innerHTML` + `selection` → Range → `paintRange`. Skip `browserOnly: true` and unsupported `load` values.

B (stale `Text` + `IndexSizeError`), D (`resolveAndPaint`), and C (parse5 recovery) are still catalog-only.

Skip `browserOnly: true`: SVG/MathML range endpoints (A31, A32, C14, C15), iframe (A35), contenteditable caret (A36), open shadow (A38), noscript scripting split (C21), and any real `getSelection` / mouseup hit-test.

### Playwright Chromium

Use this for `browserOnly` rows, E_* mouseup against the real `closest()` + toolbar, iframe/shadow probes, and confirming `parserRecovery.typical`.

Do **not** load the unpacked extension and do **not** boot WXT to consume this pack. Import `paintRange` / `flattenText` / `resolveAndPaint` or dispatch `mouseup` on a fixture document.

### Fuzzy / repair harness

Deferred. This pack is the counterexample catalog only.

## What “break” means per family

- **A** — Step 2: after `select` + wrap `paint`, assert `expect.paint` / `markCount` / joined wrap text. Most jsdom rows paint. Remaining caveats (nested existing marks, textarea text, mid-ZWJ split) are recorded on the row, not dropped.
- **B** — a second step on the live DOM (stale spans, overlap, roundtrip, unwrap) fails or corrupts offsets.
- **C** — authored HTML is not the tree you get; paths / flatten intersections do not match the author’s crossing.
- **D** — `resolveAndPaint` is `null` or the painted text is the wrong occurrence.
- **E** — the product sequence diverges from “user selected text → mark appears”: toolbar hidden, or toolbar shown + persisted record + no mark.

## Adding a row

1. Keep it a counterexample. If `paintRange` would succeed on a single text node in a `<p>`, it does not belong in phase 1.
2. Use the next id in that family (`A39`, `B15`, …).
3. Keep `html` compact. Put parser guesses in `extra.parserRecovery`, not in `html`.
4. Add the five human fields. If the row has a `selection`, `selectionAnnotated` must show `⟦`…`⟧`. If `selection` is `null`, mark the restore quote with `‹›` or say `no mouse`. Do not put those markers in `html`.
5. Update `meta.count` and `meta.families`. Bump `meta.schemaVersion` if you change the fixture schema.
6. Leave happy paths for a later `phase2-happy-fixtures.json`.
