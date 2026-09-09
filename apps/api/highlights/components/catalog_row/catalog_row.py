from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class CatalogRow(Component):
    citry = app
    name = "catalog_row"
    template_file = "catalog_row.citry-html"
    css_file = "catalog_row.css"

    @dataclass
    class Kwargs:
        catalog_id: str = ""
        title: str = ""
        origin: str = ""
        path: str = ""
        query: str = ""
        highlight_count: int = 0
        bookmarked: bool = False
        selected: bool = False
        select_url: str = ""
        source_href: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Atoms"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(
                        catalog_id="1",
                        title="Hypothesis",
                        origin="https://example.com",
                        path="/hypothesis",
                        highlight_count=2,
                        source_href="https://example.com/hypothesis",
                    ),
                    slug="catalog-row-highlighted",
                    title="CatalogRow / highlighted",
                    description="A page with underlines. Title is catalog meta.",
                ),
                meta(
                    variant(
                        catalog_id="2",
                        title="Item 321",
                        origin="https://example.com",
                        path="/item",
                        query="?id=321",
                        bookmarked=True,
                        source_href="https://example.com/item?id=321",
                    ),
                    slug="catalog-row-bookmarked",
                    title="CatalogRow / bookmarked",
                    description="Bookmark only — no underlines.",
                ),
            ]

    def template_data(self, kwargs, slots):
        heading = kwargs.title or f"{kwargs.origin}{kwargs.path}{kwargs.query}"
        location = f"{kwargs.origin}{kwargs.path}{kwargs.query}"
        htmx_attrs = (
            {
                "hx-get": kwargs.select_url,
                "hx-target": "#catalog-desk",
                "hx-swap": "outerHTML",
                "hx-push-url": "true",
            }
            if kwargs.select_url
            else {}
        )
        classes = ["catalog-row"]
        if kwargs.selected:
            classes.append("is-selected")
        return {
            "heading": heading,
            "location": location,
            "highlight_count": kwargs.highlight_count,
            "bookmarked": kwargs.bookmarked,
            "selected": kwargs.selected,
            "select_url": kwargs.select_url,
            "href": kwargs.select_url or "#",
            "class_name": " ".join(classes),
            "htmx_attrs": htmx_attrs,
        }
