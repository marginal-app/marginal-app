from importlib import import_module
from pathlib import Path

from ui.preview import Preview

COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "citry_components"


def discover_previews() -> list[Preview]:
    """Load PREVIEWS from each `citry_components/<name>/preview.py`."""
    found: list[Preview] = []
    if not COMPONENTS_DIR.is_dir():
        return found
    for child in sorted(COMPONENTS_DIR.iterdir()):
        if not (child / "preview.py").is_file():
            continue
        module = import_module(f"citry_components.{child.name}.preview")
        found.extend(getattr(module, "PREVIEWS", ()))
    return found


def merge_previews(*groups: list[Preview]) -> list[Preview]:
    merged: list[Preview] = []
    slugs: set[str] = set()
    for group in groups:
        for preview in group:
            if preview.slug in slugs:
                raise ValueError(f"Duplicate preview slug: {preview.slug}")
            slugs.add(preview.slug)
            merged.append(preview)
    return merged
