from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from citry_preview.rendering import render_component
from citry_preview.variants import meta
from config.citry_app import app
from highlights.models import CatalogMembership
from identity.request import AuthenticatedRequest

LABEL = "페이지 노트"
HINT = "이 페이지 전체에 대한 메모입니다. 하이라이트 코멘트와는 다릅니다."
PLACEHOLDER = "페이지 노트 추가..."
PAGE_NOTE = "SSR 실루엣은 이 페이지 노트에서 리뷰한다. 하이라이트 코멘트와는 별개다."
DIRTY_NOTE = "저장 전 초안이다. 하이라이트 코멘트와는 별개다."
SAVE_ERROR = "저장에 실패했습니다."
EDIT_LABEL = "편집"
SAVE_LABEL = "저장"
CANCEL_LABEL = "취소"


class CatalogNote(Component):
    citry = app
    name = "catalog_note"
    template_file = "catalog_note.citry-html"
    css_file = "catalog_note.css"

    @dataclass
    class Kwargs:
        note: str = ""
        saved_note: str = ""
        placeholder: str = PLACEHOLDER
        editing: bool = False
        dirty: bool = False
        error: str = ""
        focused: bool = False
        rows: int = 4
        edit_url: str = ""
        save_url: str = ""
        csrf_token: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(),
                    slug="catalog-note-empty",
                    title="CatalogNote / empty read",
                    description="Read mode, empty placeholder, pencil. Hint only; no auto-focus.",
                ),
                meta(
                    variant(note=PAGE_NOTE, saved_note=PAGE_NOTE),
                    slug="catalog-note-filled",
                    title="CatalogNote / filled read",
                    description="Read mode with the saved page note and a pencil.",
                ),
                meta(
                    variant(
                        note=PAGE_NOTE,
                        saved_note=PAGE_NOTE,
                        editing=True,
                        focused=True,
                    ),
                    slug="catalog-note-edit-clean",
                    title="CatalogNote / edit clean",
                    description="Edit mode, draft equals last saved. Save disabled.",
                ),
                meta(
                    variant(
                        note=DIRTY_NOTE,
                        saved_note=PAGE_NOTE,
                        editing=True,
                        dirty=True,
                        focused=True,
                    ),
                    slug="catalog-note-edit-dirty",
                    title="CatalogNote / edit dirty",
                    description="Edit mode, draft differs from last saved. Save enabled.",
                ),
                meta(
                    variant(
                        note=DIRTY_NOTE,
                        saved_note=PAGE_NOTE,
                        editing=True,
                        dirty=True,
                        error=SAVE_ERROR,
                        focused=True,
                    ),
                    slug="catalog-note-edit-error",
                    title="CatalogNote / edit error",
                    description="Save failed. Stay in edit with a short error.",
                ),
            ]

    def template_data(self, kwargs, slots):
        note = kwargs.note
        saved_note = kwargs.saved_note if kwargs.saved_note or kwargs.editing else note
        empty = not note.strip()
        edit_attrs = (
            {
                "hx-get": kwargs.edit_url,
                "hx-target": "closest .catalog-note",
                "hx-swap": "outerHTML",
            }
            if kwargs.edit_url
            else {}
        )
        form_attrs: dict[str, str] = {
            "data-saved": saved_note,
            "oninput": (
                "var save=this.querySelector('.catalog-note__actions "
                ".button:not(.quiet)');"
                "if(save)save.disabled=this.note.value===this.dataset.saved;"
            ),
        }
        if kwargs.save_url:
            form_attrs.update(
                {
                    "hx-post": kwargs.save_url,
                    "hx-target": "closest .catalog-note",
                    "hx-swap": "outerHTML",
                }
            )
        return {
            "label": LABEL,
            "hint": "" if not empty else HINT,
            "note": note,
            "saved_note": saved_note,
            "placeholder": kwargs.placeholder,
            "editing": kwargs.editing,
            "empty": empty,
            "error": kwargs.error,
            "has_error": bool(kwargs.error),
            "focused": kwargs.focused,
            "autofocus": kwargs.editing and kwargs.focused,
            "rows": kwargs.rows,
            "save_disabled": not kwargs.dirty,
            "edit_label": EDIT_LABEL,
            "save_label": SAVE_LABEL,
            "cancel_label": CANCEL_LABEL,
            "csrf_token": kwargs.csrf_token,
            "edit_attrs": edit_attrs,
            "form_attrs": form_attrs,
            "show_pencil": not kwargs.editing,
        }


def _note_kwargs(
    membership: CatalogMembership,
    request,
    *,
    editing: bool,
    note: str | None = None,
    error: str = "",
) -> dict[str, object]:
    saved = membership.note
    draft = saved if note is None else note
    note_url = reverse("catalog_note", args=[membership.catalog_id])
    return {
        "note": draft,
        "saved_note": saved,
        "editing": editing,
        "dirty": editing and draft != saved,
        "error": error,
        "focused": editing,
        "edit_url": note_url,
        "save_url": note_url,
        "csrf_token": get_token(request),
    }


@login_required
@require_http_methods(["GET", "POST"])
def catalog_note_view(request: AuthenticatedRequest, catalog_id: int) -> HttpResponse:
    membership = get_object_or_404(
        CatalogMembership.objects.select_related("catalog"),
        user=request.user,
        catalog_id=catalog_id,
    )
    if request.method == "GET":
        return HttpResponse(
            render_component(
                "catalog_note",
                _note_kwargs(membership, request, editing=True),
            )
        )
    if request.POST.get("cancel"):
        return HttpResponse(
            render_component(
                "catalog_note",
                _note_kwargs(membership, request, editing=False),
            )
        )
    draft = request.POST.get("note", "")
    try:
        membership.note = draft
        membership.save(update_fields=["note", "updated_at"])
    except Exception:  # noqa: BLE001 — any persist failure stays in edit
        return HttpResponse(
            render_component(
                "catalog_note",
                _note_kwargs(
                    membership,
                    request,
                    editing=True,
                    note=draft,
                    error=SAVE_ERROR,
                ),
            )
        )
    membership.refresh_from_db()
    return HttpResponse(
        render_component(
            "catalog_note",
            _note_kwargs(membership, request, editing=False),
        )
    )
