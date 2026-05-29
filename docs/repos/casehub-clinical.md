# casehub-clinical

**GitHub:** [casehubio/clinical](https://github.com/casehubio/clinical)
**Tier:** Application
**Status:** Active — Layers 1–6 complete; Layer 7 (trust routing) pending

## What It Is

A clinical trial coordination application built on the CaseHub agentic harness. Coordinates eligibility screening agents, safety monitoring agents, PI authorisation gates, and IRB approval gates across multiple trial sites — producing an FDA-compliant, GDPR-aware, independently verifiable audit trail. Field showcase and tutorial for Java developers in regulated healthcare (pharma, biotech, clinical research).

GCP domain knowledge is a prerequisite for this audience — and it is standard knowledge for Java developers in that field. The same developer who evaluates CaseHub for their trial coordination system is the developer who follows the tutorial to build it.

Scored 24/25 on market fit — highest of all evaluated use cases. Demonstrates that GCP, FDA, and EMA requirements cannot be met by workflow-based LLM coordination and are structurally satisfied by CaseHub's foundation.

Comparison baseline: ClinicalAgent (arXiv 2404.14777, ACM BCB '24, open source). See `docs/use-case-analysis.md` §8.1 and `docs/tutorial-strategy.md` §7 in this repo.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence. Each layer adds one foundation module and makes its value tangible relative to the previous layer. The code at every layer is production-grade. See `docs/tutorial-strategy.md §7` for teaching objectives per layer.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive Java — no CaseHub | Baseline: direct service calls, no SLA, no audit | complete (Epics 1+2, 2026-05-08) |
| 2 | casehub-work | No formal SLA for adverse event review (GCP: serious AE within 24h) | complete (Epic 4, 2026-05-12) |
| 3 | casehub-qhorus | No formal obligation when coordinating PI authorisation and safety agents | complete (Epic 5, 2026-05-15) |
| 4 | casehub-ledger | No FDA tamper-evident audit trail; no GDPR Art.17 consent withdrawal | complete (Epic 4, 2026-05-12) |
| 5 | casehub-engine | Fixed trial pipeline; no adaptive paths for grade-based escalation or IRB gates | complete (Epic 6, 2026-05-23) |
| 6 | trial-level blackboard aggregation — cross-site DSMB rollup | No cross-site pattern detection; no DSMB rollup when multiple sites have simultaneous Grade 4+ events | complete (Epic 3, 2026-05-25) |
| 7 | Trust routing | No trust model; experienced safety agents not prioritised on complex CTCAE Grade 4+ events | pending |
| 8 | Comparison vs ClinicalAgent | — | pending |

## What It Owns

- Clinical trial domain model: `ClinicalTrial`, `TrialSite`, `PatientEnrollment`, `ProtocolDeviation`, `AdverseEvent`, `IrbApproval`
- Capability tags: `eligibility-screening`, `safety-monitoring`, `protocol-review`, `irb-consultation`, `pi-authorisation`, `data-safety-monitoring`, `regulatory-submission`, `trial-supervisor`
- Trust dimensions: `safety-accuracy`, `eligibility-precision`, `protocol-adherence`
- Multi-site trial `CasePlanModel` — site-level sub-cases with trial-level aggregation
- Adverse event escalation — 24h/7d GCP SLA WorkItems with CTCAE grading
- PI authorisation — formal COMMAND creates Commitment; deviation requires named PI approval; MAJOR deviations trigger GCP §4.5 sponsor notification via `SponsorNotifier` SPI (casehub-connectors-core)
- IRB/ethics committee gate — `ClinicalDeviationCaseHub` + `deviation-review.yaml`: CRITICAL protocol deviation + PI approval → 72h WorkItem → four terminal outcomes (APPROVED/REJECTED/DEFERRED/EXPIRED); `IrbDecisionListener` bridges WorkItem lifecycle to `IrbApproval` entity + ledger
- AE escalation policy SPI — `AdverseEventEscalationPolicy` + `DefaultAdverseEventEscalationPolicy` (CTCAE-based): Grade 3 → senior monitor gate; Grade 4+ → senior monitor + DSMB in parallel; `ClinicalAdverseEventCaseHub` + `ae-escalation.yaml` drives adaptive routing via `contextChange.filter`
- `ClinicalTrialCaseHub` + `trial-coordination.yaml` — trial-level DSMB rollup binding (cross-site Grade 4+ pattern detection); owns trial-level `CasePlanModel` not just IRB gate and AE escalation
- `TrialActivationService` — `POST /trials/{id}/activate`; three-phase activation (commit status → startCase().join() → commit caseId); avoids Agroal pool deadlock
- `TrialCaseLookup` — site → trial → engineCaseId lookup for signal routing
- `TrialSafetySignalService` — observes `AeEscalationCompletedEvent`; clears `grade4Active.<siteId>` flag
- `ClinicalTrial.engineCaseId` — UUID field (V110 migration) set on ACTIVE transition
- `AdverseEvent.escalationStatus` — `AeEscalationStatus` (V111, NOT NULL DEFAULT 'NONE'); tracks AE escalation case lifecycle (NONE / REQUESTED / COMPLETED / FAILED)
- `AdverseEvent.engineCaseId` — UUID nullable (V112); set when AE escalation case starts
- `ProtocolDeviation.engineCaseId` — UUID nullable (V113); set when IRB deviation case starts
- `AeStatusUpdater` — CDI bean that extracts the COMPLETED write-back from `AeEscalationListener`; isolated in `@Transactional(REQUIRES_NEW)` for Panache mockability in tests
- `IrbCommitteeAssignmentPolicy` SPI — maps `IrbCommitteeContext(deviationId, siteId, trialId, severity)` to `IrbCommitteeAssignment(committeeId, candidateGroups)`; interface in `api/spi/`, `@DefaultBean` in `runtime/service/`; mirrors `DeviationResponsePolicy` pattern. Full SPI control of WorkItem routing for `candidateGroups` blocked by engine#387 (dynamic `candidateGroups` from case context in YAML `humanTask` binding)
- `SEVERE_GRADES = Set.of(GRADE_4, GRADE_5)` — shared grade threshold constant in signal services
- 3-site showcase scenario vs ClinicalAgent

## The Compliance Gap It Closes

ClinicalAgent (peer-reviewed baseline) structurally cannot provide:
- Adverse event SLA enforcement (GCP: serious events within 24h) — WorkItem `claimDeadline`
- Protocol deviation authorisation by named PI — COMMAND commitment lifecycle
- Consent withdrawal (GDPR Art.17) — ledger erasure and decision context sanitisation
- Multi-site independence with trial-level rollup — sub-case orchestration
- FDA tamper-evident audit trail — Merkle MMR + Ed25519-signed checkpoints
- Trust-weighted safety agent routing — Bayesian Beta from outcome attestations
- Adaptive protocol paths — IRB gate and grade-based AE escalation via casehub-engine `CasePlanModel`

## Dependencies

```
casehub-clinical
  → casehub-engine                  (IRB gate, AE escalation, CasePlanModel, stage gating; trial-level CasePlanModel via trial-coordination.yaml)
  → casehub-engine-work-adapter     (HumanTaskScheduleHandler + WorkItemLifecycleAdapter — Layer 5)
  → casehub-engine-scheduler-quartz (Quartz worker execution — Layer 5)
  → casehub-platform                (runtime scope — @DefaultBean mocks for engine CDI wiring)
  → casehub-platform-expression     (runtime scope — JQEvaluator for engine expression evaluation)
  → casehub-ledger                  (FDA Merkle audit, GDPR erasure, EU AI Act Art.12, trust scoring)
  → casehub-work                    (IRB/PI WorkItems with SLA and escalation)
  → casehub-qhorus                  (COMMAND to PI, commitment lifecycle, safety agent channels)
  → casehub-connectors-core         (sponsor notification delivery — clinical#13; DSMB/AE alerts planned — clinical#11)
```

## Layer 5 Integration Notes (casehub-engine)

These apply to any consumer adding casehub-engine to a CaseHub application. Documented from clinical Layer 5 (clinical#6).

**CDI wiring:** casehub-platform and casehub-platform-expression must be on the runtime classpath when casehub-engine is present. Without `casehub-platform`, the engine's `@DefaultBean` mock beans are absent and CDI resolution fails at augmentation time (symptom: `UnsatisfiedResolutionException` for `PreferenceProvider`). Use `<scope>runtime</scope>` — not `test` — in application modules that run the Quarkus build goal. See `docs/protocols/casehub/casehub-platform-dependency-scope.md`.

**Quartz incompatibility:** `casehub-engine-scheduler-quartz` and the casehub-work scheduler beans conflict if both are on the classpath in the same deployment unit without isolation. Use separate modules or `@IfBuildProperty` gating to avoid double-scheduler registration.

**YAML binding gotchas:**
- `inputMapping` is the correct field name — not `inputSchema`
- `on.contextChange.filter` is the correct path — not `when`

These are silent failures: the YAML parses without error but the binding has no effect at runtime.

**`WorkloadProvider` stub:** `StubWorkloadProvider` is a `@DefaultBean @ApplicationScoped` zero-returning stub required because engine#378 deleted `CasehubWorkloadProvider`. Add it to any `@QuarkusTest` context that activates casehub-engine but does not provide a real workload provider. Root cause tracked in casehubio/engine#393.

## Key Epics

1. Project scaffold — complete
2. Domain model — clinical trial entities and capability tags — complete
3. Multi-site sub-case structure — complete (2026-05-25)
4. Adverse event escalation — 24h and 7d GCP SLAs — complete
5. PI authorisation — formal commitment for protocol deviations — complete
6. IRB/ethics committee gate + AE escalation policy SPI (casehub-engine) — complete
7. GDPR and regulatory compliance — patient data
8. Trust-weighted safety agent routing
9. LLM supervisor mode — protocol amendment analysis
10. 3-site showcase and ClinicalAgent comparison

Issues: https://github.com/casehubio/clinical/issues?label=epic
