from dataclasses import dataclass
from typing import Any, ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app
from highlights.components.highlight_list.highlight_list import HIGHLIGHTS


class LibraryPanel(Component):
    citry = app
    name = "library_panel"
    template_file = "library_panel.citry-html"
    css_file = "library_panel.css"

    @dataclass
    class Kwargs:
        view: str = "highlights"
        highlights: list[dict[str, Any]] | None = None
        toggle_url: str = ""
        settings_action_url: str = ""
        server_url: str = "http://127.0.0.1:8000"
        api_token: str = "dev-token"
        settings_status: str = "idle"
        settings_error: str = ""
        csrf_token: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Pages"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(view="highlights", highlights=[]),
                    slug="panel-empty",
                    title="LibraryPanel / empty",
                    description="Composed page: header + empty state. Page-level silhouette.",
                ),
                meta(
                    variant(view="highlights", highlights=HIGHLIGHTS),
                    slug="panel-highlights",
                    title="LibraryPanel / highlights",
                    description="Composed page matching the extension side panel list.",
                ),
                meta(
                    variant(view="settings", settings_status="idle"),
                    slug="panel-settings",
                    title="LibraryPanel / settings",
                    description="Composed settings view.",
                ),
            ]

    def template_data(self, kwargs, slots):
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
            "csrf_token": kwargs.csrf_token,
        }
