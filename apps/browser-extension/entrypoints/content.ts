export default defineContentScript({
  matches: ['<all_urls>'],
  runAt: 'document_idle',
  main() {
    document.addEventListener('mouseup', () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) return;

      const range = selection.getRangeAt(0);
      const quote = range.toString().trim();
      if (!quote) return;

      const startNode = range.commonAncestorContainer;
      const containerEl =
        startNode.nodeType === Node.TEXT_NODE
          ? startNode.parentElement
          : (startNode as Element)

      const blockEl = containerEl?.closest('p, li, h1, h2, h3, h4, h5, h6')

      const rect = range.getBoundingClientRect();

      console.log({ quote, blockEl, rect })
    })
  },
});
