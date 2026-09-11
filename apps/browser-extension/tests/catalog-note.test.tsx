import { act, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, describe, expect, it } from 'vitest';
import CatalogNote, {
  HINT,
  LABEL,
  PAGE_NOTE,
  PLACEHOLDER,
  catalogNoteHint,
  emptyCatalogNote,
  filledCatalogNote,
} from '@/entrypoints/sidepanel/CatalogNote';

const mounts: Array<{ root: ReturnType<typeof createRoot>; node: HTMLDivElement }> =
  [];

afterEach(() => {
  for (const mount of mounts.splice(0)) {
    act(() => {
      mount.root.unmount();
    });
    mount.node.remove();
  }
});

function renderLive(ui: ReactNode) {
  const node = document.createElement('div');
  document.body.append(node);
  const root = createRoot(node);
  act(() => {
    root.render(ui);
  });
  mounts.push({ root, node });
  return node;
}

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

  it('commits the note field on blur without a comment payload', () => {
    const commits: string[] = [];
    const node = renderLive(
      <CatalogNote note="page-level note" onCommit={(value) => commits.push(value)} />,
    );
    const textarea = node.querySelector('textarea');
    expect(textarea?.getAttribute('name')).toBe('note');
    expect(textarea?.value).toBe('page-level note');
    act(() => {
      textarea?.dispatchEvent(new FocusEvent('blur', { bubbles: true }));
    });
    expect(commits).toEqual(['page-level note']);
  });
});
