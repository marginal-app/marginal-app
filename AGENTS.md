# Agent principles

This file is the agent gate. `CLAUDE.md` is a symlink to it. Human contributors start at [CONTRIBUTING.md](CONTRIBUTING.md).

Add each new principle as its own `##` section below. Do not fold a new rule into an existing section because it is "also about UI" or "also about review".

## UI that paints pixels

The review contract for both surfaces — the server-side rendered fullstack app in `apps/api` and the browser extension in `apps/browser-extension` — lives in [CONTRIBUTING.md](CONTRIBUTING.md).

Read that file before changing anything that paints pixels. It covers style tokens, named-state factories, construction tests, the `/dev/components/<slug>/` silhouette harness, and how the extension's three composition roots relate to the SSR review surface.

Do not restate those rules here. When they change, change CONTRIBUTING.md.
