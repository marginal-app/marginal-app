from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class Button(Component):
    citry = app
    name = "button"
    template_file = "button.citry-html"
    css_file = "button.css"

    @dataclass
    class Kwargs:
        label: str = "Save & Test Connection"
        size: str = ""
        disabled: bool = False
        focused: bool = False

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(label="Save & Test Connection"),
                    slug="button-default",
                    title="Button / default",
                    description="Primary action, default size.",
                ),
                meta(
                    variant(label="저장", size="small"),
                    slug="button-small",
                    title="Button / small",
                    description="Compact primary used on highlight cards.",
                ),
                meta(
                    variant(label="확인 중...", disabled=True),
                    slug="button-disabled",
                    title="Button / disabled",
                    description="Primary action while a test is in flight.",
                ),
                meta(
                    variant(label="Save & Test Connection", focused=True),
                    slug="button-focus",
                    title="Button / focus-visible",
                    description="Keyboard focus ring — 2px accent over a background offset.",
                ),
            ]

    def template_data(self, kwargs, slots):
        classes = ["button"]
        if kwargs.size == "small":
            classes.append("small")
        if kwargs.focused:
            classes.append("is-focused")
        return {
            "label": kwargs.label,
            "disabled": kwargs.disabled,
            "class_name": " ".join(classes),
        }
