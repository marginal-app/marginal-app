from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class LoginForm(Component):
    citry = app
    name = "login_form"
    template_file = "login_form.citry-html"
    css_file = "login_form.css"

    @dataclass
    class Kwargs:
        action_url: str = ""
        csrf_token: str = ""
        username: str = ""
        has_error: bool = False

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Desk"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(),
                    slug="identity-login-idle",
                    title="LoginForm / idle",
                    description="Empty login form.",
                ),
                meta(
                    variant(username="dev", has_error=True),
                    slug="identity-login-error",
                    title="LoginForm / error",
                    description="Wrong username or password.",
                ),
            ]

    def template_data(self, kwargs, slots):
        return {
            "action_url": kwargs.action_url,
            "csrf_token": kwargs.csrf_token,
            "username": kwargs.username,
            "has_error": kwargs.has_error,
        }
