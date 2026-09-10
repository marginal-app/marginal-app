import { OVERLAY_HOST_STYLES } from '@/components/overlay-styles';
import {
  closePopover,
  createOverlayHost,
  isPopoverOpen,
  openPopover,
} from '@/components/popover';

export type CommentSaveEvent = CustomEvent<{ comment: string }>;

const STYLES = `
${OVERLAY_HOST_STYLES}

.box {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 300px;
  padding: 12px 12px 10px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow:
    0 1px 1px rgba(20, 20, 30, 0.04),
    0 8px 12px rgba(20, 20, 30, 0.06);
}

.quote-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.quote-bar {
  width: 3px;
  align-self: stretch;
  border-radius: 1.5px;
  background: var(--highlight-yellow, #fff3b0);
  flex-shrink: 0;
}

.quote {
  margin: 0;
  flex: 1;
  min-width: 0;
  font-size: 13px;
  line-height: 19px;
  color: var(--text-secondary);
}

textarea {
  width: 100%;
  height: 72px;
  resize: none;
  padding: 8px 10px;
  font: inherit;
  font-size: 13px;
  line-height: 19px;
  color: var(--text);
  background: var(--bg);
  border: 1px solid var(--accent);
  border-radius: var(--radius);
}

textarea::placeholder {
  color: var(--text-secondary);
}

.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.goto {
  border: none;
  padding: 0;
  font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.8px;
  line-height: 14px;
  color: var(--text-secondary);
  background: transparent;
}

.save {
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font: inherit;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: -0.14px;
  background: var(--accent);
  color: var(--accent-text);
}
`;

export class CommentPopover {
  static readonly tag = 'marginal-comment-popover';

  readonly host: HTMLElement;
  #quote: HTMLParagraphElement;
  #bar: HTMLDivElement;
  #textarea: HTMLTextAreaElement;

  constructor() {
    this.host = createOverlayHost(CommentPopover.tag, STYLES);

    const box = document.createElement('div');
    box.className = 'box';

    const quoteRow = document.createElement('div');
    quoteRow.className = 'quote-row';

    this.#bar = document.createElement('div');
    this.#bar.className = 'quote-bar';

    this.#quote = document.createElement('p');
    this.#quote.className = 'quote';

    quoteRow.append(this.#bar, this.#quote);

    this.#textarea = document.createElement('textarea');
    this.#textarea.setAttribute('aria-label', '코멘트');
    this.#textarea.placeholder = '코멘트를 남기세요…';

    const actions = document.createElement('div');
    actions.className = 'actions';

    const gotoButton = document.createElement('button');
    gotoButton.type = 'button';
    gotoButton.className = 'goto';
    gotoButton.textContent = '원문으로';
    gotoButton.addEventListener('click', () => {
      this.host.dispatchEvent(
        new Event('goto-source', { bubbles: true, composed: true }),
      );
    });

    const saveButton = document.createElement('button');
    saveButton.type = 'button';
    saveButton.className = 'save';
    saveButton.textContent = '저장';
    saveButton.addEventListener('click', () => {
      this.host.dispatchEvent(
        new CustomEvent('comment-save', {
          detail: { comment: this.#textarea.value },
          bubbles: true,
          composed: true,
        }),
      );
    });

    actions.append(gotoButton, saveButton);
    box.append(quoteRow, this.#textarea, actions);
    this.host.shadowRoot!.append(box);

    this.host.addEventListener('keydown', (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return;
      event.stopPropagation();
      this.hide();
      this.host.dispatchEvent(new Event('dismiss', { bubbles: true }));
    });
  }

  get comment(): string {
    return this.#textarea.value;
  }

  set comment(value: string) {
    this.#textarea.value = value;
  }

  set quote(value: string) {
    this.#quote.textContent = value;
  }

  set accentColor(value: string) {
    this.#bar.style.backgroundColor = value || 'var(--highlight-yellow, #fff3b0)';
  }

  get open(): boolean {
    return isPopoverOpen(this.host);
  }

  showBelow(rect: DOMRectReadOnly, viewportWidth = window.innerWidth) {
    const estimatedWidth = this.host.offsetWidth || 300;
    this.host.style.top = `${rect.bottom + 8}px`;
    this.host.style.left = `${Math.max(Math.min(rect.left, viewportWidth - estimatedWidth - 16), 8)}px`;
    openPopover(this.host);
    const width = this.host.offsetWidth || estimatedWidth;
    this.host.style.left = `${Math.max(Math.min(rect.left, viewportWidth - width - 16), 8)}px`;
  }

  hide() {
    closePopover(this.host);
  }

  focusInput() {
    this.#textarea.focus();
  }
}
