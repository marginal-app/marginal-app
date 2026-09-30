import {
  extractContext,
  findToolbarBlock,
  flattenText,
  marksInPaintGroup,
  paintRange,
  quoteOffsetInBlock,
  resolveAndPaint,
  shouldPersistHighlight,
  type HighlightAnchor,
  type StoredHighlight,
} from './anchor';
import { ColorToolbar, DEFAULT_HIGHLIGHT_COLOR, HIGHLIGHT_COLORS } from './color-toolbar';
import { CommentPopover } from './comment-popover';
import { eventPathContains } from './popover';

// The only thing the highlighter knows about its host. The extension's port
// talks to `browser.runtime`; the mobile port talks to the Flutter bridge.
export interface HighlightPort {
  save(anchor: HighlightAnchor): Promise<StoredHighlight>;
  list(): Promise<StoredHighlight[]>;
  updateComment(id: string, comment: string): Promise<void>;
  onCommentUpdated?(listener: (id: string, comment: string) => void): void;
}

// Desktop selection ends on `mouseup`. Touch selection (long-press, then
// dragging native handles) never fires a reliable mouseup, so mobile waits
// for `selectionchange` to go quiet instead.
export type SelectionTrigger =
  | { kind: 'mouseup' }
  | { kind: 'selectionchange'; settleMs: number };

export interface HighlighterOptions {
  port: HighlightPort;
  trigger: SelectionTrigger;
}

export interface Highlighter {
  toolbar: ColorToolbar;
  commentBox: CommentPopover;
  restore(): Promise<void>;
}

export function mountHighlighter({ port, trigger }: HighlighterOptions): Highlighter {
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
    if (!mark || !shouldPersistHighlight(mark)) {
      hideToolbar();
      window.getSelection()?.removeAllRanges();
      return;
    }

    port
      .save({ quote, prefix, suffix, color })
      .then((record) => {
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

  function handleSelection() {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed || selection.rangeCount === 0) {
      hideToolbar();
      return;
    }

    const range = selection.getRangeAt(0);
    const quote = range.toString().trim();
    if (!quote) {
      hideToolbar();
      return;
    }

    const blockEl = findToolbarBlock(range);
    if (!blockEl) {
      hideToolbar();
      return;
    }

    const { prefix, suffix } = extractContext(
      blockEl,
      quote,
      6,
      quoteOffsetInBlock(blockEl, range),
    );
    pending = { range: range.cloneRange(), quote, prefix, suffix };

    hideCommentBox();
    toolbar.showAbove(range.getBoundingClientRect());
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

    port.updateComment(activeHighlightId, comment).catch((error) => {
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

  if (trigger.kind === 'mouseup') {
    document.addEventListener('mouseup', (event) => {
      if (eventPathContains(event, toolbar.host)) return;
      if (eventPathContains(event, commentBox.host)) return;
      handleSelection();
    });
  } else {
    // Tapping a toolbar dot can collapse the native selection before the
    // click lands. `pending` holds a cloned range, and the settle delay lets
    // the click win before a collapsed selection hides the toolbar.
    let settle: ReturnType<typeof setTimeout> | undefined;
    document.addEventListener('selectionchange', () => {
      clearTimeout(settle);
      settle = setTimeout(handleSelection, trigger.settleMs);
    });
  }

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

  port.onCommentUpdated?.((id, comment) => {
    document
      .querySelectorAll(`mark[data-highlight-id="${id}"]`)
      .forEach((mark) => {
        if (mark instanceof HTMLElement) {
          mark.dataset.comment = comment;
        }
      });
  });

  async function restore() {
    const records = await port.list();
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
  }

  return { toolbar, commentBox, restore };
}
