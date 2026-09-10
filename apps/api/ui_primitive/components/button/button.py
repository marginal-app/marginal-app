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
        kind: str = "primary"
        size: str = ""
        disabled: bool = False
        focused: bool = False
        html_type: str = "button"

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
                meta(
                    variant(label="모두 보기", kind="quiet"),
                    slug="button-quiet",
                    title="Button / quiet",
                    description="Hairline secondary — everything that is not the one real action.",
                ),
            ]

    def template_data(self, kwargs, slots):
        classes = ["button"]
        if kwargs.kind == "quiet":
            classes.append("quiet")
        if kwargs.size == "small":
            classes.append("small")
        if kwargs.focused:
            classes.append("is-focused")
        html_type = kwargs.html_type if kwargs.html_type in {"button", "submit"} else "button"
        return {
            "label": kwargs.label,
            "disabled": kwargs.disabled,
            "html_type": html_type,
            "class_name": " ".join(classes),
        }
