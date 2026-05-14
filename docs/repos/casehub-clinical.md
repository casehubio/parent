# casehub-clinical

**GitHub:** [casehubio/clinical](https://github.com/casehubio/clinical)
**Tier:** Application
**Status:** Greenfield — no code yet, epics defined

## What It Is

The clinical trial coordination application built on the CaseHub foundation. Field showcase and tutorial for Java developers in regulated healthcare — pharma, biotech, and clinical research organisations where GCP, FDA IND, EMA CTR, and GDPR requirements apply.

GCP domain knowledge is a prerequisite for this audience — and it is standard knowledge for Java developers in that field. The same developer who evaluates CaseHub for their trial coordination system is the developer who follows the tutorial to build it.

Scored 24/25 on market fit — highest of all evaluated use cases. Demonstrates that GCP, FDA, and EMA requirements cannot be met by workflow-based LLM coordination and are structurally satisfied by CaseHub's foundation.

Comparison baseline: ClinicalAgent (arXiv 2404.14777, ACM BCB '24, open source). See `docs/use-case-analysis.md` §8.1 and `docs/tutorial-strategy.md` §7 in this repo.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence. Each layer adds one foundation module and makes its value tangible relative to the previous layer. The code at every layer is production-grade. See `docs/tutorial-strategy.md §7` for teaching objectives per layer.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive Java — no CaseHub | Baseline: direct service calls, no SLA, no audit | pending |
| 2 | casehub-work | No formal SLA for adverse event review (GCP: serious AE within 24h) | pending |
| 3 | casehub-qhorus | No formal obligation when coordinating PI authorisation and safety agents | pending |
| 4 | casehub-ledger | No FDA tamper-evident audit trail; no GDPR Art.17 consent withdrawal | pending |
| 5 | casehub-engine | Fixed trial pipeline; no adaptive paths for grade-based escalation or IRB gates | pending |
| 6 | Trust routing | No trust model; experienced safety agents not prioritised on complex CTCAE Grade 4+ events | pending |
| 7 | Comparison vs ClinicalAgent | — | pending |

## What It Owns

- Clinical trial domain model: `ClinicalTrial`, `TrialSite`, `PatientEnrollment`, `ProtocolDeviation`, `AdverseEvent`, `IrbApproval`
- Capability tags: `eligibility-screening`, `safety-monitoring`, `protocol-review`, `irb-consultation`, `pi-authorisation`, `data-safety-monitoring`, `regulatory-submission`, `trial-supervisor`
- Trust dimensions: `safety-accuracy`, `eligibility-precision`, `protocol-adherence`
- Multi-site trial `CasePlanModel` — site-level sub-cases with trial-level aggregation
- Adverse event escalation — 24h/7d GCP SLA WorkItems with CTCAE grading
- PI authorisation — formal COMMAND creates Commitment; deviation requires named PI approval
- IRB/ethics committee gate — WorkItem with SLA
- 3-site showcase scenario vs ClinicalAgent

## The Compliance Gap It Closes

ClinicalAgent (peer-reviewed baseline) structurally cannot provide:
- Adverse event SLA enforcement (GCP: serious events within 24h) — WorkItem `claimDeadline`
- Protocol deviation authorisation by named PI — COMMAND commitment lifecycle
- Consent withdrawal (GDPR Art.17) — `LedgerErasureService` + `DecisionContextSanitiser`
- Multi-site independence with trial-level rollup — sub-case orchestration
- FDA tamper-evident audit trail — Merkle MMR + Ed25519-signed checkpoints
- Trust-weighted safety agent routing — Bayesian Beta from outcome attestations

## Dependencies

```
casehub-clinical
  → casehub-engine   (multi-site sub-case orchestration, CasePlanModel, stage gating)
  → casehub-ledger   (FDA Merkle audit, GDPR erasure, EU AI Act Art.12, trust scoring)
  → casehub-work     (IRB/PI WorkItems with SLA and escalation)
  → casehub-qhorus   (COMMAND to PI, commitment lifecycle, safety agent channels)
  → casehub-connectors (DSMB notifications, adverse event alerts)
```

## Critical Foundation Gap

`casehub-work-adapter` HITL wiring — WorkItem `COMPLETED` must signal plan item transition from WAITING to active. Without this, the IRB approval gate cannot complete. Raise issue in casehub-work before implementing Epic 6.

## Key Epics

1. Project scaffold
2. Domain model — clinical trial entities and capability tags
3. Multi-site sub-case structure
4. Adverse event escalation — 24h and 7d GCP SLAs
5. PI authorisation — formal commitment for protocol deviations
6. IRB/ethics committee gate
7. GDPR and regulatory compliance — patient data
8. Trust-weighted safety agent routing
9. LLM supervisor mode — protocol amendment analysis
10. 3-site showcase and ClinicalAgent comparison

Issues: https://github.com/casehubio/clinical/issues?label=epic
