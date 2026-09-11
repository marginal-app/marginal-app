export const LABEL = '페이지 노트';
export const HINT =
  '이 페이지 전체에 대한 메모입니다. 하이라이트 코멘트와는 다릅니다.';
export const PLACEHOLDER = '페이지 노트 추가...';
export const PAGE_NOTE =
  'SSR 실루엣은 이 페이지 노트에서 리뷰한다. 하이라이트 코멘트와는 별개다.';
export const DIRTY_NOTE = '저장 전 초안이다. 하이라이트 코멘트와는 별개다.';
export const SAVE_ERROR = '저장에 실패했습니다.';
export const EDIT_LABEL = '편집';
export const SAVE_LABEL = '저장';
export const CANCEL_LABEL = '취소';

export type CatalogNoteProps = {
  note: string;
  savedNote?: string;
  placeholder?: string;
  editing?: boolean;
  dirty?: boolean;
  error?: string;
  focused?: boolean;
  rows?: number;
  onEdit?: () => void;
  onChange?: (note: string) => void;
  onSave?: () => void;
  onCancel?: () => void;
};

export function catalogNoteHint(note: string): string {
  return note.trim() ? '' : HINT;
}

export function catalogNoteDirty(note: string, savedNote: string): boolean {
  return note !== savedNote;
}

function readProps(note: string): CatalogNoteProps {
  return {
    note,
    savedNote: note,
    placeholder: PLACEHOLDER,
    editing: false,
    dirty: false,
    focused: false,
    rows: 4,
  };
}

export function emptyCatalogNote(): CatalogNoteProps {
  return readProps('');
}

export function filledCatalogNote(): CatalogNoteProps {
  return readProps(PAGE_NOTE);
}

export function editCleanCatalogNote(): CatalogNoteProps {
  return {
    note: PAGE_NOTE,
    savedNote: PAGE_NOTE,
    placeholder: PLACEHOLDER,
    editing: true,
    dirty: false,
    focused: true,
    rows: 4,
  };
}

export function editDirtyCatalogNote(): CatalogNoteProps {
  return {
    note: DIRTY_NOTE,
    savedNote: PAGE_NOTE,
    placeholder: PLACEHOLDER,
    editing: true,
    dirty: true,
    focused: true,
    rows: 4,
  };
}

export function editErrorCatalogNote(): CatalogNoteProps {
  return {
    ...editDirtyCatalogNote(),
    error: SAVE_ERROR,
  };
}

function CatalogNote({
  note,
  placeholder = PLACEHOLDER,
  editing = false,
  dirty = false,
  error = '',
  focused = false,
  rows = 4,
  onEdit,
  onChange,
  onSave,
  onCancel,
}: CatalogNoteProps) {
  const hint = catalogNoteHint(note);
  const empty = !note.trim();
  const className = `ds-textarea${focused ? ' is-focused' : ''}`;

  return (
    <section className="catalog-note">
      <div className="catalog-note__head">
        <label className="ds-label">
          <span className="ds-label-text">{LABEL}</span>
          {hint ? <span className="ds-label-hint">{hint}</span> : null}
        </label>
        {editing ? null : (
          <button
            type="button"
            className="ds-icon-button"
            aria-label={EDIT_LABEL}
            title={EDIT_LABEL}
            onClick={() => onEdit?.()}
          >
            <span className="ds-icon-button__glyph" aria-hidden="true">
              ✎
            </span>
          </button>
        )}
      </div>
      {editing ? (
        <form
          className="catalog-note__edit"
          onSubmit={(event) => {
            event.preventDefault();
            onSave?.();
          }}
        >
          <textarea
            id="catalog-note"
            name="note"
            className={className}
            value={note}
            placeholder={placeholder}
            rows={rows}
            autoFocus={focused}
            onChange={(event) => onChange?.(event.target.value)}
          />
          <div className="catalog-note__actions">
            <button
              type="submit"
              className="button small"
              disabled={!dirty}
            >
              {SAVE_LABEL}
            </button>
            <button
              type="button"
              className="button quiet small"
              onClick={() => onCancel?.()}
            >
              {CANCEL_LABEL}
            </button>
          </div>
          {error ? (
            <p className="status status-error" role="status">
              <span className="status-dot" aria-hidden="true" />
              <span className="status-message">{error}</span>
            </p>
          ) : null}
        </form>
      ) : (
        <p className={`catalog-note__read${empty ? ' is-empty' : ''}`}>
          {empty ? placeholder : note}
        </p>
      )}
    </section>
  );
}

export default CatalogNote;
