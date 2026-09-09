import { defineConfig } from 'wxt';

// See https://wxt.dev/api/config.html
export default defineConfig({
  modules: ['@wxt-dev/module-react'],
  zip: {
    name: 'marginal',
  },
  manifest: ({ mode }) => ({
    name: mode === 'development' ? 'Marginal (Dev)' : 'Marginal',
    permissions: ['storage'],
  }),
  webExt: {
    // Without this, `wxt dev` launches a fresh throwaway profile every time
    // (via web-ext), so extension storage (IndexedDB included) looks wiped
    // on every relaunch. Pinning + persisting a profile fixes that.
    chromiumProfile: '.wxt/chrome-data',
    keepProfileChanges: true,
  },
});
