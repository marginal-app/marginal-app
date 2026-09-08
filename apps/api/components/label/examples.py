from ui.example import Example

EXAMPLES = [
    Example(
        slug="label-default",
        title="Label / default",
        description="Field caption with supporting hint — Cursor settings hierarchy.",
        component="label",
        group="Primitives",
        kwargs={
            "text": "Server URL",
            "hint": "Host the extension uses to sync highlights.",
        },
    ),
]
