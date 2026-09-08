export interface HighlightRecord {
  id: string;
  pageKey: string;
  quote: string;
  prefix: string;
  suffix: string;
  color: string;
  createdAt: number;
}

export type HighlightDraft = Omit<HighlightRecord, 'id' | 'createdAt'>;

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

export type HighlightMessage = SaveHighlightMessage | GetHighlightsMessage;
