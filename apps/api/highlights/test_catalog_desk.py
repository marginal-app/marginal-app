from pathlib import Path

from django.test import SimpleTestCase

from citry_preview.testing import preview_by_slug, render_component
from highlights.components.catalog_desk.catalog_desk import CatalogDesk
from highlights.components.catalog_row.catalog_row import CatalogRow


class CatalogRowConstructionTests(SimpleTestCase):
    def test_highlighted_row_shows_count(self):
        example = preview_by_slug(CatalogRow, "catalog-row-highlighted")
        html = render_component(example.component, example.kwargs)
        self.assertIn("catalog-row", html)
        self.assertIn("Hypothesis", html)
        self.assertIn("https://example.com/hypothesis", html)
        self.assertIn("밑줄 2", html)
        self.assertNotIn("is-selected", html)
        self.assertNotIn("hx-get", html)

    def test_bookmarked_row_without_underlines(self):
        example = preview_by_slug(CatalogRow, "catalog-row-bookmarked")
        html = render_component(example.component, example.kwargs)
        self.assertIn("Item 321", html)
        self.assertIn("북마크", html)
        self.assertNotIn("밑줄", html)

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
        self.assertIn('class="ds-tray"', html)
        self.assertNotIn("is-open", html)
        self.assertNotIn("Hypothesis", html)

    def test_idle_list_keeps_the_tray_closed(self):
        example = preview_by_slug(CatalogDesk, "catalog-desk-idle")
        html = render_component(example.component, example.kwargs)
        self.assertIn("Hypothesis", html)
        self.assertIn("Item 321", html)
        self.assertIn('class="ds-tray"', html)
        self.assertNotIn("is-open", html)
        self.assertNotIn('class="ds-tray-dismiss"', html)
        self.assertNotIn("Server-rendered HTML is a complete first paint.", html)

    def test_selected_opens_the_tray_with_highlight_cards(self):
        example = preview_by_slug(CatalogDesk, "catalog-desk-selected")
        html = render_component(example.component, example.kwargs)
        self.assertIn("ds-tray is-open", html)
        self.assertIn("is-selected", html)
        self.assertIn("Server-rendered HTML is a complete first paint.", html)
        self.assertIn("This is the silhouette we review before merge.", html)
        self.assertIn("원문", html)
        self.assertIn('class="ds-tray-dismiss"', html)
        self.assertIn('href="/catalog/"', html)
        self.assertIn('hx-target="#catalog-desk"', html)

    def test_named_states_are_desk(self):
        for slug in (
            "catalog-desk-empty",
            "catalog-desk-idle",
            "catalog-desk-selected",
        ):
            self.assertEqual(preview_by_slug(CatalogDesk, slug).group, "Desk")

    def test_desk_css_does_not_restyle_the_tray(self):
        css = Path(__file__).resolve().parent.joinpath(
            "components/catalog_desk/catalog_desk.css"
        ).read_text()
        self.assertNotIn("ds-tray", css)
        self.assertNotIn("22.5rem", css)
