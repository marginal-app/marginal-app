from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app
from highlights.components.catalog_desk.catalog_desk import (
    ROW_BOOKMARKED,
    ROW_HYPOTHESIS,
    ROW_SSR,
)
from highlights.components.marginalia.marginalia import NOTE, QUOTE

KICKER = "수요일, 9월 10일"
HEADLINE = "이번 주 밑줄 22개, 페이지 3개"
EDIT_LABEL = "위젯 편집"
ADD_LABEL = "+ 위젯 추가"

WEEK_BARS = (
    {"label": "목", "height": 14, "empty": False, "today": False},
    {"label": "금", "height": 34, "empty": False, "today": False},
    {"label": "토", "height": 3, "empty": True, "today": False},
    {"label": "일", "height": 7, "empty": False, "today": False},
    {"label": "월", "height": 48, "empty": False, "today": False},
    {"label": "화", "height": 27, "empty": False, "today": False},
    {"label": "수", "height": 21, "empty": False, "today": True},
)

RECENT = (
    {
        "quote": QUOTE,
        "comment": NOTE,
        "color": "var(--highlight-yellow)",
    },
    {
        "quote": "Cloud Agents can screenshot a component URL.",
        "comment": "",
        "color": "var(--highlight-blue)",
    },
)

FREQUENT_PAGES = (
    {**ROW_SSR, "folio": "01"},
    {**ROW_HYPOTHESIS, "folio": "02"},
)

BOOKMARKS = ({**ROW_BOOKMARKED, "folio": "01"},)


class HomeDesk(Component):
    citry = app
    name = "home_desk"
    template_file = "home_desk.citry-html"
    css_file = "home_desk.css"

    @dataclass
    class Kwargs:
        kicker: str = KICKER
        headline: str = HEADLINE
        underline_count: str = "22"
        page_count: str = "3"
        comment_count: str = "4"
        week_delta: str = "지난주 대비 +9"
        recent: list[dict[str, Any]] = field(default_factory=lambda: [dict(row) for row in RECENT])
        frequent: list[dict[str, Any]] = field(
            default_factory=lambda: [dict(row) for row in FREQUENT_PAGES]
        )
        bookmarks: list[dict[str, Any]] = field(
            default_factory=lambda: [dict(row) for row in BOOKMARKS]
        )

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(),
                    slug="desk-home-populated",
                    title="HomeDesk / populated",
                    description="Expanded sidebar and the four home widgets.",
                ),
            ]

    def template_data(self, kwargs, slots):
        bars = []
        for raw in WEEK_BARS:
            col_class = "home-week__col"
            if raw["empty"]:
                col_class = f"{col_class} is-empty"
            if raw["today"]:
                col_class = f"{col_class} is-today"
            bars.append(
                {
                    "label": raw["label"],
                    "col_class": col_class,
                    "bar_style": f"height: {raw['height']}px",
                }
            )
        stats = [
            {"value": kwargs.underline_count, "label": "밑줄"},
            {"value": kwargs.page_count, "label": "페이지"},
            {"value": kwargs.comment_count, "label": "코멘트"},
        ]
        return {
            "kicker": kwargs.kicker,
            "headline": kwargs.headline,
            "edit_label": EDIT_LABEL,
            "add_label": ADD_LABEL,
            "week_delta": kwargs.week_delta,
            "stats": stats,
            "bars": bars,
            "recent": kwargs.recent,
            "frequent": kwargs.frequent,
            "bookmarks": kwargs.bookmarks,
        }
