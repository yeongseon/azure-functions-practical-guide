---
title: Validation Evidence Audit
content_sources:
  references:
    - type: self-generated
      justification: Repository-local editorial inventory of retained tutorial and lab evidence, not an Azure execution or source verification record.
---

# Validation Evidence Audit

This **2026-10-25 editorial audit** separates published history from evidence that
can establish a run-owned assertion. It does not rerun Azure, delete preserved
observations, assign retrospective run IDs, or refresh live-test dates.
The [generated tutorial dashboard](validation-status.md) owns the per-tutorial
table; the separately dated snapshot below groups its underlying method claims
by retained identity, language and plan. The lab classification retains its
original audit date. Navigation pages remain outside execution-validation scope.

## How to Read the Classifications

Use the [evidence and hypothesis contract](../troubleshooting/methodology/troubleshooting-method.md#evidence-and-hypothesis-contract):

| Term | What this audit means |
|---|---|
| Documented-only | Instructions or expected evidence, not a local observation. A Learn citation is source review, not execution. |
| Historical | An earlier reported run or retained capture, useful only within its original scope; not a current rerun. |
| Observed (reported) | The guide labels a captured fact Observed. This audit preserves that claim without silently upgrading provenance. |
| unverified | Run identity, executed revision, environment, retained artifacts/digests or assertion coverage are missing or unchecked. It is not synonymous with fabricated. |
| false-negative / false-positive | A reported detector or experiment misclassification, not a universal verdict on the underlying Azure behavior. Preserve the narrower observation and its limits. |
| NOT_RUN | No live execution for the named scenario/stage is recorded. Missing evidence for a claimed historical run is instead unknown/unverified, not retroactive NOT_RUN. |

Source review, code/static checks, live Azure execution, evidence trust,
independent reproduction, recovery and cleanup are independent axes. A successful
HTTP response is not durable-work evidence; a restart is not unique causal proof;
cleanup instructions are not proof resources were removed. No row below asserts
`trusted-current`, independent reproduction or Golden approval. An incomplete
required run cannot receive a conclusive hypothesis verdict merely because an
older page calls it supported.

## Tutorial Binding Limitations

The generator audits each existing `az_cli` and `bicep` record without changing
its stored result or date. Tool versions are retained as partial environment
history. Unbound output excerpts cannot identify the source revision, full
environment, method and immutable artifacts of an end-to-end run. Optional
locators can point at existing run notes but cannot attest provenance themselves.
Missing bindings must be recovered from genuinely retained records or left
unverified; nonexistent artifacts cannot be reconstructed honestly by this PR.

## Tutorial Claims Snapshot — 2026-11-04

Computed read-only on **2026-11-04**, from the fetched `origin/main` commit
`e1c409ee42d179d65ff0033295d998dc96fb1953`: **158 tutorials, 316 method records**.
The scope is the generator's `language-guides/*/tutorial/*/*.md`, excluding
`index.md`. The committed dashboard's **2026-10-30** “as of” date and this report's
date are documentation/freshness clocks, **not execution or capture dates**.
The source SHA identifies the audited documentation, not the revision executed
by any historical run.

This inventory implements the publication-provenance slice of
[#158](https://github.com/yeongseon/azure-functions-practical-guide/issues/158)
under [tracker #161](https://github.com/yeongseon/azure-functions-practical-guide/issues/161)
and its existing [evidence contract](../troubleshooting/methodology/troubleshooting-method.md#evidence-and-hypothesis-contract).
It groups the existing helper assessments; it introduces no evaluator, stored
status value or rewritten tutorial metadata. Status correction belongs to #392.

### Non-Overlapping Inventory Labels

Assign the first applicable label in this order. These are editorial groupings,
not replacements for method result, freshness, execution status or evidence trust.

| Label | Selection / limitation |
|---|---|
| Real-run-backed (locator only) | `evidence_binding` resolves a retained note and its named run identity. Even a match requires method/environment/artifact review; it is not proof of authenticity or Azure execution. |
| Documented/reported | A dated `pass` or `fail` assessed as `fresh` or `stale`, without a resolving retained run. **Reported, unverified**, not the contract's Learn-sourced `Documented` claim level. |
| Local-only / static | Helper assessment `static-only`, including legacy `syntax_validated`; not a live Azure result. |
| Unknown / not tested / invalid | All remaining records; preserve `NOT_RUN`, `unknown` and `invalid` distinctions in the helper output. Missing evidence for historical claims is not retroactive NOT_RUN. |

| Method | Real-run-backed | Documented/reported | Local-only / static | Unknown / not tested / invalid | Total |
|---|---:|---:|---:|---:|---:|
| `az_cli` | 0 | 114 (113 pass, 1 fail) | 0 | 44 | 158 |
| `bicep` | 0 | 1 (pass) | 15 | 142 | 158 |
| **Total** | **0** | **115 (114 pass, 1 fail)** | **15** | **186** | **316** |

All 186 records in the last class are `not_tested` with `last_tested: null`,
assessed as `NOT_RUN`; there are **0 unknown, missing or invalid method records**.
Every method's evidence trust remains `unverified`. There is no blanket
“validated” count: 115 reported outcomes are neither 115 passes nor 115 retained
Azure runs, and 114 pass records do not mean 114 passing tutorials.

### Language × Plan Breakdown

Each method cell is **reported / static / not tested**. Real-run-backed and
unknown/invalid counts are zero in every cell. Each cell sums to that row's
tutorial count; both method columns together sum to 316 records.

| Language | Plan | Tutorials | `az_cli` R / S / N | `bicep` R / S / N |
|---|---|---:|---:|---:|
| dotnet | consumption | 7 | 7 / 0 / 0 | 0 / 1 / 6 |
| dotnet | dedicated | 7 | 7 / 0 / 0 | 0 / 1 / 6 |
| dotnet | flex-consumption | 9 | 7 / 0 / 2 | 0 / 1 / 8 |
| dotnet | premium | 9 | 7 / 0 / 2 | 0 / 1 / 8 |
| java | consumption | 7 | 7 / 0 / 0 | 0 / 1 / 6 |
| java | dedicated | 7 | 7 / 0 / 0 | 0 / 1 / 6 |
| java | flex-consumption | 9 | 7 / 0 / 2 | 0 / 1 / 8 |
| java | premium | 9 | 7 / 0 / 2 | 0 / 1 / 8 |
| nodejs | consumption | 7 | 7 / 0 / 0 | 0 / 1 / 6 |
| nodejs | dedicated | 7 | 7 / 0 / 0 | 0 / 1 / 6 |
| nodejs | flex-consumption | 9 | 7 / 0 / 2 | 1 / 0 / 8 |
| nodejs | premium | 9 | 7 / 0 / 2 | 0 / 1 / 8 |
| powershell | consumption | 7 | 0 / 0 / 7 | 0 / 0 / 7 |
| powershell | dedicated | 7 | 0 / 0 / 7 | 0 / 0 / 7 |
| powershell | flex-consumption | 8 | 0 / 0 / 8 | 0 / 0 / 8 |
| powershell | premium | 8 | 0 / 0 / 8 | 0 / 0 / 8 |
| python | consumption | 7 | 7 / 0 / 0 | 0 / 1 / 6 |
| python | dedicated | 7 | 7 / 0 / 0 | 0 / 1 / 6 |
| python | flex-consumption | 9 | 8 / 0 / 1 | 0 / 1 / 8 |
| python | premium | 9 | 8 / 0 / 1 | 0 / 1 / 8 |
| **Total** | **All plans** | **158** | **114 / 0 / 44** | **1 / 15 / 142** |

### Exact Dates and Recorded Environmental Scope

The following groups cover every method record with identical stored
`result`, `last_tested`, `cli_version` and `core_tools_version`. “Absent” means
the version field is not present; `null` is the stored date value, not an inferred
execution date. The [dashboard's per-method table](validation-status.md#per-method-validation-and-evidence-audit)
maps these values to each tutorial without duplicating its 316 rows here.

| Method | Stored result | `last_tested` | `cli_version` | `core_tools_version` | Records |
|---|---|---|---|---|---:|
| az_cli | pass | 2026-04-09 | 2.83.0 | 4.8.0 | 26 |
| az_cli | pass | 2026-04-10 | 2.83.0 | 4.8.0 | 74 |
| az_cli | pass | 2026-04-11 | 2.70.0 | 4.6.0 | 6 |
| az_cli | pass | 2026-04-11 | 2.83.0 | 4.8.0 | 1 |
| az_cli | pass | 2026-04-12 | 2.70.0 | 4.6.0 | 6 |
| az_cli | fail | 2026-04-12 | 2.70.0 | 4.6.0 | 1 |
| az_cli | not_tested | null | 2.83.0 | 4.8.0 | 6 |
| az_cli | not_tested | null | null | null | 28 |
| az_cli | not_tested | null | Absent | Absent | 10 |
| bicep | pass | 2026-04-10 | Absent | Absent | 1 |
| bicep | syntax_validated | 2026-06-06 | Absent | Absent | 15 |
| bicep | not_tested | null | Absent | Absent | 142 |

No method record contains `captured_at`, `run_id` or `evidence_ref`: **0 fields
present for each, 0 locators, 0 resolving run bindings**. Tool-version strings
are partial reported environment history, not a captured environment or proof
that the method ran. Language/plan are documentation-path scope, not a run-owned
record of OS, region, host/runtime versions, configuration or retained artifacts.

- The sole failed CLI claim is
    [`docs/language-guides/python/tutorial/consumption/02-first-deploy.md`](../language-guides/python/tutorial/consumption/02-first-deploy.md):
    `fail`, 2026-04-12, CLI 2.70.0 / Core Tools 4.6.0. Its failure is preserved.
- The sole Bicep pass claim is
    [`docs/language-guides/nodejs/tutorial/flex-consumption/05-infrastructure-as-code.md`](../language-guides/nodejs/tutorial/flex-consumption/05-infrastructure-as-code.md):
    `pass`, 2026-04-10, neither tool version recorded. It remains unverified.
- Applying the repository's **age >90 days** rule on 2026-11-04 yields **115
    stale, 0 fresh** dated pass/fail records: CLI 114 (including the failure),
    Bicep 1. Exactly 90 days remains fresh. The 15 static dates are not Azure
    freshness; the 186 NOT_RUN records have no attempt date.
- `tutorial_status` separately yields **113 Stale pass claim, 1 Failed claim,
    44 Not tested / no data, 0 Fresh pass claim, 0 Invalid metadata** (158 total).
    This precedence-based tutorial summary must not be added to method totals.

### Reproduce the Inventory Without Rewriting Status

Use a clean detached checkout of the desired SHA and a Python 3.11 environment
with the repository's documentation dependencies. For this snapshot, the Python
executable used was `/tmp/opencode/venv311/bin/python` (the `python` commands
below use that environment on PATH); that environment location is not part of
the evidence identity. From the repository root:

```bash
SNAPSHOT_SHA=e1c409ee42d179d65ff0033295d998dc96fb1953
git rev-parse HEAD
git diff --exit-code "$SNAPSHOT_SHA" -- docs/language-guides scripts/lib/tutorial_validation.py scripts/generate_validation_status.py
python scripts/generate_validation_status.py --as-of 2026-10-30 --check
```

The SHA output must match the checkout being inventoried. The diff checks the
snapshot inputs, while `--check` only checks the committed dashboard at its own
report date. For another SHA, select that checkout and its dashboard date; do not
write a newly generated dashboard to the repository as part of this inventory.

Save this block outside the checkout as `inventory.py`, then run
`python /path/to/inventory.py` from that checkout's root. Set `AS_OF` explicitly
for a later report. It uses `assess_method` (including `evidence_binding`) and
`tutorial_status` directly rather than copying their assessment logic.

```python
from collections import Counter
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()))
from scripts.generate_validation_status import TUTORIAL_GLOB, has_locator
from scripts.lib.tutorial_validation import (
    METHODS, assess_method, extract_tutorial_info, tutorial_status,
)

AS_OF = date.fromisoformat("2026-11-04")
root = Path.cwd()
docs = root / "docs"
tutorials = [extract_tutorial_info(p, docs)
             for p in sorted(docs.glob(TUTORIAL_GLOB)) if p.name != "index.md"]
classes: Counter[tuple[str, str, str, str]] = Counter()
profiles: Counter[tuple[str, str, str, str, str]] = Counter()
versions: Counter[tuple[str, str, str]] = Counter()
freshness: Counter[tuple[str, str]] = Counter()
statuses: Counter[str] = Counter()
fields: Counter[str] = Counter()
for tutorial in tutorials:
    assessments = []
    for method in METHODS:
        raw = tutorial.validation.get(method)
        assessment = assess_method(raw, AS_OF, root)
        assessments.append(assessment)
        resolved = assessment.binding.endswith(
            "; method/environment/artifacts require review")
        label = next(name for condition, name in (
            (resolved, "real-run-backed"),
            (assessment.freshness in {"fresh", "stale"}
             and assessment.result in {"pass", "fail"}, "documented/reported"),
            (assessment.freshness == "static-only", "local-only/static"),
            (True, "unknown/not-tested/invalid"),
        ) if condition)
        classes[tutorial.language, tutorial.plan, method, label] += 1
        freshness[method, assessment.freshness] += 1
        profiles[method, assessment.result, assessment.last_tested,
                 assessment.tools, label] += 1
        if isinstance(raw, dict):
            fields.update(key for key in ("captured_at", "run_id", "evidence_ref")
                          if key in raw)
            versions[method, str(raw.get("cli_version", "Absent")),
                     str(raw.get("core_tools_version", "Absent"))] += 1
        fields["locator"] += has_locator(raw)
        fields["resolved"] += resolved
        if assessment.result == "fail" or (
                method == "bicep" and assessment.result == "pass"):
            print("EXCEPTION", tutorial.rel_path, method, assessment)
    statuses[tutorial_status(assessments)] += 1
print("TUTORIALS", len(tutorials), "METHOD RECORDS", classes.total())
print("FIELDS", {key: fields[key] for key in (
    "captured_at", "run_id", "evidence_ref", "locator", "resolved")})
print("FRESHNESS", freshness)
print("TUTORIAL STATUS", statuses)
print("RAW VERSIONS (None means stored null)", versions)
for key, count in sorted(profiles.items()):
    print("PROFILE", key, count)
for key, count in sorted(classes.items()):
    print("MATRIX", key, count)
assert classes.total() == len(tutorials) * len(METHODS)
assert statuses.total() == len(tutorials)
```

The output reconciles **158 × 2 = 316 = 0 + 115 + 15 + 186**. On a different
snapshot, inspect every helper freshness/result and locator mismatch instead of
assuming today's zero unknown/invalid counts. This read-only grouping does not
refresh any date or claim.

### Not Established

No record establishes an executed source revision, authentic run provenance,
run-owned environment/capture window, retained sanitized artifact set/digests,
independent human reproduction, recovery or completed cleanup. The inventory
cannot prove historical Azure execution occurred, nor prove it never occurred.
Azure execution, Portal capture and independent live reproduction for this audit
are **NOT_RUN**. Local helper execution, dashboard drift checks, tests and a docs
build do not supply that missing evidence; the separate content dashboard is
source review, not tutorial execution. Recover genuine retained evidence or keep
these claims reported/unverified; never invent IDs or dates to fill the gap.

## Existing Lab Guides

The following inventory is an editorial classification, not a generated execution
verdict. Links point at the preserved guides and their evidence notes. Recovery
and cleanup are described separately from reproduction.

All 13 non-index pages are included. **Trust is unverified and independent
reproduction is not established for every row.** The tracked `labs/` tree contains
READMEs, producers and a verification script, but no retained capture bundles or
artifact digests corresponding to the historical inventories. Inline tables and
excerpts remain reported evidence; artifact filenames in a guide are not proof
those files were retained. No cleanup completion receipt was found in that tree.

| Guide / retained page evidence | Classification and reproduction limits | Recovery (reported, not independently verified) | Cleanup |
|---|---|---|---|
| [Code/storage verification](../troubleshooting/lab-guides/code-storage-verification.md#4-experiment-log) | Historical April 6 observations A–D; E–S projected/documented-only, NOT_RUN for those projected patterns. Section 4.6.1 reports resilience contradicting the projected share-removal outage. False-negative risk: FC1 HTTP 200 masks storage degradation; false-positive risk: Dedicated's pre-existing auth error is not the package failure cause. | Section 4.5 reports configuration restoration; Dedicated also required redeployment. Does not validate every projected scenario. | Commands only; completion unverified. |
| [Cold start](../troubleshooting/lab-guides/cold-start.md#4-experiment-log-artifact-based) | Historical April 4 client timing and telemetry excerpts; reported Observed latency, inferred provisioning attribution. `labs/cold-start/artifacts/<timestamp>/` inventory has no tracked capture bundle. | Warm follow-ups reported at 67–99 ms; not a new recovery experiment or proof of unique cause. | Guidance only; completion unverified. |
| [Deployment not running](../troubleshooting/lab-guides/deployment-not-running.md#4-experiment-log) | Historical April 5 excerpts separate transport acceptance from indexing/invocation. New Golden fault-package definition is explicitly NOT_RUN / NOT_TESTED; synthetic replay is static-only. False-positive success risk: HTTP transport 200 is not function execution. | Historical indexing and HTTP 200 recovery reported; new scenario recovery NOT_RUN. | New scenario none created; historical cleanup receipt absent. |
| [DNS/VNet resolution](../troubleshooting/lab-guides/dns-vnet-resolution.md#4-experiment-log) | Historical April 7 endpoint probes; App Insights ingestion unavailable. Reported Observed DNS/storage changes, not complete causal proof. False-negative risk: health and identity probes remain green while storage fails. | Private DNS and storage success reported after link restoration; auth-versus-network explanation still requires discriminating captures. | Instructions only; completion unverified. |
| [Durable replay storm](../troubleshooting/lab-guides/durable-replay-storm.md#4-experiment-log) | Historical April 7 EP1 telemetry and ContinueAsNew excerpts; source/runtime/run-owned capture binding incomplete. Published supported verdict is retained, not re-attested. | Reset-every-250 completion reported; no independent replay/reproduction of that live run. | Instructions only; completion unverified. |
| [Event Hub checkpoint lag](../troubleshooting/lab-guides/event-hub-checkpoint-lag.md#4-experiment-log) | Historical April 7 processing-delay/event-age measurements; **durable checkpoint lag not proven**. False-positive checkpoint inference: `CheckpointDelta` labels/event age are not persisted checkpoint evidence. | Delay reset and faster batches reported, with in-flight tail; durable checkpoint recovery not established. | Guidance only; completion unverified. |
| [Hosting-plan comparison matrix](../troubleshooting/lab-guides/hosting-plan-comparison-matrix.md) | Documented-only reference/synthesis, not an independent experiment. Live execution NOT_RUN for this audit; linked historical experiments retain their own limits. Do not force tutorial metadata onto this reference page. | Procedure reference, not measured restoration. | No separate experiment; not applicable to the reference itself. |
| [Hosting-plan security matrix](../troubleshooting/lab-guides/hosting-plan-security-matrix.md#4-experiment-log) | Historical reported Observed plan/fault signatures and relative timelines; unverified full run identity/captures. False-negative risks: cached identity until recycle and FC1 green health despite storage outage. Same external 503 can produce false-positive cause attribution. | Per-plan recovery notes include expected outcomes; do not treat every expectation as a measured recovery. | Instructions only; completion unverified. |
| [Managed identity auth](../troubleshooting/lab-guides/managed-identity-auth.md#4-experiment-log) | Historical April 4 role deletion/restart, auth/listener and probe excerpts. Reported Observed; shared timestamps/signatures with storage-access page do not establish independent reproduction. | Role restoration, successful probe and Timer resumption reported; not unique causal proof from restart alone. | Completion receipt absent; unverified. |
| [Out-of-memory crash](../troubleshooting/lab-guides/out-of-memory-crash.md#4-experiment-log) | Historical April 5 MemoryError/exit-137 excerpts and memory tables; named buffering/streaming ZIP packages not retained in tracked lab tree. Published causal verdict remains unverified. | Streaming implementation and successful invocation reported, not independently reproduced from retained packages. | Guidance only; completion unverified. |
| [Queue backlog scaling](../troubleshooting/lab-guides/queue-backlog-scaling.md#4-experiment-log) | Historical April 7 burst/drain telemetry; does not prove retries, poison or durable business outcomes. New retry/poison Golden definition explicitly NOT_RUN / NOT_TESTED; fixtures static-only. | Historical drain reported; new durable-work recovery NOT_RUN. | New scenario none created; historical guidance is not a receipt. |
| [Storage access failure](../troubleshooting/lab-guides/storage-access-failure.md#4-experiment-log) | Historical April 4 403/listener excerpts, including aggregate/multi-role changes; not a one-fault RBAC-versus-network discriminator. New Golden scenario explicitly NOT_RUN / NOT_TESTED. | Historical probe/listener/Timer recovery reported; controlled scenario timing NOT_RUN. | New scenario none created; historical delete command is not a receipt. |
| [Timer missed schedules](../troubleshooting/lab-guides/timer-missed-schedules.md#4-experiment-log) | Historical April 7 stop/restart and TimerFired records; reported Observed missed windows and isPastDue, not an independently reproduced run. False-positive interpretation: one catch-up fire does not establish replay of each missed window. | Post-restart catch-up and stable schedule reported; not proof each missed execution ran. | Guidance only; completion unverified. |

These false-negative/false-positive entries classify **specific diagnostic
interpretations**, not newly measured detector accuracy. Expected/projection
sections are documented-only even when they contain date-shaped example rows.
Historical published supported verdicts are not promoted to `SUPPORTED` under the
new contract without the required retained assertions, controls and provenance.

## Remaining Work

- Recover and independently inspect genuine retained tutorial run/method,
    environment, revision and artifact bindings where available. Keep unsupported
    historical passes unverified; do not invent retrospective identity or dates.
- Complete approved live captures for NOT_RUN scenarios only under a separately
    authorized Azure execution. This read-only PR and ordinary CI perform none.
- Record an independent operator's reproduction and its recovery/cleanup outcomes
    separately. Offline replay and author-entered status alone are insufficient.
- Migrate labs incrementally using their existing experiment logs; this inventory
    does not rewrite every legacy lab or declare the historical hypotheses proven.

## See Also

- [Tutorial Validation Status](validation-status.md)
- [Content Validation Status](content-validation-status.md)
- [Troubleshooting Labs](../troubleshooting/lab-guides/index.md)
- [Tutorial Validation Rules](../contributing/content-contract.md#tutorial-validation-tracking)

## Sources

This self-generated inventory uses the repository guides linked in the table and
the tracked `labs/` tree. Tutorial counts additionally use the pinned commit's
frontmatter and validation helpers. It makes no new Azure platform verification
claim; Microsoft Learn sourcing remains on the linked guides. Both audit dates
are editorial dates, not capture or execution dates.

- [Tutorial evidence parent #158](https://github.com/yeongseon/azure-functions-practical-guide/issues/158)
- [Functions evidence-model tracker #161](https://github.com/yeongseon/azure-functions-practical-guide/issues/161)
