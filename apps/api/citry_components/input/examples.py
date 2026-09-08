from ui.example import Example

EXAMPLES = [
    Example(
        slug="input-empty",
        title="Input / empty",
        description="Empty field — muted placeholder, no value.",
        component="input",
        group="Primitives",
        kwargs={"placeholder": "https://my-server.example.com"},
    ),
    Example(
        slug="input-filled",
        title="Input / filled",
        description="Filled field — primary-weight value, readable against the placeholder.",
        component="input",
        group="Primitives",
        kwargs={
            "name": "server_url",
            "value": "http://127.0.0.1:8000",
        },
    ),
]
