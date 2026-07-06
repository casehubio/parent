# casehub-life

**GitHub:** [casehubio/life](https://github.com/casehubio/life)
**Tier:** Application
**Status:** Layers 2, 3, 4 complete — casehub-work + casehub-qhorus + casehub-ledger integration

## What It Is

Personal life automation application on the CaseHub harness. Coordinates household management, health, finance, family obligations, elder care — producing a formally tracked, SLA-enforced, optionally tamper-evident record of life obligations. Field showcase and tutorial for developers evaluating CaseHub for personal automation.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence. Each layer adds one foundation module and makes its value tangible relative to the previous layer.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Domain baseline — household domain model | Baseline: direct service calls, no SLA, no audit | **complete** (casehubio/life#2) |
| 2 | casehub-work | No formal SLA on household tasks | **complete** (casehubio/life#3, 2026-05-27) |
| 3 | casehub-qhorus | No commitment tracking; no oversight gates | **complete** (casehubio/life#4) |
| 4 | casehub-ledger | No tamper-evident audit for health/financial decisions | **complete** (casehubio/life#5) |
| 5 | casehub-engine | No multi-step workflow orchestration | **in progress** — `LifeTypedCaseHub` abstract base class (life#47): `augment()` final, `configureCase()` abstract, `lifeCaseType()` abstract. 6 CaseHubs extend it (AppointmentCycle, HomeMaintenance, TravelPlan, CareCoordination, ContractorCoordination, FinancialReview). `agentWorker(capabilityName, systemPrompt, responseSchema)` helper replaces per-worker boilerplate. `CareEpisodeCaseHub` stays on `YamlCaseHub` (sub-case only). `LifeCaseService.resolve()` uses CDI `Instance<LifeTypedCaseHub>` instead of 6-arm switch (life#51). |
| 6 | Trust routing | No trust model for agent routing | **complete** (casehubio/life#11) |
| 7 | casehub-openclaw | OpenClaw as WorkerProvisioner; pre-built skill ecosystem | pending |
| 8 | Auth (casehub-platform-oidc) | No RBAC enforcement; risk thresholds role-agnostic | **complete** (casehubio/life#40, 2026-06-22) — `@RolesAllowed` on all 5 REST resources; RBAC-differentiated risk thresholds in `LifeActionRiskClassifier` (admin elevated, junior always-gate). Closes life#26. |

## What It Owns

- `LifeDomain` enum: `HEALTH`, `FINANCE`, `HOUSEHOLD`, `LEGAL`, `CARE`, `TRAVEL`
- Domain model: `ExternalActor`, `LifeTaskContext` (domain supplement: `domain`, `priority`, `externalActorId`, `jurisdiction` (ISO 3166-1/2), deadline context — held alongside the foundation `WorkItem`)
- Capability tags: `household-management`, `health-coordination`, `financial-planning`, `family-scheduling`, `travel-planning`, `legal-deadline`, `contractor-coordination`
- Trust dimensions: `deadline-reliability`, `cost-accuracy`, `factual-accuracy`, `proactive-alerting`
- `CasePlanModel` definitions: `appointment-cycle`, `home-maintenance-cycle`, `financial-review`, `travel-plan`, `contractor-coordination`, `care-coordination`
- Household permission topology: `household-admin` > `household-member` > `household-junior`
- M-of-N quorum configuration for joint decisions
- Flyway path: `classpath:db/life/migration/` (PP-20260525-607b33)

### Layer 2 — casehub-work integration

- `POST /life-tasks` — creates `WorkItem` + `LifeTaskContext` atomically via `WorkItemTemplate` lookup
- `LifeSlaBreachPolicy` — implements `casehub-work` `SlaBreachPolicy` SPI; stateless two-tier escalation: first breach escalates to `household-admin`, second breach fails

### Layer 3 — casehub-qhorus integration

- `LifeCommitmentRecord` entity — persists commitment context (task id, actor, channel, message correlation)
- `LifeCommitmentStrategy` SPI — maps household task type to channel and speech-act selection
- Channel topology: `life/delegation` (task assignment), `life/oversight` (human gates), `life/actor/{id}` (per-actor channel)
- `LifeOversightResponseObserver` — `MessageObserver` SPI implementation; bridges oversight RESPONSE/DECLINE to task lifecycle
- Flyway V103 (`life_commitment_record`) at `db/life/migration/`
- REST: `POST /life-tasks/{id}/commit`, `POST /life-oversight-gates`

## Current State

Household tasks are now formal `WorkItem`s: SLA-enforced, delegable, auditable. `LifeTaskContext` supplements each task with life-specific fields. `LifeSlaBreachPolicy` escalates to `household-admin` on first breach, fails on second. Domain model correction in Layer 2: `HouseholdTask`, `LifeGoal`, `LifeEvent` removed — they duplicated `WorkItem`, case definitions, and ledger entries respectively.

**Engine deps temporarily removed** from `pom.xml` — SNAPSHOT build broken (engine#379, engine#380). Will be restored in Layer 5 branch. Layers 5–7 remain pending.

### Layer 4 — casehub-ledger integration

- 4 `LedgerEntry` subclasses: `HealthLedgerEntry`, `FinancialLedgerEntry`, `LegalLedgerEntry` (with `jurisdiction` field — prefers task-level jurisdiction over tenant-wide config, life#48), `ExternalActorErasureLedgerEntry` (with `ledgerEntriesAffected` field for self-contained Merkle-chained erasure proof)
- `LifeLedgerWriter` — unified writer service; single injection point for all ledger writes
- `LegalDomainLedgerHandler` — prefers task-level `jurisdiction` over `casehub.life.jurisdiction` config (life#48)
- `LifeDecisionLedgerObserver` — CDI observer; bridges domain events to ledger entries
- `LifeGdprErasureService` (life#49) — dedicated GDPR erasure pipeline integrating `LedgerErasureService.erase()` for actor ID tokenisation. Replaces `ExternalActorService.erase()`
- GDPR Art.17 erasure endpoint: `DELETE /external-actors/{id}/personal-data` — returns 200 with `ErasureResponse` (was 204, life#50)
- actorId convention: `"life-system"` (platform actions) / `"household-admin"` (admin actions)
- Flyway: `db/life/ledger/migration/` (V2100+) on qhorus datasource
- Entity package: `io.casehub.life.app.ledger` (not `entity/ledger` — multi-PU prefix matching constraint forces app-level package)
- 90 tests pass (life#5). Design spec: `docs/specs/2026-05-30-layer4-casehub-ledger-design.md`

## What It Does NOT Own

Foundation capabilities that casehub-life consumes but does not implement:

- Trust scoring — casehub-ledger
- Commitment lifecycle — casehub-qhorus
- Case engine and `CasePlanModel` execution — casehub-engine
- WorkItem inbox with SLA — casehub-work
- Notification delivery — casehub-connectors
- Skill execution — casehub-openclaw

## Dependencies

```
casehub-life
  → casehub-platform-oidc     (Layer 8: OidcCurrentPrincipal, @RolesAllowed enforcement — life#40)
  → casehub-openclaw          (Layer 7: OpenClaw WorkerProvisioner, ChannelContextWindow)
  → casehub-engine            (Layer 5: CasePlanModel orchestration)
  → casehub-engine-work-adapter (HumanTaskScheduleHandler + WorkItemLifecycleAdapter)
  → casehub-engine-scheduler-quartz (Quartz worker execution)
  → casehub-ledger            (Layer 4: Merkle audit, GDPR erasure, trust scoring)
  → casehub-work              (Layer 2: WorkItems with SLA and escalation)
  → casehub-qhorus            (Layer 3: commitment lifecycle, oversight channel)
  → casehub-connectors-core   (household notifications)
```

## Key Epics

1. Project scaffold — Maven structure, CLAUDE.md, CI
2. Domain model — `LifeDomain`, `HouseholdTask`, `LifeGoal`, `LifeEvent`, `ExternalActor`, capability tags
3. casehub-work integration — household task WorkItems with SLA and escalation
4. casehub-qhorus integration — commitment tracking and oversight gates
5. casehub-ledger integration — Merkle audit and trust scoring for health/financial decisions
6. casehub-engine integration — `CasePlanModel` definitions and multi-step workflow orchestration
7. Trust routing — agent routing by `deadline-reliability`, `cost-accuracy`, and `factual-accuracy`
8. casehub-openclaw integration — OpenClaw as `WorkerProvisioner`; household skill pack

Issues: https://github.com/casehubio/life/issues?label=epic
