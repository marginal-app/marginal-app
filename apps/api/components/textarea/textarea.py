from django_components import Component, register


@register("textarea")
class Textarea(Component):
    template_file = "textarea.html"
    css_file = "textarea.css"

    class Kwargs:
        name: str = "comment"
        value: str = ""
        placeholder: str = ""
        rows: int = 3
        disabled: bool = False

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "rows": kwargs.rows,
            "disabled": kwargs.disabled,
        }
