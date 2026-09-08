from citry import Component

from config.citry_app import app


class Label(Component):
    citry = app
    name = "label"
    template_file = "label.citry-html"
    css_file = "label.css"

    class Kwargs:
        text: str = "Server URL"
        hint: str = ""
        kicker: str = ""
        html_for: str = ""

    def template_data(self, kwargs, slots):
        return {
            "text": kwargs.text,
            "hint": kwargs.hint,
            "kicker": kwargs.kicker,
            "for_attrs": {"for": kwargs.html_for} if kwargs.html_for else {},
        }
