import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  ColorToolbar,
  HIGHLIGHT_COLORS,
} from '@/components/color-toolbar';
import { closePopover, eventPathContains, openPopover } from '@/components/popover';

afterEach(() => {
  document.querySelectorAll(ColorToolbar.tag).forEach((el) => el.remove());
});

function mountToolbar() {
  const toolbar = new ColorToolbar();
  toolbar.colors = HIGHLIGHT_COLORS;
  document.body.append(toolbar.host);
  return toolbar;
}

function rect(overrides: Partial<DOMRectReadOnly> = {}): DOMRectReadOnly {
  return {
    x: 0,
    y: 0,
    top: 100,
    left: 50,
    width: 40,
    height: 20,
    bottom: 120,
    right: 90,
    toJSON() {
      return this;
    },
    ...overrides,
  };
}

describe('ColorToolbar', () => {
  it('builds a hyphenated shadow host without customElements.define', () => {
    const toolbar = new ColorToolbar();
    expect(toolbar.host.tagName.toLowerCase()).toBe(ColorToolbar.tag);
    expect(toolbar.host.shadowRoot).not.toBeNull();
  });

  it('renders a swatch button per color and emits color-pick', () => {
    const toolbar = mountToolbar();

    const dots = toolbar.host.shadowRoot!.querySelectorAll<HTMLButtonElement>('.dot');
    expect(dots).toHaveLength(HIGHLIGHT_COLORS.length);
    expect(dots[0]?.dataset.color).toBe(HIGHLIGHT_COLORS[0]);

    let picked: string | undefined;
    toolbar.host.addEventListener('color-pick', (event) => {
      picked = (event as CustomEvent<{ color: string }>).detail.color;
    });
    dots[2]?.click();

    expect(picked).toBe(HIGHLIGHT_COLORS[2]);
  });

  it('opens above a rect and hides again', () => {
    const toolbar = mountToolbar();

    expect(toolbar.open).toBe(false);

    toolbar.showAbove(rect());

    expect(toolbar.open).toBe(true);
    expect(toolbar.host.hasAttribute('data-open')).toBe(true);
    expect(toolbar.host.style.top).toMatch(/px$/);
    expect(toolbar.host.style.left).toMatch(/px$/);

    toolbar.hide();
    expect(toolbar.open).toBe(false);
  });

  it('emits dismiss on Escape', () => {
    const toolbar = mountToolbar();
    toolbar.showAbove(rect());

    let dismissed = false;
    toolbar.host.addEventListener('dismiss', () => {
      dismissed = true;
    });
    toolbar.host.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));

    expect(dismissed).toBe(true);
    expect(toolbar.open).toBe(false);
  });
});

describe('eventPathContains', () => {
  it('sees a click that originated inside the shadow tree', () => {
    const toolbar = mountToolbar();
    const dot = toolbar.host.shadowRoot!.querySelector('.dot')!;

    let contained = false;
    document.addEventListener(
      'click',
      (event) => {
        contained = eventPathContains(event, toolbar.host);
      },
      { once: true },
    );
    dot.dispatchEvent(new MouseEvent('click', { bubbles: true, composed: true }));

    expect(contained).toBe(true);
  });
});

describe('openPopover / closePopover', () => {
  it('toggles data-open on a connected host', () => {
    const host = document.createElement('div');
    document.body.append(host);

    openPopover(host);
    expect(host.hasAttribute('data-open')).toBe(true);

    closePopover(host);
    expect(host.hasAttribute('data-open')).toBe(false);

    host.remove();
  });
});

describe('isolated content script registry', () => {
  it('loads ColorToolbar when customElements is null', async () => {
    vi.resetModules();
    vi.stubGlobal('customElements', null);
    try {
      const mod = await import('@/components/color-toolbar');
      const toolbar = new mod.ColorToolbar();
      expect(toolbar.host.shadowRoot).not.toBeNull();
    } finally {
      vi.unstubAllGlobals();
    }
  });
});
