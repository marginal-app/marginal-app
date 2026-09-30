import { mountHighlighter, type HighlightPort } from '@marginal-app/overlay';

// Injected by flutter_inappwebview as a document-end UserScript. This file is
// the mobile composition root on the page side: the overlay is the same one
// the extension mounts, and only the port and the selection trigger differ.

interface FlutterBridge {
  callHandler(name: string, ...args: unknown[]): Promise<unknown>;
}

declare global {
  interface Window {
    flutter_inappwebview?: FlutterBridge;
    __marginalMounted?: boolean;
  }
}

const HANDLER = 'marginal';

// The bridge object can land after document-end; the plugin announces it.
const bridge = new Promise<FlutterBridge>((resolve) => {
  if (window.flutter_inappwebview?.callHandler) {
    resolve(window.flutter_inappwebview);
    return;
  }
  window.addEventListener(
    'flutterInAppWebViewPlatformReady',
    () => resolve(window.flutter_inappwebview!),
    { once: true },
  );
});

async function send<T>(type: string, payload: unknown): Promise<T> {
  return (await bridge).callHandler(HANDLER, { type, payload }) as Promise<T>;
}

export function flutterPort(pageKey: string): HighlightPort {
  return {
    save: (anchor) => send('SAVE_HIGHLIGHT', { pageKey, ...anchor }),
    list: () => send('GET_HIGHLIGHTS', { pageKey }),
    updateComment: async (id, comment) => {
      await send('UPDATE_COMMENT', { id, comment });
    },
  };
}

if (!window.__marginalMounted) {
  window.__marginalMounted = true;
  const highlighter = mountHighlighter({
    port: flutterPort(location.origin + location.pathname),
    trigger: { kind: 'selectionchange', settleMs: 350 },
  });
  highlighter.restore().catch((error) => {
    console.error('하이라이트 복원 실패', error);
  });
}
