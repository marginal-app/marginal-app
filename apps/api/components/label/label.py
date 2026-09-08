from django_components import Component, register


@register("label")
class Label(Component):
    template_file = "label.html"
    css_file = "label.css"

    class Kwargs:
        text: str = "Server URL"
        hint: str = ""
        html_for: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "text": kwargs.text,
            "hint": kwargs.hint,
            "html_for": kwargs.html_for,
        }
