from uuid import UUID

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_components import Component, ComponentView, register

from highlights.models import Highlight


@register("highlight_card")
class HighlightCard(Component):
    template_file = "highlight_card.html"
    css_file = "highlight_card.css"

    class Kwargs:
        highlight_id: str
        quote: str
        color: str
        comment: str = ""
        editing: bool = False
        comment_edit_url: str = ""
        comment_save_url: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "highlight_id": kwargs.highlight_id,
            "quote": kwargs.quote,
            "color": kwargs.color,
            "comment": kwargs.comment,
            "editing": kwargs.editing,
            "comment_edit_url": kwargs.comment_edit_url,
            "comment_save_url": kwargs.comment_save_url,
        }

    class View(ComponentView):
        def get(
            self,
            request: HttpRequest,
            highlight_id: UUID,
            **kwargs: object,
        ) -> HttpResponse:
            highlight = get_object_or_404(Highlight, id=highlight_id)
            return HighlightCard.render_to_response(
                request=request,
                deps_strategy="fragment",
                kwargs=_card_kwargs(highlight, editing=True),
            )

        def post(
            self,
            request: HttpRequest,
            highlight_id: UUID,
            **kwargs: object,
        ) -> HttpResponse:
            highlight = get_object_or_404(Highlight, id=highlight_id)
            highlight.comment = request.POST.get("comment", "")
            highlight.save(update_fields=["comment", "updated_at"])
            return HighlightCard.render_to_response(
                request=request,
                deps_strategy="fragment",
                kwargs=_card_kwargs(highlight, editing=False),
            )


def _card_kwargs(highlight: Highlight, *, editing: bool) -> dict[str, object]:
    comment_url = reverse("highlight_comment", args=[highlight.id])
    return {
        "highlight_id": str(highlight.id),
        "quote": highlight.quote,
        "color": highlight.color,
        "comment": highlight.comment,
        "editing": editing,
        "comment_edit_url": comment_url,
        "comment_save_url": comment_url,
    }
