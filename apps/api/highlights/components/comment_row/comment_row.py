from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

NOTE = "리뷰 실루엣은 여기서 나온다."
QUOTE = "“Server-rendered HTML is a complete first paint.”"
TITLE = "Why Server-Rendered HTML Still Wins"
HOST = "blog.example.org"
WHEN = "12분 전"


class CommentRow(Component):
    citry = app
    name = "comment_row"
    template_file = "comment_row.citry-html"
    css_file = "comment_row.css"

    @dataclass
    class Kwargs:
        note: str = NOTE
        quote: str = QUOTE
        title: str = TITLE
        host: str = HOST
        when: str = WHEN
        selected: bool = False
        color: str = "var(--highlight-yellow)"

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(),
                    slug="comment-row-default",
                    title="Comment row / default",
                    description="Comment-tab row — note, quoted quote, title, host, when.",
                ),
                meta(
                    variant(selected=True),
                    slug="comment-row-selected",
                    title="Comment row / selected",
                    description="Elevated fill. Same copy as default.",
                ),
            ]

    def template_data(self, kwargs, slots):
        class_name = "ds-comment-row"
        if kwargs.selected:
            class_name = f"{class_name} is-selected"
        return {
            "class_name": class_name,
            "note": kwargs.note,
            "quote": kwargs.quote,
            "title": kwargs.title,
            "host": kwargs.host,
            "when": kwargs.when,
            "chip_style": f"background: {kwargs.color}",
        }
