from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

QUOTE = "Server-rendered HTML is a complete first paint."
TITLE = "Why Server-Rendered HTML Still Wins"
HOST = "blog.example.org"
WHEN = "12분 전"


class HighlightRow(Component):
    citry = app
    name = "highlight_row"
    template_file = "highlight_row.citry-html"
    css_file = "highlight_row.css"

    @dataclass
    class Kwargs:
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
                    slug="highlight-row-default",
                    title="Highlight row / default",
                    description="Underline-tab row — quote, title, host, when.",
                ),
                meta(
                    variant(selected=True),
                    slug="highlight-row-selected",
                    title="Highlight row / selected",
                    description="Elevated fill. Title moves into the meta line.",
                ),
            ]

    def template_data(self, kwargs, slots):
        class_name = "ds-highlight-row"
        if kwargs.selected:
            class_name = f"{class_name} is-selected"
        return {
            "class_name": class_name,
            "quote": kwargs.quote,
            "title": kwargs.title,
            "host": kwargs.host,
            "when": kwargs.when,
            "selected": kwargs.selected,
            "show_title": not kwargs.selected,
            "chip_style": f"background: {kwargs.color}",
        }
