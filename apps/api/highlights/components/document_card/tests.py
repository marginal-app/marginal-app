from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.document_card.document_card import HOST, TITLE, DocumentCard


class DocumentCardConstructionTests(SimpleTestCase):
    def test_row_nests_pills_and_the_serif_title(self):
        example = preview_by_slug(DocumentCard, "document-card-row")
        html = render_component(example.component, example.kwargs)
        self.assertIn('class="ds-document-card"', html)
        self.assertNotIn("ds-document-card--stack", html)
        self.assertIn("ds-document-card__mark", html)
        self.assertIn(">W</span>", html)
        self.assertIn(TITLE, html)
        self.assertIn(f"{HOST} · 밑줄 2", html)
        self.assertIn("북마크", html)
        self.assertIn("웹에서 열기", html)
        self.assertIn("ds-icon--star\"", html)
        self.assertIn("ds-icon--external", html)
        self.assertEqual(example.group, "Primitives")

    def test_bookmarked_row_activates_the_star_pill(self):
        example = preview_by_slug(DocumentCard, "document-card-row-bookmarked")
        html = render_component(example.component, example.kwargs)
        self.assertIn("북마크됨", html)
        self.assertIn("ds-icon--star-filled", html)
        self.assertIn("ds-pill-button is-active", html)

    def test_stack_is_the_narrow_layout(self):
        example = preview_by_slug(DocumentCard, "document-card-stack")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-document-card ds-document-card--stack", html)
        self.assertEqual(example.group, "Primitives")

    def test_unknown_layout_stays_row(self):
        html = render_component("document_card", {"layout": "grid"})
        self.assertIn('class="ds-document-card"', html)
        self.assertNotIn("ds-document-card--stack", html)
