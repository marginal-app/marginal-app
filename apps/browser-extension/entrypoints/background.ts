import type {
  HighlightDraft,
  HighlightMessage,
  HighlightRecord,
} from '@/utils/highlight-messages';

const DB_NAME = 'marginal-highlights';
const STORE_NAME = 'highlights';

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    request.onupgradeneeded = () => {
      const store = request.result.createObjectStore(STORE_NAME, {
        keyPath: 'id',
      });
      store.createIndex('by_pageKey', 'pageKey', { unique: false });
      store.createIndex('by_createdAt', 'createdAt', { unique: false });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveHighlight(draft: HighlightDraft): Promise<HighlightRecord> {
  const db = await openDb();
  const record: HighlightRecord = {
    ...draft,
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    createdAt: Date.now(),
  };

  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).add(record);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });

  return record;
}

async function getHighlights(pageKey: string): Promise<HighlightRecord[]> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const request = tx.objectStore(STORE_NAME).index('by_pageKey').getAll(pageKey);
    request.onsuccess = () => resolve(request.result as HighlightRecord[]);
    request.onerror = () => reject(request.error);
  });
}

export default defineBackground(() => {
  // Chromium's `chrome.sidePanel` API is what makes the toolbar icon open the
  // side panel instead of an action popup. Firefox has no equivalent API: its
  // `sidebar_action` manifest key already opens the sidebar on icon click.
  if (import.meta.env.CHROME || import.meta.env.EDGE) {
    chrome.sidePanel
      .setPanelBehavior({ openPanelOnActionClick: true })
      .catch((error: unknown) => console.error(error));
  }

  browser.runtime.onMessage.addListener((message: HighlightMessage) => {
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

    return undefined;
  });
});
