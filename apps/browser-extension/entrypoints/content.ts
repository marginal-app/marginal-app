import type {
  HighlightRecord,
  SaveHighlightMessage,
  GetHighlightsMessage,
} from '@/utils/highlight-messages';

const PASTEL_COLORS = ['#FFF3B0', '#FFD6E0', '#C9F2C7', '#C7E8FF', '#E3D4FF'];

function extractContext(blockEl: Element, quote: string, wordCount = 6) {
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

function paintRange(range: Range, color: string) {
  const mark = document.createElement('mark');
  mark.style.backgroundColor = color;
  mark.style.borderRadius = '2px';

  try {
    range.surroundContents(mark);
  } catch (error) {
    console.error('여러 노드에 걸친 선택은 아직 처리 못함', error);
  }
}

interface TextSpan {
  node: Text;
  start: number;
  end: number;
}

function flattenText(root: Node): { text: string; spans: TextSpan[] } {
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

function resolveOffset(
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

function resolveAndPaint(record: HighlightRecord, spans: TextSpan[], text: string) {
  const target = record.prefix + record.quote + record.suffix;
  let idx = text.indexOf(target);
  let quoteStart: number;

  if (idx !== -1) {
    quoteStart = idx + record.prefix.length;
  } else {
    idx = text.indexOf(record.quote);
    if (idx === -1) return;
    quoteStart = idx;
  }

  const quoteEnd = quoteStart + record.quote.length;
  const start = resolveOffset(spans, quoteStart);
  const end = resolveOffset(spans, quoteEnd);
  if (!start || !end) return;

  const range = document.createRange();
  range.setStart(start.node, start.offset);
  range.setEnd(end.node, end.offset);
  paintRange(range, record.color);
}

export default defineContentScript({
  matches: ['<all_urls>'],
  runAt: 'document_idle',
  async main(ctx) {
    const pageKey = location.origin + location.pathname;

    let pending: {
      range: Range;
      quote: string;
      prefix: string;
      suffix: string;
    } | null = null;

    const ui = await createShadowRootUi(ctx, {
      name: 'marginal-toolbar',
      position: 'overlay',
      anchor: () => document.body,
      onMount(container) {
        const toolbar = document.createElement('div');
        toolbar.style.position = 'fixed';
        toolbar.style.display = 'none';
        toolbar.style.gap = '6px';
        toolbar.style.padding = '6px';
        toolbar.style.background = '#1f1f1f';
        toolbar.style.borderRadius = '999px';
        toolbar.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';

        PASTEL_COLORS.forEach((color) => {
          const dot = document.createElement('button');
          dot.style.width = '18px';
          dot.style.height = '18px';
          dot.style.borderRadius = '50%';
          dot.style.border = 'none';
          dot.style.cursor = 'pointer';
          dot.style.backgroundColor = color;

          dot.addEventListener('click', () => {
            if (!pending) return;
            const { range, quote, prefix, suffix } = pending;

            paintRange(range, color);

            const message: SaveHighlightMessage = {
              type: 'SAVE_HIGHLIGHT',
              payload: { pageKey, quote, prefix, suffix, color },
            };
            browser.runtime.sendMessage(message).catch((error) => {
              console.error('하이라이트 저장 실패', error);
            });

            hideToolbar();
            window.getSelection()?.removeAllRanges();
          });

          toolbar.appendChild(dot);
        });

        container.appendChild(toolbar);
        return toolbar;
      },
    });
    ui.mount();
    const toolbarEl = ui.mounted!;

    function hideToolbar() {
      toolbarEl.style.display = 'none';
      pending = null;
    }

    document.addEventListener('mouseup', (event) => {
      if (toolbarEl.contains(event.target as Node)) return;

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

      const rect = range.getBoundingClientRect();
      toolbarEl.style.display = 'flex';
      toolbarEl.style.top = `${Math.max(rect.top - toolbarEl.offsetHeight - 8, 8)}px`;
      toolbarEl.style.left = `${rect.left + rect.width / 2 - toolbarEl.offsetWidth / 2}px`;
    });

    document.addEventListener('scroll', hideToolbar, true);

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
            resolveAndPaint(record, spans, text);
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
