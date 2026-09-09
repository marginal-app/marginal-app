"""The Citry app instance for this Django project.

Autodiscovery walks each installed app's own component directory —
`django.apps.apps.get_app_configs()` lists every app in INSTALLED_APPS, so a
component's home is whichever app owns that domain (`highlights/components/`,
`ui_primitive/components/`, ...). A new app only needs to add that directory
to participate; there is no dirs list to maintain by hand.
"""

from pathlib import Path

from citry import Citry
from citry_django import CitryDjangoExtension
from django.apps import apps as django_apps

DEFAULT_COMPONENTS_DIR = "components"


def component_dirs() -> list[Path]:
    """Every installed app's own component directory, if it has one.

    Defaults to `<app>/components/`. An app that wants a different directory
    name sets `citry_components_dir = "..."` on its own AppConfig (in its
    `apps.py`) instead of being stuck with the literal name "components" —
    the scoping (only that one directory, not the whole app) is what avoids
    Citry autodiscovery importing unrelated files like models.py or views.py;
    the name itself is just this project's own convention, not something
    Citry requires.
    """
    dirs = []
    for app_config in django_apps.get_app_configs():
        dir_name = getattr(app_config, "citry_components_dir", DEFAULT_COMPONENTS_DIR)
        candidate = Path(app_config.path) / dir_name
        if candidate.is_dir():
            dirs.append(candidate)
    return dirs


app = Citry(
    dirs=component_dirs(),
    extensions=[CitryDjangoExtension()],
)
