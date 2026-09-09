import type {
  HighlightDraft,
  HighlightMessage,
  HighlightRecord,
} from '@/utils/highlight-messages';
import type { PageCatalogDraft } from '@/utils/page-catalog';
import { pageIdentityFromPageKey, type PageIdentity } from '@/utils/page-key';

const DB_NAME = 'marginal-highlights';
const STORE_NAME = 'highlights';
const CATALOG_STORE = 'catalogs';
const DB_VERSION = 3;

export type CatalogRecord = PageIdentity & {
  title: string;
  description: string;
  updatedAt: number;
};

type StoredHighlight = HighlightRecord & {
  origin?: string;
  path?: string;
  query?: string;
};

function migrateRecord(value: StoredHighlight): HighlightRecord {
  if (value.origin != null && value.path != null && value.query != null) {
    return value as HighlightRecord;
  }
  const identity = pageIdentityFromPageKey(value.pageKey);
  return { ...value, ...identity };
}

export function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (event) => {
      const db = request.result;
      const tx = request.transaction;
      const oldVersion = event.oldVersion;
      if (oldVersion < 1) {
        const store = db.createObjectStore(STORE_NAME, {
          keyPath: 'id',
        });
        store.createIndex('by_pageKey', 'pageKey', { unique: false });
        store.createIndex('by_createdAt', 'createdAt', { unique: false });
      }
      if (oldVersion < 2 && tx) {
        const store = tx.objectStore(STORE_NAME);
        if (!store.indexNames.contains('by_origin')) {
          store.createIndex('by_origin', 'origin', { unique: false });
        }
        const cursorRequest = store.openCursor();
        cursorRequest.onsuccess = () => {
          const cursor = cursorRequest.result;
          if (!cursor) return;
          cursor.update(migrateRecord(cursor.value as HighlightRecord));
          cursor.continue();
        };
      }
      if (oldVersion < 3) {
        if (!db.objectStoreNames.contains(CATALOG_STORE)) {
          db.createObjectStore(CATALOG_STORE, { keyPath: 'pageKey' });
        }
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function putCatalog(
  tx: IDBTransaction,
  identity: PageIdentity,
  catalog: PageCatalogDraft | undefined,
): void {
  const store = tx.objectStore(CATALOG_STORE);
  const request = store.get(identity.pageKey);
  request.onsuccess = () => {
    const current = request.result as CatalogRecord | undefined;
    const title = catalog?.title.trim() || current?.title || '';
    const description = catalog?.description.trim() || current?.description || '';
    const row: CatalogRecord = {
      ...identity,
      title,
      description,
      updatedAt: Date.now(),
    };
    store.put(row);
  };
}

export async function saveHighlight(draft: HighlightDraft): Promise<HighlightRecord> {
  const db = await openDb();
  const { catalog, ...highlightDraft } = draft;
  const identity = pageIdentityFromPageKey(highlightDraft.pageKey);
  const record: HighlightRecord = {
    ...highlightDraft,
    ...identity,
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    createdAt: Date.now(),
  };

  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction([STORE_NAME, CATALOG_STORE], 'readwrite');
    tx.objectStore(STORE_NAME).add(record);
    putCatalog(tx, identity, catalog);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });

  return record;
}

export async function getCatalog(pageKey: string): Promise<CatalogRecord | undefined> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(CATALOG_STORE, 'readonly');
    const request = tx.objectStore(CATALOG_STORE).get(pageKey);
    request.onsuccess = () => resolve(request.result as CatalogRecord | undefined);
    request.onerror = () => reject(request.error);
  });
}

export async function getHighlights(pageKey: string): Promise<HighlightRecord[]> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const request = tx.objectStore(STORE_NAME).index('by_pageKey').getAll(pageKey);
    request.onsuccess = () => resolve(request.result as HighlightRecord[]);
    request.onerror = () => reject(request.error);
  });
}

export async function updateComment(id: string, comment: string): Promise<HighlightRecord> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const getRequest = store.get(id);
    getRequest.onsuccess = () => {
      const record = getRequest.result as HighlightRecord | undefined;
      if (!record) {
        reject(new Error(`Highlight not found: ${id}`));
        return;
      }
      const updated: HighlightRecord = { ...record, comment };
      store.put(updated);
      tx.oncomplete = () => resolve(updated);
    };
    getRequest.onerror = () => reject(getRequest.error);
    tx.onerror = () => reject(tx.error);
  });
}

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
