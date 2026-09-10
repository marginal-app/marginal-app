import { useEffect, useState } from 'react';
import type { GetSyncStatusMessage } from '@/utils/highlight-messages';
import type { SyncUiState } from '@/utils/sync';

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

function hostFromUrl(value: string): string {
  try {
    return new URL(value).host;
  } catch {
    return value.replace(/^https?:\/\//, '');
  }
}

function SettingsView() {
  const [serverUrl, setServerUrl] = useState('');
  const [apiToken, setApiToken] = useState('');
  const [status, setStatus] = useState<'idle' | 'testing' | 'ok' | 'error'>(
    'idle',
  );
  const [errorMessage, setErrorMessage] = useState('');
  const [sync, setSync] = useState<SyncUiState>({
    mode: 'local-only',
    pending: 0,
    pendingIds: [],
  });

  useEffect(() => {
    loadSettings().then((settings) => {
      setServerUrl(settings.serverUrl);
      setApiToken(settings.apiToken);
    });
    const message: GetSyncStatusMessage = { type: 'GET_SYNC_STATUS' };
    browser.runtime
      .sendMessage(message)
      .then((next: SyncUiState | undefined) => {
        if (next) setSync(next);
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
      const message: GetSyncStatusMessage = { type: 'GET_SYNC_STATUS' };
      const next = (await browser.runtime.sendMessage(message)) as
        | SyncUiState
        | undefined;
      if (next) setSync(next);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : '연결에 실패했습니다',
      );
      setStatus('error');
    }
  }

  async function handleLogout() {
    await browser.storage.local.set({
      settings: { serverUrl: serverUrl.trim().replace(/\/$/, ''), apiToken: '' },
    });
    setApiToken('');
    setStatus('idle');
    setSync({ mode: 'local-only', pending: 0, pendingIds: [] });
  }

  const connected = Boolean(serverUrl && apiToken) && status !== 'error' && sync.mode !== 'error';
  const badge =
    status === 'error' || sync.mode === 'error'
      ? 'ERROR'
      : connected
        ? 'CONNECTED'
        : '';
  const accountHost = hostFromUrl(serverUrl);
  const accountName = accountHost.split('.')[0] || '이 브라우저';

  return (
    <div className="settings">
      <section className="settings-section">
        <div className="settings-kicker">
          <span>서버 연결</span>
          {badge ? <span className="settings-badge">{badge}</span> : null}
        </div>
        <p className="settings-copy">
          서버가 없거나 오프라인이어도 밑줄은 이 브라우저에 먼저 저장되고,
          연결되면 알아서 보냅니다.
        </p>
        <label className="field">
          <span className="field-label">SERVER URL</span>
          <input
            type="text"
            value={serverUrl}
            onChange={(event) => setServerUrl(event.target.value)}
            placeholder="https://my-server.example.com"
          />
        </label>
        <label className="field">
          <span className="field-label">API TOKEN</span>
          <input
            type="password"
            value={apiToken}
            onChange={(event) => setApiToken(event.target.value)}
            placeholder="dev-token"
          />
        </label>
        <button
          className="quiet-button"
          onClick={handleSaveAndTest}
          disabled={status === 'testing' || !serverUrl || !apiToken}
          type="button"
        >
          {status === 'testing' ? '확인 중...' : '저장하고 연결 확인'}
        </button>
        {status === 'ok' && (
          <p className="status status-ok">연결 성공 — 저장했습니다.</p>
        )}
        {status === 'error' && (
          <p className="status status-error">연결 실패: {errorMessage}</p>
        )}
      </section>

      {apiToken ? (
        <section className="settings-section">
          <div className="settings-kicker">
            <span>계정</span>
          </div>
          <div className="account-row">
            <span className="account-avatar" aria-hidden="true">
              {(accountName[0] ?? 'M').toUpperCase()}
            </span>
            <div className="account-body">
              <p className="account-name">{accountName}</p>
              <p className="account-host">{accountHost || '—'}</p>
            </div>
            <button type="button" className="account-logout" onClick={handleLogout}>
              로그아웃
            </button>
          </div>
        </section>
      ) : null}
    </div>
  );
}

export default SettingsView;
