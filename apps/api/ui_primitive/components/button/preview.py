from citry_preview.preview import Preview

PREVIEWS = [
    Preview(
        slug="button-default",
        title="Button / default",
        description="Primary action, default size.",
        component="button",
        group="Primitives",
        kwargs={"label": "Save & Test Connection"},
    ),
    Preview(
        slug="button-small",
        title="Button / small",
        description="Compact primary used on highlight cards.",
        component="button",
        group="Primitives",
        kwargs={"label": "저장", "size": "small"},
    ),
    Preview(
        slug="button-disabled",
        title="Button / disabled",
        description="Primary action while a test is in flight.",
        component="button",
        group="Primitives",
        kwargs={"label": "확인 중...", "disabled": True},
    ),
    Preview(
        slug="button-focus",
        title="Button / focus-visible",
        description="Keyboard focus ring — 2px accent over a background offset.",
        component="button",
        group="Primitives",
        kwargs={"label": "Save & Test Connection", "focused": True},
    ),
]
