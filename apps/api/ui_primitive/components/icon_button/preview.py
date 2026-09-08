from citry_preview.preview import Preview

DEFAULT = {
    "label": "설정 열기",
    "icon": "⚙",
}

PREVIEWS = [
    Preview(
        slug="icon-button-default",
        title="IconButton / default",
        description="32px hit target — settings gear on an elevated chip.",
        component="icon_button",
        group="Primitives",
        kwargs=DEFAULT,
    ),
    Preview(
        slug="icon-button-hover",
        title="IconButton / hover",
        description="Hover: hairline border and primary icon color.",
        component="icon_button",
        group="Primitives",
        kwargs={**DEFAULT, "state": "hover"},
    ),
    Preview(
        slug="icon-button-focus",
        title="IconButton / focus",
        description="Focus-visible: accent ring with offset.",
        component="icon_button",
        group="Primitives",
        kwargs={**DEFAULT, "state": "focus"},
    ),
]
