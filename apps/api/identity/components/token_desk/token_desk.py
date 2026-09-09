from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class TokenDesk(Component):
    citry = app
    name = "token_desk"
    template_file = "token_desk.citry-html"
    css_file = "token_desk.css"

    @dataclass
    class Kwargs:
        action_url: str = ""
        logout_url: str = ""
        csrf_token: str = ""
        username: str = ""
        hint: str = ""
        issued_token: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(username="dev"),
                    slug="identity-token-empty",
                    title="TokenDesk / empty",
                    description="Signed in, no token yet.",
                ),
                meta(
                    variant(
                        username="dev",
                        hint="k3x9",
                        issued_token="dev-token-plain-k3x9",
                    ),
                    slug="identity-token-issued",
                    title="TokenDesk / issued",
                    description="Plaintext shown once after issue.",
                ),
                meta(
                    variant(username="dev", hint="k3x9"),
                    slug="identity-token-has",
                    title="TokenDesk / has",
                    description="Hint only — rotate to see a new secret.",
                ),
            ]

    def template_data(self, kwargs, slots):
        has_token = bool(kwargs.hint or kwargs.issued_token)
        return {
            "action_url": kwargs.action_url,
            "logout_url": kwargs.logout_url,
            "csrf_token": kwargs.csrf_token,
            "username": kwargs.username,
            "hint": kwargs.hint,
            "issued_token": kwargs.issued_token,
            "has_issued": bool(kwargs.issued_token),
            "has_hint_only": bool(kwargs.hint) and not kwargs.issued_token,
            "submit_label": "다시 발급" if has_token else "토큰 발급",
        }
