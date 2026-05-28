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
| `casehub-work-api` | Pure-Java SPI (no Quarkus) | All SPIs: worker selection, registry, workload provision, SLA breach policy, spawn, skill profiling, notification channel. Depends on `casehub-platform-api` for `Path` and `Preferences` used in `SlaBreachContext`. Also owns `ActorType` / `ActorTypeResolver` via `casehub-platform-api` (moved there in ledger#88). |
| `casehub-work-core` | Jandex library (no JPA) | `WorkBroker` and built-in `WorkerSelectionStrategy` implementations — used for human task routing only; casehub-engine uses its own `AgentRoutingStrategy` SPI (engine#337) |
| `runtime` | Full Quarkus extension | WorkItem entity, services, REST API, filter engine |
| `deployment` | Quarkus extension deployment | Build-time processor (`@BuildStep`); pairs with `runtime` |
| `casehub-work-testing` | Test utilities | In-memory stores (WorkItem, audit, notes, issue links); zero-datasource alternative to JPA stores |
| `casehub-work-ledger` | Optional module | Attaches casehub-ledger for WorkItem ledger entries, trust scoring, and peer attestation. Requires both `db/migration` and `db/ledger/migration` Flyway locations in test config (since ledger#95 moved base migrations). |
| `casehub-work-queues` | Optional module | Label-based queue views with JEXL/JQ filter expressions |
| `casehub-work-queues-dashboard` | Optional module | SSE-based queue dashboard UI |
| `casehub-work-queues-postgres-broadcaster` | Optional module | Distributed SSE for queue events via PostgreSQL LISTEN/NOTIFY |
| `casehub-work-ai` | Optional module | Embedding-based semantic worker selection; confidence-gated filter routing |
| `casehub-work-notifications` | Optional module | Slack/Teams/webhook outbound notifications on lifecycle events |
| `casehub-work-reports` | Optional module | SLA compliance reporting (breach rates, actor performance, throughput, queue health) |
| `casehub-work-issue-tracker` | Optional module | Links WorkItems to GitHub/Jira issues; inbound webhook handler for close/reopen events |
| `casehub-work-postgres-broadcaster` | Optional module | Distributed SSE for WorkItem events via PostgreSQL LISTEN/NOTIFY |
| `casehub-work-persistence-mongodb` | Optional module | MongoDB-backed `WorkItemStore` alternative |
| `work-flow` | Optional module | Quarkus-Flow CDI bridge (`HumanTaskFlowBridge`, `PendingWorkItemRegistry`) |
| `casehub-work-examples` | Runnable scenarios | Demo scenarios (credit, moderation, audit search, spawn, business hours, etc.) |
| `integration-tests` | Black-box test suite | `@QuarkusIntegrationTest` + native image validation (25 tests) |

---

## Key Abstractions

### WorkItem Entity

10-status lifecycle from creation through terminal states (pending, assigned, in-progress, completed, cancelled, expired, delegated, rejected, on-hold, claim-expired).

**Key field:** `scope VARCHAR(255)` (V31 migration) — hierarchical scope path for SLA preference resolution via `casehub-platform-api`'s `Path` type; null = org root. Set by callers; propagated from casehub-engine via `HumanTaskTarget.scope` (engine#330).

See `docs/DESIGN.md` for status enumeration and field model.

### Core Services

Services cover: WorkItem lifecycle management (create, claim, complete, delegate, expire, cancel) with schema validation against templates; template CRUD and instantiation with payload override support; worker assignment via pluggable selection strategies; conflict-of-interest exclusion policy; M-of-N parallel group completion coordination; child spawning with idempotency; label-based filter routing; and SLA compliance reporting.

See `docs/DESIGN.md` for service class structure and the M-of-N coordination model.

**Inbox query:** `WorkItemStore.scanRoots(assignee, candidateUser, candidateGroups)` — three independent OR predicates; returns root WorkItems (no `parentId`) including parents of visible children.

### REST API

REST endpoints cover: WorkItem inbox and creation, lifecycle transitions (start, complete, cancel, delegate), audit history, child instance queries with group progress, SLA compliance reports, dynamic filter rules, and child WorkItem spawning.

See `docs/DESIGN.md` for the full endpoint inventory.

### CDI Events

A lifecycle event fires on every status transition, carrying the transition details and an optional named outcome (the named completion classification from the WorkItem's template). The outcome field lets downstream adapters switch on completion type without parsing the resolution payload.

See `docs/DESIGN.md` for event payload shape.

### SPI Reference (casehub-work-api)

| SPI | Method | Description |
|---|---|---|
| `WorkerSelectionStrategy` | `select(SelectionContext, List<WorkerCandidate>)` | Pluggable routing — LeastLoaded (default), ClaimFirst, RoundRobin built-in |
| `WorkerRegistry` | `resolveGroup(String)` | Resolves candidateGroup names to `WorkerCandidate` objects |
| `WorkloadProvider` | `getActiveWorkCount(String)` | Active WorkItem count per worker (used by LeastLoaded) |
| `SlaBreachPolicy` | `onBreach(SlaBreachContext) → BreachDecision` | SLA breach handling: returns `Fail`, `EscalateTo(groups, deadline)`, `Extend(by)`, or `Chained`. Replaces removed `EscalationPolicy`. |
| `ExclusionPolicy` | `check(userId, excludedUsers) → PolicyDecision` | Conflict-of-interest user exclusion |
| `SpawnPort` | `spawn(SpawnRequest) → SpawnResult` | Child WorkItem creation with idempotency |
| `AssignmentTrigger` | enum | Values: `CREATED`, `RELEASED`, `DELEGATED`, `SLA_ESCALATED` — strategies subscribe via `triggers()` |
| `SlaBreachPolicy` | `onBreach(SlaBreachContext) → BreachDecision` | `SlaBreachContext` carries `BreachType` (CLAIM_EXPIRED / COMPLETION_EXPIRED), `BreachedTask`, `Path scope`, and `Preferences`. `SLA_ESCALATED` trigger fires after `EscalateTo` execution — strategies pre-assign before `put()`. |

---

## Depends On

- `casehub-platform-api` — production dep in `casehub-work-api` for `Path`, `Preferences`, `ActorType`, and `ActorTypeResolver`. Zero-dep pure-Java; does not force Quarkus on consumers. `ActorType`/`ActorTypeResolver` moved here from `casehub-ledger` in ledger#88 — any module using these types must import from `io.casehub.platform.api.identity`, not `io.casehub.ledger.api.model`.
- `casehub-platform` (mock module) — `test` scope in library/extension modules; `runtime` scope in application modules running `quarkus:build`. Provides `MockPreferenceProvider @DefaultBean` so `@QuarkusTest` augmentation satisfies the `PreferenceProvider` CDI dep. Must be Jandex-indexed.
- `casehub-ledger` — optional only, via `casehub-work-ledger` module. Core has zero other casehubio deps.

## Depended On By

| Repo | How |
|---|---|
| `casehub-engine` | `casehub-work-api` only (compile, via work-adapter — `CaseSignalSink` injection). Routing no longer uses `casehub-work-core`/`WorkBroker` — engine uses its own `AgentRoutingStrategy` SPI (engine#337). Receives `WorkItemLifecycleEvent` and `WorkItemGroupLifecycleEvent` via CDI adapter to drive plan-item transitions. |
| `claudony` | Future, via `casehub-work-casehub` adapter (currently blocked on CaseHub stability) |
| `casehub-clinical` | Layer 2 — adverse event WorkItems with GCP SLA (24h Grade≥3, 1h Grade 5); first consumer of `SlaBreachPolicy` with DSMB escalation |

---

## What This Repo Explicitly Does NOT Do

- Orchestrate — it fires events and provides primitives. It does not decide what completing a WorkItem means.
- **Heterogeneous plan-item completion** — whether named plan items A, B, and C have all completed to advance a Stage; that is CaseHub (see LAYERING.md). Homogeneous M-of-N group completion IS casehub-work (multi-instance coordinator).
- Interpret `callerRef` — stored and echoed opaquely.
- Provision or manage AI agents (that is CaseHub/Claudony).
- Know when to spawn child WorkItems (callers drive spawn via `SpawnPort`).

---

## The Core/Runtime Split (Critical for casehub-engine)

`casehub-work-core` is a Jandex library (not a Quarkus extension) containing only `WorkBroker` and selection strategies. casehub-engine depends on this module — it gets worker routing without pulling in WorkItem entities, Flyway migrations, REST resources, or datasource requirements.

The `WorkBroker` is generic: it routes any work unit, not just WorkItems.

---

## Notification Concern

`casehub-work-notifications` currently ships Slack/Teams/webhook directly. This overlaps with `casehub-connectors`. Future direction: delegate to `casehub-connectors` connector SPI rather than maintaining a parallel implementation.

---

## Flyway Version Ranges

Each optional module owns a dedicated V-number range to prevent collision when multiple modules are loaded together:

| Range | Module |
|---|---|
| V1–V999 | `runtime` (sequential; currently at V31) |
| V2000–V2999 | `casehub-work-queues` and `casehub-work-ledger` |
| V3000–V3999 | `casehub-work-notifications` |
| V4000–V4999 | `casehub-work-ai` |
| V5000–V5999 | `casehub-work-issue-tracker` |
| V6000+ | next new optional module |

**casehub-ledger#95 note:** ledger base migrations now live at `classpath:db/ledger/migration/` (not `db/migration/`). Any module consuming `casehub-work-ledger` must configure `quarkus.flyway.locations=db/migration,db/ledger/migration` in test `application.properties`.

---

## Current State

- 746 tests in runtime module; 60 in api; 84 in queues; 73 in reports; 76 in ledger; 93 in issue-tracker; 25 integration tests. Native image validated.
- All major epics complete through #218 (CI fixes, platform-api scope rules)
- Blocking: engine#330 — `HumanTaskTarget.scope` propagation (small, unblocked)
- Pending: `casehub-work-qhorus` adapter (MCP tools for agent-driven approval flows)

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/work/main/docs/DESIGN.md) — implementation-tracking design doc
- [docs/ARCHITECTURE.md](https://raw.githubusercontent.com/casehubio/work/main/docs/ARCHITECTURE.md) — module graph, domain model, SPI contracts
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/work/main/adr/INDEX.md) — architectural decision records
