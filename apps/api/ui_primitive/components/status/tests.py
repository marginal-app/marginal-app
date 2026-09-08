from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.status.status import Status


class StatusConstructionTests(SimpleTestCase):
    def test_ok_tone_renders_success_class_and_message(self):
        example = preview_by_slug(Status, "status-ok")
        html = render_component("status", example.kwargs)
        self.assertIn('class="status status-ok"', html)
        self.assertIn("status-dot", html)
        self.assertIn("status-message", html)
        self.assertNotIn("status-error", html)
        self.assertIn("연결 성공 — 저장했습니다.", html)

    def test_error_tone_renders_error_class_and_message(self):
        example = preview_by_slug(Status, "status-error")
        html = render_component("status", example.kwargs)
        self.assertIn('class="status status-error"', html)
        self.assertIn("status-dot", html)
        self.assertIn("status-message", html)
        self.assertNotIn("status-ok", html)
        self.assertIn("연결 실패: 서버가 401로 응답했습니다", html)

    def test_named_states_are_primitives(self):
        self.assertEqual(preview_by_slug(Status, "status-ok").group, "Primitives")
        self.assertEqual(preview_by_slug(Status, "status-error").group, "Primitives")
