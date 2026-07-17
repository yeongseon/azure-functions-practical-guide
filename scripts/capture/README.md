# Screenshot capture pipeline

Portal screenshots are treated as **build artifacts driven by a manifest**, not
hand-placed files. Docs reference a screenshot by a **stable ID**; re-capturing a
blade overwrites the same file and never requires editing markdown.

This is the in-repo pilot. Once proven across a few sections it is intended to be
extracted into a central `azure-guide-capture-toolkit` and consumed by every
guide repo.

## Components

| File | Role |
|---|---|
| `manifest.yaml` | Single source of truth. One entry per screenshot: stable `id`, `file`, `alt`, `captured`/`verified` dates, `diff_threshold`. |
| `screenshot_lib.py` | Shared manifest access. Reads via PyYAML (present at docs-build time); writes lazily via ruamel round-trip to preserve comments. |
| `optimize_webp.py` | Downscales a raw PNG to `meta.target_width` (1440px) and encodes WebP, then stamps `captured`. |
| `diff_gate.py` | Compares a fresh capture to the committed image. Below `diff_threshold` it leaves the image byte-identical and only bumps `verified`; above it, re-encodes and bumps `captured`. |
| `mkdocs_macros.py` | Defines the `shot()` macro consumed at build time. |
| `portal-capture-helpers.js` | (in `scripts/`) Playwright PII text-replacement + avatar masking used during raw capture. |

## Referencing a screenshot in docs

Use the `shot()` macro with the manifest id:

```markdown
[[[ shot("01-storage-networking-all-networks") ]]]
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
    python3 scripts/capture/optimize_webp.py /path/to/raw.png --id <shot-id>
    ```

4. Reference it in markdown with `[[[ shot("<shot-id>") ]]]`.
5. `mkdocs build --strict` to verify it renders.

## Re-capturing (drift refresh)

Feed the fresh raw PNG through the diff gate instead of the optimizer:

```bash
python3 scripts/capture/diff_gate.py /path/to/fresh.png --id <shot-id>
```

- **Unchanged** (below threshold): image bytes untouched, only `verified` is
  bumped — no image churn in git.
- **Changed** (at/above threshold): image re-encoded, `captured` bumped.

## Requirements

- Docs build: `mkdocs-macros-plugin` (in `requirements-docs.txt`), PyYAML (mkdocs
  dependency). Never add a top-level `ruamel` import to `screenshot_lib.py` — the
  docs-build Python may not have it.
- Capture/CLI: Python with `Pillow` and `ruamel.yaml`; Node + Playwright.
