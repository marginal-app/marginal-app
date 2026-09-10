from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app
from highlights.components.catalog_row.catalog_row import display_host
from highlights.components.highlight_card.highlight_card import QUOTE_ONLY, WITH_COMMENT

ROW_SSR = {
    "catalog_id": "1",
    "folio": "01",
    "title": "Why Server-Rendered HTML Still Wins",
    "origin": "https://blog.example.org",
    "path": "/posts/ssr",
    "query": "",
    "highlight_count": 5,
    "bookmarked": False,
    "selected": False,
    "select_url": "",
    "source_href": "https://blog.example.org/posts/ssr",
}

ROW_HYPOTHESIS = {
    "catalog_id": "2",
    "folio": "02",
    "title": "Hypothesis",
    "origin": "https://example.com",
    "path": "/hypothesis",
    "query": "",
    "highlight_count": 2,
    "bookmarked": False,
    "selected": False,
    "select_url": "",
    "source_href": "https://example.com/hypothesis",
}

ROW_BOOKMARKED = {
    "catalog_id": "3",
    "folio": "03",
    "title": "Item 321",
    "origin": "https://example.com",
    "path": "/item",
    "query": "?id=321",
    "highlight_count": 0,
    "bookmarked": True,
    "selected": False,
    "select_url": "",
    "source_href": "https://example.com/item?id=321",
}

TRAY_HIGHLIGHTS = [
    {
        **QUOTE_ONLY,
        "color": "var(--highlight-yellow)",
        "when": "12분 전",
        "comment_edit_url": "",
        "comment_save_url": "",
    },
    {
        **WITH_COMMENT,
        "color": "var(--highlight-blue)",
        "when": "어제",
        "comment_edit_url": "",
        "comment_save_url": "",
    },
]

HIGHLIGHT_ROWS = [
    {
        "quote": "Server-rendered HTML is a complete first paint.",
        "title": "Why Server-Rendered HTML Still Wins",
        "host": "blog.example.org",
        "when": "12분 전",
        "selected": True,
        "color": "var(--highlight-yellow)",
    },
    {
        "quote": "Cloud Agents can screenshot a component URL.",
        "title": "Hypothesis",
        "host": "example.com",
        "when": "어제",
        "selected": False,
        "color": "var(--highlight-yellow)",
    },
    {
        "quote": "HTMX swaps this same component, not a second client tree.",
        "title": "Hypothesis",
        "host": "example.com",
        "when": "3일 전",
        "selected": False,
        "color": "var(--highlight-yellow)",
    },
]

COMMENT_ROWS = [
    {
        "note": "리뷰 실루엣은 여기서 나온다.",
        "quote": "“Server-rendered HTML is a complete first paint.”",
        "title": "Why Server-Rendered HTML Still Wins",
        "host": "blog.example.org",
        "when": "12분 전",
        "selected": True,
        "color": "var(--highlight-yellow)",
    },
    {
        "note": "This is the silhouette we review before merge.",
        "quote": "“Cloud Agents can screenshot a component URL.”",
        "title": "Hypothesis",
        "host": "example.com",
        "when": "어제",
        "selected": False,
        "color": "var(--highlight-yellow)",
    },
]

TABS = (
    ("toc", "목차"),
    ("highlights", "밑줄"),
    ("bookmarks", "북마크"),
    ("comments", "코멘트"),
)


class CatalogDesk(Component):
    citry = app
    name = "catalog_desk"
    template_file = "catalog_desk.citry-html"
    css_file = "catalog_desk.css"

    @dataclass
    class Kwargs:
        rows: list[dict[str, Any]] = field(default_factory=list)
        selected: bool = False
        pane_title: str = ""
        source_href: str = ""
        highlights: list[dict[str, Any]] = field(default_factory=list)
        highlight_rows: list[dict[str, Any]] = field(default_factory=list)
        comment_rows: list[dict[str, Any]] = field(default_factory=list)
        csrf_token: str = ""
        dismiss_url: str = ""
        tab: str = "toc"
        toc_count: str = ""
        highlight_count: str = ""
        bookmark_count: str = ""
        comment_count: str = ""
        pane_host: str = ""
        pane_highlight_count: int = 0
        pane_bookmarked: bool = False
        kicker: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            selected_row = {**ROW_SSR, "selected": True}
            counts = {
                "toc_count": "3",
                "highlight_count": "7",
                "bookmark_count": "2",
                "comment_count": "4",
            }
            pane = {
                "pane_title": ROW_SSR["title"],
                "source_href": ROW_SSR["source_href"],
                "pane_host": "blog.example.org",
                "pane_highlight_count": 5,
                "kicker": "페이지 · 밑줄 5",
                "highlights": TRAY_HIGHLIGHTS,
                "dismiss_url": "/catalog/",
            }
            return [
                meta(
                    variant(),
                    slug="catalog-desk-empty",
                    title="CatalogDesk / empty",
                    description="Collapsed sidebar, tabs, no marked pages.",
                ),
                meta(
                    variant(rows=[ROW_SSR, ROW_HYPOTHESIS, ROW_BOOKMARKED], **counts),
                    slug="catalog-desk-idle",
                    title="CatalogDesk / idle",
                    description="TOC tab, tray closed.",
                ),
                meta(
                    variant(
                        rows=[selected_row, ROW_HYPOTHESIS, ROW_BOOKMARKED],
                        selected=True,
                        **counts,
                        **pane,
                    ),
                    slug="catalog-desk-selected",
                    title="CatalogDesk / selected",
                    description="TOC row selected. Tray with DocumentCard.",
                ),
                meta(
                    variant(
                        rows=[selected_row, ROW_HYPOTHESIS, ROW_BOOKMARKED],
                        selected=True,
                        tab="highlights",
                        highlight_rows=HIGHLIGHT_ROWS,
                        **counts,
                        **pane,
                    ),
                    slug="catalog-desk-highlights",
                    title="CatalogDesk / highlights",
                    description="Underline tab. Selected highlight row, tray open.",
                ),
                meta(
                    variant(
                        rows=[selected_row, ROW_HYPOTHESIS, ROW_BOOKMARKED],
                        selected=True,
                        tab="comments",
                        comment_rows=COMMENT_ROWS,
                        **counts,
                        **pane,
                    ),
                    slug="catalog-desk-comments",
                    title="CatalogDesk / comments",
                    description="Comment tab. Selected comment row, tray open.",
                ),
            ]

    def template_data(self, kwargs, slots):
        selected = kwargs.selected
        highlights = kwargs.highlights
        dismiss_url = kwargs.dismiss_url if selected else ""
        tab = kwargs.tab if kwargs.tab in {key for key, _ in TABS} else "toc"
        counts = {
            "toc": kwargs.toc_count,
            "highlights": kwargs.highlight_count,
            "bookmarks": kwargs.bookmark_count,
            "comments": kwargs.comment_count,
        }
        tabs = []
        for key, label in TABS:
            item_class = "ds-view-tab"
            if key == tab:
                item_class = f"{item_class} is-active"
            else:
                item_class = f"{item_class} is-idle"
            tabs.append(
                {
                    "key": key,
                    "label": label,
                    "count": counts[key],
                    "active": key == tab,
                    "class_name": item_class,
                }
            )
        tray_highlights = []
        for row in highlights:
            comment = str(row.get("comment") or "").strip()
            tray_highlights.append(
                {
                    "quote": row.get("quote") or "",
                    "comment": comment,
                    "when": row.get("when") or "",
                    "has_comment": bool(comment),
                    "chip_style": f"background: {row.get('color') or 'var(--highlight-yellow)'}",
                }
            )
        pane_host = kwargs.pane_host
        if not pane_host and kwargs.source_href:
            pane_host = display_host(kwargs.source_href, "", "")
        kicker = kwargs.kicker
        if not kicker and selected:
            count = kwargs.pane_highlight_count
            kicker = f"페이지 · 밑줄 {count}" if count else "페이지"
        desk_class = "catalog-desk"
        if selected:
            desk_class = f"{desk_class} is-tray-open"
        return {
            "desk_class": desk_class,
            "rows": kwargs.rows,
            "is_empty": not kwargs.rows,
            "selected": selected,
            "show_toc": tab in {"toc", "bookmarks"},
            "show_highlights": tab == "highlights",
            "show_comments": tab == "comments",
            "highlight_rows": kwargs.highlight_rows,
            "comment_rows": kwargs.comment_rows,
            "pane_title": kwargs.pane_title,
            "source_href": kwargs.source_href,
            "pane_host": pane_host,
            "pane_highlight_count": kwargs.pane_highlight_count,
            "pane_bookmarked": kwargs.pane_bookmarked,
            "tray_highlights": tray_highlights,
            "csrf_token": kwargs.csrf_token,
            "dismiss_url": dismiss_url,
            "kicker": kicker,
            "tabs": tabs,
            "dismiss_attrs": (
                {
                    "hx-get": dismiss_url,
                    "hx-target": "#catalog-desk",
                    "hx-swap": "outerHTML",
                    "hx-push-url": "true",
                }
                if dismiss_url
                else {}
            ),
        }
