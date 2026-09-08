from django_components import Component, register


@register("field")
class Field(Component):
    template_file = "field.html"
    css_file = "field.css"

    class Kwargs:
        label: str = "Server URL"
        name: str = "server_url"
        value: str = ""
        placeholder: str = ""
        input_type: str = "text"
        disabled: bool = False

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "label": kwargs.label,
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "input_type": kwargs.input_type,
            "disabled": kwargs.disabled,
        }
