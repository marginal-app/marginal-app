from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

GLYPHS = (
    "home",
    "list",
    "highlighter",
    "bookmark",
    "comment",
    "settings",
    "search",
    "collapse",
    "expand",
    "star",
    "star-filled",
    "external",
    "close",
    "copy",
)


class Icon(Component):
    citry = app
    name = "icon"
    template_file = "icon.citry-html"
    css_file = "icon.css"

    @dataclass
    class Kwargs:
        name: str = "home"
        label: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(name="home", label="홈"),
                    slug="icon-default",
                    title="Icon / default",
                    description="16px home glyph. Strokes follow --text-secondary.",
                ),
            ]

    def template_data(self, kwargs, slots):
        name = kwargs.name if kwargs.name in GLYPHS else "home"
        class_name = f"ds-icon ds-icon--{name}"
        labelled = bool(kwargs.label)
        return {
            "class_name": class_name,
            "label": kwargs.label,
            "labelled": labelled,
        }
