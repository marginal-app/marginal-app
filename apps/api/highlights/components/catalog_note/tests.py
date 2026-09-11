from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.catalog_note.catalog_note import (
    HINT,
    LABEL,
    PAGE_NOTE,
    PLACEHOLDER,
    CatalogNote,
)


class CatalogNoteConstructionTests(SimpleTestCase):
    def test_empty_is_a_page_note_textarea(self):
        example = preview_by_slug(CatalogNote, "catalog-note-empty")
        html = render_component(example.component, example.kwargs)
        self.assertEqual(example.group, "Primitives")
        self.assertIn("catalog-note", html)
        self.assertIn(LABEL, html)
        self.assertIn(HINT, html)
        self.assertIn("하이라이트 코멘트", html)
        self.assertIn(PLACEHOLDER, html)
        self.assertIn('name="note"', html)
        self.assertIn("ds-textarea", html)
        self.assertNotIn("is-focused", html)
        self.assertNotIn("ds-label-kicker", html)
        self.assertNotIn("밑줄 코멘트", html)
        self.assertNotIn("autofocus", html)
        self.assertNotIn(PAGE_NOTE, html)
        self.assertNotIn("코멘트 추가", html)
        self.assertNotIn('name="comment"', html)

    def test_filled_renders_the_catalog_note(self):
        example = preview_by_slug(CatalogNote, "catalog-note-filled")
        html = render_component(example.component, example.kwargs)
        self.assertEqual(example.group, "Primitives")
        self.assertIn(PAGE_NOTE, html)
        self.assertIn(LABEL, html)
        self.assertIn('name="note"', html)
        self.assertNotIn(HINT, html)
        self.assertNotIn("is-focused", html)
        self.assertNotIn("ds-label-kicker", html)
        self.assertNotIn("코멘트 추가", html)
        self.assertNotIn('name="comment"', html)
