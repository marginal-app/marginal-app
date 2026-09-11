import { useEffect, useRef, useState } from 'react';
import type {
  CommentUpdatedMessage,
  GetCatalogMessage,
  GetHighlightsMessage,
  GetSyncStatusMessage,
  HighlightAddedMessage,
  HighlightRecord,
  RunSyncMessage,
  SetBookmarkMessage,
  UpdateCatalogNoteMessage,
  UpdateCommentMessage,
} from '@/utils/highlight-messages';
import type { CatalogRecord } from '@/utils/highlight-store';
import type { SyncUiState } from '@/utils/sync';
import { pageKeyFromHref } from '@/utils/page-key';
import CatalogNote, { SAVE_ERROR } from './CatalogNote';
import { BookmarkIcon, CommentIcon, OpenWebIcon } from './icons';

function getPageKey(url: string | undefined): string | null {
  if (!url) return null;
  return pageKeyFromHref(url);
}

function hostFromPageKey(pageKey: string | null): string {
  if (!pageKey) return '';
  try {
    return new URL(pageKey).hostname;
  } catch {
    return pageKey;
  }
}

function letterFromTitle(title: string, host: string): string {
  const source = title.trim() || host.trim();
  return (source[0] ?? 'M').toUpperCase();
}

function formatStamp(createdAt: number, now = Date.now()): string {
  const diff = now - createdAt;
  if (diff < 60_000) return '방금';
  if (diff < 86_400_000) return '오늘';
  if (diff < 2 * 86_400_000) return '어제';
  return new Date(createdAt).toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
  });
}

function HighlightsView() {
  const [pageKey, setPageKey] = useState<string | null>(null);
  const [pageUrl, setPageUrl] = useState<string | null>(null);
  const [tabTitle, setTabTitle] = useState('');
  const [highlights, setHighlights] = useState<HighlightRecord[]>([]);
  const [catalog, setCatalog] = useState<CatalogRecord | undefined>();
  const [pageNote, setPageNote] = useState('');
  const [noteDraft, setNoteDraft] = useState('');
  const [noteEditing, setNoteEditing] = useState(false);
  const [noteError, setNoteError] = useState('');
  const [sync, setSync] = useState<SyncUiState>({
    mode: 'local-only',
    pending: 0,
    pendingIds: [],
  });
  const [focusedId, setFocusedId] = useState<string | null>(null);
  const [draft, setDraft] = useState('');
  const composerRef = useRef<HTMLInputElement>(null);
  const hasCheckedFocusRef = useRef(false);

  async function refreshSync() {
    const message: GetSyncStatusMessage = { type: 'GET_SYNC_STATUS' };
    const next = (await browser.runtime.sendMessage(message)) as
      | SyncUiState
      | undefined;
    if (next) setSync(next);
  }

  async function loadForActiveTab() {
    const [tab] = await browser.tabs.query({
      active: true,
      currentWindow: true,
    });
    const key = getPageKey(tab?.url);
    setPageKey(key);
    setPageUrl(tab?.url ?? null);
    setTabTitle(tab?.title ?? '');

    if (!key) {
      setHighlights([]);
      setCatalog(undefined);
      setPageNote('');
      setNoteDraft('');
      setNoteEditing(false);
      setNoteError('');
      return;
    }

    const highlightsMessage: GetHighlightsMessage = {
      type: 'GET_HIGHLIGHTS',
      payload: { pageKey: key },
    };
    const catalogMessage: GetCatalogMessage = {
      type: 'GET_CATALOG',
      payload: { pageKey: key },
    };
    const [records, row] = await Promise.all([
      browser.runtime.sendMessage(highlightsMessage) as Promise<
        HighlightRecord[] | undefined
      >,
      browser.runtime.sendMessage(catalogMessage) as Promise<
        CatalogRecord | undefined
      >,
    ]);
    setHighlights(records ?? []);
    setCatalog(row);
    const saved = row?.note ?? '';
    setPageNote(saved);
    setNoteDraft(saved);
    setNoteEditing(false);
    setNoteError('');
    await refreshSync();
  }

  useEffect(() => {
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
        void refreshSync();
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
        setFocusedId(id);
        const match = highlights.find((highlight) => highlight.id === id);
        if (match) setDraft(match.comment ?? '');
        requestAnimationFrame(() => {
          document
            .getElementById(`highlight-${id}`)
            ?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
      });
  }, [highlights]);

  const title = catalog?.title || tabTitle || hostFromPageKey(pageKey);
  const host = hostFromPageKey(pageKey);
  const localOnly = sync.mode === 'local-only';
  const pending = new Set(sync.pendingIds);
  const isEmpty = highlights.length === 0;
  const focused = highlights.find((highlight) => highlight.id === focusedId);

  function focusHighlight(highlight: HighlightRecord) {
    setFocusedId(highlight.id);
    setDraft(highlight.comment ?? '');
    composerRef.current?.focus();
  }

  function saveComment() {
    const target =
      focused ??
      [...highlights].sort((a, b) => b.createdAt - a.createdAt)[0];
    if (!target) return;
    const message: UpdateCommentMessage = {
      type: 'UPDATE_COMMENT',
      payload: { id: target.id, comment: draft },
    };
    browser.runtime.sendMessage(message).catch((error) => {
      console.error('코멘트 저장 실패', error);
    });
  }

  async function savePageNote() {
    if (!pageKey) return;
    if (noteDraft === (catalog?.note ?? pageNote)) {
      setNoteEditing(false);
      setNoteError('');
      return;
    }
    const message: UpdateCatalogNoteMessage = {
      type: 'UPDATE_CATALOG_NOTE',
      payload: { pageKey, note: noteDraft },
    };
    try {
      const row = (await browser.runtime.sendMessage(message)) as CatalogRecord;
      setCatalog(row);
      setPageNote(row.note);
      setNoteDraft(row.note);
      setNoteEditing(false);
      setNoteError('');
      await refreshSync();
    } catch (error) {
      console.error('페이지 노트 저장 실패', error);
      setNoteError(SAVE_ERROR);
    }
  }

  async function toggleBookmark() {
    if (!pageKey) return;
    const next = !catalog?.bookmarked;
    const message: SetBookmarkMessage = {
      type: 'SET_BOOKMARK',
      payload: { pageKey, bookmarked: next },
    };
    const row = (await browser.runtime.sendMessage(message)) as CatalogRecord;
    setCatalog(row);
    await refreshSync();
  }

  function openPage() {
    if (!pageUrl) return;
    browser.tabs.create({ url: pageUrl }).catch((error) => {
      console.error('페이지 열기 실패', error);
    });
  }

  async function openLibrary() {
    const result = await browser.storage.local.get('settings');
    const settings = result.settings as { serverUrl?: string } | undefined;
    const serverUrl = settings?.serverUrl?.replace(/\/$/, '');
    if (!serverUrl) return;
    browser.tabs.create({ url: `${serverUrl}/library/` }).catch((error) => {
      console.error('라이브러리 열기 실패', error);
    });
  }

  async function runSyncNow() {
    const message: RunSyncMessage = { type: 'RUN_SYNC' };
    const next = (await browser.runtime.sendMessage(message)) as
      | SyncUiState
      | undefined;
    if (next) setSync(next);
  }

  const syncLabel =
    sync.mode === 'syncing'
      ? `동기화 중 · 대기 ${sync.pending}`
      : sync.mode === 'error'
        ? `서버 오류${sync.pending ? ` · 대기 ${sync.pending}` : ''}`
        : '동기화됨 · 방금';
  const syncAction =
    sync.mode === 'syncing'
      ? '지금 동기화'
      : sync.mode === 'error'
        ? '재시도'
        : '';

  return (
    <div className="page">
      {pageKey ? (
        <section className="document-card">
          <div className="document-main">
            <div className="document-tile" aria-hidden="true">
              {letterFromTitle(title, host)}
            </div>
            <div className="document-body">
              <p className="document-title">{title || '이 페이지'}</p>
              <p className="document-meta">
                {host || '—'} · 밑줄 {highlights.length}
              </p>
            </div>
          </div>
          {localOnly ? null : (
            <div className="document-actions">
              <button
                type="button"
                className={`pill${catalog?.bookmarked ? ' pill-active' : ''}`}
                onClick={toggleBookmark}
              >
                <BookmarkIcon filled={Boolean(catalog?.bookmarked)} />
                {catalog?.bookmarked ? '북마크됨' : '북마크'}
              </button>
              <button type="button" className="pill" onClick={openPage}>
                <OpenWebIcon />
                웹에서 열기
              </button>
            </div>
          )}
        </section>
      ) : null}

      {pageKey ? (
        <CatalogNote
          note={noteEditing ? noteDraft : pageNote}
          savedNote={pageNote}
          editing={noteEditing}
          dirty={noteDraft !== pageNote}
          error={noteError}
          focused={noteEditing}
          onEdit={() => {
            setNoteDraft(pageNote);
            setNoteError('');
            setNoteEditing(true);
          }}
          onChange={setNoteDraft}
          onSave={() => {
            void savePageNote();
          }}
          onCancel={() => {
            setNoteDraft(pageNote);
            setNoteError('');
            setNoteEditing(false);
          }}
        />
      ) : null}

      {isEmpty ? (
        <div className="empty-state">
          <p>아직 이 페이지에 남긴 밑줄이 없습니다.</p>
          <p className="empty-hint">본문을 드래그하면 색 툴바가 뜹니다.</p>
          <button type="button" className="library-link" onClick={openLibrary}>
            라이브러리에서 보기 ↗
          </button>
        </div>
      ) : (
        <ul className="highlight-list">
          {highlights.map((highlight) => {
            const saving = pending.has(highlight.id);
            return (
              <li
                key={highlight.id}
                id={`highlight-${highlight.id}`}
                className={`highlight-item${saving ? ' highlight-item-new' : ''}${focusedId === highlight.id ? ' highlight-item-focused' : ''}`}
              >
                <button
                  type="button"
                  className="highlight-hit"
                  onClick={() => focusHighlight(highlight)}
                >
                  <span
                    className="highlight-swatch"
                    style={{ backgroundColor: highlight.color }}
                  />
                  <span className="highlight-body">
                    <span className="quote">{highlight.quote}</span>
                    <span className="highlight-meta">
                      <span
                        className={
                          highlight.comment ? 'comment-text' : 'placeholder'
                        }
                      >
                        {highlight.comment ||
                          (saving ? '방금 밑줄' : '코멘트 추가')}
                      </span>
                      <span className="stamp">
                        {saving ? (
                          <>
                            <span className="stamp-dot" aria-hidden="true" />
                            저장 중…
                          </>
                        ) : (
                          formatStamp(highlight.createdAt)
                        )}
                      </span>
                    </span>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {localOnly ? null : (
        <div className="sync-line">
          <span className="stamp">
            <span className="stamp-dot" aria-hidden="true" />
            {syncLabel}
          </span>
          {syncAction ? (
            <button type="button" className="sync-action" onClick={runSyncNow}>
              {syncAction}
            </button>
          ) : null}
        </div>
      )}

      <form
        className="note-composer"
        onSubmit={(event) => {
          event.preventDefault();
          saveComment();
        }}
      >
        <CommentIcon />
        <input
          ref={composerRef}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="선택한 문장에 코멘트…"
          aria-label="코멘트"
        />
        <button type="submit" className="composer-save">
          저장
        </button>
      </form>
    </div>
  );
}

export default HighlightsView;
