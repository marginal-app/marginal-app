export interface HighlightRecord {
  id: string;
  pageKey: string;
  quote: string;
  prefix: string;
  suffix: string;
  color: string;
  comment?: string;
  createdAt: number;
}

export type HighlightDraft = Omit<HighlightRecord, 'id' | 'createdAt' | 'comment'>;

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

export type HighlightMessage =
  | SaveHighlightMessage
  | GetHighlightsMessage
  | UpdateCommentMessage
  | OpenSidePanelMessage
  | GetFocusHighlightMessage;
