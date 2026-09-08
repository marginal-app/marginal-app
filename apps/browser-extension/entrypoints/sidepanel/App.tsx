import { useEffect, useState } from 'react';
import type {
  GetHighlightsMessage,
  HighlightAddedMessage,
  HighlightRecord,
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
    function handleMessage(message: HighlightAddedMessage) {
      if (message.type !== 'HIGHLIGHT_ADDED') return;
      if (message.payload.pageKey !== pageKey) return;
      setHighlights((prev) => [...prev, message.payload]);
    }

    browser.runtime.onMessage.addListener(handleMessage);
    return () => browser.runtime.onMessage.removeListener(handleMessage);
  }, [pageKey]);

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
              className="highlight-item"
              style={{ borderLeftColor: highlight.color }}
            >
              {highlight.quote}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
