from importlib import import_module
from pathlib import Path

from ui.example import Example

COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "components"


def discover_examples() -> list[Example]:
    """Load EXAMPLES from each `components/<name>/examples.py`."""
    found: list[Example] = []
    if not COMPONENTS_DIR.is_dir():
        return found
    for child in sorted(COMPONENTS_DIR.iterdir()):
        if not (child / "examples.py").is_file():
            continue
        module = import_module(f"components.{child.name}.examples")
        found.extend(getattr(module, "EXAMPLES", ()))
    return found


def merge_examples(*groups: list[Example]) -> list[Example]:
    merged: list[Example] = []
    slugs: set[str] = set()
    for group in groups:
        for example in group:
            if example.slug in slugs:
                raise ValueError(f"Duplicate example slug: {example.slug}")
            slugs.add(example.slug)
            merged.append(example)
    return merged
