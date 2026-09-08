const PASTEL_COLORS = ['#FFF3B0', '#FFD6E0', '#C9F2C7', '#C7E8FF', '#E3D4FF'];

function extractContext(blockEl: Element, quote: string, wordCount = 6) {
  const text = blockEl.textContent ?? '';
  const idx = text.indexOf(quote);
  if (idx === -1) return { prefix: '', suffix: '' };

  const before = text.slice(0, idx);
  const after = text.slice(idx + quote.length);

  const prefixWords = before.match(/\S+/g) ?? [];
  const suffixWords = after.match(/\S+/g) ?? [];

  return {
    prefix: prefixWords.slice(-wordCount).join(' '),
    suffix: suffixWords.slice(0, wordCount).join(' '),
  };
}

export default defineContentScript({
  matches: ['<all_urls>'],
  runAt: 'document_idle',
  async main(ctx) {
    let pendingRange: Range | null = null;

    const ui = await createShadowRootUi(ctx, {
      name: 'marginal-toolbar',
      position: 'overlay',
      anchor: () => document.body,
      onMount(container) {
        const toolbar = document.createElement('div');
        toolbar.style.position = 'fixed';
        toolbar.style.display = 'none';
        toolbar.style.gap = '6px';
        toolbar.style.padding = '6px';
        toolbar.style.background = '#1f1f1f';
        toolbar.style.borderRadius = '999px';
        toolbar.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';

        PASTEL_COLORS.forEach((color) => {
          const dot = document.createElement('button');
          dot.style.width = '18px';
          dot.style.height = '18px';
          dot.style.borderRadius = '50%';
          dot.style.border = 'none';
          dot.style.cursor = 'pointer';
          dot.style.backgroundColor = color;

          dot.addEventListener('click', () => {
            if (!pendingRange) return;

            const mark = document.createElement('mark');
            mark.style.backgroundColor = color;
            mark.style.borderRadius = '2px';

            try {
              pendingRange.surroundContents(mark);
            } catch (error) {
              console.error('여러 노드에 걸친 선택은 아직 처리 못함', error);
            }

            hideToolbar();
            window.getSelection()?.removeAllRanges();
          });

          toolbar.appendChild(dot);
        });

        container.appendChild(toolbar);
        return toolbar;
      },
    });
    ui.mount();
    const toolbarEl = ui.mounted!;

    function hideToolbar() {
      toolbarEl.style.display = 'none';
      pendingRange = null;
    }

    document.addEventListener('mouseup', (event) => {
      if (toolbarEl.contains(event.target as Node)) return;

      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        hideToolbar();
        return;
      }

      const range = selection.getRangeAt(0);
      const quote = range.toString().trim();
      if (!quote) {
        hideToolbar();
        return;
      }

      const startNode = range.commonAncestorContainer;
      const containerEl =
        startNode.nodeType === Node.TEXT_NODE
          ? startNode.parentElement
          : (startNode as Element);
      const blockEl = containerEl?.closest('p, li, h1, h2, h3, h4, h5, h6');
      if (!blockEl) {
        hideToolbar();
        return;
      }

      const { prefix, suffix } = extractContext(blockEl, quote);
      console.log({ quote, prefix, suffix });

      pendingRange = range.cloneRange();

      const rect = range.getBoundingClientRect();
      toolbarEl.style.display = 'flex';
      toolbarEl.style.top = `${Math.max(rect.top - toolbarEl.offsetHeight - 8, 8)}px`;
      toolbarEl.style.left = `${rect.left + rect.width / 2 - toolbarEl.offsetWidth / 2}px`;
    });

    document.addEventListener('scroll', hideToolbar, true);
  },
});
