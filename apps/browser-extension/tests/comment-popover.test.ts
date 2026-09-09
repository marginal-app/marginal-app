import { afterEach, describe, expect, it } from 'vitest';
import { CommentPopover } from '@/components/comment-popover';

afterEach(() => {
  document.querySelectorAll(CommentPopover.tag).forEach((el) => el.remove());
});

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
    const popover = document.createElement(CommentPopover.tag);
    document.body.append(popover);

    popover.comment = 'hello';
    expect(popover.comment).toBe('hello');
    expect(
      popover.shadowRoot!.querySelector('textarea')?.value,
    ).toBe('hello');
  });

  it('emits comment-save with the current textarea value', () => {
    const popover = document.createElement(CommentPopover.tag);
    document.body.append(popover);
    popover.comment = 'note';

    let saved: string | undefined;
    popover.addEventListener('comment-save', (event) => {
      saved = (event as CustomEvent<{ comment: string }>).detail.comment;
    });
    popover.shadowRoot!.querySelector<HTMLButtonElement>('.save')?.click();

    expect(saved).toBe('note');
  });

  it('emits goto-panel', () => {
    const popover = document.createElement(CommentPopover.tag);
    document.body.append(popover);

    let jumped = false;
    popover.addEventListener('goto-panel', () => {
      jumped = true;
    });
    popover.shadowRoot!.querySelector<HTMLButtonElement>('.goto')?.click();

    expect(jumped).toBe(true);
  });

  it('opens below a rect, clamped to the viewport, and hides again', () => {
    const popover = document.createElement(CommentPopover.tag);
    document.body.append(popover);

    popover.showBelow(rect({ left: 900 }), 400);

    expect(popover.open).toBe(true);
    const left = Number.parseFloat(popover.style.left);
    expect(left).toBeGreaterThanOrEqual(8);
    expect(left).toBeLessThan(400);
    expect(popover.style.top).toBe('66px');

    popover.hide();
    expect(popover.open).toBe(false);
  });
});
