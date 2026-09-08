"""Render a registered Citry component to an HTML string, styles included."""

from typing import Any

from config.citry_app import app


def render_component(
    name: str,
    kwargs: dict[str, Any] | None = None,
    slots: dict[str, Any] | None = None,
) -> str:
    component_cls = app.get(name)
    return str(component_cls(**(kwargs or {}), slots=slots))
