from django.test import SimpleTestCase

from ui_primitive.components.label.preview import PREVIEWS
from citry_preview.testing import render_component


def _example(slug: str):
    for example in PREVIEWS:
        if example.slug == slug:
            return example
    raise KeyError(slug)


class LabelTests(SimpleTestCase):
    def test_default_renders_text(self):
        example = _example("label-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-label"', html)
        self.assertIn("ds-label-kicker", html)
        self.assertIn("ds-label-text", html)
        self.assertIn("ds-label-hint", html)
        self.assertIn("Connection", html)
        self.assertIn("Server URL", html)
        self.assertIn("Host the extension uses to sync highlights.", html)
        self.assertNotIn(" for=", html)
