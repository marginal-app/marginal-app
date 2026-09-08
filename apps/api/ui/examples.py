from ui.discover import discover_examples, merge_examples
from ui.example import Example
from ui.fixtures import EDITING, HIGHLIGHTS, QUOTE_ONLY, WITH_COMMENT

__all__ = [
    "EDITING",
    "EXAMPLES",
    "FEATURE_EXAMPLES",
    "HIGHLIGHTS",
    "QUOTE_ONLY",
    "WITH_COMMENT",
    "Example",
    "example_by_slug",
]

FEATURE_EXAMPLES: list[Example] = [
    Example(
        slug="empty-state",
        title="EmptyState",
        description="Default empty library — no highlights on the page.",
        component="empty_state",
        group="Atoms",
    ),
    Example(
        slug="highlight-card-quote",
        title="HighlightCard / quote only",
        description="Card with a color accent and the add-comment placeholder.",
        component="highlight_card",
        group="Atoms",
        kwargs=QUOTE_ONLY,
    ),
    Example(
        slug="highlight-card-comment",
        title="HighlightCard / with comment",
        description="Saved annotation under the quote.",
        component="highlight_card",
        group="Atoms",
        kwargs=WITH_COMMENT,
    ),
    Example(
        slug="highlight-card-editing",
        title="HighlightCard / editing",
        description="HTMX target state: textarea + save. Same component, different kwargs.",
        component="highlight_card",
        group="Atoms",
        kwargs=EDITING,
    ),
    Example(
        slug="highlight-list",
        title="HighlightList",
        description="Stacked cards as a fragment an HTMX swap can replace.",
        component="highlight_list",
        group="Molecules",
        kwargs={"highlights": HIGHLIGHTS},
    ),
    Example(
        slug="settings-idle",
        title="SettingsForm / idle",
        description="Connection form before a test.",
        component="settings_form",
        group="Atoms",
        kwargs={
            "server_url": "http://127.0.0.1:8000",
            "api_token": "dev-token",
            "status": "idle",
        },
    ),
    Example(
        slug="settings-ok",
        title="SettingsForm / success",
        description="Ping succeeded.",
        component="settings_form",
        group="Atoms",
        kwargs={
            "server_url": "http://127.0.0.1:8000",
            "api_token": "dev-token",
            "status": "ok",
        },
    ),
    Example(
        slug="settings-error",
        title="SettingsForm / error",
        description="Ping failed — used as an error-state silhouette.",
        component="settings_form",
        group="Atoms",
        kwargs={
            "server_url": "http://127.0.0.1:8000",
            "api_token": "wrong-token",
            "status": "error",
            "error_message": "서버가 401로 응답했습니다",
        },
    ),
    Example(
        slug="panel-empty",
        title="LibraryPanel / empty",
        description="Composed page: header + empty state. Page-level silhouette.",
        component="library_panel",
        group="Pages",
        kwargs={"view": "highlights", "highlights": []},
    ),
    Example(
        slug="panel-highlights",
        title="LibraryPanel / highlights",
        description="Composed page matching the extension side panel list.",
        component="library_panel",
        group="Pages",
        kwargs={"view": "highlights", "highlights": HIGHLIGHTS},
    ),
    Example(
        slug="panel-settings",
        title="LibraryPanel / settings",
        description="Composed settings view.",
        component="library_panel",
        group="Pages",
        kwargs={"view": "settings", "settings_status": "idle"},
    ),
]

EXAMPLES: list[Example] = merge_examples(FEATURE_EXAMPLES, discover_examples())


def example_by_slug(slug: str) -> Example:
    for example in EXAMPLES:
        if example.slug == slug:
            return example
    raise KeyError(slug)
