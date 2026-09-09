import { ColorToolbar, HIGHLIGHT_COLORS } from '@/components/color-toolbar';
import { CommentPopover } from '@/components/comment-popover';
import { eventPathContains } from '@/components/popover';
import type {
  CommentUpdatedMessage,
  GetHighlightsMessage,
  HighlightRecord,
  OpenSidePanelMessage,
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
  record: HighlightRecord,
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
      commentBox.showBelow(mark.getBoundingClientRect());
      commentBox.focusInput();
    }

    function attachCommentHandler(
      mark: HTMLElement,
      highlightId: string,
      comment: string,
    ) {
      mark.dataset.highlightId = highlightId;
      mark.dataset.comment = comment;
      mark.addEventListener('click', (event) => {
        event.stopPropagation();
        openCommentBox(mark, highlightId);
      });
    }

    toolbar.host.addEventListener('color-pick', (event) => {
      if (!(event instanceof CustomEvent)) return;
      if (!pending) return;
      const color = event.detail.color as string;
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
          if (mark) attachCommentHandler(mark, record.id, '');
        })
        .catch((error) => {
          console.error('하이라이트 저장 실패', error);
        });

      hideToolbar();
      window.getSelection()?.removeAllRanges();
    });

    toolbar.host.addEventListener('dismiss', () => {
      pending = null;
    });

    commentBox.host.addEventListener('comment-save', (event) => {
      if (!(event instanceof CustomEvent)) return;
      if (!activeHighlightId) return;
      const comment = event.detail.comment as string;
      if (activeMark) activeMark.dataset.comment = comment;

      const message: UpdateCommentMessage = {
        type: 'UPDATE_COMMENT',
        payload: { id: activeHighlightId, comment },
      };
      browser.runtime.sendMessage(message).catch((error) => {
        console.error('코멘트 저장 실패', error);
      });

      hideCommentBox();
    });

    commentBox.host.addEventListener('goto-panel', () => {
      if (!activeHighlightId) return;
      const message: OpenSidePanelMessage = {
        type: 'OPEN_SIDE_PANEL',
        payload: { highlightId: activeHighlightId },
      };
      browser.runtime.sendMessage(message).catch((error) => {
        console.error('side panel 열기 실패', error);
      });
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
      const mark = document.querySelector(
        `mark[data-highlight-id="${message.payload.id}"]`,
      );
      if (mark instanceof HTMLElement) {
        mark.dataset.comment = message.payload.comment;
      }
    });

    const getHighlightsMessage: GetHighlightsMessage = {
      type: 'GET_HIGHLIGHTS',
      payload: { pageKey },
    };
    browser.runtime
      .sendMessage(getHighlightsMessage)
      .then((records: HighlightRecord[]) => {
        if (!records?.length) return;
        // Painting each record mutates the DOM (splits text nodes), so the
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
