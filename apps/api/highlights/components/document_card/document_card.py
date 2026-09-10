from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

TITLE = "Why Server-Rendered HTML Still Wins"
HOST = "blog.example.org"


class DocumentCard(Component):
    citry = app
    name = "document_card"
    template_file = "document_card.citry-html"
    css_file = "document_card.css"

    @dataclass
    class Kwargs:
        title: str = TITLE
        host: str = HOST
        highlight_count: int = 2
        bookmarked: bool = False
        layout: str = "row"
        mark: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(layout="row"),
                    slug="document-card-row",
                    title="DocumentCard / row",
                    description="336px panel card — pills on one row, trailing.",
                ),
                meta(
                    variant(layout="row", bookmarked=True),
                    slug="document-card-row-bookmarked",
                    title="DocumentCard / row · bookmarked",
                    description="Same row card with the bookmark pill active.",
                ),
                meta(
                    variant(layout="stack"),
                    slug="document-card-stack",
                    title="DocumentCard / stack",
                    description="248px narrow card — pills stacked full width.",
                ),
                meta(
                    variant(layout="stack", bookmarked=True),
                    slug="document-card-stack-bookmarked",
                    title="DocumentCard / stack · bookmarked",
                    description="Narrow card with the bookmark pill active.",
                ),
            ]

    def template_data(self, kwargs, slots):
        layout = kwargs.layout if kwargs.layout in {"row", "stack"} else "row"
        class_name = "ds-document-card"
        if layout == "stack":
            class_name = f"{class_name} ds-document-card--stack"
        mark = (kwargs.mark or kwargs.title[:1] or "M").upper()
        meta_line = kwargs.host
        if kwargs.highlight_count:
            meta_line = f"{kwargs.host} · 밑줄 {kwargs.highlight_count}"
        return {
            "class_name": class_name,
            "mark": mark,
            "title": kwargs.title,
            "meta": meta_line,
            "bookmarked": kwargs.bookmarked,
            "bookmark_label": "북마크됨" if kwargs.bookmarked else "북마크",
            "bookmark_icon": "star-filled" if kwargs.bookmarked else "star",
        }
