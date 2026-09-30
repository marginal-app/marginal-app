import 'package:flutter_test/flutter_test.dart';
import 'package:marginal_mobile/highlight_store.dart';

void main() {
  test('saves, lists per page, and updates a comment', () {
    final store = HighlightStore();
    final saved = store.handle({
      'type': 'SAVE_HIGHLIGHT',
      'payload': {
        'pageKey': 'https://example.com/',
        'quote': 'documentation',
        'prefix': 'for use in',
        'suffix': 'examples',
        'color': '#FFF3B0',
      },
    }) as Map<String, dynamic>;

    expect(saved['id'], 'm1');

    store.handle({
      'type': 'UPDATE_COMMENT',
      'payload': {'id': 'm1', 'comment': 'hi'},
    });

    final listed = store.handle({
      'type': 'GET_HIGHLIGHTS',
      'payload': {'pageKey': 'https://example.com/'},
    }) as List;
    expect(listed.single['comment'], 'hi');

    expect(
      store.handle({
        'type': 'GET_HIGHLIGHTS',
        'payload': {'pageKey': 'https://other.test/'},
      }),
      isEmpty,
    );
  });
}
