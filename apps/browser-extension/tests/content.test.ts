import { describe, expect, it } from 'vitest';
import {
  extractContext,
  flattenText,
  resolveAndPaint,
  resolveOffset,
} from '@/entrypoints/content';
import type { HighlightRecord } from '@/utils/highlight-messages';

function makeRecord(overrides: Partial<HighlightRecord>): HighlightRecord {
  return {
    id: 'id',
    pageKey: 'pageKey',
    origin: '',
    path: 'pageKey',
    query: '',
    quote: '',
    prefix: '',
    suffix: '',
    color: '#fff',
    createdAt: 0,
    updatedAt: 0,
    ...overrides,
  };
}

describe('extractContext', () => {
  it('extracts up to N words of prefix/suffix around the quote', () => {
    document.body.innerHTML =
      '<p id="p">This domain is for use in documentation examples without needing permission. Avoid use in operations.</p>';
    const blockEl = document.getElementById('p')!;

    const result = extractContext(blockEl, 'documentation');

    expect(result.prefix).toBe('This domain is for use in');
    expect(result.suffix).toBe('examples without needing permission. Avoid use');
  });

  it('returns empty strings when the quote is not found in the block', () => {
    document.body.innerHTML = '<p id="p">Hello world</p>';
    const blockEl = document.getElementById('p')!;

    expect(extractContext(blockEl, 'missing')).toEqual({
      prefix: '',
      suffix: '',
    });
  });
});

describe('flattenText / resolveOffset', () => {
  it('flattens text across multiple text nodes and maps offsets back to (node, offset)', () => {
    document.body.innerHTML = '<p>Hello <b>bold</b> world</p>';

    const { text, spans } = flattenText(document.body);
    expect(text).toBe('Hello bold world');

    const resolved = resolveOffset(spans, 6); // start of "bold"
    expect(resolved?.node.data).toBe('bold');
    expect(resolved?.offset).toBe(0);
  });

  it('excludes script/style content', () => {
    document.body.innerHTML =
      '<p>Visible</p><script>var x = "hidden";</script><style>.a{color:red}</style>';

    const { text } = flattenText(document.body);
    expect(text).toBe('Visible');
  });
});

describe('resolveAndPaint', () => {
  it('restores a highlight by matching prefix+quote+suffix', () => {
    document.body.innerHTML =
      '<p>The quick brown fox jumps over the lazy dog.</p>';
    const { text, spans } = flattenText(document.body);

    const record = makeRecord({
      quote: 'brown fox',
      prefix: 'quick',
      suffix: 'jumps',
    });

    const mark = resolveAndPaint(record, spans, text);

    expect(mark).not.toBeNull();
    expect(mark?.tagName).toBe('MARK');
    expect(mark?.textContent).toBe('brown fox');
  });

  it('falls back to matching the quote alone when the surrounding context has drifted', () => {
    document.body.innerHTML = '<p>Some new lead-in. brown fox. A new tail.</p>';
    const { text, spans } = flattenText(document.body);

    // prefix/suffix no longer match anything in the current text, but the
    // quote itself still appears once.
    const record = makeRecord({
      quote: 'brown fox',
      prefix: 'quick',
      suffix: 'jumps',
    });

    const mark = resolveAndPaint(record, spans, text);

    expect(mark).not.toBeNull();
    expect(mark?.textContent).toBe('brown fox');
  });

  it('returns null when the quote cannot be found at all', () => {
    document.body.innerHTML = '<p>Nothing matches here.</p>';
    const { text, spans } = flattenText(document.body);

    const record = makeRecord({ quote: 'brown fox' });

    expect(resolveAndPaint(record, spans, text)).toBeNull();
  });

  it('recomputing flattenText fresh before each paint lets multiple highlights on one page restore without offset corruption', () => {
    // Regression test: painting a highlight mutates the DOM (surroundContents
    // splits text nodes), so reusing one flattenText() snapshot across
    // multiple records produces stale spans and throws IndexSizeError on the
    // second-or-later record. The fix is recomputing flattenText per record.
    document.body.innerHTML = '<p>Alpha beta gamma delta epsilon.</p>';

    const records = [
      makeRecord({ id: '1', quote: 'beta', prefix: 'Alpha', suffix: 'gamma' }),
      makeRecord({ id: '2', quote: 'epsilon', prefix: 'delta', suffix: '' }),
    ];

    for (const record of records) {
      const { text, spans } = flattenText(document.body);
      const mark = resolveAndPaint(record, spans, text);
      expect(mark).not.toBeNull();
    }

    expect(document.querySelectorAll('mark')).toHaveLength(2);
  });
});
