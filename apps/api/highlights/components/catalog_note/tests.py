from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.catalog_note.catalog_note import (
    CANCEL_LABEL,
    DIRTY_NOTE,
    EDIT_LABEL,
    HINT,
    LABEL,
    PAGE_NOTE,
    PLACEHOLDER,
    SAVE_ERROR,
    SAVE_LABEL,
    CatalogNote,
)


class CatalogNoteConstructionTests(SimpleTestCase):
    def test_empty_read_shows_placeholder_and_pencil(self):
        example = preview_by_slug(CatalogNote, "catalog-note-empty")
        html = render_component(example.component, example.kwargs)
        self.assertEqual(example.group, "Primitives")
        self.assertIn("catalog-note", html)
        self.assertIn(LABEL, html)
        self.assertIn(HINT, html)
        self.assertIn("하이라이트 코멘트", html)
        self.assertIn(PLACEHOLDER, html)
        self.assertIn("catalog-note__read is-empty", html)
        self.assertIn(EDIT_LABEL, html)
        self.assertIn("✎", html)
        self.assertNotIn("<textarea", html)
        self.assertNotIn(SAVE_LABEL, html)
        self.assertNotIn("is-focused", html)
        self.assertNotIn("ds-label-kicker", html)
        self.assertNotIn("밑줄 코멘트", html)
        self.assertNotIn("autofocus", html)
        self.assertNotIn(PAGE_NOTE, html)
        self.assertNotIn("코멘트 추가", html)
        self.assertNotIn('name="comment"', html)
        self.assertNotIn("onblur", html.lower())

    def test_filled_read_shows_the_note_and_hides_the_hint(self):
        example = preview_by_slug(CatalogNote, "catalog-note-filled")
        html = render_component(example.component, example.kwargs)
        self.assertIn(PAGE_NOTE, html)
        self.assertIn(LABEL, html)
        self.assertIn("catalog-note__read", html)
        self.assertIn(EDIT_LABEL, html)
        self.assertNotIn(HINT, html)
        self.assertNotIn("<textarea", html)
        self.assertNotIn(SAVE_LABEL, html)
        self.assertNotIn("is-focused", html)
        self.assertNotIn("ds-label-kicker", html)
        self.assertNotIn("코멘트 추가", html)
        self.assertNotIn('name="comment"', html)
        self.assertNotIn("onblur", html.lower())

    def test_edit_clean_disables_save(self):
        example = preview_by_slug(CatalogNote, "catalog-note-edit-clean")
        html = render_component(example.component, example.kwargs)
        self.assertIn("<textarea", html)
        self.assertIn(PAGE_NOTE, html)
        self.assertIn('name="note"', html)
        self.assertIn(SAVE_LABEL, html)
        self.assertIn(CANCEL_LABEL, html)
        self.assertIn("disabled", html)
        self.assertNotIn(EDIT_LABEL, html)
        self.assertNotIn(HINT, html)
        self.assertNotIn(SAVE_ERROR, html)
        self.assertNotIn("onblur", html.lower())
        self.assertNotIn('name="comment"', html)

    def test_edit_dirty_enables_save(self):
        example = preview_by_slug(CatalogNote, "catalog-note-edit-dirty")
        html = render_component(example.component, example.kwargs)
        self.assertIn(DIRTY_NOTE, html)
        self.assertIn(SAVE_LABEL, html)
        self.assertIn(CANCEL_LABEL, html)
        self.assertIn('name="note"', html)
        self.assertNotRegex(html, r"disabled[^>]*>저장")
        self.assertNotIn(EDIT_LABEL, html)
        self.assertNotIn(HINT, html)
        self.assertNotIn(SAVE_ERROR, html)
        self.assertNotIn("onblur", html.lower())

    def test_edit_error_stays_in_edit_with_a_short_error(self):
        example = preview_by_slug(CatalogNote, "catalog-note-edit-error")
        html = render_component(example.component, example.kwargs)
        self.assertIn("<textarea", html)
        self.assertIn(DIRTY_NOTE, html)
        self.assertIn(SAVE_ERROR, html)
        self.assertIn("status-error", html)
        self.assertIn(SAVE_LABEL, html)
        self.assertIn(CANCEL_LABEL, html)
        self.assertNotIn(EDIT_LABEL, html)
        self.assertNotIn("onblur", html.lower())
