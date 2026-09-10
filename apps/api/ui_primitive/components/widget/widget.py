from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component, SlotInput

from citry_preview.variants import meta
from config.citry_app import app

TITLE = "이번 주"
META = "지난주 대비 +9"
PLACEHOLDER = "Slot"


class Widget(Component):
    citry = app
    name = "widget"
    template_file = "widget.citry-html"
    css_file = "widget.css"

    @dataclass
    class Kwargs:
        title: str = TITLE
        meta: str = META
        show_meta: bool = True
        placeholder: str = PLACEHOLDER

    class Slots:
        default: SlotInput | None = None

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(),
                    slug="widget-meta",
                    title="Widget / meta",
                    description="Head with title and stamp. Slot is a placeholder.",
                ),
                meta(
                    variant(show_meta=False),
                    slug="widget-title",
                    title="Widget / title only",
                    description="Head is the title. Slot is a placeholder.",
                ),
            ]

    def template_data(self, kwargs, slots):
        return {
            "title": kwargs.title,
            "meta": kwargs.meta,
            "show_meta": kwargs.show_meta,
            "placeholder": kwargs.placeholder,
        }
