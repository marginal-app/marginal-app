import { adoptStyles } from '@/components/overlay-styles';

export function supportsPopover(el: HTMLElement): boolean {
  return typeof el.showPopover === 'function';
}

export function isPopoverOpen(el: HTMLElement): boolean {
  return el.hasAttribute('data-open');
}

export function openPopover(el: HTMLElement) {
  el.setAttribute('data-open', '');
  if (!supportsPopover(el)) return;
  try {
    if (!el.matches(':popover-open')) el.showPopover();
  } catch {
    // Not connected, already open, or the engine stubbed the API.
  }
}

export function closePopover(el: HTMLElement) {
  el.removeAttribute('data-open');
  if (!supportsPopover(el)) return;
  try {
    if (el.matches(':popover-open')) el.hidePopover();
  } catch {
    // Already closed, or the engine stubbed the API.
  }
}

export function bindPopoverHost(el: HTMLElement) {
  if (el.hasAttribute('popover')) return;
  el.setAttribute('popover', 'manual');
  el.addEventListener('toggle', (event: Event) => {
    const next = 'newState' in event ? String((event as { newState: unknown }).newState) : '';
    if (next === 'open') el.setAttribute('data-open', '');
    if (next === 'closed') el.removeAttribute('data-open');
  });
}

export function createOverlayHost(tag: string, css: string): HTMLElement {
  // Isolated content scripts have no CustomElementRegistry (`customElements`
  // is null). A hyphenated tag still gets a shadow root without define().
  const host = document.createElement(tag);
  const root = host.attachShadow({ mode: 'open' });
  adoptStyles(root, css);
  bindPopoverHost(host);
  return host;
}

export function eventPathContains(event: Event, el: Element): boolean {
  // Elements rendered inside a shadow root get retargeted to the shadow
  // host when observed from a listener outside the shadow tree, so
  // `event.target` is useless for containment checks — `composedPath()`
  // still carries the real, un-retargeted path.
  return event.composedPath().includes(el);
}
