import { afterEach, describe, expect, it } from 'vitest';
import { CommentPopover } from '@/components/comment-popover';

afterEach(() => {
  document.querySelectorAll(CommentPopover.tag).forEach((el) => el.remove());
});

function mountPopover() {
  const popover = new CommentPopover();
  document.body.append(popover.host);
  return popover;
}

function rect(overrides: Partial<DOMRectReadOnly> = {}): DOMRectReadOnly {
  return {
    x: 0,
    y: 0,
    top: 40,
    left: 80,
    width: 120,
    height: 18,
    bottom: 58,
    right: 200,
    toJSON() {
      return this;
    },
    ...overrides,
  };
}

describe('CommentPopover', () => {
  it('round-trips the comment value through the textarea', () => {
    const popover = mountPopover();

    popover.comment = 'hello';
    expect(popover.comment).toBe('hello');
    expect(
      popover.host.shadowRoot!.querySelector('textarea')?.value,
    ).toBe('hello');
  });

  it('emits comment-save with the current textarea value', () => {
    const popover = mountPopover();
    popover.comment = 'note';

    let saved: string | undefined;
    popover.host.addEventListener('comment-save', (event) => {
      saved = (event as CustomEvent<{ comment: string }>).detail.comment;
    });
    popover.host.shadowRoot!.querySelector<HTMLButtonElement>('.save')?.click();

    expect(saved).toBe('note');
  });

  it('renders the quote and emits goto-source', () => {
    const popover = mountPopover();
    popover.quote = 'Server-rendered HTML is a complete first paint.';
    popover.accentColor = '#FFF3B0';

    expect(popover.host.shadowRoot!.querySelector('.quote')?.textContent).toBe(
      'Server-rendered HTML is a complete first paint.',
    );

    let jumped = false;
    popover.host.addEventListener('goto-source', () => {
      jumped = true;
    });
    popover.host.shadowRoot!.querySelector<HTMLButtonElement>('.goto')?.click();

    expect(jumped).toBe(true);
    expect(
      popover.host.shadowRoot!.querySelector<HTMLButtonElement>('.goto')
        ?.textContent,
    ).toBe('원문으로');
  });

  it('opens below a rect, clamped to the viewport, and hides again', () => {
    const popover = mountPopover();

    popover.showBelow(rect({ left: 900 }), 400);

    expect(popover.open).toBe(true);
    const left = Number.parseFloat(popover.host.style.left);
    expect(left).toBeGreaterThanOrEqual(8);
    expect(left).toBeLessThan(400);
    expect(popover.host.style.top).toBe('66px');

    popover.hide();
    expect(popover.open).toBe(false);
  });
});
