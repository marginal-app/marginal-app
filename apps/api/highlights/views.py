import json
import uuid

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from identity.request import AuthenticatedRequest

from .auth import require_api_token
from .clock import datetime_from_ms, epoch_ms
from .models import Catalog, CatalogMembership, Highlight, HighlightConflict
from .page_key import canonicalize_page_key, catalog_meta_from_payload


def _parse_uuid(raw: object) -> uuid.UUID | None:
    try:
        return uuid.UUID(str(raw))
    except (TypeError, ValueError, AttributeError):
        return None


def _created_at_from_payload(data: dict):
    raw = data.get("createdAt")
    if raw is None:
        return timezone.now()
    try:
        return datetime_from_ms(int(raw))
    except (TypeError, ValueError, OSError):
        return timezone.now()


@csrf_exempt
@require_api_token
@require_http_methods(["GET", "POST"])
def highlights_view(request: AuthenticatedRequest) -> JsonResponse:
    user = request.bearer_user
    if request.method == "POST":
        data = json.loads(request.body)
        highlight_id = _parse_uuid(data.get("id"))
        if highlight_id is None:
            return JsonResponse({"error": "id is required"}, status=400)
        page_key = canonicalize_page_key(data["pageKey"])
        title, description = catalog_meta_from_payload(data)
        try:
            highlight, created = Highlight.upsert_for_user(
                user,
                highlight_id=highlight_id,
                page_key=page_key,
                quote=data["quote"],
                prefix=data.get("prefix", ""),
                suffix=data.get("suffix", ""),
                color=data["color"],
                comment=data.get("comment", ""),
                created_at=_created_at_from_payload(data),
                title=title,
                description=description,
            )
        except HighlightConflict:
            return JsonResponse({"error": "conflict"}, status=409)
        return JsonResponse(highlight.to_dict(), status=201 if created else 200)

    queryset = Highlight.objects.filter(user=user)
    page_key = request.GET.get("pageKey")
    if page_key:
        queryset = queryset.filter(page_key=canonicalize_page_key(page_key))
    return JsonResponse([h.to_dict() for h in queryset], safe=False)


@csrf_exempt
@require_api_token
@require_http_methods(["PATCH"])
def highlight_detail_view(request: AuthenticatedRequest, id: str) -> JsonResponse:
    try:
        highlight = Highlight.objects.get(id=id, user=request.bearer_user)
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
    page_key = canonicalize_page_key(data["pageKey"])
    title, description = catalog_meta_from_payload(data)
    catalog = Catalog.get_or_create_from_page_key(page_key)
    membership, created = CatalogMembership.upsert(
        request.bearer_user,
        catalog,
        title=title,
        description=description,
        bookmarked=True,
    )
    return JsonResponse(membership.to_dict(), status=201 if created else 200)


def _max_cursor_ms(rows: list, fallback: int) -> int:
    if not rows:
        return fallback
    return max(epoch_ms(row.updated_at) for row in rows)


@csrf_exempt
@require_api_token
@require_http_methods(["GET"])
def sync_pull_view(request: AuthenticatedRequest) -> JsonResponse:
    raw_since = request.GET.get("since", "0")
    try:
        since = int(raw_since)
    except (TypeError, ValueError):
        return JsonResponse({"error": "invalid since"}, status=400)
    if since < 0:
        return JsonResponse({"error": "invalid since"}, status=400)

    since_dt = datetime_from_ms(since + 1)
    user = request.bearer_user
    highlights = [
        row
        for row in Highlight.objects.filter(user=user, updated_at__gte=since_dt).select_related(
            "catalog"
        )
        if epoch_ms(row.updated_at) > since
    ]
    memberships = [
        row
        for row in CatalogMembership.objects.filter(
            user=user, updated_at__gte=since_dt
        ).select_related("catalog")
        if epoch_ms(row.updated_at) > since
    ]
    cursor = max(
        _max_cursor_ms(highlights, since),
        _max_cursor_ms(memberships, since),
    )
    return JsonResponse(
        {
            "cursor": cursor,
            "highlights": [row.to_dict() for row in highlights],
            "memberships": [row.to_dict() for row in memberships],
        }
    )


@csrf_exempt
@require_api_token
@require_http_methods(["POST"])
def sync_push_view(request: AuthenticatedRequest) -> JsonResponse:
    data = json.loads(request.body)
    membership_payloads = data.get("memberships") or []
    highlight_payloads = data.get("highlights") or []
    if not isinstance(membership_payloads, list) or not isinstance(highlight_payloads, list):
        return JsonResponse({"error": "invalid payload"}, status=400)

    user = request.bearer_user
    memberships: list[CatalogMembership] = []
    highlights: list[Highlight] = []
    try:
        with transaction.atomic():
            for raw in membership_payloads:
                if not isinstance(raw, dict) or not raw.get("pageKey"):
                    return JsonResponse({"error": "invalid membership"}, status=400)
                page_key = canonicalize_page_key(str(raw["pageKey"]))
                catalog = Catalog.get_or_create_from_page_key(page_key)
                bookmarked = raw.get("bookmarked")
                membership, _created = CatalogMembership.upsert(
                    user,
                    catalog,
                    title=str(raw.get("title") or ""),
                    description=str(raw.get("description") or ""),
                    bookmarked=bookmarked if isinstance(bookmarked, bool) else None,
                )
                membership.save(update_fields=["updated_at"])
                memberships.append(membership)

            for raw in highlight_payloads:
                if not isinstance(raw, dict):
                    return JsonResponse({"error": "invalid highlight"}, status=400)
                highlight_id = _parse_uuid(raw.get("id"))
                if highlight_id is None or not raw.get("pageKey"):
                    return JsonResponse({"error": "invalid highlight"}, status=400)
                title, description = catalog_meta_from_payload(raw)
                highlight, _created = Highlight.upsert_for_user(
                    user,
                    highlight_id=highlight_id,
                    page_key=canonicalize_page_key(str(raw["pageKey"])),
                    quote=str(raw.get("quote") or ""),
                    prefix=str(raw.get("prefix") or ""),
                    suffix=str(raw.get("suffix") or ""),
                    color=str(raw.get("color") or ""),
                    comment=str(raw.get("comment") or ""),
                    created_at=_created_at_from_payload(raw),
                    title=title,
                    description=description,
                )
                highlights.append(highlight)
    except HighlightConflict:
        return JsonResponse({"error": "conflict"}, status=409)

    return JsonResponse(
        {
            "highlights": [row.to_dict() for row in highlights],
            "memberships": [row.to_dict() for row in memberships],
        }
    )


@require_api_token
@require_http_methods(["GET"])
def ping_view(request: AuthenticatedRequest) -> JsonResponse:
    return JsonResponse({"ok": True})
