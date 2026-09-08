from config.citry_app import app
from citry import Component


class Input(Component):
    citry = app
    name = "input"
    template_file = "input.citry-html"
    css_file = "input.css"

    class Kwargs:
        name: str = ""
        value: str = ""
        placeholder: str = ""
        input_type: str = "text"
        disabled: bool = False

    def template_data(self, kwargs, slots):
        return {
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "input_type": kwargs.input_type,
            "disabled": kwargs.disabled,
        }
