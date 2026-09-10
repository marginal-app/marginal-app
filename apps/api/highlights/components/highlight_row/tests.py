from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.highlight_row.highlight_row import HOST, QUOTE, TITLE, HighlightRow


class HighlightRowConstructionTests(SimpleTestCase):
    def test_default_shows_title_under_the_quote(self):
        example = preview_by_slug(HighlightRow, "highlight-row-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-highlight-row"', html)
        self.assertNotIn("is-selected", html)
        self.assertIn("ds-highlight-row__chip", html)
        self.assertIn(QUOTE, html)
        self.assertIn("ds-highlight-row__title", html)
        self.assertIn(TITLE, html)
        self.assertIn(HOST, html)
        self.assertIn("12분 전", html)
        self.assertEqual(example.group, "Desk")

    def test_selected_moves_title_into_meta(self):
        example = preview_by_slug(HighlightRow, "highlight-row-selected")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-highlight-row is-selected", html)
        self.assertIn("ds-highlight-row__kicker", html)
        self.assertNotIn("ds-highlight-row__title", html)
        self.assertIn(TITLE, html)
        self.assertEqual(example.group, "Desk")
