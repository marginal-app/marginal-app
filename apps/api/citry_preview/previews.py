from citry_preview.discover import discover_previews
from citry_preview.preview import Preview

__all__ = [
    "PREVIEWS",
    "Preview",
    "preview_by_slug",
]

PREVIEWS: list[Preview] = discover_previews()


def preview_by_slug(slug: str) -> Preview:
    for preview in PREVIEWS:
        if preview.slug == slug:
            return preview
    raise KeyError(slug)
