# casehub-engine — Platform Deep Dive

**GitHub:** [casehubio/engine](https://github.com/casehubio/engine) (local: `casehub-engine`)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/PLATFORM.md)

> **Note:** The original `casehub` repo (local: `~/claude/casehub-poc`) is retiring. Do not add features there. All active development is in `casehub-engine`.

---

## Purpose

Hybrid choreography+orchestration coordination engine for multi-agent work. Implements the Blackboard Architecture with CMMN terminology. Coordinates workers (AI agents, humans) via case definitions, binding rules, and optional synchronous orchestration.

---

## Module Structure

| Module | Type | Purpose |
|---|---|---|
| `engine-model` | Pure POJOs (no Quarkus) | `CaseMetaModel`, `CaseInstance`, `EventLog`; persistence SPIs |
| `engine` | Quarkus module | Choreography handlers, orchestration, worker scheduling, Quartz integration |
| `api` | SPI definitions | 8 worker provisioner SPIs (4 blocking + 4 reactive) |
| `casehub-blackboard` | Optional module | CMMN/Blackboard orchestration layer |
| `casehub-ledger` | Optional module | `CaseLedgerEntry` subclass of `LedgerEntry`; `CaseLedgerEventCapture` |
| `casehub-work-adapter` | Module | Bridges `WorkItemLifecycleEvent` → `PlanItem` transitions |
| `casehub-persistence-hibernate` | Module | JPA/Panache persistence implementations |

---

## Key Abstractions

### Core Model (`engine-model`)

| Class | Purpose |
|---|---|
| `CaseMetaModel` | Case definition — capabilities, workers, bindings, goals, milestones (YAML DSL) |
| `CaseInstance` | Running case — status: PENDING / RUNNING / WAITING / COMPLETED / FAULTED / CANCELLED |
| `EventLog` | Append-only decision audit trail (engine-internal; used for restart recovery) |
| `CaseLifecycleEvent` | CDI event fired async on case transitions |

### Engine Handlers

| Bean | Purpose |
|---|---|
| `CaseContextChangedEventHandler` | Choreography path — evaluates bindings on context change |
| `WorkerScheduleEventHandler` | Schedules work via Quartz |
| `WorkflowExecutionCompletedHandler` | Resumes WAITING cases |
| `WorkOrchestrator` | `submitAndWait()` — orchestration: suspends case, returns `CompletionStage<WorkResult>` |
| `PendingWorkRegistry` | Restart-durable orchestration correlation |

`WorkBroker` (from `casehub-work-core`) is used for worker selection. casehub-engine does NOT depend on the casehub-work runtime.

### Worker Provisioner SPIs (`api/spi/`)

These are operational contracts — environment-specific implementations belong in the deploying app (Claudony):

| SPI | Purpose |
|---|---|
| `WorkerProvisioner` / `ReactiveWorkerProvisioner` | Provision and terminate workers |
| `WorkerStatusListener` / `ReactiveWorkerStatusListener` | Worker lifecycle callbacks (started, completed, stalled) |
| `CaseChannelProvider` / `ReactiveCaseChannelProvider` | Open/close/post to backend-agnostic channels |
| `WorkerContextProvider` / `ReactiveWorkerContextProvider` | Build worker startup context from ledger lineage |

Default no-op implementations: `NoOpWorkerProvisioner`, `NoOpWorkerStatusListener`, `NoOpCaseChannelProvider`, `EmptyWorkerContextProvider`.

### Ledger Integration (`casehub-ledger`)

| Class | Purpose |
|---|---|
| `CaseLedgerEntry` | `LedgerEntry` subclass with `caseId`, `commandType`, `eventType`, `caseStatus` |
| `CaseLedgerEventCapture` | `@ObservesAsync CaseLifecycleEvent` → writes ledger entry |

Status: `casehub-ledger` module exists in a `feat/casehub-ledger-integration` branch — not yet merged to main.

### Work Adapter (`casehub-work-adapter`)

Bridges `WorkItemLifecycleEvent` CDI events to `PlanItem` transitions via `BlackboardRegistry`. Choreography path only. Uses `CallerRef.parse()` to extract `caseId` and `planItemId` from `WorkItem.callerRef`.

`callerRef` format: `case:{caseId}/pi:{planItemId}` — use `CallerRef.encode()` / `CallerRef.parse()`.

---

## Depends On

| Repo | How |
|---|---|
| `casehub-work-core` | `WorkBroker` and selection strategies — NOT the casehub-work runtime |
| `quarkus-ledger` | Optional, via `casehub-ledger` module |

## Depended On By

| Repo | How |
|---|---|
| `claudony` | Implements the 4 worker provisioner SPIs in `claudony-casehub` module |

---

## What This Repo Explicitly Does NOT Do

- Manage human task inboxes (that is casehub-work)
- Handle agent-to-agent messaging protocols (that is quarkus-qhorus)
- Provide a terminal/session UI (that is claudony)
- Implement worker provisioner SPIs — only defines the contracts
- Include Flyway migrations (Hibernate `drop-and-create` for now — no prod instances)

---

## Schema Management

No Flyway — Hibernate `drop-and-create` only:
```properties
quarkus.hibernate-orm.schema-management.strategy=drop-and-create
```
No Quartz JDBC store — RAM store only:
```properties
quarkus.quartz.store-type=ram
```

---

## Two Audit Mechanisms (Known Gap)

- `EventLog` — engine-internal, append-only, used for restart recovery via `PendingWorkRegistry`
- `CaseLedgerEntry` — external, tamper-evident, written via `@ObservesAsync CaseLifecycleEvent`

These are complementary, not redundant. A lifecycle transition that doesn't fire `CaseLifecycleEvent` won't be captured in the external ledger.

---

## Current State

- Active development. Core choreography and orchestration done.
- WAITING state durability (restart-safe) done.
- `casehub-ledger` integration done but unmerged.
- Worker↔Session↔Channel triple correlation (for Claudony dashboard) not yet stored.
- Human worker integration, escalation rules, lineage-driven planning still ahead.

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/engine/main/docs/DESIGN.md) — choreography+orchestration models, worker SPI contracts, ledger integration
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/engine/main/adr/INDEX.md) — architectural decision records (ADR-0003 naming, ADR-0004 claim SLA, ADR-0005 provisioner SPI placement, ADR-0006 worker registration as normative act)
