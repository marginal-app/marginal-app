from django_components import Component, register


@register("status")
class Status(Component):
    template_file = "status.html"
    css_file = "status.css"

    class Kwargs:
        tone: str = "ok"
        message: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "tone": kwargs.tone,
            "message": kwargs.message,
            "is_ok": kwargs.tone == "ok",
        }
