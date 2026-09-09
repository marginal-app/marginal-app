# Contributing

This file is the repo gate. `AGENTS.md` and `CLAUDE.md` are symlinks to it.

Add each new principle as its own `##` section below. The silhouette check is one principle. It is not the whole file. Do not fold a new rule into an existing section because it is "also about UI" or "also about review".

## UI that paints pixels

This monorepo has two surfaces that paint pixels. They are not the same app and they are not reviewed the same way.

| Surface | Tree | What it is |
| --- | --- | --- |
| Browser extension | `apps/browser-extension` | Content script paints the page. Background owns IndexedDB and messages. Side panel is the live React client. |
| Server-side rendered fullstack | `apps/api` | Sync API plus `django-components` + HTMX. This is the silhouette review surface for panel pixels. |

A reviewer approves a UI PR from the diff plus a silhouette PNG — they do not run the app, and they do not load an unpacked extension. Screenshots are a review contract, not a demo. Commands, attach flags, and the SSR harness live in [Reviewing UI from a silhouette](#reviewing-ui-from-a-silhouette).

### Style belongs to the design system

Appearance still belongs to the shared tokens (`--bg`, `--accent`, `--radius`, type). Today they live in `apps/api/static/ui/app.css` and `apps/browser-extension/entrypoints/sidepanel/style.css`. A feature that paints pixels consumes those tokens. It does not invent a second palette, a second type ramp, or a one-off panel chrome.

The two copies must not drift. A token change lands in both files, or it is not a token change. Colocated CSS next to a `django-components` component, or in the extension's `App.css`, is for layout that only that surface owns.

This subsection is the style rule. The rest of this principle is the structure-and-review rule. Neither replaces the other.

### Composition

A feature that paints pixels splits the values on screen from the commands that change them. The public view receives props (or kwargs). A composition root is the only place that knows IndexedDB, `browser.*`, `fetch`, session cookies, or the live API. A component test is another composition root: it injects a named state. Do not add a BaseScreen framework, a generic view-model, or a second router for tests.

UI PRs that change what a reviewer can see ship:

- Named-state factories next to the feature — idle, empty, populated, error, and one distinctive in-progress, or whichever of those the surface can actually show. Do not invent a state the UI cannot reach.
- A test that constructs the public view with that state. It does not boot Vite, WXT, `runserver`, Chrome, or the API.
- A silhouette PNG that is `f(named state)`, attached to the pull request body. A gitignored file on the author's disk is not the review contract — reviewers never open the worktree.

Prefer one `--attach` per named-state PNG, with the state in the fragment:

```bash
gh pr create --attach './apps/api/.silhouettes/panel-empty.png#empty'
```

GitHub CLI 2.99 and later rewrites a Markdown image only when the path in the body matches the `--attach` path character for character, including `./`. `![empty](panel-empty.png)` will not rewrite against `--attach './apps/api/.silhouettes/panel-empty.png'`.

Label-only differences are text assertions, not extra goldens.

Do:

- Keep live fetch, session cookies, IndexedDB, and the API client out of the presentational view.
- Feed the construction test and the PNG from the same factory.
- Attach stills. An MP4 is welcome only when the slice's point is motion, and never instead of stills.

Don't:

- Fetch inside the presentational view "because the test can mock it".
- Snapshot every theme × tab × empty × error combination. Name the states that change the silhouette.
- Commit golden PNGs. They rot, they bloat the clone, and they are not what a reviewer sees.
- Treat "I ran it locally" or "I loaded the unpacked extension" as evidence. The reviewer did not.
- Add Storybook, a visual-regression service, or a screenshot comparison gate for this. The PNG is attached to the PR; it is not a CI oracle.

How that split is wired depends on the surface.

### Server-side rendered fullstack

`apps/api` is a Django app that paints the library panel with `django-components` and swaps the same registered components over HTMX. It is a fullstack app, not a JSON-only API with a gallery bolted on. The gallery exists so a reviewer can see named states without a session, an extension, or a React tree.

The public component receives kwargs. The Django view — or that component's nested `View` — is the only composition root that knows the request, the ORM, session cookies, or the live API.

`get_template_data` maps kwargs onto template context. It does not query `Highlight`, read cookies, or call an HTTP client. HTMX attributes may appear in the template; the swap target is the same registered component, not a second client tree.

The named-state catalog is `apps/api/citry_preview/previews.py`. The gallery at `/citry/preview/` and the raw silhouette at `/citry/preview/<slug>/` render those previews. That catalog is the screenshot surface. It is not Storybook.

Today the factories are the `Preview` rows and shared kwargs (`QUOTE_ONLY`, `WITH_COMMENT`, `EDITING`) in `apps/api/citry_preview/previews.py`. A construction test calls `registry.get(...).render(kwargs=...)` or `Component.render(...)`.

A change to panel pixels lands here first. The extension side panel is a live client of the same look, not a second source of truth for silhouettes.

### Browser extension

`apps/browser-extension` is a WXT + React extension. It has three composition roots, and none of them is a silhouette URL.

| Root | Owns | Test |
| --- | --- | --- |
| Content script | Selecting text, painting `<mark>`, restoring highlights onto a page | jsdom + `resolveAndPaint`. No Chrome. |
| Background | IndexedDB and `browser.runtime` messages | `fake-indexeddb` + the exported store helpers. No Chrome. |
| Side panel | The live React client: `browser.tabs`, `browser.runtime`, `browser.storage`, `fetch` to the API | Not a visual review surface. |

Page paint is not a panel silhouette. A content-script change ships DOM assertions (`flattenText`, `resolveAndPaint`). A background change ships store assertions. Do not attach a library-panel PNG for either.

The side panel is allowed to be a live client. It is not allowed to be a second design system. Panel chrome that changes what a reviewer can see is reviewed through the matching [server-side rendered fullstack](#server-side-rendered-fullstack) named state — update `apps/api/citry_preview/previews.py` and the `django-components` twin, then attach that PNG. Two looks is a bug.

Do not add Storybook, a component gallery, or a `/citry/preview` route to the extension to get a screenshot. The SSR harness already exists. Do not boot WXT or load an unpacked build to prove appearance.

### Reviewing UI from a silhouette

The harness lives in `apps/api`. Do not add another, and do not point it at the extension.

| Surface | What it is |
| --- | --- |
| `apps/api/citry_preview/previews.py` | Named states. One `Preview` per silhouette the panel can actually show. |
| `/citry/preview/` | Gallery. Every preview, 360px panel, fixture kwargs only. |
| `/citry/preview/<slug>/` | Raw silhouette. This is the screenshot target. |
| `apps/api/.silhouettes/` | Author-local PNGs. Gitignored. Attach them; do not commit them. |
| `uv run python manage.py test citry_preview ui_primitive highlights` | Construction tests. `Component.render()` / gallery URL smoke. No Chrome. |
| `pnpm --filter @marginal-app/browser-extension test` | Extension construction tests. jsdom / fake-indexeddb. No Chrome. |

Name files from the preview slug and the state that changes the silhouette:

```text
apps/api/.silhouettes/panel-empty.png
apps/api/.silhouettes/panel-highlights.png
apps/api/.silhouettes/settings-error.png
apps/api/.silhouettes/highlight-card-editing.png
```

Capture the raw URL, not the gallery grid, and not the extension side panel:

```bash
cd apps/api
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Open `http://127.0.0.1:8000/citry/preview/panel-empty/` and save a PNG of the 360px `.silhouette` panel. Repeat for every named state the PR changes. Then attach:

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

`/library/` is the live HTMX composition of the same components. Use it to prove a swap. Do not substitute a library walkthrough — or an unpacked extension — for the stills. When the slice's point is motion, attach stills of the before and after named states; an MP4 may accompany them.

## Design system primitives

The design system is `django-components`, not a React package. Tokens stay in `apps/api/static/ui/app.css` and `apps/browser-extension/entrypoints/sidepanel/style.css` (see [Style belongs to the design system](#style-belongs-to-the-design-system)). A primitive is a new registered component. Feature components (`highlight_card`, `settings_form`, `library_panel`, …) stay as they are until a later compose pass.

v1 primitives — one pull request each:

| Primitive | Named states | Today's class |
| --- | --- | --- |
| `button` | default, small, disabled | `.primary-button` |
| `input` | empty, filled | settings / comment fields |
| `textarea` | empty, filled | comment edit |
| `label` | default | `.field-label` |
| `field` | default | `.field` |
| `card` | default | bordered panel chrome |
| `icon_button` | default | `.icon-button` |
| `status` | ok, error | `.status` |
| `tray` | closed, open | slide-in panel (`translateX`) |

A primitive PR:

- Adds only `apps/api/ui_primitive/components/<name>/` — the component, `preview.py`, and construction tests. `config/citry_app.py` builds its `dirs=` by walking `INSTALLED_APPS` and picking up each app's own `components/` folder, so a component's real home is whichever app owns that domain (a `highlights` component lives in `apps/api/highlights/components/<name>/`, not here) — `ui_primitive/components/` is just where anything without a more specific owning app lands, primitives included.
- Registers named states as `PREVIEWS` in that folder. `citry_preview/previews.py` discovers those files; do not append rows to the feature catalog.
- Reuses the current tokens. It does not invent a second palette, and it does not restyle an existing feature component.
- Attaches a silhouette PNG per named state that changes the picture. Capture the raw URL with `uv run python scripts/capture_silhouette.py <slug>` while `runserver` is up. Playwright clips `.silhouette`. Do not commit goldens. Cloud Agents attach per [Cursor Cloud Agent silhouette attach](#cursor-cloud-agent-silhouette-attach).

Do not add shadcn, Tailwind, or a `packages/ui` React tree for this.

## Cursor Cloud Agent silhouette attach

`gh pr create --attach` is the human attach path. It is not the Cursor Cloud Agent path.

A Cloud Agent must not put `![empty](./apps/api/.silhouettes/panel-empty.png)` (or `/workspace/apps/api/.silhouettes/…`) in the pull request body unless GitHub has already rewritten that path to a `user-attachments` URL. Those files are gitignored. GitHub then tries to thumbnail a path that is not in the repo and shows "Couldn't open thumbnail image."

A Cloud Agent attaches the same runtime PNG this way:

- Capture the raw silhouette URL at review time with `uv run python scripts/capture_silhouette.py <slug>` (Playwright clips `.silhouette`). Do not commit the PNG.
- Create or update the PR with the Cursor PR tool. Embed each still as an HTML `<img>` whose `src` is the absolute file path on the agent machine (for example `/workspace/apps/api/.silhouettes/panel-empty.png`). The tool uploads the file and rewrites the tag to a Cursor artifact URL.
- Do not also leave the gitignored relative markdown path in the body. GitHub will try to thumbnail it and fail.
- Do not use `gh pr create` / `gh pr edit --attach` from a Cloud Agent. The agent token cannot upload GitHub user-attachments (`unsupported authentication type`).

A human opening a PR from their laptop still uses `--attach` as in [Reviewing UI from a silhouette](#reviewing-ui-from-a-silhouette). The review contract is unchanged: the PNG is attached to the PR, not committed, and not a CI oracle.

## Desk silhouettes

The 360px `.silhouette` frame is the extension panel. Catalog list and the highlight tray live on a second frame.

`Preview.group == "Desk"` renders `.silhouette-desk` (~1024px). `capture.py` clips that node and uses a wider viewport. `"Primitives"` stays on the padded 360px `.silhouette-atom`. The gallery is still one URL. Do not add a second harness on the extension.

This is its own principle. Do not fold it into [UI that paints pixels](#ui-that-paints-pixels).

## Ruff before a commit

CI runs `uv run ruff check .` and `uv run ruff format --check .` in `apps/api`. A commit that touches that tree runs the same two commands first. Do not wait for the GitHub job.

The hook is `.githooks/pre-commit`. Install it on a clone with `scripts/install-git-hooks`. That only writes `.git/hooks/pre-commit`. It does not change git config.

`--no-verify` is not a pass.

This is its own principle. Do not fold it into [Desk silhouettes](#desk-silhouettes).
