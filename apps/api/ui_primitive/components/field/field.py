from dataclasses import dataclass
from typing import Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class Field(Component):
    citry = app
    name = "field"
    template_file = "field.citry-html"
    css_file = "field.css"

    @dataclass
    class Kwargs:
        label: str = "Server URL"
        name: str = "server_url"
        value: str = ""
        placeholder: str = ""
        input_type: str = "text"
        disabled: bool = False

    class PreviewVariant(Kwargs):
        group = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(
                        label="Server URL",
                        value="http://127.0.0.1:8000",
                        placeholder="https://my-server.example.com",
                    ),
                    slug="field-default",
                    title="Field / default",
                    description="Settings Server URL field with a saved value.",
                ),
            ]

    def template_data(self, kwargs, slots):
        return {
            "label": kwargs.label,
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "input_type": kwargs.input_type,
            "disabled": kwargs.disabled,
        }
