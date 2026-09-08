from dataclasses import dataclass
from typing import Any, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app
from highlights.components.highlight_card.highlight_card import QUOTE_ONLY, WITH_COMMENT

HIGHLIGHTS = [QUOTE_ONLY, WITH_COMMENT]


class HighlightList(Component):
    citry = app
    name = "highlight_list"
    template_file = "highlight_list.citry-html"
    css_file = "highlight_list.css"

    @dataclass
    class Kwargs:
        highlights: list[dict[str, Any]]
        csrf_token: str = ""

    class PreviewVariant(Kwargs):
        group = "Molecules"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(highlights=HIGHLIGHTS),
                    slug="highlight-list",
                    title="HighlightList",
                    description="Stacked cards as a fragment an HTMX swap can replace.",
                ),
            ]

    def template_data(self, kwargs, slots):
        return {"highlights": kwargs.highlights, "csrf_token": kwargs.csrf_token}
