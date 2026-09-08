from citry_preview.preview import Preview
from citry_preview.variants import merge_previews, previews_from_variants
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
        groups.append(previews_from_variants(component_cls))
    return merge_previews(*groups)
