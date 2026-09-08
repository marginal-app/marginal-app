from ui.example import Example

EXAMPLES = [
    Example(
        slug="field-default",
        title="Field / default",
        description="Settings Server URL field with a saved value.",
        component="field",
        group="Primitives",
        kwargs={
            "label": "Server URL",
            "value": "http://127.0.0.1:8000",
            "placeholder": "https://my-server.example.com",
        },
    ),
]
