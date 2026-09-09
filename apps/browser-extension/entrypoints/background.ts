import type { HighlightMessage } from '@/utils/highlight-messages';
import {
  getHighlights,
  saveHighlight,
  updateComment,
} from '@/utils/highlight-store';

export {
  getCatalog,
  getHighlights,
  saveHighlight,
  updateComment,
} from '@/utils/highlight-store';

// Set by OPEN_SIDE_PANEL right before opening the panel, consumed once by
// the side panel's GET_AND_CLEAR_FOCUS_HIGHLIGHT call right after it mounts.
let pendingFocusHighlightId: string | null = null;

export default defineBackground(() => {
  // Chromium's `chrome.sidePanel` API is what makes the toolbar icon open the
  // side panel instead of an action popup. Firefox has no equivalent API: its
  // `sidebar_action` manifest key already opens the sidebar on icon click.
  if (import.meta.env.CHROME || import.meta.env.EDGE) {
    chrome.sidePanel
      .setPanelBehavior({ openPanelOnActionClick: true })
      .catch((error: unknown) => console.error(error));
  }

  browser.runtime.onMessage.addListener((message: HighlightMessage, sender) => {
    if (message.type === 'SAVE_HIGHLIGHT') {
      return saveHighlight(message.payload).then((record) => {
        browser.runtime
          .sendMessage({ type: 'HIGHLIGHT_ADDED', payload: record })
          .catch(() => {
            // No listener open (e.g. side panel closed) — safe to ignore.
          });
        return record;
      });
    }

    if (message.type === 'GET_HIGHLIGHTS') {
      return getHighlights(message.payload.pageKey);
    }

    if (message.type === 'UPDATE_COMMENT') {
      return updateComment(message.payload.id, message.payload.comment).then(
        (record) => {
          browser.runtime
            .sendMessage({
              type: 'COMMENT_UPDATED',
              payload: {
                id: record.id,
                pageKey: record.pageKey,
                comment: record.comment ?? '',
              },
            })
            .catch(() => {
              // No listener open — safe to ignore.
            });
          return record;
        },
      );
    }

    if (message.type === 'OPEN_SIDE_PANEL') {
      pendingFocusHighlightId = message.payload.highlightId;
      if (import.meta.env.FIREFOX) {
        // Firefox's `sidebarAction` isn't part of the cross-browser polyfill
        // typings (it's Firefox-only), hence the cast.
        (browser as unknown as { sidebarAction: { open(): Promise<void> } }).sidebarAction
          .open()
          .catch((error: unknown) => console.error(error));
      } else {
        const tabId = sender.tab?.id;
        if (tabId != null) {
          chrome.sidePanel
            .open({ tabId })
            .catch((error: unknown) => console.error(error));
        }
      }
      return undefined;
    }

    if (message.type === 'GET_AND_CLEAR_FOCUS_HIGHLIGHT') {
      const id = pendingFocusHighlightId;
      pendingFocusHighlightId = null;
      return Promise.resolve(id);
    }

    return undefined;
  });
});
