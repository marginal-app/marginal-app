// Pure DOM anchoring: turn a selection into quote + context, and paint a
// stored anchor back onto a page. No storage, no messaging.

export interface HighlightAnchor {
  quote: string;
  prefix: string;
  suffix: string;
  color: string;
}

export interface StoredHighlight extends HighlightAnchor {
  id: string;
  comment?: string;
}

export function extractContext(blockEl: Element, quote: string, wordCount = 6) {
  const text = blockEl.textContent ?? '';
  const idx = text.indexOf(quote);
  if (idx === -1) return { prefix: '', suffix: '' };

  const before = text.slice(0, idx);
  const after = text.slice(idx + quote.length);

  const prefixWords = before.match(/\S+/g) ?? [];
  const suffixWords = after.match(/\S+/g) ?? [];

  return {
    prefix: prefixWords.slice(-wordCount).join(' '),
    suffix: suffixWords.slice(0, wordCount).join(' '),
  };
}

export function paintRange(range: Range, color: string): HTMLElement | null {
  const mark = document.createElement('mark');
  mark.style.backgroundColor = color;
  mark.style.borderRadius = '2px';
  mark.style.cursor = 'pointer';

  try {
    range.surroundContents(mark);
    return mark;
  } catch (error) {
    console.error('여러 노드에 걸친 선택은 아직 처리 못함', error);
    return null;
  }
}

export interface TextSpan {
  node: Text;
  start: number;
  end: number;
}

export function flattenText(root: Node): { text: string; spans: TextSpan[] } {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = (node as Text).parentElement;
      if (!parent) return NodeFilter.FILTER_REJECT;
      if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(parent.tagName)) {
        return NodeFilter.FILTER_REJECT;
      }
      return NodeFilter.FILTER_ACCEPT;
    },
  });

  let text = '';
  const spans: TextSpan[] = [];
  let node: Node | null;
  while ((node = walker.nextNode())) {
    const textNode = node as Text;
    const start = text.length;
    text += textNode.data;
    spans.push({ node: textNode, start, end: text.length });
  }
  return { text, spans };
}

export function resolveOffset(
  spans: TextSpan[],
  offset: number,
): { node: Text; offset: number } | null {
  for (const span of spans) {
    if (offset >= span.start && offset < span.end) {
      return { node: span.node, offset: offset - span.start };
    }
  }
  const last = spans[spans.length - 1];
  if (last && offset === last.end) {
    return { node: last.node, offset: last.end - last.start };
  }
  return null;
}

export function resolveAndPaint(
  record: HighlightAnchor,
  spans: TextSpan[],
  text: string,
): HTMLElement | null {
  const target = record.prefix + record.quote + record.suffix;
  let idx = text.indexOf(target);
  let quoteStart: number;

  if (idx !== -1) {
    quoteStart = idx + record.prefix.length;
  } else {
    idx = text.indexOf(record.quote);
    if (idx === -1) return null;
    quoteStart = idx;
  }

  const quoteEnd = quoteStart + record.quote.length;
  const start = resolveOffset(spans, quoteStart);
  const end = resolveOffset(spans, quoteEnd);
  if (!start || !end) return null;

  const range = document.createRange();
  range.setStart(start.node, start.offset);
  range.setEnd(end.node, end.offset);
  return paintRange(range, record.color);
}
