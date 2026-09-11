from pathlib import Path

from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.catalog_desk.catalog_desk import CatalogDesk
from highlights.components.catalog_note.catalog_note import LABEL, PAGE_NOTE
from highlights.components.catalog_row.catalog_row import CatalogRow


class CatalogRowConstructionTests(SimpleTestCase):
    def test_highlighted_row_shows_count(self):
        example = preview_by_slug(CatalogRow, "catalog-row-highlighted")
        html = render_component(example.component, example.kwargs)
        self.assertIn("catalog-row", html)
        self.assertIn("catalog-row-folio", html)
        self.assertIn("03", html)
        self.assertIn("Why Server-Rendered HTML Still Wins", html)
        self.assertIn("blog.example.org/posts/ssr", html)
        self.assertIn("밑줄 5", html)
        self.assertNotIn("is-selected", html)
        self.assertNotIn("hx-get", html)
        self.assertEqual(example.group, "Desk")

    def test_bookmarked_row_without_underlines(self):
        example = preview_by_slug(CatalogRow, "catalog-row-bookmarked")
        html = render_component(example.component, example.kwargs)
        self.assertIn("Item 321", html)
        self.assertIn("example.com/item?id=321", html)
        self.assertIn("북마크", html)
        self.assertNotIn("밑줄", html)
        self.assertIn("is-bookmarked", html)

    def test_active_row_is_elevated(self):
        example = preview_by_slug(CatalogRow, "catalog-row-highlighted-active")
        html = render_component(example.component, example.kwargs)
        self.assertIn("is-selected", html)
        self.assertEqual(example.group, "Desk")

    def test_select_url_wires_htmx_onto_the_same_desk(self):
        html = render_component(
            "catalog_row",
            {
                "catalog_id": "1",
                "title": "Hypothesis",
                "origin": "https://example.com",
                "path": "/hypothesis",
                "highlight_count": 2,
                "select_url": "/catalog/1/",
            },
        )
        self.assertIn('hx-get="/catalog/1/"', html)
        self.assertIn('hx-target="#catalog-desk"', html)
        self.assertIn('href="/catalog/1/"', html)
        selected = render_component(
            "catalog_row",
            {
                "title": "Hypothesis",
                "origin": "https://example.com",
                "path": "/hypothesis",
                "selected": True,
            },
        )
        self.assertIn("is-selected", selected)


class CatalogDeskConstructionTests(SimpleTestCase):
    def test_empty_list_has_a_closed_tray(self):
        example = preview_by_slug(CatalogDesk, "catalog-desk-empty")
        html = render_component(example.component, example.kwargs)
        self.assertIn("표시를 남긴 페이지가 없습니다", html)
        self.assertIn("ds-sidebar--collapsed", html)
        self.assertIn("라이브러리", html)
        self.assertIn("ds-view-tab", html)
        self.assertIn('class="ds-tray"', html)
        self.assertNotIn("is-open", html)
        self.assertNotIn("Hypothesis", html)
        self.assertNotIn('name="note"', html)

    def test_idle_list_keeps_the_tray_closed(self):
        example = preview_by_slug(CatalogDesk, "catalog-desk-idle")
        html = render_component(example.component, example.kwargs)
        self.assertIn("Why Server-Rendered HTML Still Wins", html)
        self.assertIn("Hypothesis", html)
        self.assertIn("Item 321", html)
        self.assertIn("ds-view-tab is-active", html)
        self.assertIn('class="ds-tray"', html)
        self.assertNotIn("is-open", html)
        self.assertNotIn('class="ds-tray-dismiss"', html)
        self.assertNotIn("Server-rendered HTML is a complete first paint.", html)

    def test_selected_opens_the_tray_with_a_document_card(self):
        example = preview_by_slug(CatalogDesk, "catalog-desk-selected")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-tray is-open", html)
        self.assertIn("is-selected", html)
        self.assertIn("ds-document-card", html)
        self.assertIn("Server-rendered HTML is a complete first paint.", html)
        self.assertIn("This is the silhouette we review before merge.", html)
        self.assertIn("웹에서 열기", html)
        self.assertIn("페이지 · 밑줄 5", html)
        self.assertIn(LABEL, html)
        self.assertIn(PAGE_NOTE, html)
        self.assertIn('name="note"', html)
        self.assertIn("코멘트 추가", html)
        self.assertIn('class="ds-tray-dismiss"', html)
        self.assertIn('href="/catalog/"', html)
        self.assertIn('hx-target="#catalog-desk"', html)

    def test_highlights_tab_uses_highlight_rows(self):
        example = preview_by_slug(CatalogDesk, "catalog-desk-highlights")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-highlight-row is-selected", html)
        self.assertIn("Cloud Agents can screenshot a component URL.", html)
        self.assertIn(LABEL, html)
        self.assertIn(PAGE_NOTE, html)
        self.assertEqual(example.group, "Desk")

    def test_comments_tab_uses_comment_rows(self):
        example = preview_by_slug(CatalogDesk, "catalog-desk-comments")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-comment-row is-selected", html)
        self.assertIn("리뷰 실루엣은 여기서 나온다.", html)
        self.assertEqual(example.group, "Desk")

    def test_named_states_are_desk(self):
        for slug in (
            "catalog-desk-empty",
            "catalog-desk-idle",
            "catalog-desk-selected",
            "catalog-desk-highlights",
            "catalog-desk-comments",
        ):
            self.assertEqual(preview_by_slug(CatalogDesk, slug).group, "Desk")

    def test_desk_css_does_not_restyle_the_tray(self):
        css = (
            Path(__file__)
            .resolve()
            .parent.joinpath("components/catalog_desk/catalog_desk.css")
            .read_text()
        )
        self.assertNotIn("ds-tray", css)
        self.assertNotIn("22.5rem", css)
