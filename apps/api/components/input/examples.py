from ui.example import Example

EXAMPLES = [
    Example(
        slug="input-empty",
        title="Input / empty",
        description="Settings field before a value is entered.",
        component="input",
        group="Primitives",
        kwargs={"placeholder": "https://my-server.example.com"},
    ),
    Example(
        slug="input-filled",
        title="Input / filled",
        description="Server URL with a saved value.",
        component="input",
        group="Primitives",
        kwargs={
            "name": "server_url",
            "value": "http://127.0.0.1:8000",
        },
    ),
]
