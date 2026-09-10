export interface HighlightRecord {
  id: string;
  pageKey: string;
  origin: string;
  path: string;
  query: string;
  quote: string;
  prefix: string;
  suffix: string;
  color: string;
  comment?: string;
  createdAt: number;
  updatedAt: number;
}

import type { PageCatalogDraft } from '@/utils/page-catalog';

export type HighlightDraft = Omit<
  HighlightRecord,
  'id' | 'createdAt' | 'updatedAt' | 'comment' | 'origin' | 'path' | 'query'
> & {
  catalog?: PageCatalogDraft;
};

export type SaveHighlightMessage = {
  type: 'SAVE_HIGHLIGHT';
  payload: HighlightDraft;
};

export type GetHighlightsMessage = {
  type: 'GET_HIGHLIGHTS';
  payload: { pageKey: string };
};

export type HighlightAddedMessage = {
  type: 'HIGHLIGHT_ADDED';
  payload: HighlightRecord;
};

export type UpdateCommentMessage = {
  type: 'UPDATE_COMMENT';
  payload: { id: string; comment: string };
};

export type CommentUpdatedMessage = {
  type: 'COMMENT_UPDATED';
  payload: { id: string; pageKey: string; comment: string };
};

export type OpenSidePanelMessage = {
  type: 'OPEN_SIDE_PANEL';
  payload: { highlightId: string };
};

export type GetFocusHighlightMessage = {
  type: 'GET_AND_CLEAR_FOCUS_HIGHLIGHT';
};

export type GetCatalogMessage = {
  type: 'GET_CATALOG';
  payload: { pageKey: string };
};

export type SetBookmarkMessage = {
  type: 'SET_BOOKMARK';
  payload: { pageKey: string; bookmarked: boolean };
};

export type UpdateCatalogNoteMessage = {
  type: 'UPDATE_CATALOG_NOTE';
  payload: { pageKey: string; note: string };
};

export type GetSyncStatusMessage = {
  type: 'GET_SYNC_STATUS';
};

export type RunSyncMessage = {
  type: 'RUN_SYNC';
};

export type HighlightMessage =
  | SaveHighlightMessage
  | GetHighlightsMessage
  | UpdateCommentMessage
  | OpenSidePanelMessage
  | GetFocusHighlightMessage
  | GetCatalogMessage
  | SetBookmarkMessage
  | UpdateCatalogNoteMessage
  | GetSyncStatusMessage
  | RunSyncMessage;
