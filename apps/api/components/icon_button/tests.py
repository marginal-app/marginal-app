from django.test import SimpleTestCase
from django_components import registry


class IconButtonConstructionTests(SimpleTestCase):
    def test_default_icon_button(self):
        html = registry.get("icon_button").render(
            kwargs={"icon": "⚙", "aria_label": "설정 열기"},
        )
        self.assertIn('class="ds-icon-button"', html)
        self.assertIn('type="button"', html)
        self.assertIn('aria-label="설정 열기"', html)
        self.assertIn('title="설정 열기"', html)
        self.assertIn("⚙", html)
        self.assertNotIn("disabled", html)

    def test_disabled_icon_button(self):
        html = registry.get("icon_button").render(
            kwargs={"icon": "⚙", "aria_label": "설정 열기", "disabled": True},
        )
        self.assertIn('class="ds-icon-button"', html)
        self.assertIn("disabled", html)
        self.assertIn("⚙", html)
