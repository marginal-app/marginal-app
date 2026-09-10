from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.marginalia.marginalia import NOTE, PLACEHOLDER, QUOTE, Marginalia


class MarginaliaConstructionTests(SimpleTestCase):
    def test_quote_shows_the_placeholder(self):
        example = preview_by_slug(Marginalia, "marginalia-quote")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-marginalia", html)
        self.assertIn("ds-marginalia__rule", html)
        self.assertIn(QUOTE, html)
        self.assertIn(PLACEHOLDER, html)
        self.assertIn("is-placeholder", html)
        self.assertNotIn(NOTE, html)
        self.assertEqual(example.group, "Primitives")

    def test_note_is_the_saved_comment(self):
        example = preview_by_slug(Marginalia, "marginalia-note")
        html = render_component(example.component, example.kwargs)
        self.assertIn(NOTE, html)
        self.assertNotIn(PLACEHOLDER, html)
        self.assertNotIn("is-placeholder", html)
        self.assertEqual(example.group, "Primitives")
