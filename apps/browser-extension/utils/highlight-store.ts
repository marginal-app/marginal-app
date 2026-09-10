import type { PageCatalogDraft } from '@/utils/page-catalog';
import type { HighlightDraft, HighlightRecord } from '@/utils/highlight-messages';
import { bumpUpdatedAt } from '@/utils/clock';
import { pageIdentityFromPageKey, type PageIdentity } from '@/utils/page-key';

const DB_NAME = 'marginal-highlights';
const STORE_NAME = 'highlights';
const CATALOG_STORE = 'catalogs';
const DB_VERSION = 4;

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export type CatalogRecord = PageIdentity & {
  title: string;
  description: string;
  bookmarked: boolean;
  updatedAt: number;
};

type StoredHighlight = HighlightRecord & {
  origin?: string;
  path?: string;
  query?: string;
  updatedAt?: number;
};

type StoredCatalog = Partial<CatalogRecord> & {
  pageKey: string;
};

function isUuid(id: string): boolean {
  return UUID_RE.test(id);
}

function migrateRecord(value: StoredHighlight): HighlightRecord {
  const identity =
    value.origin != null && value.path != null && value.query != null
      ? {
          origin: value.origin,
          path: value.path,
          query: value.query,
          pageKey: value.pageKey,
        }
      : pageIdentityFromPageKey(value.pageKey);
  return {
    ...value,
    ...identity,
    updatedAt: value.updatedAt ?? value.createdAt,
  };
}

function migrateHighlightV4(value: HighlightRecord): HighlightRecord {
  return {
    ...value,
    id: isUuid(value.id) ? value.id : crypto.randomUUID(),
    updatedAt: value.updatedAt ?? value.createdAt,
  };
}

function migrateCatalogV4(value: StoredCatalog, identity: PageIdentity): CatalogRecord {
  return {
    ...identity,
    title: value.title ?? '',
    description: value.description ?? '',
    bookmarked: value.bookmarked ?? false,
    updatedAt: value.updatedAt ?? Date.now(),
  };
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
      }
      if (oldVersion < 3) {
        if (!db.objectStoreNames.contains(CATALOG_STORE)) {
          db.createObjectStore(CATALOG_STORE, { keyPath: 'pageKey' });
        }
      }
      if (oldVersion < 4 && tx) {
        const highlightStore = tx.objectStore(STORE_NAME);
        const replacements: HighlightRecord[] = [];
        const staleIds: string[] = [];
        const highlightCursor = highlightStore.openCursor();
        highlightCursor.onsuccess = () => {
          const cursor = highlightCursor.result;
          if (cursor) {
            const migrated = migrateHighlightV4(
              migrateRecord(cursor.value as StoredHighlight),
            );
            if (migrated.id !== (cursor.value as HighlightRecord).id) {
              staleIds.push((cursor.value as HighlightRecord).id);
              replacements.push(migrated);
            } else {
              cursor.update(migrated);
            }
            cursor.continue();
            return;
          }
          for (const id of staleIds) {
            highlightStore.delete(id);
          }
          for (const row of replacements) {
            highlightStore.add(row);
          }
        };
        if (db.objectStoreNames.contains(CATALOG_STORE)) {
          const catalogStore = tx.objectStore(CATALOG_STORE);
          const catalogCursor = catalogStore.openCursor();
          catalogCursor.onsuccess = () => {
            const cursor = catalogCursor.result;
            if (!cursor) return;
            const current = cursor.value as StoredCatalog;
            const identity = pageIdentityFromPageKey(current.pageKey);
            cursor.update(migrateCatalogV4(current, identity));
            cursor.continue();
          };
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
    const bookmarked = current?.bookmarked ?? false;
    const created = current == null;
    const metaChanged =
      title !== (current?.title ?? '') ||
      description !== (current?.description ?? '');
    const row: CatalogRecord = {
      ...identity,
      title,
      description,
      bookmarked,
      updatedAt:
        created || metaChanged
          ? bumpUpdatedAt(current?.updatedAt ?? 0)
          : current.updatedAt,
    };
    store.put(row);
  };
}

export async function saveHighlight(draft: HighlightDraft): Promise<HighlightRecord> {
  const db = await openDb();
  const { catalog, ...highlightDraft } = draft;
  const identity = pageIdentityFromPageKey(highlightDraft.pageKey);
  const now = Date.now();
  const record: HighlightRecord = {
    ...highlightDraft,
    ...identity,
    id: crypto.randomUUID(),
    createdAt: now,
    updatedAt: now,
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

export async function getAllHighlights(): Promise<HighlightRecord[]> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly');
    const request = tx.objectStore(STORE_NAME).getAll();
    request.onsuccess = () => resolve(request.result as HighlightRecord[]);
    request.onerror = () => reject(request.error);
  });
}

export async function getAllCatalogs(): Promise<CatalogRecord[]> {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(CATALOG_STORE, 'readonly');
    const request = tx.objectStore(CATALOG_STORE).getAll();
    request.onsuccess = () => resolve(request.result as CatalogRecord[]);
    request.onerror = () => reject(request.error);
  });
}

export async function putHighlight(record: HighlightRecord): Promise<void> {
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).put(record);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

export async function putCatalogRecord(record: CatalogRecord): Promise<void> {
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(CATALOG_STORE, 'readwrite');
    tx.objectStore(CATALOG_STORE).put(record);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

export async function setBookmarked(
  pageKey: string,
  bookmarked: boolean,
): Promise<CatalogRecord> {
  const current = await getCatalog(pageKey);
  const identity = pageIdentityFromPageKey(pageKey);
  const row: CatalogRecord = {
    ...identity,
    title: current?.title ?? '',
    description: current?.description ?? '',
    bookmarked,
    updatedAt: bumpUpdatedAt(current?.updatedAt ?? 0),
  };
  await putCatalogRecord(row);
  return row;
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
      const updated: HighlightRecord = {
        ...record,
        comment,
        updatedAt: bumpUpdatedAt(record.updatedAt),
      };
      store.put(updated);
      tx.oncomplete = () => resolve(updated);
    };
    getRequest.onerror = () => reject(getRequest.error);
    tx.onerror = () => reject(tx.error);
  });
}
