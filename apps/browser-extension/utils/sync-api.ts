import { pageIdentityFromPageKey } from '@/utils/page-key';
import type { HighlightRecord } from '@/utils/highlight-messages';
import type { CatalogRecord } from '@/utils/highlight-store';

export type SyncCredentials = {
  serverUrl: string;
  apiToken: string;
};

export type ApiHighlight = {
  id: string;
  pageKey: string;
  quote: string;
  prefix: string;
  suffix: string;
  color: string;
  comment: string;
  createdAt: number;
  updatedAt: number;
};

export type ApiMembership = {
  pageKey: string;
  bookmarked: boolean;
  title: string;
  description: string;
  createdAt: number;
  updatedAt: number;
};

export type PullPayload = {
  cursor: number;
  highlights: ApiHighlight[];
  memberships: ApiMembership[];
};

export type PushBody = {
  highlights: Array<{
    id: string;
    pageKey: string;
    quote: string;
    prefix: string;
    suffix: string;
    color: string;
    comment: string;
    createdAt: number;
  }>;
  memberships: Array<{
    pageKey: string;
    bookmarked: boolean;
    title: string;
    description: string;
  }>;
};

async function apiJson(
  credentials: SyncCredentials,
  path: string,
  init?: RequestInit,
): Promise<unknown> {
  const response = await fetch(`${credentials.serverUrl}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${credentials.apiToken}`,
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw new Error(`sync failed: ${response.status}`);
  }
  return response.json();
}

export async function pullSync(
  credentials: SyncCredentials,
  since: number,
): Promise<PullPayload> {
  const params = new URLSearchParams({ since: String(since) });
  return (await apiJson(credentials, `/api/sync/pull?${params}`)) as PullPayload;
}

export async function pushSync(
  credentials: SyncCredentials,
  body: PushBody,
): Promise<{ highlights: ApiHighlight[]; memberships: ApiMembership[] }> {
  return (await apiJson(credentials, '/api/sync/push', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })) as { highlights: ApiHighlight[]; memberships: ApiMembership[] };
}

export function highlightFromApi(row: ApiHighlight): HighlightRecord {
  return {
    ...pageIdentityFromPageKey(row.pageKey),
    id: row.id,
    quote: row.quote,
    prefix: row.prefix,
    suffix: row.suffix,
    color: row.color,
    comment: row.comment,
    createdAt: row.createdAt,
    updatedAt: row.updatedAt,
  };
}

export function membershipFromApi(row: ApiMembership): CatalogRecord {
  return {
    ...pageIdentityFromPageKey(row.pageKey),
    title: row.title,
    description: row.description,
    bookmarked: row.bookmarked,
    updatedAt: row.updatedAt,
  };
}

export function highlightToApi(row: HighlightRecord): PushBody['highlights'][number] {
  return {
    id: row.id,
    pageKey: row.pageKey,
    quote: row.quote,
    prefix: row.prefix,
    suffix: row.suffix,
    color: row.color,
    comment: row.comment ?? '',
    createdAt: row.createdAt,
  };
}

export function membershipToApi(row: CatalogRecord): PushBody['memberships'][number] {
  return {
    pageKey: row.pageKey,
    bookmarked: row.bookmarked,
    title: row.title,
    description: row.description,
  };
}
