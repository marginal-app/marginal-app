import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';

// One classic script for flutter_inappwebview's UserScript: no module
// loader on the page, so the overlay and the port bundle into an IIFE.
export default defineConfig({
  build: {
    lib: {
      entry: fileURLToPath(new URL('./main.ts', import.meta.url)),
      formats: ['iife'],
      name: 'MarginalBridge',
      fileName: () => 'marginal.js',
    },
    outDir: fileURLToPath(new URL('../assets/bridge', import.meta.url)),
    emptyOutDir: true,
    target: 'es2020',
    minify: false,
  },
});
