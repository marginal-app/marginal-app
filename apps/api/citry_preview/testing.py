"""Test-only helpers: render a component and look up one of its previews."""

import re
from typing import Any

from citry_preview.preview import Preview
from citry_preview.rendering import render_component as _render_component
from citry_preview.variants import previews_from_variants

_STYLE_BLOCK = re.compile(r"<style\b[^>]*>.*?</style>", re.DOTALL)


def render_component(
    name: str,
    kwargs: dict[str, Any] | None = None,
    slots: dict[str, Any] | None = None,
) -> str:
    """Render a component and strip its inlined <style> block.

    Citry inlines each rendered instance's full CSS file, so a variant's HTML
    always carries every other variant's selectors too (e.g. rendering
    "status-ok" still contains the `.status-error { ... }` rule in its
    stylesheet). Assertions almost always care about the markup, not the
    stylesheet text, so this is stripped here rather than in every test.

    Test-only: production code must render through
    `citry_preview.rendering.render_component`, which keeps the styles.
    """
    html = _render_component(name, kwargs, slots)
    return _STYLE_BLOCK.sub("", html)


def preview_by_slug(component_cls: type, slug: str) -> Preview:
    """Look up one of a component's own previews by slug.

    Runs the same `previews_from_variants()` the gallery uses, so
    `example.kwargs` is already the plain dict `render_component` needs —
    tests exercise the real slug-resolution and Kwargs-to-dict conversion,
    not a parallel copy of it.
    """
    return next(p for p in previews_from_variants(component_cls) if p.slug == slug)
