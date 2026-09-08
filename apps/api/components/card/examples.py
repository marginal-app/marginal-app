from ui.example import Example

EXAMPLES = [
    Example(
        slug="card-default",
        title="Card / default",
        description="Cursor-style panel chrome — subtle border, soft elevation, padding.",
        component="card",
        group="Primitives",
        kwargs={
            "body": "Server-rendered HTML is a complete first paint.",
        },
    ),
]
