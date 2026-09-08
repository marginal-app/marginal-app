from config.citry_app import app
from citry import Component

_STATE_CLASS = {
    "hover": "is-hover",
    "focus": "is-focus",
}


class IconButton(Component):
    citry = app
    name = "icon_button"
    template_file = "icon_button.citry-html"
    css_file = "icon_button.css"

    class Kwargs:
        label: str = "설정 열기"
        icon: str = "⚙"
        href: str = ""
        title: str = ""
        state: str = ""
        attrs: dict[str, str] | None = None

    def template_data(self, kwargs, slots):
        class_name = "ds-icon-button"
        modifier = _STATE_CLASS.get(kwargs.state, "")
        if modifier:
            class_name = f"{class_name} {modifier}"
        return {
            "label": kwargs.label,
            "icon": kwargs.icon,
            "href": kwargs.href,
            "title": kwargs.title or kwargs.label,
            "is_link": bool(kwargs.href),
            "class_name": class_name,
            "attrs": kwargs.attrs or {},
        }
