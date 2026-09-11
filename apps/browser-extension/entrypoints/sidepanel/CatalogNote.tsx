export const LABEL = '페이지 노트';
export const HINT =
  '이 페이지 전체에 대한 메모입니다. 하이라이트 코멘트와는 다릅니다.';
export const PLACEHOLDER = '페이지 노트 추가...';
export const PAGE_NOTE =
  'SSR 실루엣은 이 페이지 노트에서 리뷰한다. 하이라이트 코멘트와는 별개다.';

export type CatalogNoteProps = {
  note: string;
  placeholder?: string;
  focused?: boolean;
  rows?: number;
  onChange?: (note: string) => void;
  onCommit?: (note: string) => void;
};

export function emptyCatalogNote(): CatalogNoteProps {
  return {
    note: '',
    placeholder: PLACEHOLDER,
    focused: false,
    rows: 4,
  };
}

export function filledCatalogNote(): CatalogNoteProps {
  return {
    note: PAGE_NOTE,
    placeholder: PLACEHOLDER,
    focused: false,
    rows: 4,
  };
}

export function catalogNoteHint(note: string): string {
  return note.trim() ? '' : HINT;
}

function CatalogNote({
  note,
  placeholder = PLACEHOLDER,
  focused = false,
  rows = 4,
  onChange,
  onCommit,
}: CatalogNoteProps) {
  const hint = catalogNoteHint(note);
  const className = `ds-textarea${focused ? ' is-focused' : ''}`;

  return (
    <section className="catalog-note">
      <label className="ds-label" htmlFor="catalog-note">
        <span className="ds-label-text">{LABEL}</span>
        {hint ? <span className="ds-label-hint">{hint}</span> : null}
      </label>
      <textarea
        id="catalog-note"
        name="note"
        className={className}
        value={note}
        placeholder={placeholder}
        rows={rows}
        onChange={(event) => onChange?.(event.target.value)}
        onBlur={(event) => onCommit?.(event.target.value)}
      />
    </section>
  );
}

export default CatalogNote;
