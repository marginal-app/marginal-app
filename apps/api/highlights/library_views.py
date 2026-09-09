from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from citry_preview.rendering import render_component
from highlights.models import Catalog, CatalogMembership, Highlight
from identity.models import User
from identity.request import AuthenticatedRequest
from identity.tokens import user_from_bearer

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


def _authenticated_user(user: object) -> User | None:
    if isinstance(user, User) and user.is_authenticated:
        return user
    return None


def _seed_demo_highlights(user: User | None) -> list[Highlight]:
    owner = _authenticated_user(user)
    if owner is None:
        return []
    catalog = Catalog.get_or_create_from_page_key("https://example.com/hypothesis")
    CatalogMembership.objects.get_or_create(
        user=owner,
        catalog=catalog,
        defaults={"title": "Hypothesis"},
    )
    rows: list[Highlight] = []
    for payload in DEMO_HIGHLIGHTS:
        existing = Highlight.objects.filter(id=payload["id"]).first()
        if existing is not None:
            if existing.user.pk == owner.pk:
                rows.append(existing)
            continue
        rows.append(
            Highlight.objects.create(
                id=payload["id"],
                user=owner,
                catalog=catalog,
                page_key=payload["page_key"],
                quote=payload["quote"],
                color=payload["color"],
                comment=payload["comment"],
            )
        )
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
    highlights = [
        _highlight_kwargs(row) for row in _seed_demo_highlights(_authenticated_user(request.user))
    ]
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
    return render(request, "highlights/library.html", {"panel_kwargs": kwargs})


@login_required
@require_http_methods(["GET"])
def library_highlights_view(request: AuthenticatedRequest) -> HttpResponse:
    return _library_response(request, _library_kwargs(request, view="highlights"))


@require_http_methods(["GET", "POST"])
def library_settings_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        server_url = request.POST.get("server_url", "").strip()
        api_token = request.POST.get("api_token", "").strip()
        if not server_url or not api_token:
            kwargs = _library_kwargs(
                request,
                view="settings",
                status="error",
                error="Server URL과 API Token이 필요합니다",
                server_url=server_url,
                api_token=api_token,
            )
        elif user_from_bearer(api_token) is None:
            kwargs = _library_kwargs(
                request,
                view="settings",
                status="error",
                error="서버가 401로 응답했습니다",
                server_url=server_url,
                api_token=api_token,
            )
        else:
            kwargs = _library_kwargs(
                request,
                view="settings",
                status="ok",
                server_url=server_url,
                api_token=api_token,
            )
        return _library_response(request, kwargs)
    return _library_response(request, _library_kwargs(request, view="settings"))
