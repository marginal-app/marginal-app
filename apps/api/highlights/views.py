import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from identity.request import AuthenticatedRequest

from .auth import require_api_token
from .models import Bookmark, Catalog, Highlight
from .page_key import canonicalize_page_key, catalog_meta_from_payload


@csrf_exempt
@require_api_token
@require_http_methods(["GET", "POST"])
def highlights_view(request: AuthenticatedRequest) -> JsonResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        page_key = canonicalize_page_key(data["pageKey"])
        title, description = catalog_meta_from_payload(data)
        highlight = Highlight.objects.create(
            page_key=page_key,
            quote=data["quote"],
            prefix=data.get("prefix", ""),
            suffix=data.get("suffix", ""),
            color=data["color"],
            comment=data.get("comment", ""),
        )
        Catalog.upsert_from_page_key(page_key, title=title, description=description)
        return JsonResponse(highlight.to_dict(), status=201)

    page_key = request.GET.get("pageKey")
    queryset = Highlight.objects.all()
    if page_key:
        queryset = queryset.filter(page_key=canonicalize_page_key(page_key))
    return JsonResponse([h.to_dict() for h in queryset], safe=False)


@csrf_exempt
@require_api_token
@require_http_methods(["PATCH"])
def highlight_detail_view(request: AuthenticatedRequest, id: str) -> JsonResponse:
    try:
        highlight = Highlight.objects.get(id=id)
    except Highlight.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    data = json.loads(request.body)
    if "comment" in data:
        highlight.comment = data["comment"]
        highlight.save(update_fields=["comment", "updated_at"])
    return JsonResponse(highlight.to_dict())


@csrf_exempt
@require_api_token
@require_http_methods(["POST"])
def bookmarks_view(request: AuthenticatedRequest) -> JsonResponse:
    data = json.loads(request.body)
    title, description = catalog_meta_from_payload(data)
    bookmark, created = Bookmark.upsert_from_page_key(
        data["pageKey"],
        title=title,
        description=description,
    )
    return JsonResponse(bookmark.to_dict(), status=201 if created else 200)


@require_api_token
@require_http_methods(["GET"])
def ping_view(request: AuthenticatedRequest) -> JsonResponse:
    return JsonResponse({"ok": True})
