from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from ui_primitive.components.wordmark.wordmark import Wordmark


class WordmarkConstructionTests(SimpleTestCase):
    def test_lg_is_the_desk_masthead(self):
        example = preview_by_slug(Wordmark, "wordmark-lg")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-wordmark"', html)
        self.assertNotIn("ds-wordmark--sm", html)
        self.assertIn("Marginal", html)
        self.assertIn("ds-wordmark__rule", html)
        self.assertEqual(example.group, "Primitives")

    def test_sm_is_the_compact_sidebar_mark(self):
        example = preview_by_slug(Wordmark, "wordmark-sm")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-wordmark ds-wordmark--sm", html)
        self.assertIn("Marginal", html)

    def test_unknown_size_falls_back_to_lg(self):
        html = render_component("wordmark", {"size": "xl"})
        self.assertIn('class="ds-wordmark"', html)
        self.assertNotIn("ds-wordmark--sm", html)
