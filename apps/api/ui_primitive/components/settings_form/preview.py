from citry_preview.preview import Preview

PREVIEWS = [
    Preview(
        slug="settings-idle",
        title="SettingsForm / idle",
        description="Connection form before a test.",
        component="settings_form",
        group="Atoms",
        kwargs={
            "server_url": "http://127.0.0.1:8000",
            "api_token": "dev-token",
            "status": "idle",
        },
    ),
    Preview(
        slug="settings-ok",
        title="SettingsForm / success",
        description="Ping succeeded.",
        component="settings_form",
        group="Atoms",
        kwargs={
            "server_url": "http://127.0.0.1:8000",
            "api_token": "dev-token",
            "status": "ok",
        },
    ),
    Preview(
        slug="settings-error",
        title="SettingsForm / error",
        description="Ping failed — used as an error-state silhouette.",
        component="settings_form",
        group="Atoms",
        kwargs={
            "server_url": "http://127.0.0.1:8000",
            "api_token": "wrong-token",
            "status": "error",
            "error_message": "서버가 401로 응답했습니다",
        },
    ),
]
