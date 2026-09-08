from citry_preview.preview import Preview

QUOTE_ONLY = {
    "highlight_id": "preview-quote",
    "quote": "Server-rendered HTML is a complete first paint.",
    "color": "#f5d76e",
    "comment": "",
    "editing": False,
    "comment_edit_url": "",
    "comment_save_url": "",
}

WITH_COMMENT = {
    **QUOTE_ONLY,
    "highlight_id": "preview-comment",
    "quote": "Cloud Agents can screenshot a component URL.",
    "color": "#8b8bff",
    "comment": "This is the silhouette we review before merge.",
}

EDITING = {
    **QUOTE_ONLY,
    "highlight_id": "preview-editing",
    "quote": "HTMX swaps this same component, not a second client tree.",
    "color": "#57cf85",
    "comment": "Draft note from a Cloud Agent",
    "editing": True,
}

PREVIEWS = [
    Preview(
        slug="highlight-card-quote",
        title="HighlightCard / quote only",
        description="Card with a color accent and the add-comment placeholder.",
        component="highlight_card",
        group="Atoms",
        kwargs=QUOTE_ONLY,
    ),
    Preview(
        slug="highlight-card-comment",
        title="HighlightCard / with comment",
        description="Saved annotation under the quote.",
        component="highlight_card",
        group="Atoms",
        kwargs=WITH_COMMENT,
    ),
    Preview(
        slug="highlight-card-editing",
        title="HighlightCard / editing",
        description="HTMX target state: textarea + save. Same component, different kwargs.",
        component="highlight_card",
        group="Atoms",
        kwargs=EDITING,
    ),
]
