import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import CatalogNote, {
  HINT,
  LABEL,
  PAGE_NOTE,
  PLACEHOLDER,
  catalogNoteHint,
  emptyCatalogNote,
  filledCatalogNote,
} from '@/entrypoints/sidepanel/CatalogNote';

describe('CatalogNote', () => {
  it('empty is a page note textarea without kicker, comment field, or auto-focus', () => {
    const html = renderToStaticMarkup(<CatalogNote {...emptyCatalogNote()} />);
    expect(html).toContain('catalog-note');
    expect(html).toContain(LABEL);
    expect(html).toContain(HINT);
    expect(html).toContain('하이라이트 코멘트');
    expect(html).toContain(PLACEHOLDER);
    expect(html).toContain('name="note"');
    expect(html).toContain('ds-textarea');
    expect(html).not.toContain('is-focused');
    expect(html).not.toContain('ds-label-kicker');
    expect(html).not.toContain('autofocus');
    expect(html).not.toContain('밑줄 코멘트');
    expect(html).not.toContain(PAGE_NOTE);
    expect(html).not.toContain('코멘트 추가');
    expect(html).not.toContain('name="comment"');
  });

  it('filled hides the hint and keeps the note field', () => {
    const html = renderToStaticMarkup(<CatalogNote {...filledCatalogNote()} />);
    expect(html).toContain(PAGE_NOTE);
    expect(html).toContain(LABEL);
    expect(html).toContain('name="note"');
    expect(html).not.toContain(HINT);
    expect(html).not.toContain('ds-label-hint');
    expect(html).not.toContain('is-focused');
    expect(html).not.toContain('ds-label-kicker');
    expect(html).not.toContain('코멘트 추가');
    expect(html).not.toContain('name="comment"');
  });

  it('treats whitespace-only notes as empty for the hint', () => {
    expect(catalogNoteHint('')).toBe(HINT);
    expect(catalogNoteHint('   ')).toBe(HINT);
    expect(catalogNoteHint(PAGE_NOTE)).toBe('');
  });
});
