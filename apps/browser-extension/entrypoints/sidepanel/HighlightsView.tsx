import { useEffect, useRef, useState } from 'react';
import type {
  CommentUpdatedMessage,
  GetHighlightsMessage,
  HighlightAddedMessage,
  HighlightRecord,
  UpdateCommentMessage,
} from '@/utils/highlight-messages';
import { pageKeyFromHref } from '@/utils/page-key';

function getPageKey(url: string | undefined): string | null {
  if (!url) return null;
  return pageKeyFromHref(url);
}

function HighlightsView() {
  const [pageKey, setPageKey] = useState<string | null>(null);
  const [highlights, setHighlights] = useState<HighlightRecord[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState('');
  const hasCheckedFocusRef = useRef(false);

  useEffect(() => {
    async function loadForActiveTab() {
      const [tab] = await browser.tabs.query({
        active: true,
        currentWindow: true,
      });
      const key = getPageKey(tab?.url);
      setPageKey(key);

      if (!key) {
        setHighlights([]);
        return;
      }

      const message: GetHighlightsMessage = {
        type: 'GET_HIGHLIGHTS',
        payload: { pageKey: key },
      };
      const records = (await browser.runtime.sendMessage(message)) as
        | HighlightRecord[]
        | undefined;
      setHighlights(records ?? []);
    }

    loadForActiveTab();

    browser.tabs.onActivated.addListener(loadForActiveTab);
    browser.tabs.onUpdated.addListener(loadForActiveTab);
    return () => {
      browser.tabs.onActivated.removeListener(loadForActiveTab);
      browser.tabs.onUpdated.removeListener(loadForActiveTab);
    };
  }, []);

  useEffect(() => {
    function handleMessage(
      message: HighlightAddedMessage | CommentUpdatedMessage,
    ) {
      if (message.type === 'HIGHLIGHT_ADDED') {
        if (message.payload.pageKey !== pageKey) return;
        setHighlights((prev) => [...prev, message.payload]);
      }
      if (message.type === 'COMMENT_UPDATED') {
        if (message.payload.pageKey !== pageKey) return;
        setHighlights((prev) =>
          prev.map((highlight) =>
            highlight.id === message.payload.id
              ? { ...highlight, comment: message.payload.comment }
              : highlight,
          ),
        );
      }
    }

    browser.runtime.onMessage.addListener(handleMessage);
    return () => browser.runtime.onMessage.removeListener(handleMessage);
  }, [pageKey]);

  useEffect(() => {
    if (hasCheckedFocusRef.current || highlights.length === 0) return;
    hasCheckedFocusRef.current = true;

    browser.runtime
      .sendMessage({ type: 'GET_AND_CLEAR_FOCUS_HIGHLIGHT' })
      .then((id: string | null) => {
        if (!id) return;
        requestAnimationFrame(() => {
          document
            .getElementById(`highlight-${id}`)
            ?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
      });
  }, [highlights]);

  function startEditing(highlight: HighlightRecord) {
    setEditingId(highlight.id);
    setDraft(highlight.comment ?? '');
  }

  function saveComment(id: string) {
    const message: UpdateCommentMessage = {
      type: 'UPDATE_COMMENT',
      payload: { id, comment: draft },
    };
    browser.runtime.sendMessage(message).catch((error) => {
      console.error('코멘트 저장 실패', error);
    });
    setEditingId(null);
  }

  if (highlights.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-icon" aria-hidden="true">
          ✎
        </span>
        <p>이 페이지에 저장된 하이라이트가 없습니다.</p>
        <p className="empty-hint">본문을 드래그해서 하이라이트를 만들어보세요.</p>
      </div>
    );
  }

  return (
    <ul className="highlight-list">
      {highlights.map((highlight) => (
        <li
          key={highlight.id}
          id={`highlight-${highlight.id}`}
          className="highlight-item"
        >
          <div
            className="highlight-accent"
            style={{ backgroundColor: highlight.color }}
          />
          <div className="highlight-body">
            <p className="quote">{highlight.quote}</p>
            {editingId === highlight.id ? (
              <div className="comment-edit">
                <textarea
                  value={draft}
                  onChange={(event) => setDraft(event.target.value)}
                  autoFocus
                />
                <button
                  className="primary-button small"
                  onClick={() => saveComment(highlight.id)}
                >
                  저장
                </button>
              </div>
            ) : (
              <button
                className="comment-trigger"
                onClick={() => startEditing(highlight)}
              >
                {highlight.comment || (
                  <span className="placeholder">코멘트 추가...</span>
                )}
              </button>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}

export default HighlightsView;
