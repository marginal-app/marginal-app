import type {
  CommentUpdatedMessage,
  GetHighlightsMessage,
  HighlightRecord,
  OpenSidePanelMessage,
  SaveHighlightMessage,
  UpdateCommentMessage,
} from '@/utils/highlight-messages';

const PASTEL_COLORS = ['#FFF3B0', '#FFD6E0', '#C9F2C7', '#C7E8FF', '#E3D4FF'];

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

export function pathContains(event: Event, el: Element): boolean {
  // Elements rendered inside a shadow root (our toolbar/comment box) get
  // retargeted to the shadow host when observed from a listener outside the
  // shadow tree, so `event.target` is useless for containment checks here —
  // `composedPath()` still carries the real, un-retargeted path.
  return event.composedPath().includes(el);
}

function styleSmallButton(button: HTMLButtonElement) {
  button.style.border = 'none';
  button.style.borderRadius = '4px';
  button.style.padding = '4px 8px';
  button.style.fontSize = '12px';
  button.style.cursor = 'pointer';
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

    let activeHighlightId: string | null = null;
    let activeMark: HTMLElement | null = null;

    const ui = await createShadowRootUi(ctx, {
      name: 'marginal-toolbar',
      position: 'overlay',
      anchor: () => document.body,
      zIndex: 2147483647,
      onMount(container) {
        const toolbar = document.createElement('div');
        toolbar.style.position = 'fixed';
        toolbar.style.display = 'none';
        toolbar.style.gap = '6px';
        toolbar.style.padding = '6px';
        toolbar.style.background = '#1f1f1f';
        toolbar.style.borderRadius = '999px';
        toolbar.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
        toolbar.style.zIndex = '2147483647';

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

            const mark = paintRange(range, color);

            const message: SaveHighlightMessage = {
              type: 'SAVE_HIGHLIGHT',
              payload: { pageKey, quote, prefix, suffix, color },
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

          toolbar.appendChild(dot);
        });

        const commentBox = document.createElement('div');
        commentBox.style.position = 'fixed';
        commentBox.style.display = 'none';
        commentBox.style.flexDirection = 'column';
        commentBox.style.gap = '6px';
        commentBox.style.width = '220px';
        commentBox.style.padding = '10px';
        commentBox.style.background = '#1f1f1f';
        commentBox.style.borderRadius = '8px';
        commentBox.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
        commentBox.style.zIndex = '2147483647';

        const textarea = document.createElement('textarea');
        textarea.style.width = '100%';
        textarea.style.minHeight = '60px';
        textarea.style.resize = 'vertical';
        textarea.style.border = 'none';
        textarea.style.borderRadius = '4px';
        textarea.style.padding = '6px';
        textarea.style.fontSize = '13px';
        textarea.style.boxSizing = 'border-box';
        commentBox.appendChild(textarea);

        const actions = document.createElement('div');
        actions.style.display = 'flex';
        actions.style.justifyContent = 'space-between';
        actions.style.gap = '6px';

        const gotoButton = document.createElement('button');
        gotoButton.textContent = '패널에서 보기';
        styleSmallButton(gotoButton);

        const saveButton = document.createElement('button');
        saveButton.textContent = '저장';
        styleSmallButton(saveButton);

        actions.appendChild(gotoButton);
        actions.appendChild(saveButton);
        commentBox.appendChild(actions);

        container.appendChild(toolbar);
        container.appendChild(commentBox);
        return { toolbar, commentBox, textarea, gotoButton, saveButton };
      },
    });
    ui.mount();
    const { toolbar: toolbarEl, commentBox, textarea, gotoButton, saveButton } =
      ui.mounted!;

    function hideToolbar() {
      toolbarEl.style.display = 'none';
      pending = null;
    }

    function hideCommentBox() {
      commentBox.style.display = 'none';
      activeHighlightId = null;
      activeMark = null;
    }

    function openCommentBox(mark: HTMLElement, highlightId: string) {
      activeHighlightId = highlightId;
      activeMark = mark;
      textarea.value = mark.dataset.comment ?? '';

      const rect = mark.getBoundingClientRect();
      commentBox.style.display = 'flex';
      commentBox.style.top = `${rect.bottom + 8}px`;
      commentBox.style.left = `${Math.min(rect.left, window.innerWidth - 236)}px`;
      textarea.focus();
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

    saveButton.addEventListener('click', () => {
      if (!activeHighlightId) return;
      if (activeMark) activeMark.dataset.comment = textarea.value;

      const message: UpdateCommentMessage = {
        type: 'UPDATE_COMMENT',
        payload: { id: activeHighlightId, comment: textarea.value },
      };
      browser.runtime.sendMessage(message).catch((error) => {
        console.error('코멘트 저장 실패', error);
      });

      hideCommentBox();
    });

    gotoButton.addEventListener('click', () => {
      if (!activeHighlightId) return;
      const message: OpenSidePanelMessage = {
        type: 'OPEN_SIDE_PANEL',
        payload: { highlightId: activeHighlightId },
      };
      browser.runtime.sendMessage(message).catch((error) => {
        console.error('side panel 열기 실패', error);
      });
    });

    document.addEventListener('mouseup', (event) => {
      if (pathContains(event, toolbarEl)) return;
      if (pathContains(event, commentBox)) return;

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

    document.addEventListener(
      'click',
      (event) => {
        if (pathContains(event, commentBox)) return;
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
