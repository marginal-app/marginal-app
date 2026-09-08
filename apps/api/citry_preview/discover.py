from typing import cast

from citry_preview.preview import Preview
from citry_preview.variants import PreviewableComponent, merge_previews, previews_from_variants
from config.citry_app import app


def discover_previews() -> list[Preview]:
    """Build PREVIEWS from every registered component's own `PreviewVariant`.

    No filesystem walk and no per-component preview.py: `app.components`
    already triggers Citry's own autodiscovery and returns every registered
    component class directly, so a component with no `PreviewVariant`
    (nothing to preview yet) is just skipped.
    """
    groups: list[list[Preview]] = []
    seen: set[int] = set()
    for component_cls in app.components.values():
        if id(component_cls) in seen:
            continue
        seen.add(id(component_cls))
        if getattr(component_cls, "PreviewVariant", None) is None:
            continue
        # The getattr check just confirmed PreviewVariant exists at runtime;
        # Component itself doesn't declare it, so this cast states what was
        # actually verified rather than leaving the call as `type[Component]`.
        groups.append(previews_from_variants(cast(type[PreviewableComponent], component_cls)))
    return merge_previews(*groups)
