# Capture plan — Python / Flex Consumption tutorial track

Proof-of-concept capture plan for issue **#108** (step-by-step tutorial
screenshots) and sub-issue **#109** (Python). It maps every planned Portal
screenshot for the Python **Flex Consumption** track to a stable manifest id,
the exact Portal blade to capture, the alt text, and the ready-to-paste
`Purpose / Look for / Expected result / Next step` caption block.

This is the **template** the other tracks (Consumption, Premium, Dedicated) and
the other languages (Node.js, Java, .NET, PowerShell) follow.

## How to use this plan

1. Deploy the track end-to-end by following the tutorial pages under
   `docs/language-guides/python/tutorial/flex-consumption/`. Real captures
   require a **live deployment** — an automated agent cannot produce them.
2. Authenticate a **device-compliant** browser (see the "Authenticating the
   capture browser (Conditional Access)" section in the repo-root `AGENTS.md`).
   A fresh isolated Chromium cannot pass Conditional Access.
3. For each row below, navigate to the **Blade / navigation** path, apply the
   PII helper (`scripts/portal-capture-helpers.js`), and capture a raw PNG.
4. Encode and stamp it:

    ```bash
    capture-optimize-webp /path/to/raw.png --id <shot-id>
    ```

    This writes `docs/assets/<file>` and stamps `captured`/`verified` in
    `scripts/capture/manifest.yaml`.
5. Insert the reference into the tutorial page at the **Insert after** location,
   immediately followed by the caption block (already written below):

    ```markdown
    [[[ shot("<shot-id>") ]]]
    ```

6. Run `mkdocs build --strict` to confirm the image resolves. Only reference a
   `shot()` **after** its `.webp` exists — a missing image fails the strict
   build.

> **Manifest state:** all 14 entries are already registered in
> `scripts/capture/manifest.yaml` with `status: planned` and **no** `captured`
> date. Registering them does not affect the build because no page references
> them yet.

## PII and verification requirements (per `AGENTS.md`)

Every capture MUST, before merge:

- Zero out subscription IDs, tenant IDs, and object IDs.
- Remove employee identifiers, emails, phone numbers, and avatar pixels.
- Carry no secrets, keys, or connection string values (mask App settings values).
- Be visually verified on the **final committed `.webp` bytes**, not just the raw
  PNG — a WebP re-encode is re-verified, not assumed from the source.
- Have alt text that accurately describes the rendered image.

## Step 01 — Run Locally

| Field | Value |
|---|---|
| Shot id | `py-flex-01-core-tools-local-start` |
| Blade / navigation | Local terminal — `func start` (no Portal) |
| What to capture | Core Tools host output listing discovered `helloHttp` and `health` functions with their `http://localhost:7071/api/...` endpoints |
| Insert after | The `func start` command block under the local-run step |

```markdown
[[[ shot("py-flex-01-core-tools-local-start") ]]]

**Purpose:** Confirm the Python v2 app indexes locally before you deploy.
**Look for:** Both `helloHttp` and `health` listed with `http://localhost:7071/api/...` URLs.
**Expected result:** The host reaches `Host started` with no indexing errors.
**Next step:** Deploy the same app to Flex Consumption in step 02.
```

## Step 02 — First Deploy

| Field | Value |
|---|---|
| Shot id | `py-flex-02-function-app-overview-running` |
| Blade / navigation | Function App → Overview |
| What to capture | Overview blade: **Status: Running**, plan type **Flex Consumption (FC1)**, Linux, Python 3.11 |
| Insert after | Step 8 "Validate deployment" (after the `az functionapp function list` block) |

```markdown
[[[ shot("py-flex-02-function-app-overview-running") ]]]

**Purpose:** Confirm the Function App provisioned on the Flex Consumption plan.
**Look for:** Status **Running** and an App Service Plan of type **Flex Consumption (FC1)**.
**Expected result:** The app is Running with a public `*.azurewebsites.net` URL.
**Next step:** Confirm your functions were indexed in the Functions blade.
```

| Field | Value |
|---|---|
| Shot id | `py-flex-02-functions-list` |
| Blade / navigation | Function App → Functions |
| What to capture | Functions blade listing `helloHttp` and `health`, **Enabled**, HTTP trigger |
| Insert after | The `py-flex-02-function-app-overview-running` caption block |

```markdown
[[[ shot("py-flex-02-functions-list") ]]]

**Purpose:** Verify the deployed package registered its HTTP functions.
**Look for:** `helloHttp` and `health` rows with **Enabled** status and HTTP trigger type.
**Expected result:** Both functions appear; none are in an error state.
**Next step:** Call the endpoints and confirm the health response.
```

| Field | Value |
|---|---|
| Shot id | `py-flex-02-deployment-storage-container` |
| Blade / navigation | Storage account → Containers → `app-package` |
| What to capture | The `app-package` container with the uploaded deployment zip blob |
| Insert after | Step 3 "Create the deployment container" (verification) |

```markdown
[[[ shot("py-flex-02-deployment-storage-container") ]]]

**Purpose:** Show where Flex Consumption stores the deployment package.
**Look for:** The `app-package` container holding the uploaded zip blob.
**Expected result:** Exactly one deployment package blob after the first publish.
**Next step:** Flex mounts this package at runtime — no Kudu/Azure Files content share.
```

## Step 03 — Configuration

| Field | Value |
|---|---|
| Shot id | `py-flex-03-environment-variables` |
| Blade / navigation | Function App → Settings → Environment variables (App settings tab) |
| What to capture | App settings showing `QueueStorage`, `TIMER_LAB_SCHEDULE`, `APPLICATIONINSIGHTS_CONNECTION_STRING` — **values hidden/masked** |
| Insert after | Step 3 "Set Additional App Settings" |

```markdown
[[[ shot("py-flex-03-environment-variables") ]]]

**Purpose:** Confirm the trigger and telemetry settings the host needs to index.
**Look for:** `QueueStorage`, `TIMER_LAB_SCHEDULE`, and `APPLICATIONINSIGHTS_CONNECTION_STRING`.
**Expected result:** All three keys present; values are hidden (never screenshot secret values).
**Next step:** Confirm the app uses a managed identity for storage in the Identity blade.
```

| Field | Value |
|---|---|
| Shot id | `py-flex-03-identity-system-assigned` |
| Blade / navigation | Function App → Settings → Identity → System assigned |
| What to capture | System assigned identity **Status: On** with an Object (principal) ID |
| Insert after | Step 2 "Configure Identity-Based Host Storage" |

```markdown
[[[ shot("py-flex-03-identity-system-assigned") ]]]

**Purpose:** Verify the managed identity used for identity-based storage access.
**Look for:** **Status: On** under the System assigned tab.
**Expected result:** A principal (object) ID is shown — zero it out before committing.
**Next step:** This identity holds the Storage Blob Data Contributor role from step 02.
```

## Step 04 — Logging & Monitoring

| Field | Value |
|---|---|
| Shot id | `py-flex-04-app-insights-logs-requests` |
| Blade / navigation | Application Insights → Logs (run the `requests` KQL query) |
| What to capture | KQL result grid with `GET /api/health` and `GET /api/info` rows, `resultCode` 200 |
| Insert after | Step 4 "Query Request and Exception Telemetry" |

```markdown
[[[ shot("py-flex-04-app-insights-logs-requests") ]]]

**Purpose:** Prove request telemetry reaches Application Insights.
**Look for:** `GET /api/health` and `GET /api/info` rows with `resultCode` **200**.
**Expected result:** Recent rows within the query time window (ingestion lag 2–5 min).
**Next step:** Watch the same traffic live in Live Metrics.
```

| Field | Value |
|---|---|
| Shot id | `py-flex-04-live-metrics` |
| Blade / navigation | Application Insights → Live Metrics |
| What to capture | Live Metrics with incoming request rate and server health while `curl` traffic runs |
| Insert after | The `py-flex-04-app-insights-logs-requests` caption block |

```markdown
[[[ shot("py-flex-04-live-metrics") ]]]

**Purpose:** Confirm real-time telemetry with no ingestion delay.
**Look for:** A non-zero incoming request rate and at least one healthy server.
**Expected result:** The request line moves as you generate traffic.
**Next step:** Inspect the handled exception in Transaction search.
```

| Field | Value |
|---|---|
| Shot id | `py-flex-04-transaction-search-exception` |
| Blade / navigation | Application Insights → Transaction search |
| What to capture | The handled `ValueError` from `GET /api/exceptions/test-error` |
| Insert after | The exceptions KQL block in step 4 |

```markdown
[[[ shot("py-flex-04-transaction-search-exception") ]]]

**Purpose:** Show how handled exceptions surface in telemetry.
**Look for:** A `ValueError` exception tied to the `GET /api/exceptions/test-error` request.
**Expected result:** The exception is captured while the request still returns a payload.
**Next step:** Codify all of this infrastructure in Bicep in step 05.
```

## Step 05 — Infrastructure as Code

| Field | Value |
|---|---|
| Shot id | `py-flex-05-deployment-history` |
| Blade / navigation | Resource group → Settings → Deployments |
| What to capture | A **Succeeded** Bicep deployment that provisioned the app + dependencies |
| Insert after | The `az deployment group create` verification block |

```markdown
[[[ shot("py-flex-05-deployment-history") ]]]

**Purpose:** Confirm the Bicep template deployed reproducibly.
**Look for:** A **Succeeded** deployment listing the Function App, storage, and App Insights.
**Expected result:** All resources provisioned in a single deployment.
**Next step:** Automate this deployment with GitHub Actions in step 06.
```

## Step 06 — CI/CD

| Field | Value |
|---|---|
| Shot id | `py-flex-06-github-actions-run` |
| Blade / navigation | GitHub → Actions → workflow run |
| What to capture | A successful (green) build+deploy run using OIDC federated credentials |
| Insert after | Step 6 "Add Flex Deployment Workflow" |

```markdown
[[[ shot("py-flex-06-github-actions-run") ]]]

**Purpose:** Verify the workflow deploys via OIDC without stored secrets.
**Look for:** A green build and deploy job; no publish-profile or client secret in use.
**Expected result:** The run completes successfully and deploys the package.
**Next step:** Confirm the deployment source in the Portal Deployment Center.
```

| Field | Value |
|---|---|
| Shot id | `py-flex-06-deployment-center` |
| Blade / navigation | Function App → Deployment → Deployment Center |
| What to capture | Deployment Center showing the GitHub source and a successful deployment log entry |
| Insert after | Step 7 "Verify Deployment Health" |

```markdown
[[[ shot("py-flex-06-deployment-center") ]]]

**Purpose:** Confirm the Portal recognizes the GitHub Actions deployment.
**Look for:** The GitHub source with the repository and branch, and a success log entry.
**Expected result:** The latest commit maps to the running deployment.
**Next step:** Extend the app with non-HTTP triggers in step 07.
```

## Step 07 — Extending with Triggers

| Field | Value |
|---|---|
| Shot id | `py-flex-07-functions-list-multi-trigger` |
| Blade / navigation | Function App → Functions |
| What to capture | Functions blade listing HTTP, Timer, Queue, and Blob triggered functions, all **Enabled** |
| Insert after | Step 6 "Publish and Validate Trigger Registration" |

```markdown
[[[ shot("py-flex-07-functions-list-multi-trigger") ]]]

**Purpose:** Verify the new trigger types registered after publish.
**Look for:** HTTP, Timer, Queue, and Blob functions all with **Enabled** status.
**Expected result:** Every added trigger appears; none are in an error state.
**Next step:** Wire blob events through Event Grid to the blob trigger.
```

| Field | Value |
|---|---|
| Shot id | `py-flex-07-event-grid-subscription` |
| Blade / navigation | Storage account → Events → Event Subscriptions |
| What to capture | The blob-created Event Grid subscription targeting the Function App blob webhook |
| Insert after | Step 5 "Create Event Subscription for Blob Events" |

```markdown
[[[ shot("py-flex-07-event-grid-subscription") ]]]

**Purpose:** Confirm blob events route to the function via Event Grid.
**Look for:** A `Microsoft.Storage.BlobCreated` subscription pointing to the blob extension webhook.
**Expected result:** The subscription is provisioned and enabled.
**Next step:** Upload a blob and confirm the trigger fires in telemetry.
```

## Rollout checklist (per track)

- [ ] Deploy the track end-to-end against a live subscription.
- [ ] Capture all shots above with a device-compliant, PII-scrubbed browser.
- [ ] `capture-optimize-webp` each raw PNG (stamps `captured`/`verified`).
- [ ] Insert each `[[[ shot("<id>") ]]]` + caption at its **Insert after** point.
- [ ] Visually verify every final `.webp` for PII and caption accuracy.
- [ ] `mkdocs build --strict` passes.
- [ ] Repeat for Consumption, Premium, Dedicated tracks and other languages.
