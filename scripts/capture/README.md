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

## Planned first-deploy captures

These entries are preparation only and remain **BLOCKED / NOT_CAPTURED** until a
live deployment and an authorized, device-compliant human browser session are
available. Do not add tutorial `shot()` references while the WebP files are
missing.

| Issue | Tutorial | Stable ID | Portal blade | Guide-derived expectation | Insert after capture |
|---|---|---|---|---|---|
| [#228](https://github.com/yeongseon/azure-functions-practical-guide/issues/228) | [`docs/language-guides/nodejs/tutorial/flex-consumption/02-first-deploy.md`](../../docs/language-guides/nodejs/tutorial/flex-consumption/02-first-deploy.md) | `node-flex-02-function-app-overview` | Function App → Overview | Linux Node.js 20 app on Flex Consumption (FC1) | Step 7 deployment validation block |
| [#228](https://github.com/yeongseon/azure-functions-practical-guide/issues/228) | [`docs/language-guides/nodejs/tutorial/flex-consumption/02-first-deploy.md`](../../docs/language-guides/nodejs/tutorial/flex-consumption/02-first-deploy.md) | `node-flex-02-functions-list` | Function App → Functions | Functions indexed from the deployed Node.js v4 app; use only rows actually visible | Overview capture and its observed caption |
| [#229](https://github.com/yeongseon/azure-functions-practical-guide/issues/229) | [`docs/language-guides/java/tutorial/premium/02-first-deploy.md`](../../docs/language-guides/java/tutorial/premium/02-first-deploy.md) | `java-premium-02-function-app-overview` | Function App → Overview | Linux Java 17 app on Elastic Premium (EP1) | Step 8 app-state validation block |
| [#229](https://github.com/yeongseon/azure-functions-practical-guide/issues/229) | [`docs/language-guides/java/tutorial/premium/02-first-deploy.md`](../../docs/language-guides/java/tutorial/premium/02-first-deploy.md) | `java-premium-02-functions-list` | Function App → Functions | Functions indexed from the deployed Java app; do not preclaim a count | Overview capture and its observed caption |
| [#230](https://github.com/yeongseon/azure-functions-practical-guide/issues/230) | [`docs/language-guides/dotnet/tutorial/premium/02-first-deploy.md`](../../docs/language-guides/dotnet/tutorial/premium/02-first-deploy.md) | `dotnet-premium-02-function-app-overview` | Function App → Overview | Linux .NET 8 isolated app on Elastic Premium (EP1) | Verification app-state block |
| [#230](https://github.com/yeongseon/azure-functions-practical-guide/issues/230) | [`docs/language-guides/dotnet/tutorial/premium/02-first-deploy.md`](../../docs/language-guides/dotnet/tutorial/premium/02-first-deploy.md) | `dotnet-premium-02-functions-list` | Function App → Functions | Functions indexed from the deployed .NET isolated app; use only rows actually visible | Step 8 function-list verification block |

For all six captures, reuse the documented authorized browser flow and apply
`scripts/portal-capture-helpers.js`. Record the capture source, time, tool,
authorized environment, and resource cleanup. Remove private identifiers,
emails, avatars, secrets, keys, and connection-string values. After encoding,
inspect the final WebP bytes for PII and accuracy, replace the planned alt text
with observed wording, and write one observed `Purpose / Look for / Expected
result / Next step` caption. A screenshot must not preclaim runtime fields,
function counts, or successful states that are not visible in the final image.

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
