from citry_preview.preview import Preview
from highlights.components.highlight_list.preview import HIGHLIGHTS

PREVIEWS = [
    Preview(
        slug="panel-empty",
        title="LibraryPanel / empty",
        description="Composed page: header + empty state. Page-level silhouette.",
        component="library_panel",
        group="Pages",
        kwargs={"view": "highlights", "highlights": []},
    ),
    Preview(
        slug="panel-highlights",
        title="LibraryPanel / highlights",
        description="Composed page matching the extension side panel list.",
        component="library_panel",
        group="Pages",
        kwargs={"view": "highlights", "highlights": HIGHLIGHTS},
    ),
    Preview(
        slug="panel-settings",
        title="LibraryPanel / settings",
        description="Composed settings view.",
        component="library_panel",
        group="Pages",
        kwargs={"view": "settings", "settings_status": "idle"},
    ),
]
