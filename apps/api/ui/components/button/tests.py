from django.test import SimpleTestCase

from ui.components.button.preview import PREVIEWS
from citry_components.testing import render_component


def _example(slug: str):
    return next(example for example in PREVIEWS if example.slug == slug)


class ButtonConstructionTests(SimpleTestCase):
    def test_default_button(self):
        example = _example("button-default")
        html = render_component("button", example.kwargs)
        self.assertIn('class="button"', html)
        self.assertNotIn("small", html)
        self.assertIn("Save &amp; Test Connection", html)
        self.assertNotIn("disabled", html)
        self.assertNotIn("is-focused", html)

    def test_small_button(self):
        example = _example("button-small")
        html = render_component("button", example.kwargs)
        self.assertIn("button", html)
        self.assertIn("small", html)
        self.assertIn("저장", html)
        self.assertNotIn("disabled", html)

    def test_disabled_button(self):
        example = _example("button-disabled")
        html = render_component("button", example.kwargs)
        self.assertIn("button", html)
        self.assertIn("확인 중...", html)
        self.assertIn("disabled", html)
        self.assertNotIn("small", html)
        self.assertNotIn("is-focused", html)

    def test_focused_button(self):
        example = _example("button-focus")
        html = render_component("button", example.kwargs)
        self.assertIn("is-focused", html)
        self.assertIn("Save &amp; Test Connection", html)
        self.assertNotIn("disabled", html)

    def test_named_states_are_primitives(self):
        slugs = {example.slug: example.group for example in PREVIEWS}
        self.assertEqual(slugs["button-default"], "Primitives")
        self.assertEqual(slugs["button-small"], "Primitives")
        self.assertEqual(slugs["button-disabled"], "Primitives")
        self.assertEqual(slugs["button-focus"], "Primitives")
