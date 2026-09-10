from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

PLACEHOLDER = "코멘트 추가…"
QUOTE = "서버가 그린 HTML은 그 자체로 완결된 첫 화면이다."
NOTE = "리뷰 실루엣은 여기서 나온다."


class Marginalia(Component):
    citry = app
    name = "marginalia"
    template_file = "marginalia.citry-html"
    css_file = "marginalia.css"

    @dataclass
    class Kwargs:
        quote: str = QUOTE
        comment: str = ""
        color: str = "var(--highlight-yellow)"

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(quote=QUOTE),
                    slug="marginalia-quote",
                    title="Marginalia / quote",
                    description="Underline with a placeholder — no note yet.",
                ),
                meta(
                    variant(quote=QUOTE, comment=NOTE),
                    slug="marginalia-note",
                    title="Marginalia / note",
                    description="Quote plus a saved margin note.",
                ),
            ]

    def template_data(self, kwargs, slots):
        comment = kwargs.comment.strip()
        has_note = bool(comment)
        note_class = "ds-marginalia__note"
        if not has_note:
            note_class = f"{note_class} is-placeholder"
        return {
            "quote": kwargs.quote,
            "note": comment or PLACEHOLDER,
            "note_class": note_class,
            "rule_style": f"background: {kwargs.color}",
        }
