from dataclasses import dataclass

from django.http import Http404, HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from citry_preview.rendering import render_component
from highlights.models import Highlight
from citry_preview.previews import PREVIEWS, Preview, preview_by_slug


@dataclass(frozen=True)
class RenderedPreview:
    slug: str
    title: str
    description: str
    group: str
    html: str
    is_atom: bool = False


def _render_preview(preview: Preview, request: HttpRequest) -> str:  # noqa: ARG001
    return render_component(preview.component, preview.kwargs)


def _rendered(preview: Preview, request: HttpRequest) -> RenderedPreview:
    return RenderedPreview(
        slug=preview.slug,
        title=preview.title,
        description=preview.description,
        group=preview.group,
        html=_render_preview(preview, request),
        is_atom=preview.group == "Primitives",
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
    request: HttpRequest,
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
        "csrf_token": get_token(request),
    }


def _library_response(request: HttpRequest, kwargs: dict[str, object]) -> HttpResponse:
    if _is_htmx(request):
        html = render_component("library_panel", kwargs)
        return HttpResponse(html)
    return render(request, "citry_preview/library.html", {"panel_kwargs": kwargs})


@require_http_methods(["GET"])
def gallery_view(request: HttpRequest) -> HttpResponse:
    previews = [_rendered(preview, request) for preview in PREVIEWS]
    return render(request, "citry_preview/gallery.html", {"previews": previews})


@require_http_methods(["GET"])
def silhouette_view(request: HttpRequest, slug: str) -> HttpResponse:
    try:
        preview = preview_by_slug(slug)
    except KeyError as exc:
        raise Http404(f"Unknown preview: {slug}") from exc
    return render(request, "citry_preview/silhouette.html", {"preview": _rendered(preview, request)})


@require_http_methods(["GET"])
def library_highlights_view(request: HttpRequest) -> HttpResponse:
    return _library_response(request, _library_kwargs(request, view="highlights"))


@require_http_methods(["GET", "POST"])
def library_settings_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        server_url = request.POST.get("server_url", "").strip()
        api_token = request.POST.get("api_token", "").strip()
        if server_url and api_token:
            kwargs = _library_kwargs(
                request,
                view="settings",
                status="ok",
                server_url=server_url,
                api_token=api_token,
            )
        else:
            kwargs = _library_kwargs(
                request,
                view="settings",
                status="error",
                error="Server URL과 API Token이 필요합니다",
                server_url=server_url,
                api_token=api_token,
            )
        return _library_response(request, kwargs)
    return _library_response(request, _library_kwargs(request, view="settings"))
