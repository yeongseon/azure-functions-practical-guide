# Screenshot capture pipeline

Portal screenshots are treated as **build artifacts driven by a manifest**, not
hand-placed files. Docs reference a screenshot by a **stable ID**; re-capturing a
blade overwrites the same file and never requires editing markdown.

The implementation lives in the central
[`azure-guide-capture-toolkit`](https://github.com/yeongseon/azure-guide-capture-toolkit)
package (installed via `requirements-docs.txt`). This directory keeps only the
repo-specific pieces: `manifest.yaml` (the screenshot registry for this guide)
and `portal-capture-helpers.js` (in `scripts/`).

## Components

| Piece | Where | Role |
|---|---|---|
| `manifest.yaml` | this directory | Single source of truth. One entry per screenshot: stable `id`, `file`, `alt`, `captured`/`verified` dates, `diff_threshold`. |
| `screenshot_lib` | toolkit package | Shared manifest access. Reads via PyYAML (present at docs-build time); writes lazily via ruamel round-trip to preserve comments. |
| `optimize_webp` | toolkit package | Downscales a raw PNG to `meta.target_width` (1440px) and encodes WebP, then stamps `captured`. |
| `diff_gate` | toolkit package | Compares a fresh capture to the committed image. Below `diff_threshold` it leaves the image byte-identical and only bumps `verified`; above it, re-encodes and bumps `captured`. |
| `mkdocs_macros` | toolkit package | Defines the `shot()` macro consumed at build time. Wired via the mkdocs-macros `modules:` option in `mkdocs.yml`. |
| `portal-capture-helpers.js` | `scripts/` | Playwright PII text-replacement + avatar masking used during raw capture. |

## Referencing a screenshot in docs

Use the `shot()` macro with the manifest id:

```markdown
[[[ shot("01-function-app-overview-healthy") ]]]
```

This renders the correct relative path plus the manifest `alt` text. The macro
uses custom Jinja delimiters `[[[ ]]]` / `[[% %]]` / `[[# #]]` (configured in
`mkdocs.yml`) so it never collides with the `{{ }}`, `{% %}`, or `{#anchor}`
sequences already present across the docs.

## Adding a new screenshot

1. Capture the raw Portal PNG with Playwright + `portal-capture-helpers.js`
   (see `scripts/portal-capture-helpers.md`).
2. Add an entry to `manifest.yaml` (new `id` = intended file stem).
3. Encode and stamp:

    ```bash
    capture-optimize-webp /path/to/raw.png --id <shot-id>
    ```

4. Reference it in markdown with `[[[ shot("<shot-id>") ]]]`.
5. `mkdocs build --strict` to verify it renders.

## Re-capturing (drift refresh)

Feed the fresh raw PNG through the diff gate instead of the optimizer:

```bash
capture-diff-gate /path/to/fresh.png --id <shot-id>
```

- **Unchanged** (below threshold): image bytes untouched, only `verified` is
  bumped — no image churn in git.
- **Changed** (at/above threshold): image re-encoded, `captured` bumped.

## Requirements

- Docs build: `mkdocs-macros-plugin` and the `azure-guide-capture-toolkit`
  package (both in `requirements-docs.txt`), plus PyYAML (mkdocs dependency).
  The base toolkit install pulls only PyYAML; `ruamel.yaml` and `Pillow` are
  loaded lazily and are only needed for capture/CLI work.
- Capture/CLI: install the toolkit with its `capture` extra
  (`pip install "azure-guide-capture-toolkit[capture] @ git+https://github.com/yeongseon/azure-guide-capture-toolkit@v0.1.0"`)
  to get `Pillow` and `ruamel.yaml`; Node + Playwright for raw capture.
