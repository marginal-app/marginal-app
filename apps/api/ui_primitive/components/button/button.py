from citry import Component

from config.citry_app import app


class Button(Component):
    citry = app
    name = "button"
    template_file = "button.citry-html"
    css_file = "button.css"

    class Kwargs:
        label: str = "Save & Test Connection"
        size: str = ""
        disabled: bool = False
        focused: bool = False

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
