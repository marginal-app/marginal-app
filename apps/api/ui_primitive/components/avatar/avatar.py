from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class Avatar(Component):
    citry = app
    name = "avatar"
    template_file = "avatar.citry-html"
    css_file = "avatar.css"

    @dataclass
    class Kwargs:
        initials: str = "M"

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Primitives"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(initials="M"),
                    slug="avatar-default",
                    title="Avatar / default",
                    description="28px identity chip — accent initials on an elevated disc.",
                ),
            ]

    def template_data(self, kwargs, slots):
        initials = kwargs.initials.strip() or "M"
        return {"initials": initials}
