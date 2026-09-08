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

HIGHLIGHTS = [QUOTE_ONLY, WITH_COMMENT]
