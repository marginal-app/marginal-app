from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.label.label import Label


class LabelTests(SimpleTestCase):
    def test_default_renders_text(self):
        example = preview_by_slug(Label, "label-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-label"', html)
        self.assertIn("ds-label-kicker", html)
        self.assertIn("ds-label-text", html)
        self.assertIn("ds-label-hint", html)
        self.assertIn("Connection", html)
        self.assertIn("Server URL", html)
        self.assertIn("Host the extension uses to sync highlights.", html)
        self.assertNotIn(" for=", html)
