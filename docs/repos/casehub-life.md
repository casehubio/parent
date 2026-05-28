# casehub-life

**GitHub:** [casehubio/life](https://github.com/casehubio/life)
**Tier:** Application
**Status:** Layer 2 complete (2026-05-27) — casehub-work integration

## What It Is

Personal life automation application on the CaseHub harness. Coordinates household management, health, finance, family obligations, elder care — producing a formally tracked, SLA-enforced, optionally tamper-evident record of life obligations. Field showcase and tutorial for developers evaluating CaseHub for personal automation.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence. Each layer adds one foundation module and makes its value tangible relative to the previous layer.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Domain baseline — household domain model | Baseline: direct service calls, no SLA, no audit | **complete** (casehubio/life#2) |
| 2 | casehub-work | No formal SLA on household tasks | **complete** (casehubio/life#3, 2026-05-27) |
| 3 | casehub-qhorus | No commitment tracking; no oversight gates | pending |
| 4 | casehub-ledger | No tamper-evident audit for health/financial decisions | pending |
| 5 | casehub-engine | No multi-step workflow orchestration | pending |
| 6 | Trust routing | No trust model for agent routing | pending |
| 7 | casehub-openclaw | OpenClaw as WorkerProvisioner; pre-built skill ecosystem | pending |

## What It Owns

- `LifeDomain` enum: `HEALTH`, `FINANCE`, `HOUSEHOLD`, `LEGAL`, `CARE`, `TRAVEL`
- Domain model: `ExternalActor`, `LifeTaskContext` (domain supplement: `domain`, `priority`, `externalActorId`, deadline context — held alongside the foundation `WorkItem`)
- Capability tags: `household-management`, `health-coordination`, `financial-planning`, `family-scheduling`, `travel-planning`, `legal-deadline`, `contractor-coordination`
- Trust dimensions: `deadline-reliability`, `cost-accuracy`, `factual-accuracy`, `proactive-alerting`
- `CasePlanModel` definitions: `appointment-cycle`, `home-maintenance-cycle`, `financial-review`, `travel-plan`, `contractor-coordination`, `care-coordination`
- Household permission topology: `household-admin` > `household-member` > `household-junior`
- M-of-N quorum configuration for joint decisions
- Flyway path: `classpath:db/life/migration/` (PP-20260525-607b33)

### Layer 2 — casehub-work integration

- `POST /life-tasks` — creates `WorkItem` + `LifeTaskContext` atomically via `WorkItemTemplate` lookup
- `LifeSlaBreachPolicy` — implements `casehub-work` `SlaBreachPolicy` SPI; stateless two-tier escalation: first breach escalates to `household-admin`, second breach fails

## Current State

Household tasks are now formal `WorkItem`s: SLA-enforced, delegable, auditable. `LifeTaskContext` supplements each task with life-specific fields. `LifeSlaBreachPolicy` escalates to `household-admin` on first breach, fails on second. Domain model correction in Layer 2: `HouseholdTask`, `LifeGoal`, `LifeEvent` removed — they duplicated `WorkItem`, case definitions, and ledger entries respectively.

**Engine deps temporarily removed** from `pom.xml` — SNAPSHOT build broken (engine#379, engine#380). Will be restored in Layer 5 branch. Layers 3–7 remain pending.

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
