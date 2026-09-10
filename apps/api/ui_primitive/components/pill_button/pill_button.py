from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app
from ui_primitive.components.icon.icon import GLYPHS


class PillButton(Component):
    citry = app
    name = "pill_button"
    template_file = "pill_button.citry-html"
    css_file = "pill_button.css"

    @dataclass
    class Kwargs:
        label: str = "북마크"
        icon: str = "star"
        active: bool = False

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(label="북마크", icon="star", active=False),
                    slug="pill-button-default",
                    title="PillButton / default",
                    description="Icon + label pill — hairline on --bg.",
                ),
                meta(
                    variant(label="북마크됨", icon="star-filled", active=True),
                    slug="pill-button-active",
                    title="PillButton / active",
                    description="Accent hairline on --bg-elevated, e.g. bookmarked.",
                ),
            ]

    def template_data(self, kwargs, slots):
        icon = kwargs.icon if kwargs.icon in GLYPHS else "star"
        class_name = "ds-pill-button"
        if kwargs.active:
            class_name = f"{class_name} is-active"
        return {
            "class_name": class_name,
            "label": kwargs.label,
            "icon": icon,
        }
