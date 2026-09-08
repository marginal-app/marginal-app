from ui.example import Example

EXAMPLES = [
    Example(
        slug="button-default",
        title="Button / default",
        description="Primary action, default size.",
        component="button",
        group="Primitives",
        kwargs={"label": "Save & Test Connection"},
    ),
    Example(
        slug="button-small",
        title="Button / small",
        description="Compact primary used on highlight cards.",
        component="button",
        group="Primitives",
        kwargs={"label": "저장", "size": "small"},
    ),
    Example(
        slug="button-disabled",
        title="Button / disabled",
        description="Primary action while a test is in flight.",
        component="button",
        group="Primitives",
        kwargs={"label": "확인 중...", "disabled": True},
    ),
]
