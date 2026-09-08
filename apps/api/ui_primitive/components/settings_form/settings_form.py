from dataclasses import dataclass
from typing import ClassVar, Self

from citry import Component

from citry_preview.variants import meta
from config.citry_app import app


class SettingsForm(Component):
    citry = app
    name = "settings_form"
    template_file = "settings_form.citry-html"
    css_file = "settings_form.css"

    @dataclass
    class Kwargs:
        action_url: str = ""
        server_url: str = ""
        api_token: str = ""
        status: str = "idle"
        error_message: str = ""
        csrf_token: str = ""

    class PreviewVariant(Kwargs):
        group: ClassVar[str] = "Atoms"

        @classmethod
        def variants(variant: type[Self]):
            return [
                meta(
                    variant(
                        server_url="http://127.0.0.1:8000",
                        api_token="dev-token",
                        status="idle",
                    ),
                    slug="settings-idle",
                    title="SettingsForm / idle",
                    description="Connection form before a test.",
                ),
                meta(
                    variant(
                        server_url="http://127.0.0.1:8000",
                        api_token="dev-token",
                        status="ok",
                    ),
                    slug="settings-ok",
                    title="SettingsForm / success",
                    description="Ping succeeded.",
                ),
                meta(
                    variant(
                        server_url="http://127.0.0.1:8000",
                        api_token="wrong-token",
                        status="error",
                        error_message="서버가 401로 응답했습니다",
                    ),
                    slug="settings-error",
                    title="SettingsForm / error",
                    description="Ping failed — used as an error-state silhouette.",
                ),
            ]

    def template_data(self, kwargs, slots):
        busy = kwargs.status == "testing"
        can_submit = bool(kwargs.server_url and kwargs.api_token)
        return {
            "action_url": kwargs.action_url,
            "server_url": kwargs.server_url,
            "api_token": kwargs.api_token,
            "status": kwargs.status,
            "error_message": kwargs.error_message,
            "csrf_token": kwargs.csrf_token,
            "submit_disabled": busy or not can_submit,
            "submit_label": "확인 중..." if busy else "Save & Test Connection",
            "form_attrs": (
                {
                    "hx-post": kwargs.action_url,
                    "hx-target": "closest .panel",
                    "hx-swap": "outerHTML",
                }
                if kwargs.action_url
                else {}
            ),
        }
