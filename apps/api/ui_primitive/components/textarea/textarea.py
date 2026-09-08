from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class Textarea(Component):
    citry = app
    name = "textarea"
    template_file = "textarea.citry-html"
    css_file = "textarea.css"

    @dataclass
    class Kwargs:
        name: str = "comment"
        value: str = ""
        placeholder: str = ""
        rows: int = 4
        disabled: bool = False
        focused: bool = False
        autofocus: bool = False

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(placeholder="코멘트 추가...", focused=True),
                    slug="textarea-empty",
                    title="Textarea / empty",
                    description="Empty comment field with a focus ring — ready to type.",
                ),
                meta(
                    variant(value="Draft note from a Cloud Agent"),
                    slug="textarea-filled",
                    title="Textarea / filled",
                    description="Draft comment ready to save.",
                ),
            ]

    def template_data(self, kwargs, slots):
        class_name = "ds-textarea" + (" is-focused" if kwargs.focused else "")
        return {
            "class_name": class_name,
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "rows": kwargs.rows,
            "disabled": kwargs.disabled,
            "autofocus": kwargs.autofocus,
        }
