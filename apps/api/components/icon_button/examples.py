from ui.example import Example

DEFAULT = {
    "label": "설정 열기",
    "icon": "⚙",
}

EXAMPLES = [
    Example(
        slug="icon-button-default",
        title="IconButton / default",
        description="Default icon button — settings gear glyph.",
        component="icon_button",
        group="Primitives",
        kwargs=DEFAULT,
    ),
]
