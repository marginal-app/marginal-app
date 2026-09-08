# Contributing

This file is the repo gate. `AGENTS.md` and `CLAUDE.md` are symlinks to it.

A reviewer approves a UI PR from the diff plus a silhouette PNG — they do not run the app. Screenshots are a review contract, not a demo. Commands, attach flags, and the harness live in [Reviewing UI from a silhouette](#reviewing-ui-from-a-silhouette).

## Style belongs to the design system

Appearance still belongs to the tokens in `apps/api/static/ui/app.css` and the colocated `*.css` next to each `django-components` component. A feature that paints pixels consumes those tokens. It does not invent a second palette, a second type ramp, or a one-off panel chrome.

This section is the style rule. [UI that paints pixels](#ui-that-paints-pixels) is the structure-and-review rule. Neither replaces the other.

## UI that paints pixels

A feature that paints pixels splits the values on screen from the commands that change them. The public `django-components` component receives kwargs. The Django view — or that component's nested `View` — is the only composition root that knows the request, the ORM, session cookies, or the live API. A component test is another composition root: it injects a named state. Do not add a BaseScreen framework, a generic view-model, or a second URL tree for tests.

`get_template_data` maps kwargs onto template context. It does not query `Highlight`, read cookies, or call an HTTP client. HTMX attributes may appear in the template; the swap target is the same registered component, not a second client tree.

The named-state catalog is `apps/api/ui/examples.py`. The gallery at `/` and the raw silhouette at `/dev/components/<slug>/` render those examples. That catalog is the screenshot surface. It is not Storybook.

UI PRs ship:

- Named-state factories next to the feature — idle, empty, populated, error, and one distinctive in-progress, or whichever of those the surface can actually show. Do not invent a state the UI cannot reach. Today those factories are the `Example` rows and shared kwargs (`QUOTE_ONLY`, `WITH_COMMENT`, `EDITING`) in `apps/api/ui/examples.py`.
- A test that constructs the public component with that state via `registry.get(...).render(kwargs=...)` or `Component.render(...)`. It does not boot `runserver`, the browser extension, Vite, or a live HTTP server.
- A silhouette PNG that is `f(named state)`, attached to the pull request body. A gitignored file on the author's disk is not the review contract — reviewers never open the worktree.

Prefer one `--attach` per named-state PNG, with the state in the fragment:

```bash
gh pr create --attach './apps/api/.silhouettes/panel-empty.png#empty'
```

GitHub CLI 2.99 and later rewrites a Markdown image only when the path in the body matches the `--attach` path character for character, including `./`. `![empty](panel-empty.png)` will not rewrite against `--attach './apps/api/.silhouettes/panel-empty.png'`.

Label-only differences are text assertions, not extra goldens.

### Do

- Keep the ORM, session cookies, and the API client out of the presentational component.
- Feed the construction test and the PNG from the same factory (`Example.kwargs` or the named dict it wraps).
- Attach stills. An MP4 is welcome only when the slice's point is motion (an HTMX swap), and never instead of stills.

### Don't

- Query or fetch inside `get_template_data` "because the test can mock it".
- Snapshot every theme × tab × empty × error combination. Name the states that change the silhouette.
- Commit golden PNGs. They rot, they bloat the clone, and they are not what a reviewer sees.
- Treat "I ran it locally" as evidence. The reviewer did not.
- Add Storybook, a visual-regression service, or a screenshot comparison gate for this. The PNG is attached to the PR; it is not a CI oracle. The gallery at `/` is a named-state catalog, not a visual-regression tool.

## Reviewing UI from a silhouette

The harness is already in the tree. Do not add another.

| Surface | What it is |
| --- | --- |
| `apps/api/ui/examples.py` | Named states. One `Example` per silhouette the UI can actually show. |
| `/` | Gallery. Every example, 360px panel, fixture kwargs only. |
| `/dev/components/<slug>/` | Raw silhouette. This is the screenshot target. |
| `apps/api/.silhouettes/` | Author-local PNGs. Gitignored. Attach them; do not commit them. |
| `uv run python manage.py test ui` | Construction tests. `Component.render()` / gallery URL smoke. No Chrome. |

Name files from the example slug and the state that changes the silhouette:

```text
apps/api/.silhouettes/panel-empty.png
apps/api/.silhouettes/panel-highlights.png
apps/api/.silhouettes/settings-error.png
apps/api/.silhouettes/highlight-card-editing.png
```

Capture the raw URL, not the gallery grid:

```bash
cd apps/api
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Open `http://127.0.0.1:8000/dev/components/panel-empty/` and save a PNG of the 360px `.silhouette` panel. Repeat for every named state the PR changes. Then attach:

```bash
gh pr create \
  --attach './apps/api/.silhouettes/panel-empty.png#empty' \
  --attach './apps/api/.silhouettes/panel-highlights.png#populated' \
  --attach './apps/api/.silhouettes/settings-error.png#error'
```

Put matching image tags in the PR body, paths identical to `--attach` (including `./`):

```markdown
![empty](./apps/api/.silhouettes/panel-empty.png)
![populated](./apps/api/.silhouettes/panel-highlights.png)
![error](./apps/api/.silhouettes/settings-error.png)
```

`/library/` is the live HTMX composition of the same components. Use it to prove a swap. Do not substitute a library walkthrough for the stills. When the slice's point is motion, attach stills of the before and after named states; an MP4 may accompany them.
