from django_components import Component, register


@register("button")
class Button(Component):
    template_file = "button.html"
    css_file = "button.css"

    class Kwargs:
        label: str = "저장"
        variant: str = "primary"
        size: str = "default"
        disabled: bool = False
        type: str = "button"

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "label": kwargs.label,
            "variant": kwargs.variant,
            "size": kwargs.size,
            "disabled": kwargs.disabled,
            "type": kwargs.type,
            "is_small": kwargs.size == "small",
        }
