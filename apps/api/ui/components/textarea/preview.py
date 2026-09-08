from ui.preview import Preview

PREVIEWS = [
    Preview(
        slug="textarea-empty",
        title="Textarea / empty",
        description="Empty comment field with a focus ring — ready to type.",
        component="textarea",
        group="Primitives",
        kwargs={"placeholder": "코멘트 추가...", "focused": True},
    ),
    Preview(
        slug="textarea-filled",
        title="Textarea / filled",
        description="Draft comment ready to save.",
        component="textarea",
        group="Primitives",
        kwargs={"value": "Draft note from a Cloud Agent"},
    ),
]
