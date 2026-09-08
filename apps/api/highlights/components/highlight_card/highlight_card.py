from dataclasses import dataclass
from typing import Self
from uuid import UUID

from citry import Component
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from citry_preview.variants import meta
from config.citry_app import app
from highlights.models import Highlight

QUOTE_ONLY = {
    "highlight_id": "preview-quote",
    "quote": "Server-rendered HTML is a complete first paint.",
    "color": "#f5d76e",
    "comment": "",
    "editing": False,
    "comment_edit_url": "",
    "comment_save_url": "",
}

WITH_COMMENT = {
    **QUOTE_ONLY,
    "highlight_id": "preview-comment",
    "quote": "Cloud Agents can screenshot a component URL.",
    "color": "#8b8bff",
    "comment": "This is the silhouette we review before merge.",
}

EDITING = {
    **QUOTE_ONLY,
    "highlight_id": "preview-editing",
    "quote": "HTMX swaps this same component, not a second client tree.",
    "color": "#57cf85",
    "comment": "Draft note from a Cloud Agent",
    "editing": True,
}


class HighlightCard(Component):
    citry = app
    name = "highlight_card"
    template_file = "highlight_card.citry-html"
    css_file = "highlight_card.css"

    @dataclass
    class Kwargs:
        highlight_id: str
        quote: str
        color: str
        comment: str = ""
        editing: bool = False
        comment_edit_url: str = ""
        comment_save_url: str = ""
        csrf_token: str = ""

    class PreviewVariant(Kwargs):
        group = "Atoms"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(**QUOTE_ONLY),
                    slug="highlight-card-quote",
                    title="HighlightCard / quote only",
                    description="Card with a color accent and the add-comment placeholder.",
                ),
                meta(
                    variant(**WITH_COMMENT),
                    slug="highlight-card-comment",
                    title="HighlightCard / with comment",
                    description="Saved annotation under the quote.",
                ),
                meta(
                    variant(**EDITING),
                    slug="highlight-card-editing",
                    title="HighlightCard / editing",
                    description=(
                        "HTMX target state: textarea + save. Same component, different kwargs."
                    ),
                ),
            ]

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
