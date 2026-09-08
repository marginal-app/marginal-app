from django.test import SimpleTestCase
from django_components import registry


class StatusConstructionTests(SimpleTestCase):
    def test_ok_tone_renders_success_class_and_message(self):
        html = registry.get("status").render(
            kwargs={"tone": "ok", "message": "연결 성공 — 저장했습니다."},
        )
        self.assertIn("ds-status", html)
        self.assertIn("ds-status-ok", html)
        self.assertNotIn("ds-status-error", html)
        self.assertIn("연결 성공 — 저장했습니다.", html)

    def test_error_tone_renders_error_class_and_message(self):
        html = registry.get("status").render(
            kwargs={
                "tone": "error",
                "message": "연결 실패: 서버가 401로 응답했습니다",
            },
        )
        self.assertIn("ds-status", html)
        self.assertIn("ds-status-error", html)
        self.assertNotIn("ds-status-ok", html)
        self.assertIn("연결 실패: 서버가 401로 응답했습니다", html)
