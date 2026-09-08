from importlib import import_module
from pathlib import Path

from config.citry_app import component_dirs
from citry_preview.preview import Preview

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def discover_previews() -> list[Preview]:
    """Load PREVIEWS from every installed app's `components/**/preview.py`."""
    found: list[Preview] = []
    for base_dir in component_dirs():
        for path in sorted(base_dir.rglob("preview.py")):
            relative = path.relative_to(PROJECT_ROOT).with_suffix("")
            module = import_module(".".join(relative.parts))
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
