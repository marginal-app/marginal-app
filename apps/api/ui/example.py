from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Example:
    slug: str
    title: str
    description: str
    component: str
    group: str
    kwargs: dict[str, Any] = field(default_factory=dict)
