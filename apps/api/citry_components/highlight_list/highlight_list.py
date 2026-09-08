from typing import Any

from config.citry_app import app
from citry import Component


class HighlightList(Component):
    citry = app
    name = "highlight_list"
    template_file = "highlight_list.citry-html"
    css_file = "highlight_list.css"

    class Kwargs:
        highlights: list[dict[str, Any]]
        csrf_token: str = ""

    def template_data(self, kwargs, slots):
        return {"highlights": kwargs.highlights, "csrf_token": kwargs.csrf_token}
