# Marginal mobile (spike)

Hypothesis: the extension's in-page overlay (`@marginal-app/overlay`) runs
unchanged inside a Flutter WebView. Only the port (Flutter bridge instead of
`browser.runtime`) and the selection trigger (`selectionchange` instead of
`mouseup`) differ.

Android only for now. iOS is added with `flutter create --platforms=ios .`
plus an iOS `SelectionMenuPolicy`.

## Run

```bash
pnpm --filter @marginal-app/mobile build:bridge   # writes assets/bridge/marginal.js (gitignored)
cd apps/mobile
flutter run
```

| Piece | Where |
| --- | --- |
| Page-side composition root (port + trigger) | `bridge/main.ts` |
| Dart composition root (in-memory store) | `lib/highlight_store.dart` |
| Native selection menu seam | `lib/selection_menu_policy.dart` |

`flutter_inappwebview` is pinned to `6.2.0-beta.3`: 6.1.x's Android module
uses `proguard-android.txt`, which AGP 9 rejects.
