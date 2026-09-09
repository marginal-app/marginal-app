import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .auth import require_api_token
from .models import Highlight
from .page_key import canonicalize_page_key


@csrf_exempt
@require_api_token
@require_http_methods(["GET", "POST"])
def highlights_view(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        highlight = Highlight.objects.create(
            page_key=canonicalize_page_key(data["pageKey"]),
            quote=data["quote"],
            prefix=data.get("prefix", ""),
            suffix=data.get("suffix", ""),
            color=data["color"],
            comment=data.get("comment", ""),
        )
        return JsonResponse(highlight.to_dict(), status=201)

    page_key = request.GET.get("pageKey")
    queryset = Highlight.objects.all()
    if page_key:
        queryset = queryset.filter(page_key=canonicalize_page_key(page_key))
    return JsonResponse([h.to_dict() for h in queryset], safe=False)


@csrf_exempt
@require_api_token
@require_http_methods(["PATCH"])
def highlight_detail_view(request: HttpRequest, id: str) -> JsonResponse:
    try:
        highlight = Highlight.objects.get(id=id)
    except Highlight.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    data = json.loads(request.body)
    if "comment" in data:
        highlight.comment = data["comment"]
        highlight.save(update_fields=["comment", "updated_at"])
    return JsonResponse(highlight.to_dict())


@require_api_token
@require_http_methods(["GET"])
def ping_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"ok": True})
