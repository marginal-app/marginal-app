import { useEffect, useRef, useState } from 'react';
import type {
  CommentUpdatedMessage,
  GetHighlightsMessage,
  HighlightAddedMessage,
  HighlightRecord,
  UpdateCommentMessage,
} from '@/utils/highlight-messages';
import './App.css';

function getPageKey(url: string | undefined): string | null {
  if (!url) return null;
  try {
    const parsed = new URL(url);
    return parsed.origin + parsed.pathname;
  } catch {
    return null;
  }
}

function App() {
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

  return (
    <div className="panel">
      <h1>Marginal</h1>
      {highlights.length === 0 ? (
        <p className="empty">이 페이지에 저장된 하이라이트가 없습니다.</p>
      ) : (
        <ul className="highlight-list">
          {highlights.map((highlight) => (
            <li
              key={highlight.id}
              id={`highlight-${highlight.id}`}
              className="highlight-item"
              style={{ borderLeftColor: highlight.color }}
            >
              <div className="quote">{highlight.quote}</div>
              {editingId === highlight.id ? (
                <div className="comment-edit">
                  <textarea
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    autoFocus
                  />
                  <button onClick={() => saveComment(highlight.id)}>
                    저장
                  </button>
                </div>
              ) : (
                <div
                  className="comment"
                  onClick={() => startEditing(highlight)}
                >
                  {highlight.comment ? (
                    highlight.comment
                  ) : (
                    <span className="placeholder">코멘트 추가...</span>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
