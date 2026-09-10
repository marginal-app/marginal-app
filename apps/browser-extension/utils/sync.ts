import type { HighlightRecord } from '@/utils/highlight-messages';
import type { CatalogRecord } from '@/utils/highlight-store';
import { rebaseRows, rowsToPush } from '@/utils/rebase';
import {
  highlightFromApi,
  highlightToApi,
  membershipFromApi,
  membershipToApi,
  pullSync,
  pushSync,
  type SyncCredentials,
} from '@/utils/sync-api';
import {
  getAllCatalogs,
  getAllHighlights,
  putCatalogRecord,
  putHighlight,
} from '@/utils/highlight-store';

const SETTINGS_KEY = 'settings';
const SYNC_KEY = 'sync';
const DEBOUNCE_MS = 1000;

export type SyncState = {
  cursor: number;
  ackedHighlights: Record<string, number>;
  ackedMemberships: Record<string, number>;
  lastError?: string;
  lastSyncedAt?: number;
};

export type SyncUiState = {
  mode: 'local-only' | 'syncing' | 'synced' | 'error';
  pending: number;
  pendingIds: string[];
  lastSyncedAt?: number;
  error?: string;
};

export async function loadCredentials(): Promise<SyncCredentials | null> {
  const result = await browser.storage.local.get(SETTINGS_KEY);
  const settings = result.settings as
    | { serverUrl?: string; apiToken?: string }
    | undefined;
  if (!settings?.serverUrl || !settings?.apiToken) {
    return null;
  }
  return {
    serverUrl: settings.serverUrl.replace(/\/$/, ''),
    apiToken: settings.apiToken,
  };
}

export async function loadSyncState(): Promise<SyncState> {
  const result = await browser.storage.local.get(SYNC_KEY);
  const raw = result[SYNC_KEY] as Partial<SyncState> | undefined;
  return {
    cursor: raw?.cursor ?? 0,
    ackedHighlights: raw?.ackedHighlights ?? {},
    ackedMemberships: raw?.ackedMemberships ?? {},
    lastError: raw?.lastError,
    lastSyncedAt: raw?.lastSyncedAt,
  };
}

export async function getSyncUiState(): Promise<SyncUiState> {
  const credentials = await loadCredentials();
  const state = await loadSyncState();
  const highlights = await getAllHighlights();
  const memberships = await getAllCatalogs();
  const pendingHighlights = rowsToPush(
    highlights,
    state.ackedHighlights,
    (row) => row.id,
  );
  const pendingMemberships = rowsToPush(
    memberships,
    state.ackedMemberships,
    (row) => row.pageKey,
  );
  const pending = pendingHighlights.length + pendingMemberships.length;
  const pendingIds = pendingHighlights.map((row) => row.id);

  if (!credentials) {
    return { mode: 'local-only', pending, pendingIds };
  }
  if (state.lastError) {
    return {
      mode: 'error',
      pending,
      pendingIds,
      lastSyncedAt: state.lastSyncedAt,
      error: state.lastError,
    };
  }
  if (pending > 0) {
    return { mode: 'syncing', pending, pendingIds, lastSyncedAt: state.lastSyncedAt };
  }
  return { mode: 'synced', pending: 0, pendingIds: [], lastSyncedAt: state.lastSyncedAt };
}

export async function saveSyncState(state: SyncState): Promise<void> {
  await browser.storage.local.set({ [SYNC_KEY]: state });
}

function ackIfRemoteWon<T extends { updatedAt: number }>(
  merged: T[],
  remote: T[],
  acked: Record<string, number>,
  keyOf: (row: T) => string,
): void {
  const remoteByKey = new Map(remote.map((row) => [keyOf(row), row]));
  for (const row of merged) {
    const remoteRow = remoteByKey.get(keyOf(row));
    if (remoteRow && row.updatedAt === remoteRow.updatedAt) {
      acked[keyOf(row)] = remoteRow.updatedAt;
    }
  }
}

export async function runSync(): Promise<void> {
  const credentials = await loadCredentials();
  if (!credentials) {
    return;
  }
  const state = await loadSyncState();
  try {
    const pulled = await pullSync(credentials, state.cursor);
  const remoteHighlights = pulled.highlights.map(highlightFromApi);
  const remoteMemberships = pulled.memberships.map(membershipFromApi);
  const highlights = rebaseRows(
    await getAllHighlights(),
    remoteHighlights,
    (row: HighlightRecord) => row.id,
  );
  const memberships = rebaseRows(
    await getAllCatalogs(),
    remoteMemberships,
    (row: CatalogRecord) => row.pageKey,
  );
  await Promise.all(highlights.map((row) => putHighlight(row)));
  await Promise.all(memberships.map((row) => putCatalogRecord(row)));
  ackIfRemoteWon(highlights, remoteHighlights, state.ackedHighlights, (row) => row.id);
  ackIfRemoteWon(
    memberships,
    remoteMemberships,
    state.ackedMemberships,
    (row) => row.pageKey,
  );

  const toPushHighlights = rowsToPush(highlights, state.ackedHighlights, (row) => row.id);
  const toPushMemberships = rowsToPush(
    memberships,
    state.ackedMemberships,
    (row) => row.pageKey,
  );
  let pushedHighlightTimes: number[] = [];
  let pushedMembershipTimes: number[] = [];
  if (toPushHighlights.length > 0 || toPushMemberships.length > 0) {
    const pushed = await pushSync(credentials, {
      highlights: toPushHighlights.map(highlightToApi),
      memberships: toPushMemberships.map(membershipToApi),
    });
    const highlightById = new Map(highlights.map((row) => [row.id, row]));
    for (const row of pushed.highlights) {
      const local = highlightById.get(row.id);
      if (local) {
        local.updatedAt = row.updatedAt;
        await putHighlight(local);
      }
      state.ackedHighlights[row.id] = row.updatedAt;
      pushedHighlightTimes.push(row.updatedAt);
    }
    const membershipByKey = new Map(memberships.map((row) => [row.pageKey, row]));
    for (const row of pushed.memberships) {
      const local = membershipByKey.get(row.pageKey);
      if (local) {
        local.updatedAt = row.updatedAt;
        await putCatalogRecord(local);
      }
      state.ackedMemberships[row.pageKey] = row.updatedAt;
      pushedMembershipTimes.push(row.updatedAt);
    }
  }

  state.cursor = Math.max(
    pulled.cursor,
    state.cursor,
    ...pushedHighlightTimes,
    ...pushedMembershipTimes,
  );
  state.lastError = undefined;
  state.lastSyncedAt = Date.now();
  await saveSyncState(state);
  } catch (error) {
    state.lastError = error instanceof Error ? error.message : String(error);
    await saveSyncState(state);
    throw error;
  }
}

let syncTimer: ReturnType<typeof setTimeout> | null = null;

export function scheduleSync(delay = DEBOUNCE_MS): void {
  if (syncTimer != null) {
    clearTimeout(syncTimer);
  }
  syncTimer = setTimeout(() => {
    syncTimer = null;
    void runSync().catch((error: unknown) => console.error(error));
  }, delay);
}
