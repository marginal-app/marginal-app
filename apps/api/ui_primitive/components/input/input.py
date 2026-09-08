from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class Input(Component):
    citry = app
    name = "input"
    template_file = "input.citry-html"
    css_file = "input.css"

    @dataclass
    class Kwargs:
        name: str = ""
        value: str = ""
        placeholder: str = ""
        input_type: str = "text"
        disabled: bool = False

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(placeholder="https://my-server.example.com"),
                    slug="input-empty",
                    title="Input / empty",
                    description="Empty field — muted placeholder, no value.",
                ),
                meta(
                    variant(name="server_url", value="http://127.0.0.1:8000"),
                    slug="input-filled",
                    title="Input / filled",
                    description=(
                        "Filled field — primary-weight value, readable against the placeholder."
                    ),
                ),
            ]

    def template_data(self, kwargs, slots):
        return {
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "input_type": kwargs.input_type,
            "disabled": kwargs.disabled,
        }
