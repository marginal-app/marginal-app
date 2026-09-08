from citry import Component

from config.citry_app import app


class Status(Component):
    citry = app
    name = "status"
    template_file = "status.citry-html"
    css_file = "status.css"

    class Kwargs:
        tone: str = "ok"
        message: str = ""

    def template_data(self, kwargs, slots):
        return {
            "class_name": f"status status-{kwargs.tone}",
            "message": kwargs.message,
        }
