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
The [generated tutorial dashboard](validation-status.md) owns tutorial counts and
per-method freshness; this page owns the concise lab classification and audit
limitations. Navigation pages remain outside execution-validation scope.

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
the tracked `labs/` tree. It makes no new Azure platform verification claim;
Microsoft Learn sourcing remains on the linked guides. The audit date is an
editorial date, not a capture or execution date.
