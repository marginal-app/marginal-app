from typing import Any

from django_components import Component, register


@register("library_panel")
class LibraryPanel(Component):
    template_file = "library_panel.html"
    css_file = "library_panel.css"

    class Kwargs:
        view: str = "highlights"
        highlights: list[dict[str, Any]] | None = None
        toggle_url: str = ""
        settings_action_url: str = ""
        server_url: str = "http://127.0.0.1:8000"
        api_token: str = "dev-token"
        settings_status: str = "idle"
        settings_error: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        highlights = kwargs.highlights or []
        is_settings = kwargs.view == "settings"
        return {
            "is_settings": is_settings,
            "title": "설정" if is_settings else "Marginal",
            "toggle_url": kwargs.toggle_url,
            "highlights": highlights,
            "is_empty": not highlights,
            "settings_action_url": kwargs.settings_action_url,
            "server_url": kwargs.server_url,
            "api_token": kwargs.api_token,
            "settings_status": kwargs.settings_status,
            "settings_error": kwargs.settings_error,
        }
