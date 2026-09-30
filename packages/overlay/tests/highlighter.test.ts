import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { HighlightAnchor, StoredHighlight } from '../src/anchor';
import { ColorToolbar } from '../src/color-toolbar';
import { CommentPopover } from '../src/comment-popover';
import { mountHighlighter, type HighlightPort } from '../src/highlighter';

function fakePort(stored: StoredHighlight[] = []) {
  const saved: HighlightAnchor[] = [];
  const port: HighlightPort = {
    save: vi.fn(async (anchor: HighlightAnchor) => {
      saved.push(anchor);
      return { id: `h${saved.length}`, ...anchor };
    }),
    list: vi.fn(async () => stored),
    updateComment: vi.fn(async () => {}),
  };
  return { port, saved };
}

function selectWord(word: string) {
  const p = document.querySelector('p')!;
  const textNode = p.firstChild as Text;
  const start = textNode.data.indexOf(word);
  const range = document.createRange();
  range.setStart(textNode, start);
  range.setEnd(textNode, start + word.length);
  const selection = window.getSelection()!;
  selection.removeAllRanges();
  selection.addRange(range);
}

function pickColor(toolbar: ColorToolbar, color: string) {
  toolbar.host.shadowRoot!
    .querySelector<HTMLButtonElement>(`button[data-color="${color}"]`)!
    .click();
}

beforeEach(() => {
  // jsdom has no layout; the toolbar only needs a rect to position against.
  Range.prototype.getBoundingClientRect = () => new DOMRect(40, 100, 60, 18);
  document.body.innerHTML =
    '<p>This domain is for use in documentation examples without needing permission.</p>';
});

afterEach(() => {
  document
    .querySelectorAll(`${ColorToolbar.tag}, ${CommentPopover.tag}`)
    .forEach((el) => el.remove());
  vi.useRealTimers();
});

describe('mountHighlighter', () => {
  it('mouseup: opens the toolbar over the selection and saves the anchor through the port', async () => {
    const { port, saved } = fakePort();
    const { toolbar } = mountHighlighter({ port, trigger: { kind: 'mouseup' } });

    selectWord('documentation');
    document.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
    expect(toolbar.open).toBe(true);

    pickColor(toolbar, '#C9F2C7');
    await vi.waitFor(() => expect(port.save).toHaveBeenCalled());

    expect(saved[0]).toEqual({
      quote: 'documentation',
      prefix: 'This domain is for use in',
      suffix: 'examples without needing permission.',
      color: '#C9F2C7',
    });
    expect(document.querySelector('mark')?.textContent).toBe('documentation');
    expect(toolbar.open).toBe(false);
    await vi.waitFor(() =>
      expect(document.querySelector('mark')?.dataset.highlightId).toBe('h1'),
    );
  });

  it('selectionchange: waits for the selection to settle before opening the toolbar', () => {
    vi.useFakeTimers();
    const { port } = fakePort();
    const { toolbar } = mountHighlighter({
      port,
      trigger: { kind: 'selectionchange', settleMs: 250 },
    });

    selectWord('documentation');
    document.dispatchEvent(new Event('selectionchange'));
    vi.advanceTimersByTime(200);
    expect(toolbar.open).toBe(false);

    vi.advanceTimersByTime(60);
    expect(toolbar.open).toBe(true);
  });

  it('selectionchange: a tap that collapses the selection still saves the pending range', async () => {
    vi.useFakeTimers();
    const { port, saved } = fakePort();
    const { toolbar } = mountHighlighter({
      port,
      trigger: { kind: 'selectionchange', settleMs: 250 },
    });

    selectWord('examples');
    document.dispatchEvent(new Event('selectionchange'));
    vi.advanceTimersByTime(250);

    window.getSelection()!.removeAllRanges();
    document.dispatchEvent(new Event('selectionchange'));
    pickColor(toolbar, '#FFF3B0');

    expect(saved[0]?.quote).toBe('examples');
    expect(document.querySelector('mark')?.textContent).toBe('examples');
  });

  it('restore paints stored highlights returned by the port', async () => {
    const { port } = fakePort([
      {
        id: 'r1',
        quote: 'documentation',
        prefix: 'for use in',
        suffix: 'examples',
        color: '#C7E8FF',
        comment: 'note',
      },
    ]);
    const highlighter = mountHighlighter({ port, trigger: { kind: 'mouseup' } });

    await highlighter.restore();

    const mark = document.querySelector('mark')!;
    expect(mark.textContent).toBe('documentation');
    expect(mark.dataset.highlightId).toBe('r1');
    expect(mark.dataset.comment).toBe('note');
  });
});
