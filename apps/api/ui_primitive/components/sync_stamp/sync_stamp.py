from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

TONES = ("ok", "syncing", "error")

_DEFAULT_LABEL = {
    "ok": "SYNCED · 12:04",
    "syncing": "SYNCING…",
    "error": "SYNC FAILED · 401",
}


class SyncStamp(Component):
    citry = app
    name = "sync_stamp"
    template_file = "sync_stamp.citry-html"
    css_file = "sync_stamp.css"

    @dataclass
    class Kwargs:
        tone: str = "ok"
        label: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(tone="ok", label=_DEFAULT_LABEL["ok"]),
                    slug="sync-stamp-ok",
                    title="SyncStamp / ok",
                    description="Printer's mark — success dot, secondary mono label.",
                ),
                meta(
                    variant(tone="syncing", label=_DEFAULT_LABEL["syncing"]),
                    slug="sync-stamp-syncing",
                    title="SyncStamp / syncing",
                    description="In-flight stamp — accent dot, same secondary ink.",
                ),
                meta(
                    variant(tone="error", label=_DEFAULT_LABEL["error"]),
                    slug="sync-stamp-error",
                    title="SyncStamp / error",
                    description="Failed stamp — danger dot, still not a status chip.",
                ),
            ]

    def template_data(self, kwargs, slots):
        tone = kwargs.tone if kwargs.tone in TONES else "ok"
        label = kwargs.label.strip() or _DEFAULT_LABEL[tone]
        return {
            "class_name": f"ds-sync-stamp ds-sync-stamp--{tone}",
            "label": label,
        }
