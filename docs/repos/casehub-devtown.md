# casehub-devtown

**GitHub:** [casehubio/devtown](https://github.com/casehubio/devtown)
**Tier:** Application
**Status:** Layers 1, 3, 4, 5, 6 complete; Layer 2 code complete (LAYER-LOG entry pending engine#326)

## What It Is

A software engineering coordination application built on the CaseHub agentic harness. Coordinates specialist code reviewers (security, architecture, test coverage), human review task gates with SLA, and adaptive PR routing based on code content — producing a tamper-evident review record where every missed finding is traceable. Field showcase and tutorial for Java developers in software engineering and DevOps.

This is the CaseHub answer to Gastown — same domain (software engineering coordination), but built on the domain-agnostic foundation rather than baked into infrastructure. See `docs/gastown-casehub-analysis-v2.md` in this repo for the full architectural comparison.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence. Each layer adds one foundation module and makes its value tangible relative to the previous layer. The code at every layer is production-grade. See `../parent/docs/tutorial-strategy.md §7.5` for teaching objectives per layer.

LAYER-LOG.md in the project root is the authoritative layer-by-layer record with cross-references, key wiring, and gotchas. Update it when a layer completes or makes significant progress.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive Java — no CaseHub | Baseline: direct service calls to analysis agents, no accountability | ✅ complete — scaffold (#8), vocabulary (#9), naive service (#27) |
| 2 | casehub-work | No formal SLA for reviewer response; reviewer assignments not tracked | **in progress** — devtown#41 ✅ devtown#42 ✅; LAYER-LOG entry pending engine#326 |
| 3 | casehub-qhorus | No formal obligation per specialist reviewer; DECLINE when outside expertise | ✅ complete — devtown#52 + devtown#64; LAYER-LOG entry complete. `QhorusPrReviewService` sets `allowedWriters=ORCHESTRATOR` on all three channels; `requireContract()` validates both `allowedTypes` and `allowedWriters`. DONE/DECLINE dispatches use ORCHESTRATOR sender (agents will use own identity in Layer 6). |
| 4 | casehub-ledger | No tamper-evident review record; cannot trace production incident to missed finding | ✅ complete (devtown#5, devtown#73) — `MergeDecisionLedgerEntry`, `MergeDecisionObserver`, `CodeReviewComplianceResource`, `domainContentBytes()` override; V2003: index on `(repository, pr_number)` + dropped `tenancy_id` from join table |
| 5 | casehub-engine | Fixed review pipeline; no adaptive routing on security flags or architecture changes | ✅ complete — PR review CasePlanModel (#10); 38 tests |
| 6 | Trust routing | No trust model; experienced security reviewers not prioritised on sensitive PRs | ✅ complete — devtown#57; LAYER-LOG entry complete |
| 7 | Comparison vs naive AI code review | — | pending |

## What It Owns

- Capability tag definitions for the software development domain (`code-analysis`, `security-review`, `architecture-review`, `style-review`, `test-coverage`, `merge-executor`, etc.)
- Trust dimension definitions (`review-thoroughness`, `false-positive-rate`, `scope-calibration`)
- Routing thresholds per capability (e.g. `security-review` requires ≥ 0.70 trust)
- PR review `CasePlanModel` — goals, bindings, content-driven routing from code analysis findings
- `PrReviewCaseDefinition` (promoted to `review/src/main/` in devtown#60) — fluent DSL factory with `LambdaExpressionEvaluator` for binding conditions; uses `HumanTaskTarget.inline()` for human-approval binding; `PrReviewCaseDefinitionEquivalenceTest` verifies structural parity with YAML
- Merge queue `CasePlanModel` (casehub-refinery) — batch-then-bisect strategy as binding conditions
- Cross-repo coordinated merge — parent case + per-repo sub-cases with automatic rollback on fault
- Trust-weighted selection strategy for code review domain. See docs/DESIGN.md for implementation detail.
- Post-merge trust feedback — FLAGGED attestation when production incident traced to missed review
- **`POST /api/incident-feedback`** (devtown#5, devtown#73) — records FLAGGED attestations against agents whose PR reviews missed issues found in production incidents. `IncidentFeedbackService` + `IncidentFeedbackResource` with `@RolesAllowed("admin")`. Idempotent via `findAttestationsByAttestorIdAndCapabilityTag` (tokenisation-proof). New domain types: `IncidentSeverity` (severity→confidence mapping), `IncidentFeedback`, `IncidentFeedbackResult`, `FlaggedAgent`, `ReviewDomain.REVIEW_CAPABILITIES` validation set. V2003 migration: index on `(repository, pr_number)` for PR lookup; dropped `tenancy_id` column from `merge_decision_ledger_entry` join table (field shadowing removal per ledger#131).
- GitHub integration — PR webhook receiver, CI status reader, merge executor worker
- **CaseMemoryStore integration (devtown#43):** contributor history, reviewer agent context, and code-area history injected before PR review case starts; review outcomes written to memory at case close.
  - New domain types: `DevtownMemoryDomain`, `DevtownMemoryKeys`, `ReviewOutcome`, `ModulePathNormalizer` (devtown-domain)
  - New review types: `ReviewCompletedEvent`, `MemoryContext` (devtown-review)
  - New CDI components: `ReviewOutcomeObserver`, `CaseMemoryEmitter`, `CaseMemoryRecaller` (devtown-app)
  - `PrPayload` enhanced with `contributor` + `changedPaths`
  - Emission flow: `PlanItemCompletedEvent` → `ReviewOutcomeObserver` → `ReviewCompletedEvent` → `CaseMemoryEmitter` → `storeAll()`
  - Recall: `CaseMemoryRecaller` called before `PrReviewCaseService.startCase()`
  - Known tech debt: `CrossTenantCaseInstanceRepository` in async observer (engine#429 tracks fix)
  - Follow-up: engine#428–430, qhorus#251, devtown#65–68

## What It Does NOT Own

Everything below belongs in the foundation:
- Trust scoring computation (casehub-ledger)
- Commitment lifecycle (casehub-qhorus)
- Case engine and blackboard (casehub-engine)
- WorkItem inbox (casehub-work)
- Notification delivery (casehub-connectors)

## Dependencies

```
casehub-devtown
  → casehub-engine   (CasePlanModel, sub-cases, bindings)
  → casehub-ledger   (Merkle audit, trust scoring, GDPR)
  → casehub-work     (human review WorkItem, SLA, escalation)
  → casehub-qhorus   (COMMAND/RESPONSE per reviewer, commitment lifecycle)
  → casehub-connectors (Slack/Teams for review assignments and failures)
  → casehub-platform-memory-inmem (in-memory CaseMemoryStore for @QuarkusTest isolation)
```

## Key Epics

1. Project scaffold
2. Domain model — capability tags, trust dimensions, routing thresholds
3. PR review CasePlanModel — content-driven routing and parallel checks
4. Merge queue (casehub-refinery) — batch-then-bisect
5. Cross-repo coordinated merge
6. Trust-weighted reviewer routing and post-merge feedback
7. Failure handling — DECLINED vs FAILED routing
8. GitHub integration
9. Notification wiring
10. Observability and operational tooling

Issues: https://github.com/casehubio/devtown/issues?label=epic
