from django_components import Component, register


@register("button")
class Button(Component):
    template_file = "button.html"
    css_file = "button.css"

    class Kwargs:
        label: str = "Save & Test Connection"
        size: str = ""
        disabled: bool = False
        type: str = "button"

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "label": kwargs.label,
            "disabled": kwargs.disabled,
            "type": kwargs.type,
            "is_small": kwargs.size == "small",
        }
