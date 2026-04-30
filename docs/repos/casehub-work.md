# casehub-work — Platform Deep Dive

**GitHub:** [casehubio/work](https://github.com/casehubio/work)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Human task lifecycle management extension. Provides a human task inbox (WorkItem) with status lifecycle, SLA, delegation, escalation, spawn, and audit trail. Usable standalone or integrated with CaseHub and Qhorus.

A `WorkItem` is deliberately NOT called `Task` — CNCF Serverless Workflow and CaseHub both have `Task` concepts with different semantics.

---

## Module Structure

| Module | Type | Purpose |
|---|---|---|
| `casehub-work-api` | Pure-Java SPI (no Quarkus) | All SPIs: `WorkerSelectionStrategy`, `WorkerRegistry`, `WorkloadProvider`, `EscalationPolicy`, `SpawnPort`, `SkillProfile*`, `NotificationChannel` |
| `casehub-work-core` | Jandex library (no JPA) | `WorkBroker`, `LeastLoadedStrategy`, `ClaimFirstStrategy`, `NoOpWorkerRegistry` — used directly by casehub-engine |
| `runtime` | Full Quarkus extension | `WorkItem` entity, services, REST API, filter engine |
| `casehub-work-ledger` | Optional module | Attaches casehub-ledger for `WorkItemLedgerEntry` |
| `casehub-work-queues` | Optional module | Label-based queue views |
| `casehub-work-ai` | Optional module | `SemanticWorkerSelectionStrategy`, `LowConfidenceFilterProducer` |
| `casehub-work-notifications` | Optional module | Slack/Teams/webhook outbound notifications |
| `casehub-work-reports` | Optional module | SLA compliance reporting (`/workitems/reports/*`) |
| `work-flow` | Optional module | Quarkus-Flow CDI bridge |
| `casehub-work-testing` | Test utilities | `InMemoryWorkItemStore`, `InMemoryAuditEntryStore` |

---

## Key Abstractions

### WorkItem Entity

10 statuses: PENDING → ASSIGNED → IN_PROGRESS → COMPLETED / CANCELLED / EXPIRED / DELEGATED / REJECTED / ON_HOLD / CLAIM_EXPIRED

Key fields: `title`, `description`, `assigneeId`, `candidateUsers`, `candidateGroups`, `priority`, `category`, `deadline`, `claimDeadline`, `labels`, `callerRef` (opaque — CaseHub stores `case:{id}/pi:{planItemId}` here), `formSchemaId`, `formPayload`

### Core Services

| Bean | Purpose |
|---|---|
| `WorkItemService` | Lifecycle management: create, start, complete, cancel, delegate, expire |
| `WorkItemAssignmentService` | Routing via `WorkBroker` → `WorkerSelectionStrategy` |
| `WorkItemSpawnService` | Child spawning with idempotency key; implements `SpawnPort` |
| `FilterRegistryEngine` | JEXL/JQ condition evaluation for label-based routing |
| `MultiInstanceSpawnService` | Creates parent + spawn group + N children for M-of-N templates |
| `MultiInstanceCoordinator` | `@ObservesAsync` — drives group policy on child terminal events |
| `MultiInstanceGroupPolicy` | OCC M-of-N counter update and parent transition |

### REST API

- `GET/POST /workitems` — inbox + creation
- `GET /workitems/inbox` — always returns thread roots (`parentId IS NULL`) with aggregate stats; coordinator parents visible via descendant assignment
- `POST /workitems/{id}/start|complete|cancel|delegate`
- `GET /workitems/{id}/audit` — audit history
- `GET /workitems/{id}/instances` — child instances with group summary (M-of-N progress)
- `GET /workitems/reports` — SLA compliance reporting
- `GET/POST /filter-rules` — dynamic filter rules
- `POST /workitems/{id}/spawn` — child WorkItem creation

### CDI Events

`WorkItemLifecycleEvent` fired on every status transition. Carries `callerRef` opaquely — CaseHub uses it to route completions back to the right `PlanItem`.

---

## Depends On

- `casehub-ledger` — optional only, via `casehub-work-ledger` module. Core has zero casehubio deps.

## Depended On By

| Repo | How |
|---|---|
| `casehub-engine` | `casehub-work-core` only — `WorkBroker` for worker selection. NOT the full runtime. |
| `claudony` | Future, via `casehub-work-casehub` adapter (currently blocked on CaseHub stability) |

---

## What This Repo Explicitly Does NOT Do

- Orchestrate — it fires events and provides primitives. It does not decide what completing a WorkItem means.
- **Heterogeneous plan-item completion** — whether named plan items A, B, and C have all completed to advance a Stage; that is CaseHub (see LAYERING.md). Homogeneous M-of-N group completion IS casehub-work (`MultiInstanceCoordinator`).
- Interpret `callerRef` — stored and echoed opaquely.
- Provision or manage AI agents (that is CaseHub/Claudony).
- Know when to spawn child WorkItems (callers drive spawn via `SpawnPort`).

---

## The Core/Runtime Split (Critical for casehub-engine)

`casehub-work-core` is a Jandex library (not a Quarkus extension) containing only `WorkBroker` and selection strategies. casehub-engine depends on this module — it gets worker routing without pulling in WorkItem entities, Flyway migrations, REST resources, or datasource requirements.

The `WorkBroker` is generic: it routes any work unit, not just WorkItems.

---

## Notification Concern

`casehub-work-notifications` currently ships Slack/Teams/webhook directly. This overlaps with `casehub-connectors`. Future direction: delegate to `casehub-connectors` `Connector` SPI rather than maintaining a parallel implementation.

---

## Current State

- 637+ tests passing in runtime module; native image validated at 0.084s startup
- All major epics complete: Business-Hours Deadlines (#101), SLA Compliance Reporting (#104), Multi-Instance Tasks (#106)
- Pending: `casehub-work-qhorus` adapter (MCP tools for agent-driven approval flows)

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/work/main/docs/DESIGN.md) — implementation-tracking design doc
- [docs/architecture/LAYERING.md](https://raw.githubusercontent.com/casehubio/work/main/docs/architecture/LAYERING.md) — definitive boundary statement between casehub-work and CaseHub
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/work/main/adr/INDEX.md) — architectural decision records
