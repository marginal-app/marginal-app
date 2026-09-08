from dataclasses import dataclass
from typing import Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

_STATE_CLASS = {
    "hover": "is-hover",
    "focus": "is-focus",
}


class IconButton(Component):
    citry = app
    name = "icon_button"
    template_file = "icon_button.citry-html"
    css_file = "icon_button.css"

    @dataclass
    class Kwargs:
        label: str = "설정 열기"
        icon: str = "⚙"
        href: str = ""
        title: str = ""
        state: str = ""
        attrs: dict[str, str] | None = None

    class PreviewVariant(Kwargs):
        group = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(label="설정 열기", icon="⚙"),
                    slug="icon-button-default",
                    title="IconButton / default",
                    description="32px hit target — settings gear on an elevated chip.",
                ),
                meta(
                    variant(label="설정 열기", icon="⚙", state="hover"),
                    slug="icon-button-hover",
                    title="IconButton / hover",
                    description="Hover: hairline border and primary icon color.",
                ),
                meta(
                    variant(label="설정 열기", icon="⚙", state="focus"),
                    slug="icon-button-focus",
                    title="IconButton / focus",
                    description="Focus-visible: accent ring with offset.",
                ),
            ]

    def template_data(self, kwargs, slots):
        class_name = "ds-icon-button"
        modifier = _STATE_CLASS.get(kwargs.state, "")
        if modifier:
            class_name = f"{class_name} {modifier}"
        return {
            "label": kwargs.label,
            "icon": kwargs.icon,
            "href": kwargs.href,
            "title": kwargs.title or kwargs.label,
            "is_link": bool(kwargs.href),
            "class_name": class_name,
            "attrs": kwargs.attrs or {},
        }
