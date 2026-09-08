from ui.example import Example

EXAMPLES = [
    Example(
        slug="textarea-empty",
        title="Textarea / empty",
        description="Comment field before a note is typed.",
        component="textarea",
        group="Primitives",
        kwargs={"placeholder": "코멘트 추가..."},
    ),
    Example(
        slug="textarea-filled",
        title="Textarea / filled",
        description="Draft comment ready to save.",
        component="textarea",
        group="Primitives",
        kwargs={"value": "Draft note from a Cloud Agent"},
    ),
]
