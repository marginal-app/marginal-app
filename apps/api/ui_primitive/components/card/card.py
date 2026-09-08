from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component, SlotInput

from citry_preview.variants import meta
from config.citry_app import app


class Card(Component):
    citry = app
    name = "card"
    template_file = "card.citry-html"
    css_file = "card.css"

    @dataclass
    class Kwargs:
        body: str = ""

    class Slots:
        default: SlotInput | None = None

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(body="Server-rendered HTML is a complete first paint."),
                    slug="card-default",
                    title="Card / default",
                    description=(
                        "Cursor-style panel chrome — subtle border, soft elevation, padding."
                    ),
                ),
            ]

    def template_data(self, kwargs, slots):
        return {
            "body": kwargs.body,
        }
