import { mountHighlighter, type HighlightPort } from '@marginal-app/overlay';
import type {
  CommentUpdatedMessage,
  GetHighlightsMessage,
  HighlightRecord,
  SaveHighlightMessage,
  UpdateCommentMessage,
} from '@/utils/highlight-messages';
import { pageCatalogFromDocument } from '@/utils/page-catalog';
import { pageKeyFromLocation } from '@/utils/page-key';

export function runtimePort(pageKey: string): HighlightPort {
  return {
    save(anchor) {
      const message: SaveHighlightMessage = {
        type: 'SAVE_HIGHLIGHT',
        payload: {
          pageKey,
          ...anchor,
          catalog: pageCatalogFromDocument(document),
        },
      };
      return browser.runtime.sendMessage(message) as Promise<HighlightRecord>;
    },
    list() {
      const message: GetHighlightsMessage = {
        type: 'GET_HIGHLIGHTS',
        payload: { pageKey },
      };
      return browser.runtime.sendMessage(message) as Promise<HighlightRecord[]>;
    },
    async updateComment(id, comment) {
      const message: UpdateCommentMessage = {
        type: 'UPDATE_COMMENT',
        payload: { id, comment },
      };
      await browser.runtime.sendMessage(message);
    },
    onCommentUpdated(listener) {
      browser.runtime.onMessage.addListener((message: CommentUpdatedMessage) => {
        if (message.type !== 'COMMENT_UPDATED') return;
        if (message.payload.pageKey !== pageKey) return;
        listener(message.payload.id, message.payload.comment);
      });
    },
  };
}

export default defineContentScript({
  matches: ['<all_urls>'],
  runAt: 'document_idle',
  main() {
    const highlighter = mountHighlighter({
      port: runtimePort(pageKeyFromLocation(location)),
      trigger: { kind: 'mouseup' },
    });
    highlighter.restore().catch((error) => {
      console.error('하이라이트 복원 실패', error);
    });
  },
});
