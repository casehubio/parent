# Known Overlap Risks

> **Scope:** Semantic collisions between repos and capabilities in wrong modules
> **Audience:** Platform builders primarily; app builders for awareness

## Known Overlap Risks

1. **`EventLog` vs `CaseLedgerEntry`** (engine) — `EventLog` is operational (restart recovery, observability). `CaseLedgerEntry` is the compliance record (tamper-evident). If a lifecycle transition doesn't fire `CaseLifecycleEvent`, it won't be ledgered — and the async observer can fail silently. See `casehub/garden: docs/protocols/casehub/dual-trail-audit-pattern.md` for the write rule, failure modes, and detection queries.

2. **`AuditEntry` vs `WorkItemLedgerEntry`** (work) — `AuditEntry` is always-on operational. `WorkItemLedgerEntry` is opt-in tamper-evident and is what trust score computation reads. A state transition that calls `audit()` but omits the CDI event produces an operational record but no compliance record, and silently corrupts trust scores. See `casehub/garden: docs/protocols/casehub/dual-trail-audit-pattern.md`.

3. **`CommitmentState.DELEGATED` (Qhorus) ≠ `WorkItemStatus.DELEGATED` (work)** — same word, opposite terminal semantics. Qhorus DELEGATED is **terminal** for the original obligor (obligation transferred, closed, child Commitment created for the named target). Work DELEGATED is **non-terminal** (`isTerminal()` returns false — work reassigned to a named actor, item stays active). Integration code bridging a Qhorus HANDOFF to WorkItem delegation will misapply terminal semantics. A developer reasoning about a HANDOFF-then-DELEGATED path expects the obligation to end — it does not. See javadoc on `CommitmentState.DELEGATED` and `WorkItemStatus.DELEGATED`.

4. **Notification duplication** — `casehub-connectors` and `casehub-work-notifications` both provide Slack/Teams. Must converge (parent#5, open).

5. **`callerRef` format is implicit** — carries `case:{caseId}/pi:{planItemId}`. casehub-work treats it as opaque. Consumers must know this format out of band.

## Known Placement Violations

SPIs and capabilities that exist in the wrong module pending extraction. Do not add new consumers — use the intended home once extracted.

| Capability | Current home | Intended home | Tracking |
|---|---|---|---|
| `OversightGateService` | `casehub-openclaw` | `casehub-engine-api` | *(untracked — file issue before implementing)* |
