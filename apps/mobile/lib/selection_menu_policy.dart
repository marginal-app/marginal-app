import 'package:flutter_inappwebview/flutter_inappwebview.dart';

/// What happens to the platform's own text-selection menu (Copy, Share,
/// Select all) while the in-page toolbar is showing.
///
/// This is the platform seam: the page-side overlay is shared, but Android
/// and iOS each draw a native menu over the selection that can collide with
/// it. iOS gets its own policy when it is added.
enum SelectionMenuPolicy {
  /// Suppress the system items so only the Marginal toolbar shows.
  hideSystem('Hide system menu'),

  /// Leave the system menu alone, to see how the two overlap.
  keepSystem('Keep system menu');

  const SelectionMenuPolicy(this.label);

  final String label;

  ContextMenu get contextMenu => ContextMenu(
    settings: ContextMenuSettings(
      hideDefaultSystemContextMenuItems: this == hideSystem,
    ),
  );
}
