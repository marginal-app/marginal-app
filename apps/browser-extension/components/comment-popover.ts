import { adoptStyles, OVERLAY_HOST_STYLES } from '@/components/overlay-styles';
import {
  bindPopoverHost,
  closePopover,
  defineOnce,
  isPopoverOpen,
  openPopover,
} from '@/components/popover';

export type CommentSaveEvent = CustomEvent<{ comment: string }>;

const STYLES = `
${OVERLAY_HOST_STYLES}

.box {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 220px;
  padding: 10px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 10px 30px rgba(20, 20, 30, 0.08);
}

textarea {
  width: 100%;
  min-height: 60px;
  resize: vertical;
  padding: 6px;
  font: inherit;
  font-size: 13px;
  color: var(--text);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.actions {
  display: flex;
  justify-content: space-between;
  gap: 6px;
}

button {
  font: inherit;
  cursor: pointer;
}

.goto {
  border: none;
  border-radius: var(--radius);
  padding: 4px 8px;
  font-size: 12px;
  color: var(--text-secondary);
  background: transparent;
}

.save {
  border: none;
  border-radius: var(--radius);
  padding: 0.3rem 0.6rem;
  font-size: 0.78rem;
  font-weight: 600;
  background: var(--accent);
  color: var(--accent-text);
}
`;

export class CommentPopover extends HTMLElement {
  static readonly tag = 'marginal-comment-popover';

  #textarea: HTMLTextAreaElement;

  constructor() {
    super();
    const root = this.attachShadow({ mode: 'open' });
    adoptStyles(root, STYLES);

    const box = document.createElement('div');
    box.className = 'box';

    this.#textarea = document.createElement('textarea');
    this.#textarea.setAttribute('aria-label', 'Comment');

    const actions = document.createElement('div');
    actions.className = 'actions';

    const gotoButton = document.createElement('button');
    gotoButton.type = 'button';
    gotoButton.className = 'goto';
    gotoButton.textContent = '패널에서 보기';
    gotoButton.addEventListener('click', () => {
      this.dispatchEvent(
        new Event('goto-panel', { bubbles: true, composed: true }),
      );
    });

    const saveButton = document.createElement('button');
    saveButton.type = 'button';
    saveButton.className = 'save';
    saveButton.textContent = '저장';
    saveButton.addEventListener('click', () => {
      this.dispatchEvent(
        new CustomEvent('comment-save', {
          detail: { comment: this.#textarea.value },
          bubbles: true,
          composed: true,
        }),
      );
    });

    actions.append(gotoButton, saveButton);
    box.append(this.#textarea, actions);
    root.append(box);

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

  get comment(): string {
    return this.#textarea.value;
  }

  set comment(value: string) {
    this.#textarea.value = value;
  }

  get open(): boolean {
    return isPopoverOpen(this);
  }

  showBelow(rect: DOMRectReadOnly, viewportWidth = window.innerWidth) {
    const estimatedWidth = this.offsetWidth || 220;
    this.style.top = `${rect.bottom + 8}px`;
    this.style.left = `${Math.max(Math.min(rect.left, viewportWidth - estimatedWidth - 16), 8)}px`;
    openPopover(this);
    const width = this.offsetWidth || estimatedWidth;
    this.style.left = `${Math.max(Math.min(rect.left, viewportWidth - width - 16), 8)}px`;
  }

  hide() {
    closePopover(this);
  }

  focusInput() {
    this.#textarea.focus();
  }
}

defineOnce(CommentPopover.tag, CommentPopover);

declare global {
  interface HTMLElementTagNameMap {
    'marginal-comment-popover': CommentPopover;
  }
}
