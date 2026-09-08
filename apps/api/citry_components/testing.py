"""Test-only helper: render a component and strip its inlined <style> block."""

import re
from typing import Any

from citry_components.rendering import render_component as _render_component

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
    `citry_components.rendering.render_component`, which keeps the styles.
    """
    html = _render_component(name, kwargs, slots)
    return _STYLE_BLOCK.sub("", html)
