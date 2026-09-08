from citry import Component

from config.citry_app import app


class Field(Component):
    citry = app
    name = "field"
    template_file = "field.citry-html"
    css_file = "field.css"

    class Kwargs:
        label: str = "Server URL"
        name: str = "server_url"
        value: str = ""
        placeholder: str = ""
        input_type: str = "text"
        disabled: bool = False

    def template_data(self, kwargs, slots):
        return {
            "label": kwargs.label,
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "input_type": kwargs.input_type,
            "disabled": kwargs.disabled,
        }
