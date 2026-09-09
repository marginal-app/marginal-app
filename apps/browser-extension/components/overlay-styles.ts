// Token values stay in lockstep with entrypoints/sidepanel/style.css.
// Shadow roots do not inherit the side panel's :root, so the overlay host
// redeclares the same names rather than inventing a second palette.

const TOKEN_STYLES = `
:host {
  color-scheme: light dark;
  --bg: #ffffff;
  --bg-elevated: #f6f6f7;
  --text: #1a1a1a;
  --text-secondary: #6b6b6b;
  --border: #e3e3e5;
  --accent: #5b5bd6;
  --accent-text: #ffffff;
  --danger: #c23b3b;
  --success: #237a45;
  --radius: 8px;
}

@media (prefers-color-scheme: dark) {
  :host {
    --bg: #1e1f22;
    --bg-elevated: #28292c;
    --text: #f0f0f0;
    --text-secondary: #9a9a9e;
    --border: #3a3b3e;
    --accent: #8b8bff;
    --accent-text: #17171a;
    --danger: #ff7a7a;
    --success: #57cf85;
  }
}
`;

const POPOVER_RESET = `
:host {
  box-sizing: border-box;
  position: fixed;
  inset: unset;
  margin: 0;
  padding: 0;
  border: none;
  width: fit-content;
  height: fit-content;
  overflow: visible;
  background: transparent;
  color: var(--text);
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, system-ui, sans-serif;
  font-size: 14px;
}

:host *,
:host *::before,
:host *::after {
  box-sizing: border-box;
}

:host:not([data-open]) {
  display: none;
}

:host([data-open]) {
  display: block;
}
`;

export const OVERLAY_HOST_STYLES = TOKEN_STYLES + POPOVER_RESET;

export function adoptStyles(root: ShadowRoot, css: string) {
  try {
    if (typeof CSSStyleSheet !== 'undefined' && 'replaceSync' in CSSStyleSheet.prototype) {
      const sheet = new CSSStyleSheet();
      sheet.replaceSync(css);
      root.adoptedStyleSheets = [...(root.adoptedStyleSheets ?? []), sheet];
      return;
    }
  } catch {
    // jsdom stubs CSSStyleSheet but not adoptedStyleSheets.
  }

  const style = document.createElement('style');
  style.textContent = css;
  root.prepend(style);
}
