import { useState } from 'react';
import HighlightsView from './HighlightsView';
import SettingsView from './SettingsView';
import { SettingsIcon } from './icons';
import './App.css';

function App() {
  const [view, setView] = useState<'highlights' | 'settings'>('highlights');
  const isSettings = view === 'settings';

  return (
    <div className="panel">
      <header className={`panel-header${isSettings ? ' panel-header-settings' : ''}`}>
        {isSettings ? (
          <>
            <span className="brand-mark" aria-hidden="true">
              M
            </span>
            <h1>설정</h1>
            <button
              className="text-back"
              onClick={() => setView('highlights')}
              type="button"
            >
              ← 이 페이지
            </button>
          </>
        ) : (
          <>
            <div className="brand">
              <span className="brand-mark" aria-hidden="true">
                M
              </span>
              <h1>Marginal</h1>
            </div>
            <button
              className="icon-button"
              onClick={() => setView('settings')}
              aria-label="설정 열기"
              title="설정"
              type="button"
            >
              <SettingsIcon />
            </button>
          </>
        )}
      </header>
      {isSettings ? <SettingsView /> : <HighlightsView />}
    </div>
  );
}

export default App;
