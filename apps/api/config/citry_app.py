"""The Citry app instance for this Django project.

Autodiscovery (the default) walks `dirs` and imports every component module
under it, exactly like django-components' `ComponentsSettings(dirs=...)` —
no manual per-component import list to maintain.
"""

from pathlib import Path

from citry import Citry
from citry_django import CitryDjangoExtension

BASE_DIR = Path(__file__).resolve().parent.parent

app = Citry(
    dirs=[BASE_DIR / "citry_components"],
    extensions=[CitryDjangoExtension()],
)
