from ui.preview import Preview

PREVIEWS = [
    Preview(
        slug="label-default",
        title="Label / default",
        description="Cursor settings caption — kicker, title, and supporting hint.",
        component="label",
        group="Primitives",
        kwargs={
            "kicker": "Connection",
            "text": "Server URL",
            "hint": "Host the extension uses to sync highlights.",
        },
    ),
]
