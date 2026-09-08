from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.button.button import Button


class ButtonConstructionTests(SimpleTestCase):
    def test_default_button(self):
        example = preview_by_slug(Button, "button-default")
        html = render_component("button", example.kwargs)
        self.assertIn('class="button"', html)
        self.assertNotIn("small", html)
        self.assertIn("Save &amp; Test Connection", html)
        self.assertNotIn("disabled", html)
        self.assertNotIn("is-focused", html)

    def test_small_button(self):
        example = preview_by_slug(Button, "button-small")
        html = render_component("button", example.kwargs)
        self.assertIn("button", html)
        self.assertIn("small", html)
        self.assertIn("저장", html)
        self.assertNotIn("disabled", html)

    def test_disabled_button(self):
        example = preview_by_slug(Button, "button-disabled")
        html = render_component("button", example.kwargs)
        self.assertIn("button", html)
        self.assertIn("확인 중...", html)
        self.assertIn("disabled", html)
        self.assertNotIn("small", html)
        self.assertNotIn("is-focused", html)

    def test_focused_button(self):
        example = preview_by_slug(Button, "button-focus")
        html = render_component("button", example.kwargs)
        self.assertIn("is-focused", html)
        self.assertIn("Save &amp; Test Connection", html)
        self.assertNotIn("disabled", html)

    def test_named_states_are_primitives(self):
        for slug in ("button-default", "button-small", "button-disabled", "button-focus"):
            self.assertEqual(preview_by_slug(Button, slug).group, "Primitives")
