# api

Django API for the marginal-app highlighter monorepo.

This package is managed with [uv](https://docs.astral.sh/uv/) and type-checked with [Pyrefly](https://pyrefly.org/). `django-stubs` is a dev dependency so Pyrefly can resolve Django imports. Open this directory (`apps/api`) as the editor workspace so Helix and Zed pick up the project-local language server configs.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

This creates `.venv`, installs Django and the Pyrefly language server from `uv.lock`, and uses the Python version pinned in `.python-version`.

## Common commands

```bash
uv run python manage.py check
uv run python manage.py migrate
uv run python manage.py runserver
uv run python manage.py test
uv run pyrefly check
```

## UI examples

`django-components` lives in `components/`. Isolated silhouettes (the Cloud Agent review surface) are at:

- http://127.0.0.1:8000/ — gallery of every example
- http://127.0.0.1:8000/dev/components/<slug>/ — one component on a 360px panel
- http://127.0.0.1:8000/library/ — HTMX composition of the same components

Click **raw** on a gallery card to open the screenshot URL for that silhouette.

## Editors

- Helix: `.helix/languages.toml` registers Pyrefly as the Python language server.
- Zed: `.zed/settings.json` enables Pyrefly and disables basedpyright, Pyright, and pylsp.

Install the Pyrefly extension in Zed, then open `apps/api` as the project root.
