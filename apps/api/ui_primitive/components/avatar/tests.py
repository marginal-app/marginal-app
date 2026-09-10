from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.avatar.avatar import Avatar


class AvatarConstructionTests(SimpleTestCase):
    def test_default_renders_accent_initials(self):
        example = preview_by_slug(Avatar, "avatar-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-avatar"', html)
        self.assertIn("M", html)
        self.assertEqual(example.group, "Primitives")

    def test_blank_initials_fall_back_to_m(self):
        html = render_component("avatar", {"initials": "  "})
        self.assertIn(">M</span>", html)
