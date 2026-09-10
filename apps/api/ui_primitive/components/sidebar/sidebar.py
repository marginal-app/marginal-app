from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

NavItem = dict[str, Any]

NAV_ITEMS: list[NavItem] = [
    {"key": "search", "icon": "search", "label": "검색", "count": "", "footer": False},
    {"key": "home", "icon": "home", "label": "홈", "count": "", "footer": False},
    {
        "key": "library",
        "icon": "list",
        "label": "라이브러리",
        "count": "12",
        "footer": False,
    },
    {"key": "settings", "icon": "settings", "label": "설정", "count": "", "footer": True},
]


def copy_nav() -> list[NavItem]:
    return [dict(row) for row in NAV_ITEMS]


def _paint_items(items: list[NavItem], active: str) -> tuple[list[NavItem], list[NavItem]]:
    main: list[NavItem] = []
    footer: list[NavItem] = []
    for raw in items:
        is_active = raw.get("key") == active
        class_name = "ds-sidebar__item"
        if is_active:
            class_name = f"{class_name} is-active"
        count = str(raw.get("count") or "")
        painted = {
            "icon": raw.get("icon") or "home",
            "label": raw.get("label") or "",
            "count": count,
            "has_count": bool(count),
            "class_name": class_name,
        }
        if raw.get("footer"):
            footer.append(painted)
        else:
            main.append(painted)
    return main, footer


class Sidebar(Component):
    citry = app
    name = "sidebar"
    template_file = "sidebar.citry-html"
    css_file = "sidebar.css"

    @dataclass
    class Kwargs:
        state: str = "expanded"
        active: str = "home"
        items: list[NavItem] = field(default_factory=copy_nav)
        account_name: str = "malkoG"
        account_host: str = "127.0.0.1:8000"
        account_initials: str = "M"
        sync_tone: str = "ok"
        sync_label: str = "SYNCED · 12:04"

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(state="expanded"),
                    slug="sidebar-expanded",
                    title="Sidebar / expanded",
                    description="216px rail — labels, library count, stamp, account.",
                ),
                meta(
                    variant(state="collapsed"),
                    slug="sidebar-collapsed",
                    title="Sidebar / collapsed",
                    description="56px icon rail — brand mark, expand, avatar with sync dot.",
                ),
            ]

    def template_data(self, kwargs, slots):
        collapsed = kwargs.state == "collapsed"
        items = kwargs.items or copy_nav()
        main, footer = _paint_items(items, kwargs.active)
        class_name = "ds-sidebar"
        if collapsed:
            class_name = f"{class_name} ds-sidebar--collapsed"
        return {
            "class_name": class_name,
            "collapsed": collapsed,
            "expanded": not collapsed,
            "items": main,
            "footer_items": footer,
            "account_name": kwargs.account_name,
            "account_host": kwargs.account_host,
            "account_initials": kwargs.account_initials,
            "sync_tone": kwargs.sync_tone,
            "sync_label": kwargs.sync_label,
        }
