import { adoptStyles, OVERLAY_HOST_STYLES } from '@/components/overlay-styles';
import {
  bindPopoverHost,
  closePopover,
  defineOnce,
  isPopoverOpen,
  openPopover,
} from '@/components/popover';

export const HIGHLIGHT_COLORS = [
  '#FFF3B0',
  '#FFD6E0',
  '#C9F2C7',
  '#C7E8FF',
  '#E3D4FF',
];

export type ColorPickEvent = CustomEvent<{ color: string }>;

const STYLES = `
${OVERLAY_HOST_STYLES}

.bar {
  display: flex;
  gap: 6px;
  padding: 6px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 999px;
  box-shadow: 0 10px 30px rgba(20, 20, 30, 0.08);
}

.dot {
  width: 18px;
  height: 18px;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: 50%;
  cursor: pointer;
}
`;

export class ColorToolbar extends HTMLElement {
  static readonly tag = 'marginal-color-toolbar';

  #bar: HTMLDivElement;

  constructor() {
    super();
    const root = this.attachShadow({ mode: 'open' });
    adoptStyles(root, STYLES);

    this.#bar = document.createElement('div');
    this.#bar.className = 'bar';
    root.append(this.#bar);

    this.addEventListener('keydown', (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      event.stopPropagation();
      this.hide();
      this.dispatchEvent(new Event('dismiss', { bubbles: true }));
    });
  }

  connectedCallback() {
    bindPopoverHost(this);
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
        this.dispatchEvent(
          new CustomEvent('color-pick', {
            detail: { color },
            bubbles: true,
            composed: true,
          }),
        );
      });
      this.#bar.append(dot);
    }
  }

  get open(): boolean {
    return isPopoverOpen(this);
  }

  showAbove(rect: DOMRectReadOnly) {
    this.style.top = `${Math.max(rect.top, 8)}px`;
    this.style.left = `${rect.left}px`;
    openPopover(this);
    const top = Math.max(rect.top - this.offsetHeight - 8, 8);
    const left = rect.left + rect.width / 2 - this.offsetWidth / 2;
    this.style.top = `${top}px`;
    this.style.left = `${Math.max(left, 8)}px`;
  }

  hide() {
    closePopover(this);
  }
}

defineOnce(ColorToolbar.tag, ColorToolbar);

declare global {
  interface HTMLElementTagNameMap {
    'marginal-color-toolbar': ColorToolbar;
  }
}
