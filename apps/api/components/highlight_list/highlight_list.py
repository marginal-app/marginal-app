from typing import Any

from django_components import Component, register


@register("highlight_list")
class HighlightList(Component):
    template_file = "highlight_list.html"
    css_file = "highlight_list.css"

    class Kwargs:
        highlights: list[dict[str, Any]]

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {"highlights": kwargs.highlights}
