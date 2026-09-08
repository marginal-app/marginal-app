from ui.example import Example

EXAMPLES = [
    Example(
        slug="card-default",
        title="Card / default",
        description="Generic bordered container with title and body.",
        component="card",
        group="Primitives",
        kwargs={
            "title": "Highlight",
            "body": "Server-rendered HTML is a complete first paint.",
        },
    ),
]
