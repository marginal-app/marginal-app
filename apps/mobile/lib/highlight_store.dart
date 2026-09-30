/// In-memory stand-in for the extension's background store.
///
/// The spike only proves that the overlay's port reaches Dart; persistence
/// and sync are out of scope, so highlights live until the app restarts.
class HighlightStore {
  final Map<String, List<Map<String, dynamic>>> _byPage = {};
  int _nextId = 1;

  /// Handles one `{type, payload}` message from the page's `flutterPort`.
  /// Message names mirror `apps/browser-extension/utils/highlight-messages.ts`.
  Object? handle(Map<String, dynamic> message) {
    final payload = Map<String, dynamic>.from(message['payload'] as Map);
    switch (message['type']) {
      case 'SAVE_HIGHLIGHT':
        final record = {...payload, 'id': 'm${_nextId++}'};
        _byPage.putIfAbsent(payload['pageKey'] as String, () => []).add(record);
        return record;
      case 'GET_HIGHLIGHTS':
        return _byPage[payload['pageKey']] ?? const [];
      case 'UPDATE_COMMENT':
        for (final records in _byPage.values) {
          for (final record in records) {
            if (record['id'] == payload['id']) {
              record['comment'] = payload['comment'];
            }
          }
        }
        return null;
    }
    throw ArgumentError('unknown message type: ${message['type']}');
  }
}
