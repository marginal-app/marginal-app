from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class ViewTab(Component):
    citry = app
    name = "view_tab"
    template_file = "view_tab.citry-html"
    css_file = "view_tab.css"

    @dataclass
    class Kwargs:
        label: str = "목차"
        count: str = "3"
        active: bool = False

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(active=True),
                    slug="view-tab-active",
                    title="View tab / active",
                    description="Accent rule under the label and count.",
                ),
                meta(
                    variant(active=False),
                    slug="view-tab-default",
                    title="View tab / default",
                    description="Idle tab — no accent rule.",
                ),
            ]

    def template_data(self, kwargs, slots):
        class_name = "ds-view-tab"
        if kwargs.active:
            class_name = f"{class_name} is-active"
        return {
            "class_name": class_name,
            "label": kwargs.label,
            "count": kwargs.count,
            "active": kwargs.active,
        }
