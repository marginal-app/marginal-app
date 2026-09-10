from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.pill_button.pill_button import PillButton


class PillButtonConstructionTests(SimpleTestCase):
    def test_default_nests_the_star_icon(self):
        example = preview_by_slug(PillButton, "pill-button-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-pill-button"', html)
        self.assertNotIn("is-active", html)
        self.assertIn("ds-icon--star\"", html)
        self.assertNotIn("ds-icon--star-filled", html)
        self.assertIn("북마크", html)
        self.assertEqual(example.group, "Primitives")

    def test_active_is_an_accent_hairline(self):
        example = preview_by_slug(PillButton, "pill-button-active")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-pill-button is-active", html)
        self.assertIn("ds-icon--star-filled", html)
        self.assertIn("북마크됨", html)

    def test_unknown_icon_falls_back_to_star(self):
        html = render_component("pill_button", {"icon": "not-a-glyph", "label": "저장"})
        self.assertIn("ds-icon--star", html)
        self.assertNotIn("ds-icon--not-a-glyph", html)
        self.assertIn("저장", html)
