export default defineBackground(() => {
  console.log('Hello background!', { id: browser.runtime.id });

  // Chromium's `chrome.sidePanel` API is what makes the toolbar icon open the
  // side panel instead of an action popup. Firefox has no equivalent API: its
  // `sidebar_action` manifest key already opens the sidebar on icon click.
  if (import.meta.env.CHROME || import.meta.env.EDGE) {
    chrome.sidePanel
      .setPanelBehavior({ openPanelOnActionClick: true })
      .catch((error: unknown) => console.error(error));
  }
});
