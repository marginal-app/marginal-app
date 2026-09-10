from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.icon.icon import GLYPHS, Icon


class IconConstructionTests(SimpleTestCase):
    def test_default_renders_the_home_glyph(self):
        example = preview_by_slug(Icon, "icon-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-icon ds-icon--home"', html)
        self.assertIn('role="img"', html)
        self.assertIn('aria-label="홈"', html)
        self.assertNotIn("aria-hidden", html)
        self.assertEqual(example.group, "Primitives")

    def test_unlabelled_glyph_is_hidden_from_assistive_tech(self):
        html = render_component("icon", {"name": "settings"})
        self.assertIn('class="ds-icon ds-icon--settings"', html)
        self.assertIn('aria-hidden="true"', html)
        self.assertNotIn("role=", html)
        self.assertNotIn("aria-label", html)

    def test_every_named_glyph_has_a_modifier_class(self):
        for name in GLYPHS:
            html = render_component("icon", {"name": name})
            self.assertIn(f"ds-icon--{name}", html)

    def test_unknown_name_falls_back_to_home(self):
        html = render_component("icon", {"name": "not-a-glyph"})
        self.assertIn("ds-icon--home", html)
        self.assertNotIn("ds-icon--not-a-glyph", html)
