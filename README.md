# marginal-app

Self-hosted web highlighter monorepo (extension + sync + server)

## Apps

- [`apps/api`](apps/api) — Django API (uv + Ruff + Pyrefly + pytest) plus a `django-components` gallery at `/`

GitHub Actions runs Ruff, Pyrefly, and pytest on the API for every push and pull request. A `v*` tag also zips the development Chrome extension and attaches it to the GitHub release.
