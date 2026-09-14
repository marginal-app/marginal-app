import { ColorToolbar, DEFAULT_HIGHLIGHT_COLOR, HIGHLIGHT_COLORS } from '@/components/color-toolbar';
import { CommentPopover } from '@/components/comment-popover';
import { eventPathContains } from '@/components/popover';
import type {
  CommentUpdatedMessage,
  GetHighlightsMessage,
  HighlightRecord,
  SaveHighlightMessage,
  UpdateCommentMessage,
} from '@/utils/highlight-messages';
import { pageCatalogFromDocument } from '@/utils/page-catalog';
import { pageKeyFromLocation } from '@/utils/page-key';

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

const SKIP_PAINT_PARENTS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT']);

function shouldSkipPaintText(node: Text): boolean {
  const parent = node.parentElement;
  if (!parent) return true;
  return SKIP_PAINT_PARENTS.has(parent.tagName);
}

function collectTextNodesInRange(range: Range): Text[] {
  const ancestor = range.commonAncestorContainer;
  if (ancestor.nodeType === Node.TEXT_NODE) {
    const text = ancestor as Text;
    return shouldSkipPaintText(text) ? [] : [text];
  }

  const walker = document.createTreeWalker(ancestor, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const text = node as Text;
      if (shouldSkipPaintText(text)) return NodeFilter.FILTER_REJECT;
      return range.intersectsNode(text)
        ? NodeFilter.FILTER_ACCEPT
        : NodeFilter.FILTER_REJECT;
    },
  });

  const nodes: Text[] = [];
  let current: Node | null;
  while ((current = walker.nextNode())) {
    nodes.push(current as Text);
  }
  return nodes;
}

function sliceTextToOffsets(
  node: Text,
  start: number,
  end: number,
): Text | null {
  const length = node.length;
  const from = Math.max(0, Math.min(start, length));
  const to = Math.max(0, Math.min(end, length));
  if (from >= to) return null;
  if (to < length) node.splitText(to);
  if (from > 0) return node.splitText(from);
  return node;
}

function createMark(color: string, paintGroup: string): HTMLMarkElement {
  const mark = document.createElement('mark');
  mark.style.backgroundColor = color;
  mark.style.borderRadius = '2px';
  mark.style.cursor = 'pointer';
  mark.dataset.paintGroup = paintGroup;
  return mark;
}

function wrapTextNode(
  node: Text,
  color: string,
  paintGroup: string,
): HTMLMarkElement | null {
  if (!node.data.length || !node.parentNode) return null;
  const mark = createMark(color, paintGroup);
  node.parentNode.insertBefore(mark, node);
  mark.appendChild(node);
  return mark;
}

function marksInPaintGroup(mark: HTMLElement): HTMLElement[] {
  const group = mark.dataset.paintGroup;
  if (!group) return [mark];
  return [
    ...document.querySelectorAll<HTMLElement>(
      `mark[data-paint-group="${group}"]`,
    ),
  ];
}

/**
 * Wrap each intersecting text node in a `<mark>`. Pieces of one selection
 * share `data-paint-group` until save/restore stamps `data-highlight-id`.
 * Does not use `surroundContents`. Returns the first mark, or null when
 * there is no paintable text.
 */
export function paintRange(range: Range, color: string): HTMLElement | null {
  try {
    if (range.collapsed) return null;

    const nodes = collectTextNodesInRange(range);
    if (nodes.length === 0) return null;

    const paintGroup = crypto.randomUUID();
    const segments: Text[] = [];

    if (nodes.length === 1) {
      const only = nodes[0];
      const sliced = sliceTextToOffsets(
        only,
        range.startContainer === only ? range.startOffset : 0,
        range.endContainer === only ? range.endOffset : only.length,
      );
      if (sliced) segments.push(sliced);
    } else {
      const first = nodes[0];
      const last = nodes[nodes.length - 1];
      const firstSliced = sliceTextToOffsets(
        first,
        range.startContainer === first ? range.startOffset : 0,
        first.length,
      );
      const lastSliced = sliceTextToOffsets(
        last,
        0,
        range.endContainer === last ? range.endOffset : last.length,
      );
      if (firstSliced) segments.push(firstSliced);
      for (let i = 1; i < nodes.length - 1; i++) {
        segments.push(nodes[i]);
      }
      if (lastSliced) segments.push(lastSliced);
    }

    let firstMark: HTMLElement | null = null;
    for (const segment of segments) {
      const mark = wrapTextNode(segment, color, paintGroup);
      if (mark && !firstMark) firstMark = mark;
    }
    return firstMark;
  } catch (error) {
    console.error('하이라이트 칠하기 실패', error);
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

const RESTORE_BLOCK_SELECTOR =
  'p, li, h1, h2, h3, h4, h5, h6, td, th, dt, dd, blockquote, pre, div, tr, section, article, header, footer, main, figcaption, caption';

function enclosingBlock(node: Node): Element | null {
  const el =
    node.nodeType === Node.TEXT_NODE
      ? (node as Text).parentElement
      : (node as Element);
  return el?.closest(RESTORE_BLOCK_SELECTOR) ?? el;
}

function rangeCrossesBlock(
  spans: TextSpan[],
  start: number,
  end: number,
): boolean {
  const from = resolveOffset(spans, start);
  const to = resolveOffset(spans, end);
  if (!from || !to) return true;
  if (from.node === to.node) return false;
  return enclosingBlock(from.node) !== enclosingBlock(to.node);
}

function isWordChar(ch: string | undefined): boolean {
  return !!ch && /\p{L}|\p{N}/u.test(ch);
}

function isWordBounded(text: string, start: number, end: number): boolean {
  return !isWordChar(text[start - 1]) && !isWordChar(text[end]);
}

function normalizeForRestore(text: string): {
  normalized: string;
  toOriginal: number[];
} {
  const chars: string[] = [];
  const toOriginal: number[] = [];
  let lastWasSpace = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (ch === '\u00ad') continue;
    const space =
      ch === '\u00a0' ||
      ch === ' ' ||
      ch === '\t' ||
      ch === '\n' ||
      ch === '\r' ||
      ch === '\f';
    if (space) {
      if (lastWasSpace) continue;
      chars.push(' ');
      toOriginal.push(i);
      lastWasSpace = true;
      continue;
    }
    chars.push(ch);
    toOriginal.push(i);
    lastWasSpace = false;
  }
  return { normalized: chars.join(''), toOriginal };
}

function allIndices(haystack: string, needle: string): number[] {
  const hits: number[] = [];
  if (!needle) return hits;
  let from = 0;
  while (from <= haystack.length - needle.length) {
    const idx = haystack.indexOf(needle, from);
    if (idx === -1) break;
    hits.push(idx);
    from = idx + 1;
  }
  return hits;
}

function hasTrailingContext(
  before: string,
  prefix: string,
): 'exact' | 'contains' | null {
  if (!prefix) return null;
  const normBefore = normalizeForRestore(before).normalized.replace(/ +$/, '');
  const normPrefix = normalizeForRestore(prefix).normalized.replace(/ +$/, '');
  if (!normPrefix) return null;
  if (normBefore.endsWith(normPrefix)) return 'exact';
  if (normBefore.includes(normPrefix)) return 'contains';
  return null;
}

function hasLeadingContext(
  after: string,
  suffix: string,
): 'exact' | 'contains' | null {
  if (!suffix) return null;
  const normAfter = normalizeForRestore(after).normalized.replace(/^ +/, '');
  const normSuffix = normalizeForRestore(suffix).normalized.replace(/^ +/, '');
  if (!normSuffix) return null;
  if (normAfter.startsWith(normSuffix)) return 'exact';
  if (normAfter.includes(normSuffix)) return 'contains';
  return null;
}

function insideExistingMark(spans: TextSpan[], offset: number): boolean {
  const resolved = resolveOffset(spans, offset);
  return Boolean(resolved?.node.parentElement?.closest('mark'));
}

function scoreCandidate(
  record: HighlightRecord,
  text: string,
  spans: TextSpan[],
  start: number,
  end: number,
): number {
  let score = 0;
  const prefixHit = hasTrailingContext(text.slice(0, start), record.prefix);
  if (prefixHit === 'exact') score += 10;
  else if (prefixHit === 'contains') score += 3;
  const suffixHit = hasLeadingContext(text.slice(end), record.suffix);
  if (suffixHit === 'exact') score += 10;
  else if (suffixHit === 'contains') score += 3;
  if (isWordBounded(text, start, end)) score += 3;
  if (insideExistingMark(spans, start)) score -= 5;
  return score;
}

function resolveQuoteOffsets(
  record: HighlightRecord,
  spans: TextSpan[],
  text: string,
): { start: number; end: number } | null {
  if (!record.quote.trim()) return null;

  const glued = record.prefix + record.quote + record.suffix;
  if (record.prefix || record.suffix) {
    const gluedAt = text.indexOf(glued);
    if (gluedAt !== -1) {
      const start = gluedAt + record.prefix.length;
      const end = start + record.quote.length;
      if (!rangeCrossesBlock(spans, start, end)) {
        return { start, end };
      }
    }
  }

  const folded = normalizeForRestore(text);
  const normQuote = normalizeForRestore(record.quote).normalized;
  if (!normQuote) return null;

  const candidates: { start: number; end: number; score: number }[] = [];
  for (const nStart of allIndices(folded.normalized, normQuote)) {
    const nEnd = nStart + normQuote.length;
    const start = folded.toOriginal[nStart];
    const last = folded.toOriginal[nEnd - 1];
    if (start == null || last == null) continue;
    const end = last + 1;
    if (rangeCrossesBlock(spans, start, end)) continue;
    candidates.push({
      start,
      end,
      score: scoreCandidate(record, text, spans, start, end),
    });
  }

  if (candidates.length === 0) return null;
  if (candidates.length === 1) return candidates[0];
  candidates.sort((a, b) => b.score - a.score);
  if (candidates[0].score > candidates[1].score) return candidates[0];
  return null;
}

export function resolveAndPaint(
  record: HighlightRecord,
  spans: TextSpan[],
  text: string,
): HTMLElement | null {
  const resolved = resolveQuoteOffsets(record, spans, text);
  if (!resolved) return null;

  const start = resolveOffset(spans, resolved.start);
  const end = resolveOffset(spans, resolved.end);
  if (!start || !end) return null;

  const range = document.createRange();
  range.setStart(start.node, start.offset);
  range.setEnd(end.node, end.offset);
  return paintRange(range, record.color);
}

export default defineContentScript({
  matches: ['<all_urls>'],
  runAt: 'document_idle',
  main() {
    const pageKey = pageKeyFromLocation(location);

    let pending: {
      range: Range;
      quote: string;
      prefix: string;
      suffix: string;
    } | null = null;

    let activeHighlightId: string | null = null;
    let activeMark: HTMLElement | null = null;

    const toolbar = new ColorToolbar();
    toolbar.colors = HIGHLIGHT_COLORS;

    const commentBox = new CommentPopover();

    document.documentElement.append(toolbar.host, commentBox.host);

    function hideToolbar() {
      toolbar.hide();
      pending = null;
    }

    function hideCommentBox() {
      commentBox.hide();
      activeHighlightId = null;
      activeMark = null;
    }

    function openCommentBox(mark: HTMLElement, highlightId: string) {
      hideToolbar();
      activeHighlightId = highlightId;
      activeMark = mark;
      commentBox.comment = mark.dataset.comment ?? '';
      commentBox.quote = mark.textContent?.trim() ?? '';
      commentBox.accentColor = mark.style.backgroundColor;
      commentBox.showBelow(mark.getBoundingClientRect());
      commentBox.focusInput();
    }

    function savePendingHighlight(color: string, openComment: boolean) {
      if (!pending) return;
      const { range, quote, prefix, suffix } = pending;
      const mark = paintRange(range, color);

      const message: SaveHighlightMessage = {
        type: 'SAVE_HIGHLIGHT',
        payload: {
          pageKey,
          quote,
          prefix,
          suffix,
          color,
          catalog: pageCatalogFromDocument(document),
        },
      };
      browser.runtime
        .sendMessage(message)
        .then((record: HighlightRecord) => {
          if (!mark) return;
          attachCommentHandler(mark, record.id, '');
          if (openComment) openCommentBox(mark, record.id);
        })
        .catch((error) => {
          console.error('하이라이트 저장 실패', error);
        });

      hideToolbar();
      window.getSelection()?.removeAllRanges();
    }

    function attachCommentHandler(
      mark: HTMLElement,
      highlightId: string,
      comment: string,
    ) {
      for (const piece of marksInPaintGroup(mark)) {
        piece.dataset.highlightId = highlightId;
        piece.dataset.comment = comment;
        piece.addEventListener('click', (event) => {
          event.stopPropagation();
          openCommentBox(piece, highlightId);
        });
      }
    }

    toolbar.host.addEventListener('color-pick', (event) => {
      if (!(event instanceof CustomEvent)) return;
      savePendingHighlight(event.detail.color as string, false);
    });

    toolbar.host.addEventListener('comment-shortcut', () => {
      savePendingHighlight(DEFAULT_HIGHLIGHT_COLOR, true);
    });

    toolbar.host.addEventListener('dismiss', () => {
      pending = null;
    });

    commentBox.host.addEventListener('comment-save', (event) => {
      if (!(event instanceof CustomEvent)) return;
      if (!activeHighlightId) return;
      const comment = event.detail.comment as string;
      if (activeMark) {
        for (const piece of marksInPaintGroup(activeMark)) {
          piece.dataset.comment = comment;
        }
      }

      const message: UpdateCommentMessage = {
        type: 'UPDATE_COMMENT',
        payload: { id: activeHighlightId, comment },
      };
      browser.runtime.sendMessage(message).catch((error) => {
        console.error('코멘트 저장 실패', error);
      });

      hideCommentBox();
    });

    commentBox.host.addEventListener('goto-source', () => {
      activeMark?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    commentBox.host.addEventListener('dismiss', () => {
      activeHighlightId = null;
      activeMark = null;
    });

    document.addEventListener('mouseup', (event) => {
      if (eventPathContains(event, toolbar.host)) return;
      if (eventPathContains(event, commentBox.host)) return;

      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        hideToolbar();
        return;
      }

      const range = selection.getRangeAt(0);
      const quote = range.toString().trim();
      if (!quote) {
        hideToolbar();
        return;
      }

      const startNode = range.commonAncestorContainer;
      const containerEl =
        startNode.nodeType === Node.TEXT_NODE
          ? startNode.parentElement
          : (startNode as Element);
      const blockEl = containerEl?.closest('p, li, h1, h2, h3, h4, h5, h6');
      if (!blockEl) {
        hideToolbar();
        return;
      }

      const { prefix, suffix } = extractContext(blockEl, quote);
      pending = { range: range.cloneRange(), quote, prefix, suffix };

      hideCommentBox();
      toolbar.showAbove(range.getBoundingClientRect());
    });

    document.addEventListener(
      'click',
      (event) => {
        if (eventPathContains(event, commentBox.host)) return;
        hideCommentBox();
      },
      true,
    );

    document.addEventListener(
      'scroll',
      () => {
        hideToolbar();
        hideCommentBox();
      },
      true,
    );

    browser.runtime.onMessage.addListener((message: CommentUpdatedMessage) => {
      if (message.type !== 'COMMENT_UPDATED') return;
      if (message.payload.pageKey !== pageKey) return;
      document
        .querySelectorAll(`mark[data-highlight-id="${message.payload.id}"]`)
        .forEach((mark) => {
          if (mark instanceof HTMLElement) {
            mark.dataset.comment = message.payload.comment;
          }
        });
    });

    const getHighlightsMessage: GetHighlightsMessage = {
      type: 'GET_HIGHLIGHTS',
      payload: { pageKey },
    };
    browser.runtime
      .sendMessage(getHighlightsMessage)
      .then((records: HighlightRecord[]) => {
        if (!records?.length) return;
        // Painting each record mutates the DOM (wrap splits text nodes), so
        // flattened text/offsets must be recomputed fresh before every
        // record — reusing one snapshot across records goes stale after
        // the first paint and produces out-of-range offsets for the rest.
        records.forEach((record) => {
          try {
            const { text, spans } = flattenText(document.body);
            const mark = resolveAndPaint(record, spans, text);
            if (mark) attachCommentHandler(mark, record.id, record.comment ?? '');
          } catch (error) {
            console.error('하이라이트 복원 실패', record.id, error);
          }
        });
      })
      .catch((error) => {
        console.error('하이라이트 복원 실패', error);
      });
  },
});
