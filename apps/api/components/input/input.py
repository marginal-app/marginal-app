from django_components import Component, register


@register("input")
class Input(Component):
    template_file = "input.html"
    css_file = "input.css"

    class Kwargs:
        name: str = ""
        value: str = ""
        placeholder: str = ""
        input_type: str = "text"
        disabled: bool = False

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "input_type": kwargs.input_type,
            "disabled": kwargs.disabled,
        }
