from citry import Component

from config.citry_app import app


class Textarea(Component):
    citry = app
    name = "textarea"
    template_file = "textarea.citry-html"
    css_file = "textarea.css"

    class Kwargs:
        name: str = "comment"
        value: str = ""
        placeholder: str = ""
        rows: int = 4
        disabled: bool = False
        focused: bool = False
        autofocus: bool = False

    def template_data(self, kwargs, slots):
        class_name = "ds-textarea" + (" is-focused" if kwargs.focused else "")
        return {
            "class_name": class_name,
            "name": kwargs.name,
            "value": kwargs.value,
            "placeholder": kwargs.placeholder,
            "rows": kwargs.rows,
            "disabled": kwargs.disabled,
            "autofocus": kwargs.autofocus,
        }
