from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.comment_row.comment_row import HOST, NOTE, QUOTE, TITLE, CommentRow


class CommentRowConstructionTests(SimpleTestCase):
    def test_default_shows_note_quote_and_meta(self):
        example = preview_by_slug(CommentRow, "comment-row-default")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-comment-row"', html)
        self.assertNotIn("is-selected", html)
        self.assertIn("ds-comment-row__chip", html)
        self.assertIn(NOTE, html)
        self.assertIn(QUOTE, html)
        self.assertIn(TITLE, html)
        self.assertIn(HOST, html)
        self.assertIn("12분 전", html)
        self.assertEqual(example.group, "Desk")

    def test_selected_keeps_the_same_copy_on_an_elevated_fill(self):
        example = preview_by_slug(CommentRow, "comment-row-selected")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-comment-row is-selected", html)
        self.assertIn(NOTE, html)
        self.assertIn(QUOTE, html)
        self.assertIn(TITLE, html)
        self.assertEqual(example.group, "Desk")
