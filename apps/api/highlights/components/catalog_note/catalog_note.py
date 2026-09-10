from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

LABEL = "페이지 노트"
HINT = "이 페이지 전체에 대한 메모입니다. 밑줄 코멘트와는 다릅니다."
PLACEHOLDER = "페이지 노트 추가..."
PAGE_NOTE = "SSR 실루엣은 이 페이지 노트에서 리뷰한다. 밑줄 코멘트와는 별개다."


class CatalogNote(Component):
    citry = app
    name = "catalog_note"
    template_file = "catalog_note.citry-html"
    css_file = "catalog_note.css"

    @dataclass
    class Kwargs:
        note: str = ""
        placeholder: str = PLACEHOLDER
        focused: bool = False
        rows: int = 4

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(focused=True),
                    slug="catalog-note-empty",
                    title="CatalogNote / empty",
                    description="Empty page-level note. Distinct from highlight comment.",
                ),
                meta(
                    variant(note=PAGE_NOTE),
                    slug="catalog-note-filled",
                    title="CatalogNote / filled",
                    description="Saved catalog page note in the textarea.",
                ),
            ]

    def template_data(self, kwargs, slots):
        return {
            "label": LABEL,
            "hint": HINT,
            "note": kwargs.note,
            "placeholder": kwargs.placeholder,
            "focused": kwargs.focused,
            "rows": kwargs.rows,
        }
