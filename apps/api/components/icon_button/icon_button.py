from django_components import Component, register


@register("icon_button")
class IconButton(Component):
    template_file = "icon_button.html"
    css_file = "icon_button.css"

    class Kwargs:
        icon: str = "⚙"
        aria_label: str = "설정 열기"
        disabled: bool = False
        type: str = "button"

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "icon": kwargs.icon,
            "aria_label": kwargs.aria_label,
            "disabled": kwargs.disabled,
            "type": kwargs.type,
        }
