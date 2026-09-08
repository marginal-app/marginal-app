"""The Citry app instance for this Django project.

Autodiscovery walks each installed app's own `components/` directory —
`django.apps.apps.get_app_configs()` lists every app in INSTALLED_APPS, so a
component's home is whichever app owns that domain (`highlights/components/`,
`ui/components/`, ...). A new app only needs to add a `components/` folder to
participate; there is no dirs list to maintain by hand.
"""

from pathlib import Path

from citry import Citry
from citry_django import CitryDjangoExtension
from django.apps import apps as django_apps


def component_dirs() -> list[Path]:
    """Every installed app's own `components/` directory, if it has one."""
    dirs = []
    for app_config in django_apps.get_app_configs():
        candidate = Path(app_config.path) / "components"
        if candidate.is_dir():
            dirs.append(candidate)
    return dirs


app = Citry(
    dirs=component_dirs(),
    extensions=[CitryDjangoExtension()],
)
