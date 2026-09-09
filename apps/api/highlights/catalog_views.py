from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from citry_preview.rendering import render_component
from highlights.library_views import _highlight_kwargs, _is_htmx, _seed_demo_highlights
from highlights.models import Bookmark, Catalog, Highlight


def _seed_catalog_desk() -> None:
    _seed_demo_highlights()
    Catalog.objects.get_or_create(
        origin="https://example.com",
        path="/hypothesis",
        query="",
        defaults={"title": "Hypothesis"},
    )
    item, _ = Catalog.objects.get_or_create(
        origin="https://example.com",
        path="/item",
        query="?id=321",
        defaults={"title": "Item 321"},
    )
    Bookmark.objects.get_or_create(catalog=item)


def _row_kwargs(catalog: Catalog, *, selected_id: int | None) -> dict[str, object]:
    page_key = catalog.page_key
    return {
        "catalog_id": str(catalog.id),
        "title": catalog.title,
        "origin": catalog.origin,
        "path": catalog.path,
        "query": catalog.query,
        "highlight_count": Highlight.objects.filter(page_key=page_key).count(),
        "bookmarked": Bookmark.objects.filter(catalog=catalog).exists(),
        "selected": selected_id == catalog.id,
        "select_url": reverse("catalog_desk_detail", args=[catalog.id]),
        "source_href": page_key,
    }


def _desk_kwargs(request: HttpRequest, catalog: Catalog | None) -> dict[str, object]:
    _seed_catalog_desk()
    selected_id = catalog.id if catalog else None
    rows = [
        _row_kwargs(row, selected_id=selected_id)
        for row in Catalog.objects.order_by("-updated_at")
    ]
    highlights: list[dict[str, object]] = []
    if catalog:
        highlights = [
            _highlight_kwargs(highlight)
            for highlight in Highlight.objects.filter(page_key=catalog.page_key).order_by(
                "created_at"
            )
        ]
    return {
        "rows": rows,
        "selected": catalog is not None,
        "pane_title": (catalog.title or catalog.page_key) if catalog else "",
        "source_href": catalog.page_key if catalog else "",
        "highlights": highlights,
        "csrf_token": get_token(request),
        "dismiss_url": reverse("catalog_desk"),
    }


def _desk_response(request: HttpRequest, kwargs: dict[str, object]) -> HttpResponse:
    if _is_htmx(request):
        return HttpResponse(render_component("catalog_desk", kwargs))
    return render(request, "highlights/catalog.html", {"desk_kwargs": kwargs})


@require_http_methods(["GET"])
def catalog_desk_view(request: HttpRequest) -> HttpResponse:
    return _desk_response(request, _desk_kwargs(request, None))


@require_http_methods(["GET"])
def catalog_desk_detail_view(request: HttpRequest, catalog_id: int) -> HttpResponse:
    catalog = get_object_or_404(Catalog, id=catalog_id)
    return _desk_response(request, _desk_kwargs(request, catalog))
