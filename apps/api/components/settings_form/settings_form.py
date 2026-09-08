from django_components import Component, register


@register("settings_form")
class SettingsForm(Component):
    template_file = "settings_form.html"
    css_file = "settings_form.css"

    class Kwargs:
        action_url: str = ""
        server_url: str = ""
        api_token: str = ""
        status: str = "idle"
        error_message: str = ""

    def get_template_data(self, args, kwargs: Kwargs, slots, context):
        return {
            "action_url": kwargs.action_url,
            "server_url": kwargs.server_url,
            "api_token": kwargs.api_token,
            "status": kwargs.status,
            "error_message": kwargs.error_message,
            "busy": kwargs.status == "testing",
            "can_submit": bool(kwargs.server_url and kwargs.api_token),
        }
