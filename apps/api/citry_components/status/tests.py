from django.test import SimpleTestCase

from citry_components.status.examples import EXAMPLES
from citry_components.testing import render_component


def _example(slug: str):
    return next(example for example in EXAMPLES if example.slug == slug)


class StatusConstructionTests(SimpleTestCase):
    def test_ok_tone_renders_success_class_and_message(self):
        example = _example("status-ok")
        html = render_component("status", example.kwargs)
        self.assertIn('class="status status-ok"', html)
        self.assertIn("status-dot", html)
        self.assertIn("status-message", html)
        self.assertNotIn("status-error", html)
        self.assertIn("연결 성공 — 저장했습니다.", html)

    def test_error_tone_renders_error_class_and_message(self):
        example = _example("status-error")
        html = render_component("status", example.kwargs)
        self.assertIn('class="status status-error"', html)
        self.assertIn("status-dot", html)
        self.assertIn("status-message", html)
        self.assertNotIn("status-ok", html)
        self.assertIn("연결 실패: 서버가 401로 응답했습니다", html)

    def test_named_states_are_primitives(self):
        slugs = {example.slug: example.group for example in EXAMPLES}
        self.assertEqual(slugs["status-ok"], "Primitives")
        self.assertEqual(slugs["status-error"], "Primitives")
