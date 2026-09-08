from django.test import SimpleTestCase
from django_components import registry


class ButtonRenderTests(SimpleTestCase):
    def test_default_button(self):
        html = registry.get("button").render(
            kwargs={"label": "Save & Test Connection"},
        )
        self.assertIn('class="ds-button"', html)
        self.assertNotIn("ds-button-small", html)
        self.assertIn("Save & Test Connection", html)
        self.assertNotIn("disabled", html)

    def test_small_button(self):
        html = registry.get("button").render(
            kwargs={"label": "저장", "size": "small"},
        )
        self.assertIn("ds-button", html)
        self.assertIn("ds-button-small", html)
        self.assertIn("저장", html)
        self.assertNotIn("disabled", html)

    def test_disabled_button(self):
        html = registry.get("button").render(
            kwargs={"label": "확인 중...", "disabled": True},
        )
        self.assertIn("ds-button", html)
        self.assertIn("확인 중...", html)
        self.assertIn("disabled", html)
        self.assertNotIn("ds-button-small", html)
