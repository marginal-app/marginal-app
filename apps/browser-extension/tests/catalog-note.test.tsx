import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import CatalogNote, {
  CANCEL_LABEL,
  DIRTY_NOTE,
  EDIT_LABEL,
  HINT,
  LABEL,
  PAGE_NOTE,
  PLACEHOLDER,
  SAVE_ERROR,
  SAVE_LABEL,
  catalogNoteDirty,
  catalogNoteHint,
  editCleanCatalogNote,
  editDirtyCatalogNote,
  editErrorCatalogNote,
  emptyCatalogNote,
  filledCatalogNote,
} from '@/entrypoints/sidepanel/CatalogNote';

describe('CatalogNote', () => {
  it('empty read shows the placeholder and pencil, not a textarea', () => {
    const html = renderToStaticMarkup(<CatalogNote {...emptyCatalogNote()} />);
    expect(html).toContain('catalog-note');
    expect(html).toContain(LABEL);
    expect(html).toContain(HINT);
    expect(html).toContain('하이라이트 코멘트');
    expect(html).toContain(PLACEHOLDER);
    expect(html).toContain('catalog-note__read is-empty');
    expect(html).toContain(EDIT_LABEL);
    expect(html).toContain('✎');
    expect(html).not.toContain('<textarea');
    expect(html).not.toContain(SAVE_LABEL);
    expect(html).not.toContain('is-focused');
    expect(html).not.toContain('ds-label-kicker');
    expect(html).not.toContain('autofocus');
    expect(html).not.toContain('밑줄 코멘트');
    expect(html).not.toContain(PAGE_NOTE);
    expect(html).not.toContain('코멘트 추가');
    expect(html).not.toContain('name="comment"');
    expect(html).not.toContain('onBlur');
  });

  it('filled read shows the note and hides the hint', () => {
    const html = renderToStaticMarkup(<CatalogNote {...filledCatalogNote()} />);
    expect(html).toContain(PAGE_NOTE);
    expect(html).toContain(LABEL);
    expect(html).toContain('catalog-note__read');
    expect(html).toContain(EDIT_LABEL);
    expect(html).not.toContain(HINT);
    expect(html).not.toContain('ds-label-hint');
    expect(html).not.toContain('<textarea');
    expect(html).not.toContain(SAVE_LABEL);
    expect(html).not.toContain('is-focused');
    expect(html).not.toContain('ds-label-kicker');
    expect(html).not.toContain('코멘트 추가');
    expect(html).not.toContain('name="comment"');
  });

  it('edit clean keeps save disabled', () => {
    const html = renderToStaticMarkup(
      <CatalogNote {...editCleanCatalogNote()} />,
    );
    expect(html).toContain('<textarea');
    expect(html).toContain(PAGE_NOTE);
    expect(html).toContain('name="note"');
    expect(html).toContain(SAVE_LABEL);
    expect(html).toContain(CANCEL_LABEL);
    expect(html).toContain('disabled');
    expect(html).not.toContain(EDIT_LABEL);
    expect(html).not.toContain(HINT);
    expect(html).not.toContain(SAVE_ERROR);
  });

  it('edit dirty enables save', () => {
    const html = renderToStaticMarkup(
      <CatalogNote {...editDirtyCatalogNote()} />,
    );
    expect(html).toContain(DIRTY_NOTE);
    expect(html).toContain(SAVE_LABEL);
    expect(html).toContain(CANCEL_LABEL);
    expect(html).toContain('name="note"');
    expect(html).not.toMatch(/disabled[^>]*>저장/);
    expect(html).not.toContain(EDIT_LABEL);
    expect(html).not.toContain(HINT);
    expect(html).not.toContain(SAVE_ERROR);
  });

  it('edit error stays in edit with a short error', () => {
    const html = renderToStaticMarkup(
      <CatalogNote {...editErrorCatalogNote()} />,
    );
    expect(html).toContain('<textarea');
    expect(html).toContain(DIRTY_NOTE);
    expect(html).toContain(SAVE_ERROR);
    expect(html).toContain('status-error');
    expect(html).toContain(SAVE_LABEL);
    expect(html).toContain(CANCEL_LABEL);
    expect(html).not.toContain(EDIT_LABEL);
  });

  it('treats whitespace-only notes as empty for the hint', () => {
    expect(catalogNoteHint('')).toBe(HINT);
    expect(catalogNoteHint('   ')).toBe(HINT);
    expect(catalogNoteHint(PAGE_NOTE)).toBe('');
  });

  it('marks dirty only when the draft differs from the last saved note', () => {
    expect(catalogNoteDirty(PAGE_NOTE, PAGE_NOTE)).toBe(false);
    expect(catalogNoteDirty(DIRTY_NOTE, PAGE_NOTE)).toBe(true);
    expect(catalogNoteDirty('hello ', 'hello')).toBe(true);
  });
});
