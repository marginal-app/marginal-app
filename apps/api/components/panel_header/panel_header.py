from django_components import Component, register


@register("panel_header")
class PanelHeader(Component):
    template_file = "panel_header.html"
    css_file = "panel_header.css"

    class Kwargs:
        title: str = "Marginal"
        is_settings: bool = False
        toggle_url: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "title": kwargs.title,
            "is_settings": kwargs.is_settings,
            "toggle_url": kwargs.toggle_url,
            "toggle_label": "목록으로 돌아가기" if kwargs.is_settings else "설정 열기",
            "toggle_title": "목록으로" if kwargs.is_settings else "설정",
            "toggle_icon": "←" if kwargs.is_settings else "⚙",
        }
