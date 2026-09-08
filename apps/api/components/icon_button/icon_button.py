from django_components import Component, register


@register("icon_button")
class IconButton(Component):
    template_file = "icon_button.html"
    css_file = "icon_button.css"

    class Kwargs:
        label: str = "설정 열기"
        icon: str = "⚙"
        href: str = ""
        title: str = ""
        attrs: dict[str, str] | None = None

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "label": kwargs.label,
            "icon": kwargs.icon,
            "href": kwargs.href,
            "title": kwargs.title or kwargs.label,
            "is_link": bool(kwargs.href),
            "attrs": kwargs.attrs or {},
        }
