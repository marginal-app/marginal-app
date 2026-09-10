from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class Wordmark(Component):
    citry = app
    name = "wordmark"
    template_file = "wordmark.citry-html"
    css_file = "wordmark.css"

    @dataclass
    class Kwargs:
        size: str = "lg"

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(size="lg"),
                    slug="wordmark-lg",
                    title="Wordmark / lg",
                    description="Desk masthead — accent rule over Instrument Serif.",
                ),
                meta(
                    variant(size="sm"),
                    slug="wordmark-sm",
                    title="Wordmark / sm",
                    description="Compact mark for the sidebar header.",
                ),
            ]

    def template_data(self, kwargs, slots):
        size = kwargs.size if kwargs.size in {"lg", "sm"} else "lg"
        class_name = "ds-wordmark"
        if size == "sm":
            class_name = f"{class_name} ds-wordmark--sm"
        return {"class_name": class_name}
