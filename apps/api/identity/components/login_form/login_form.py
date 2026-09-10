from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app

ERROR_MESSAGE = "사용자 이름 또는 비밀번호가 올바르지 않습니다"


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
        password: str = ""
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
                    description="Centered 400px sheet — Wordmark sm, fields, primary.",
                ),
                meta(
                    variant(username="dev", password="secret", has_error=True),
                    slug="identity-login-error",
                    title="LoginForm / error",
                    description="Filled fields, danger password border, SyncStamp error.",
                ),
            ]

    def template_data(self, kwargs, slots):
        sheet = "identity-login__sheet"
        password_field = "identity-login__field"
        if kwargs.has_error:
            password_field = f"{password_field} is-invalid"
        return {
            "action_url": kwargs.action_url,
            "csrf_token": kwargs.csrf_token,
            "username": kwargs.username,
            "password": kwargs.password,
            "has_error": kwargs.has_error,
            "sheet_class": sheet,
            "password_field_class": password_field,
            "error_message": ERROR_MESSAGE,
        }
