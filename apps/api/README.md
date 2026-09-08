# api

Django API for the marginal-app highlighter monorepo.

This package is managed with [uv](https://docs.astral.sh/uv/). CI runs [Ruff](https://docs.astral.sh/ruff/) (lint + format), [Pyrefly](https://pyrefly.org/) (types), and [pytest](https://docs.pytest.org/) (via pytest-django). `django-stubs` is a dev dependency so Pyrefly can resolve Django imports. Open this directory (`apps/api`) as the editor workspace so Helix and Zed pick up the project-local language server configs.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

This creates `.venv`, installs Django and the dev tools (Ruff, Pyrefly, pytest) from `uv.lock`, and uses the Python version pinned in `.python-version`.

## Common commands

```bash
uv run python manage.py check
uv run python manage.py migrate
uv run python manage.py runserver
uv run ruff check .
uv run ruff format
uv run pyrefly check
uv run pytest
```

## UI examples

`django-components` lives in `components/`. Isolated silhouettes (the Cloud Agent review surface) are at:

- http://127.0.0.1:8000/ — gallery of every example
- http://127.0.0.1:8000/dev/components/<slug>/ — one component on a 360px panel
- http://127.0.0.1:8000/library/ — HTMX composition of the same components

Click **raw** on a gallery card to open the screenshot URL for that silhouette.

Named states for a new primitive live in `components/<name>/examples.py`. The gallery catalog at `ui/examples.py` discovers those files. Feature examples stay in `ui/examples.py` until a compose pass. Tokens stay in `static/ui/app.css`.

Capture a review PNG (gitignored) by clipping the 360px `.silhouette` panel. This is the camera. CI does not compare goldens yet.

```bash
uv sync --group dev
uv run playwright install chromium
uv run python manage.py runserver
uv run python scripts/capture_silhouette.py empty-state
```

## Editors

- Helix: `.helix/languages.toml` registers Pyrefly as the Python language server.
- Zed: `.zed/settings.json` enables Pyrefly and disables basedpyright, Pyright, and pylsp.

Install the Pyrefly extension in Zed, then open `apps/api` as the project root.
