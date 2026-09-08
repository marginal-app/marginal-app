from django.test import SimpleTestCase
from django_components import registry

from components.status.examples import EXAMPLES


def _example(slug: str):
    return next(example for example in EXAMPLES if example.slug == slug)


class StatusConstructionTests(SimpleTestCase):
    def test_ok_tone_renders_success_class_and_message(self):
        example = _example("status-ok")
        html = registry.get("status").render(kwargs=example.kwargs)
        self.assertIn("status", html)
        self.assertIn("status-ok", html)
        self.assertNotIn("status-error", html)
        self.assertIn("연결 성공 — 저장했습니다.", html)

    def test_error_tone_renders_error_class_and_message(self):
        example = _example("status-error")
        html = registry.get("status").render(kwargs=example.kwargs)
        self.assertIn("status", html)
        self.assertIn("status-error", html)
        self.assertNotIn("status-ok", html)
        self.assertIn("연결 실패: 서버가 401로 응답했습니다", html)

    def test_named_states_are_primitives(self):
        slugs = {example.slug: example.group for example in EXAMPLES}
        self.assertEqual(slugs["status-ok"], "Primitives")
        self.assertEqual(slugs["status-error"], "Primitives")
