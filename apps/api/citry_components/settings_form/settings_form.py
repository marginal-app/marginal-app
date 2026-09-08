from config.citry_app import app
from citry import Component


class SettingsForm(Component):
    citry = app
    name = "settings_form"
    template_file = "settings_form.citry-html"
    css_file = "settings_form.css"

    class Kwargs:
        action_url: str = ""
        server_url: str = ""
        api_token: str = ""
        status: str = "idle"
        error_message: str = ""
        csrf_token: str = ""

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
