from uuid import UUID

from citry import Component
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from config.citry_app import app
from highlights.models import Highlight


class HighlightCard(Component):
    citry = app
    name = "highlight_card"
    template_file = "highlight_card.citry-html"
    css_file = "highlight_card.css"

    class Kwargs:
        highlight_id: str
        quote: str
        color: str
        comment: str = ""
        editing: bool = False
        comment_edit_url: str = ""
        comment_save_url: str = ""
        csrf_token: str = ""

    def template_data(self, kwargs, slots):
        return {
            "highlight_id": kwargs.highlight_id,
            "quote": kwargs.quote,
            "color": kwargs.color,
            "comment": kwargs.comment,
            "editing": kwargs.editing,
            "comment_edit_url": kwargs.comment_edit_url,
            "comment_save_url": kwargs.comment_save_url,
            "csrf_token": kwargs.csrf_token,
            "form_attrs": (
                {
                    "hx-post": kwargs.comment_save_url,
                    "hx-target": "closest .highlight-item",
                    "hx-swap": "outerHTML",
                }
                if kwargs.comment_save_url
                else {}
            ),
        }


def highlight_card_edit_view(
    request: HttpRequest,
    highlight_id: UUID,
) -> HttpResponse:
    highlight = get_object_or_404(Highlight, id=highlight_id)
    if request.method == "POST":
        highlight.comment = request.POST.get("comment", "")
        highlight.save(update_fields=["comment", "updated_at"])
        editing = False
    else:
        editing = True
    return render(
        request,
        "highlight_card_fragment.citry-html",
        _card_context(highlight, request, editing=editing),
    )


def _card_context(
    highlight: Highlight, request: HttpRequest, *, editing: bool
) -> dict[str, object]:
    comment_url = reverse("highlight_comment", args=[highlight.id])
    return {
        "highlight_id": str(highlight.id),
        "quote": highlight.quote,
        "color": highlight.color,
        "comment": highlight.comment,
        "editing": editing,
        "comment_edit_url": comment_url,
        "comment_save_url": comment_url,
        "csrf_token": get_token(request),
    }
