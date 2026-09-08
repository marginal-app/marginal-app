from dataclasses import dataclass
from typing import Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class Label(Component):
    citry = app
    name = "label"
    template_file = "label.citry-html"
    css_file = "label.css"

    @dataclass
    class Kwargs:
        text: str = "Server URL"
        hint: str = ""
        kicker: str = ""
        html_for: str = ""

    class PreviewVariant(Kwargs):
        group = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(
                        kicker="Connection",
                        text="Server URL",
                        hint="Host the extension uses to sync highlights.",
                    ),
                    slug="label-default",
                    title="Label / default",
                    description="Cursor settings caption — kicker, title, and supporting hint.",
                ),
            ]

    def template_data(self, kwargs, slots):
        return {
            "text": kwargs.text,
            "hint": kwargs.hint,
            "kicker": kwargs.kicker,
            "for_attrs": {"for": kwargs.html_for} if kwargs.html_for else {},
        }
