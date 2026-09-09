from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component, SlotInput

from citry_preview.variants import meta
from config.citry_app import app

TRAY_BODY = "Server-rendered HTML is a complete first paint."


class Tray(Component):
    citry = app
    name = "tray"
    template_file = "tray.citry-html"
    css_file = "tray.css"

    @dataclass
    class Kwargs:
        open: bool = False
        body: str = ""
        staged: bool = False
        dismiss_url: str = ""
        dismiss_attrs: dict[str, str] | None = None

    class Slots:
        default: SlotInput | None = None

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(staged=True, body=TRAY_BODY),
                    slug="tray-closed",
                    title="Tray / closed",
                    description="Off-canvas. translateX(100%) — the panel is not in view.",
                ),
                meta(
                    variant(open=True, staged=True, body=TRAY_BODY),
                    slug="tray-open",
                    title="Tray / open",
                    description="Slid in from the right. translateX(0).",
                ),
            ]

    def template_data(self, kwargs, slots):
        host = ["ds-tray-host"]
        if kwargs.staged:
            host.append("is-staged")
        panel = ["ds-tray"]
        if kwargs.open:
            panel.append("is-open")
        return {
            "host_class": " ".join(host),
            "class_name": " ".join(panel),
            "aria_hidden": "false" if kwargs.open else "true",
            "body": kwargs.body,
            "show_dismiss": kwargs.open and bool(kwargs.dismiss_url),
            "dismiss_url": kwargs.dismiss_url,
            "dismiss_attrs": kwargs.dismiss_attrs or {},
        }
