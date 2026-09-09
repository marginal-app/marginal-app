from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app
from highlights.components.highlight_card.highlight_card import QUOTE_ONLY, WITH_COMMENT

ROW_MARKED = {
    "catalog_id": "1",
    "title": "Hypothesis",
    "origin": "https://example.com",
    "path": "/hypothesis",
    "query": "",
    "highlight_count": 2,
    "bookmarked": False,
    "selected": False,
    "select_url": "",
    "source_href": "https://example.com/hypothesis",
}

ROW_BOOKMARKED = {
    "catalog_id": "2",
    "title": "Item 321",
    "origin": "https://example.com",
    "path": "/item",
    "query": "?id=321",
    "highlight_count": 0,
    "bookmarked": True,
    "selected": False,
    "select_url": "",
    "source_href": "https://example.com/item?id=321",
}

PANE_HIGHLIGHTS = [
    {**QUOTE_ONLY, "comment_edit_url": "", "comment_save_url": ""},
    {**WITH_COMMENT, "comment_edit_url": "", "comment_save_url": ""},
]


class CatalogDesk(Component):
    citry = app
    name = "catalog_desk"
    template_file = "catalog_desk.citry-html"
    css_file = "catalog_desk.css"

    @dataclass
    class Kwargs:
        rows: list[dict[str, Any]] = field(default_factory=list)
        selected: bool = False
        pane_title: str = ""
        source_href: str = ""
        highlights: list[dict[str, Any]] = field(default_factory=list)
        csrf_token: str = ""
        dismiss_url: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            selected_row = {**ROW_MARKED, "selected": True}
            return [
                meta(
                    variant(),
                    slug="catalog-desk-empty",
                    title="CatalogDesk / empty",
                    description="No marked pages yet.",
                ),
                meta(
                    variant(rows=[ROW_MARKED, ROW_BOOKMARKED]),
                    slug="catalog-desk-idle",
                    title="CatalogDesk / idle",
                    description="List on the left. Nothing selected.",
                ),
                meta(
                    variant(
                        rows=[selected_row, ROW_BOOKMARKED],
                        selected=True,
                        pane_title="Hypothesis",
                        source_href="https://example.com/hypothesis",
                        highlights=PANE_HIGHLIGHTS,
                        dismiss_url="/catalog/",
                    ),
                    slug="catalog-desk-selected",
                    title="CatalogDesk / selected",
                    description="Click a row; highlights open on the right.",
                ),
            ]

    def template_data(self, kwargs, slots):
        selected = kwargs.selected
        highlights = kwargs.highlights
        dismiss_url = kwargs.dismiss_url if selected else ""
        return {
            "rows": kwargs.rows,
            "is_empty": not kwargs.rows,
            "selected": selected,
            "show_highlights": selected and bool(highlights),
            "show_bookmark_empty": selected and not highlights,
            "pane_title": kwargs.pane_title,
            "source_href": kwargs.source_href,
            "highlights": highlights,
            "csrf_token": kwargs.csrf_token,
            "dismiss_url": dismiss_url,
            "dismiss_attrs": (
                {
                    "hx-get": dismiss_url,
                    "hx-target": "#catalog-desk",
                    "hx-swap": "outerHTML",
                    "hx-push-url": "true",
                }
                if dismiss_url
                else {}
            ),
        }
