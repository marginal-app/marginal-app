from config.citry_app import app
from citry import Component


class PanelHeader(Component):
    citry = app
    name = "panel_header"
    template_file = "panel_header.citry-html"
    css_file = "panel_header.css"

    class Kwargs:
        title: str = "Marginal"
        is_settings: bool = False
        toggle_url: str = ""

    def template_data(self, kwargs, slots):
        return {
            "title": kwargs.title,
            "toggle_url": kwargs.toggle_url,
            "toggle_label": "목록으로 돌아가기" if kwargs.is_settings else "설정 열기",
            "toggle_title": "목록으로" if kwargs.is_settings else "설정",
            "toggle_icon": "←" if kwargs.is_settings else "⚙",
            "toggle_attrs": (
                {
                    "hx-get": kwargs.toggle_url,
                    "hx-target": "closest .panel",
                    "hx-swap": "outerHTML",
                    "hx-push-url": "true",
                }
                if kwargs.toggle_url
                else {}
            ),
        }
