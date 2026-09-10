from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

UNDERLINED = {
    "catalog_id": "1",
    "folio": "03",
    "title": "Why Server-Rendered HTML Still Wins",
    "origin": "https://blog.example.org",
    "path": "/posts/ssr",
    "highlight_count": 5,
    "source_href": "https://blog.example.org/posts/ssr",
}

BOOKMARKED = {
    "catalog_id": "2",
    "folio": "03",
    "title": "Item 321",
    "origin": "https://example.com",
    "path": "/item",
    "query": "?id=321",
    "bookmarked": True,
    "source_href": "https://example.com/item?id=321",
}


def display_host(origin: str, path: str, query: str) -> str:
    host = origin.removeprefix("https://").removeprefix("http://")
    return f"{host}{path}{query}"


class CatalogRow(Component):
    citry = app
    name = "catalog_row"
    template_file = "catalog_row.citry-html"
    css_file = "catalog_row.css"

    @dataclass
    class Kwargs:
        catalog_id: str = ""
        folio: str = ""
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
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(**UNDERLINED),
                    slug="catalog-row-highlighted",
                    title="CatalogRow / underlined",
                    description="TOC line — folio, serif title, host, underline count.",
                ),
                meta(
                    variant(**UNDERLINED, selected=True),
                    slug="catalog-row-highlighted-active",
                    title="CatalogRow / underlined · active",
                    description="Active TOC line — elevated fill, accent folio.",
                ),
                meta(
                    variant(**BOOKMARKED),
                    slug="catalog-row-bookmarked",
                    title="CatalogRow / bookmarked",
                    description="Bookmark mark instead of an underline count.",
                ),
                meta(
                    variant(**BOOKMARKED, selected=True),
                    slug="catalog-row-bookmarked-active",
                    title="CatalogRow / bookmarked · active",
                    description="Active bookmark line — elevated fill, accent folio.",
                ),
            ]

    def template_data(self, kwargs, slots):
        heading = kwargs.title or f"{kwargs.origin}{kwargs.path}{kwargs.query}"
        location = display_host(kwargs.origin, kwargs.path, kwargs.query)
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
        if kwargs.bookmarked:
            classes.append("is-bookmarked")
        return {
            "folio": kwargs.folio,
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
