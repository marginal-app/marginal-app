import { useState } from 'react';
import HighlightsView from './HighlightsView';
import SettingsView from './SettingsView';
import './App.css';

function App() {
  const [view, setView] = useState<'highlights' | 'settings'>('highlights');
  const isSettings = view === 'settings';

  return (
    <div className="panel">
      <header className="panel-header">
        <h1>{isSettings ? '설정' : 'Marginal'}</h1>
        <button
          className="icon-button"
          onClick={() => setView(isSettings ? 'highlights' : 'settings')}
          aria-label={isSettings ? '목록으로 돌아가기' : '설정 열기'}
          title={isSettings ? '목록으로' : '설정'}
        >
          {isSettings ? '←' : '⚙'}
        </button>
      </header>
      {isSettings ? <SettingsView /> : <HighlightsView />}
    </div>
  );
}

export default App;
