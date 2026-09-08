import { useEffect, useState } from 'react';

interface StoredSettings {
  serverUrl: string;
  apiToken: string;
}

async function loadSettings(): Promise<StoredSettings> {
  const result = await browser.storage.local.get('settings');
  const settings = result.settings as Partial<StoredSettings> | undefined;
  return {
    serverUrl: settings?.serverUrl ?? '',
    apiToken: settings?.apiToken ?? '',
  };
}

function SettingsView() {
  const [serverUrl, setServerUrl] = useState('');
  const [apiToken, setApiToken] = useState('');
  const [status, setStatus] = useState<'idle' | 'testing' | 'ok' | 'error'>(
    'idle',
  );
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    loadSettings().then((settings) => {
      setServerUrl(settings.serverUrl);
      setApiToken(settings.apiToken);
    });
  }, []);

  async function handleSaveAndTest() {
    setStatus('testing');
    setErrorMessage('');
    const trimmedUrl = serverUrl.trim().replace(/\/$/, '');

    try {
      const response = await fetch(`${trimmedUrl}/api/ping`, {
        headers: { Authorization: `Bearer ${apiToken}` },
      });
      if (!response.ok) {
        throw new Error(`서버가 ${response.status}로 응답했습니다`);
      }

      await browser.storage.local.set({
        settings: { serverUrl: trimmedUrl, apiToken },
      });
      setStatus('ok');
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : '연결에 실패했습니다',
      );
      setStatus('error');
    }
  }

  return (
    <div className="settings">
      <label className="field">
        <span className="field-label">Server URL</span>
        <input
          type="text"
          value={serverUrl}
          onChange={(event) => setServerUrl(event.target.value)}
          placeholder="https://my-server.example.com"
        />
      </label>

      <label className="field">
        <span className="field-label">API Token</span>
        <input
          type="password"
          value={apiToken}
          onChange={(event) => setApiToken(event.target.value)}
          placeholder="dev-token"
        />
      </label>

      <button
        className="primary-button"
        onClick={handleSaveAndTest}
        disabled={status === 'testing' || !serverUrl || !apiToken}
      >
        {status === 'testing' ? '확인 중...' : 'Save & Test Connection'}
      </button>

      {status === 'ok' && (
        <p className="status status-ok">연결 성공 — 저장했습니다.</p>
      )}
      {status === 'error' && (
        <p className="status status-error">연결 실패: {errorMessage}</p>
      )}
    </div>
  );
}

export default SettingsView;
