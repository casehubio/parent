# casehub-devtown

**GitHub:** [casehubio/devtown](https://github.com/casehubio/devtown)
**Tier:** Application
**Status:** Layer 1 complete; Layer 5 shipped (Epic 3) — PR review CasePlanModel with content-driven routing

## What It Is

A software engineering coordination application built on the CaseHub agentic harness. Coordinates specialist code reviewers (security, architecture, test coverage), human review task gates with SLA, and adaptive PR routing based on code content — producing a tamper-evident review record where every missed finding is traceable. Field showcase and tutorial for Java developers in software engineering and DevOps.

This is the CaseHub answer to Gastown — same domain (software engineering coordination), but built on the domain-agnostic foundation rather than baked into infrastructure. See `docs/gastown-casehub-analysis-v2.md` in this repo for the full architectural comparison.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence. Each layer adds one foundation module and makes its value tangible relative to the previous layer. The code at every layer is production-grade. See `../parent/docs/tutorial-strategy.md §7.5` for teaching objectives per layer.

LAYER-LOG.md in the project root is the authoritative layer-by-layer record with cross-references, key wiring, and gotchas. Update it when a layer completes or makes significant progress.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive Java — no CaseHub | Baseline: direct service calls to analysis agents, no accountability | ✅ complete — scaffold (#8), vocabulary (#9), naive service (#27) |
| 2 | casehub-work | No formal SLA for reviewer response; reviewer assignments not tracked | **in progress** — devtown#41 |
| 3 | casehub-qhorus | No formal obligation per specialist reviewer; DECLINE when outside expertise | pending |
| 4 | casehub-ledger | No tamper-evident review record; cannot trace production incident to missed finding | pending |
| 5 | casehub-engine | Fixed review pipeline; no adaptive routing on security flags or architecture changes | ✅ complete — PR review CasePlanModel (#10); 38 tests |
| 6 | Trust routing | No trust model; experienced security reviewers not prioritised on sensitive PRs | pending |
| 7 | Comparison vs naive AI code review | — | pending |

## What It Owns

- Capability tag definitions for the software development domain (`code-analysis`, `security-review`, `architecture-review`, `style-review`, `test-coverage`, `merge-executor`, etc.)
- Trust dimension definitions (`review-thoroughness`, `false-positive-rate`, `scope-calibration`)
- Routing thresholds per capability (e.g. `security-review` requires ≥ 0.70 trust)
- PR review `CasePlanModel` — goals, bindings, content-driven routing from code analysis findings
- Merge queue `CasePlanModel` (casehub-refinery) — batch-then-bisect strategy as binding conditions
- Cross-repo coordinated merge — parent case + per-repo sub-cases with automatic rollback on fault
- Trust-weighted selection strategy for code review domain. See docs/DESIGN.md for implementation detail.
- Post-merge trust feedback — FLAGGED attestation when production incident traced to missed review
- GitHub integration — PR webhook receiver, CI status reader, merge executor worker

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
