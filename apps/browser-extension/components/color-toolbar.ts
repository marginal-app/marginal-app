import commentGlyphUrl from '@/assets/icons/comment.svg?url';
import { OVERLAY_HOST_STYLES } from '@/components/overlay-styles';
import {
  closePopover,
  createOverlayHost,
  isPopoverOpen,
  openPopover,
} from '@/components/popover';

export const HIGHLIGHT_COLORS = [
  '#FFF3B0',
  '#FFD6E0',
  '#C9F2C7',
  '#C7E8FF',
  '#E3D4FF',
] as const;

export const DEFAULT_HIGHLIGHT_COLOR = HIGHLIGHT_COLORS[0];

export type ColorPickEvent = CustomEvent<{ color: string }>;

const STYLES = `
${OVERLAY_HOST_STYLES}

.bar {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 6px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 999px;
  box-shadow:
    0 1px 1px rgba(20, 20, 30, 0.04),
    0 8px 12px rgba(20, 20, 30, 0.06);
}

.dot {
  width: 18px;
  height: 18px;
  padding: 0;
  border: none;
  border-radius: 50%;
  cursor: pointer;
}

.rule {
  width: 1px;
  height: 14px;
  background: var(--border);
  flex-shrink: 0;
}

.comment {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  padding: 0;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
}

.comment img {
  display: block;
  width: 16px;
  height: 16px;
}

.comment:hover {
  background: var(--bg-elevated);
}
`;

export class ColorToolbar {
  static readonly tag = 'marginal-color-toolbar';

  readonly host: HTMLElement;
  #bar: HTMLDivElement;

  constructor() {
    this.host = createOverlayHost(ColorToolbar.tag, STYLES);
    this.#bar = document.createElement('div');
    this.#bar.className = 'bar';
    this.host.shadowRoot!.append(this.#bar);

    this.host.addEventListener('keydown', (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      event.stopPropagation();
      this.hide();
      this.host.dispatchEvent(new Event('dismiss', { bubbles: true }));
    });
  }

  set colors(value: readonly string[]) {
    this.#bar.replaceChildren();
    for (const color of value) {
      const dot = document.createElement('button');
      dot.type = 'button';
      dot.className = 'dot';
      dot.dataset.color = color;
      dot.style.backgroundColor = color;
      dot.setAttribute('aria-label', `Highlight with ${color}`);
      dot.addEventListener('click', () => {
        this.host.dispatchEvent(
          new CustomEvent('color-pick', {
            detail: { color },
            bubbles: true,
            composed: true,
          }),
        );
      });
      this.#bar.append(dot);
    }

    const rule = document.createElement('div');
    rule.className = 'rule';
    rule.setAttribute('aria-hidden', 'true');
    this.#bar.append(rule);

    const comment = document.createElement('button');
    comment.type = 'button';
    comment.className = 'comment';
    comment.setAttribute('aria-label', '코멘트 남기기');
    const glyph = document.createElement('img');
    glyph.src = commentGlyphUrl;
    glyph.alt = '';
    glyph.width = 16;
    glyph.height = 16;
    comment.append(glyph);
    comment.addEventListener('click', () => {
      this.host.dispatchEvent(
        new Event('comment-shortcut', { bubbles: true, composed: true }),
      );
    });
    this.#bar.append(comment);
  }

  get open(): boolean {
    return isPopoverOpen(this.host);
  }

  showAbove(rect: DOMRectReadOnly) {
    this.host.style.top = `${Math.max(rect.top, 8)}px`;
    this.host.style.left = `${rect.left}px`;
    openPopover(this.host);
    const top = Math.max(rect.top - this.host.offsetHeight - 8, 8);
    const left = rect.left + rect.width / 2 - this.host.offsetWidth / 2;
    this.host.style.top = `${top}px`;
    this.host.style.left = `${Math.max(left, 8)}px`;
  }

  hide() {
    closePopover(this.host);
  }
}
