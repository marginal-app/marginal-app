from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from citry_preview.rendering import render_component
from highlights.library_views import _highlight_kwargs, _is_htmx, _seed_demo_highlights
from highlights.models import Catalog, CatalogMembership, Highlight
from identity.models import User
from identity.request import AuthenticatedRequest


def _seed_catalog_desk(user: User) -> None:
    _seed_demo_highlights(user)
    hypothesis = Catalog.get_or_create_from_page_key("https://example.com/hypothesis")
    CatalogMembership.objects.get_or_create(
        user=user,
        catalog=hypothesis,
        defaults={"title": "Hypothesis"},
    )
    item = Catalog.get_or_create_from_page_key("https://example.com/item?id=321")
    CatalogMembership.objects.get_or_create(
        user=user,
        catalog=item,
        defaults={"title": "Item 321", "bookmarked": True},
    )


def _row_kwargs(
    membership: CatalogMembership,
    *,
    selected_id: int | None,
) -> dict[str, object]:
    catalog = membership.catalog
    page_key = catalog.page_key
    return {
        "catalog_id": str(catalog.id),
        "title": membership.title,
        "origin": catalog.origin,
        "path": catalog.path,
        "query": catalog.query,
        "highlight_count": Highlight.objects.filter(user=membership.user, catalog=catalog).count(),
        "bookmarked": membership.bookmarked,
        "selected": selected_id == catalog.id,
        "select_url": reverse("catalog_desk_detail", args=[catalog.id]),
        "source_href": page_key,
    }


def _desk_kwargs(request: AuthenticatedRequest, catalog: Catalog | None) -> dict[str, object]:
    _seed_catalog_desk(request.user)
    selected_id = catalog.id if catalog else None
    memberships = (
        CatalogMembership.objects.filter(user=request.user)
        .select_related("catalog")
        .order_by("-updated_at")
    )
    rows = [_row_kwargs(row, selected_id=selected_id) for row in memberships]
    highlights: list[dict[str, object]] = []
    pane_title = ""
    if catalog:
        membership = CatalogMembership.objects.filter(user=request.user, catalog=catalog).first()
        pane_title = membership.title if membership and membership.title else catalog.page_key
        highlights = [
            _highlight_kwargs(highlight)
            for highlight in Highlight.objects.filter(user=request.user, catalog=catalog).order_by(
                "created_at"
            )
        ]
    return {
        "rows": rows,
        "selected": catalog is not None,
        "pane_title": pane_title,
        "source_href": catalog.page_key if catalog else "",
        "highlights": highlights,
        "csrf_token": get_token(request),
        "dismiss_url": reverse("catalog_desk"),
    }


def _desk_response(request: AuthenticatedRequest, kwargs: dict[str, object]) -> HttpResponse:
    if _is_htmx(request):
        return HttpResponse(render_component("catalog_desk", kwargs))
    return render(request, "highlights/catalog.html", {"desk_kwargs": kwargs})


@login_required
@require_http_methods(["GET"])
def catalog_desk_view(request: AuthenticatedRequest) -> HttpResponse:
    return _desk_response(request, _desk_kwargs(request, None))


@login_required
@require_http_methods(["GET"])
def catalog_desk_detail_view(request: AuthenticatedRequest, catalog_id: int) -> HttpResponse:
    membership = get_object_or_404(
        CatalogMembership.objects.select_related("catalog"),
        user=request.user,
        catalog_id=catalog_id,
    )
    return _desk_response(request, _desk_kwargs(request, membership.catalog))
