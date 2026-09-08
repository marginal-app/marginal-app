from dataclasses import dataclass

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_components import registry

from highlights.models import Highlight
from ui.examples import EXAMPLES, Example, example_by_slug


@dataclass(frozen=True)
class RenderedExample:
    slug: str
    title: str
    description: str
    group: str
    html: str


def _render_example(example: Example, request: HttpRequest) -> str:
    return registry.get(example.component).render(
        request=request,
        kwargs=example.kwargs,
        deps_strategy="fragment",
    )


DEMO_HIGHLIGHTS = (
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "page_key": "https://example.com/hypothesis",
        "quote": "A component URL is enough for a Cloud Agent screenshot.",
        "color": "#f5d76e",
        "comment": "",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "page_key": "https://example.com/hypothesis",
        "quote": "HTMX returns the same HighlightCard, not a React tree.",
        "color": "#8b8bff",
        "comment": "Review this silhouette, then merge.",
    },
)


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


def _seed_demo_highlights() -> list[Highlight]:
    rows: list[Highlight] = []
    for payload in DEMO_HIGHLIGHTS:
        highlight, _created = Highlight.objects.get_or_create(
            id=payload["id"],
            defaults={
                "page_key": payload["page_key"],
                "quote": payload["quote"],
                "color": payload["color"],
                "comment": payload["comment"],
            },
        )
        rows.append(highlight)
    return rows


def _highlight_kwargs(highlight: Highlight) -> dict[str, object]:
    comment_url = reverse("highlight_comment", args=[highlight.id])
    return {
        "highlight_id": str(highlight.id),
        "quote": highlight.quote,
        "color": highlight.color,
        "comment": highlight.comment,
        "editing": False,
        "comment_edit_url": comment_url,
        "comment_save_url": comment_url,
    }


def _library_kwargs(
    *,
    view: str,
    status: str = "idle",
    error: str = "",
    server_url: str = "http://127.0.0.1:8000",
    api_token: str = "dev-token",
) -> dict[str, object]:
    highlights = [_highlight_kwargs(row) for row in _seed_demo_highlights()]
    return {
        "view": view,
        "highlights": highlights,
        "toggle_url": (
            reverse("library_highlights") if view == "settings" else reverse("library_settings")
        ),
        "settings_action_url": reverse("library_settings"),
        "server_url": server_url,
        "api_token": api_token,
        "settings_status": status,
        "settings_error": error,
    }


def _library_response(request: HttpRequest, kwargs: dict[str, object]) -> HttpResponse:
    component = registry.get("library_panel")
    if _is_htmx(request):
        return component.render_to_response(
            request=request,
            kwargs=kwargs,
            deps_strategy="fragment",
        )
    return render(request, "ui/library.html", {"panel_kwargs": kwargs})


@require_http_methods(["GET"])
def gallery_view(request: HttpRequest) -> HttpResponse:
    examples = [
        RenderedExample(
            slug=example.slug,
            title=example.title,
            description=example.description,
            group=example.group,
            html=_render_example(example, request),
        )
        for example in EXAMPLES
    ]
    return render(request, "ui/gallery.html", {"examples": examples})


@require_http_methods(["GET"])
def silhouette_view(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        example = example_by_slug(slug)
    except KeyError as exc:
        raise Http404(f"Unknown example: {slug}") from exc
    rendered = RenderedExample(
        slug=example.slug,
        title=example.title,
        description=example.description,
        group=example.group,
        html=_render_example(example, request),
    )
    return render(request, "ui/silhouette.html", {"example": rendered})


@require_http_methods(["GET"])
def library_highlights_view(request: HttpRequest) -> HttpResponse:
    return _library_response(request, _library_kwargs(view="highlights"))


@require_http_methods(["GET", "POST"])
def library_settings_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        server_url = request.POST.get("server_url", "").strip()
        api_token = request.POST.get("api_token", "").strip()
        if server_url and api_token:
            kwargs = _library_kwargs(
                view="settings",
                status="ok",
                server_url=server_url,
                api_token=api_token,
            )
        else:
            kwargs = _library_kwargs(
                view="settings",
                status="error",
                error="Server URL과 API Token이 필요합니다",
                server_url=server_url,
                api_token=api_token,
            )
        return _library_response(request, kwargs)
    return _library_response(request, _library_kwargs(view="settings"))
