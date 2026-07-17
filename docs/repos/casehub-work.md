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
| `casehub-work-api` | Pure-Java SPI (no Quarkus) | All SPIs: worker selection, registry, workload provision, SLA breach policy, spawn, skill profiling, notification channel, and WorkItem lifecycle SPIs (`io.casehub.work.api.spi`). Depends on `casehub-platform-api` for `Path` and `Preferences` used in `SlaBreachContext`. Also owns `ActorType` / `ActorTypeResolver` via `casehub-platform-api` (moved there in ledger#88). `WorkCloudEventTypes` — pure-Java CloudEvent type constants (`io.casehub.work.workitem.*` prefix, extension attribute names `tenancyid`/`templateid`). New in engine#56: `WorkItemCallerRef.parseCaseId(String callerRef): UUID`. New in work#275: `WorkItemCreator`, `WorkItemLifecycle` SPIs + `WorkItemRef`, `WorkItemEvent`, `WorkItemSpiAdapter` types in `io.casehub.work.api.spi`. |
| `casehub-work-core` | Jandex library (no JPA) | `WorkBroker` and built-in `WorkerSelectionStrategy` implementations — used for human task routing only; casehub-engine uses its own `AgentRoutingStrategy` SPI (engine#337) |
| `runtime` | Full Quarkus extension | WorkItem entity, services, filter engine |
| `rest` | Jandex library | JAX-RS resources (12), request/response DTOs, exception mappers, WorkItemMapper — opt-in REST surface (work#292). No `quarkus:build` goal — library JAR, not an application. |
| `deployment` | Quarkus extension deployment | Build-time processor (`@BuildStep`); pairs with `runtime` |
| `casehub-work-persistence-memory` (`persistence-memory/`) | Test utilities | In-memory stores (WorkItem, audit, notes, issue links, routing cursor) using `ConcurrentHashMap` (thread-safe); `@Alternative @Priority(100)` (Tier 3 — ephemeral); zero-datasource alternative to JPA stores |
| `casehub-work-ledger` | Optional module | Attaches casehub-ledger for WorkItem ledger entries, trust scoring, and peer attestation. Requires both `db/migration` and `db/ledger/migration` Flyway locations in test config (since ledger#95 moved base migrations). |
| `casehub-work-queues` | Optional module | Label-based queue views with JEXL/JQ filter expressions, periodic trend snapshots (`QueueSnapshotJob`, Quartz-scheduled), `GET /queues/{id}/trend` and `GET /queues/{id}/summary` REST endpoints |
| `casehub-work-queues-dashboard` | Optional module | SSE-based queue dashboard UI |
| `casehub-work-queues-postgres-broadcaster` | Optional module | Distributed SSE for queue events via PostgreSQL LISTEN/NOTIFY |
| `casehub-work-ai` | Optional module | Embedding-based semantic worker selection; confidence-gated filter routing |
| `casehub-work-notifications` | Optional module | Slack/Teams/webhook outbound notifications on lifecycle events |
| `casehub-work-reports` | Optional module | SLA compliance reporting (breach rates, actor performance, throughput, queue health) |
| `casehub-work-issue-tracker` | Optional module | Links WorkItems to GitHub/Jira issues; inbound webhook handler for close/reopen events |
| `casehub-work-postgres-broadcaster` | Optional module | Distributed SSE for WorkItem events via PostgreSQL LISTEN/NOTIFY |
| `casehub-work-persistence-mongodb` | Optional module | MongoDB-backed persistence — 13 tenant-scoped stores + 3 cross-tenant stores (`@CrossTenant`). Unique compound indexes via `MongoIndexInitializer`. `MongoTenancyMigration` backfills default tenancy on existing documents at startup. |
| `work-flow` | Optional module | Quarkus-Flow CDI bridge (`HumanTaskFlowBridge`, `PendingWorkItemRegistry`) |
| `casehub-work-engine-adapter` (`engine-adapter/`) | Bridge module | Two-way bridge between casehub-work WorkItem lifecycle and CaseHub engine blackboard PlanItem transitions. Relocated from `casehub-engine/work-adapter`. Contains: `HumanTaskScheduleHandler` (outbound), `WorkItemLifecycleAdapter` (inbound), `ActionGateWorkItemHandler`/`ActionGateCompletionApplier` (gate bridge), `WorkStrategyContributor` (NamedStrategy registration), `HumanTaskRecoveryService` (startup recovery), `JpaPlanItemStore`. |
| `casehub-work-examples` | Runnable scenarios | Demo scenarios (credit, moderation, audit search, spawn, business hours, etc.) |
| `casehub-work-queues-examples` (`queues-examples/`) | Runnable scenarios | Queue pattern demonstrations: security escalation, queue lifecycle, support triage, document review, finance approval, legal routing |
| `casehub-work-flow-examples` (`flow-examples/`) | Runnable scenarios | WorkItemsFlow DSL integration: contract review workflow with candidateGroups, assigneeId, priority, payloadFrom, suspension/resume cycle |
| `integration-tests` | Black-box test suite | `@QuarkusIntegrationTest` + native image validation (25 tests) |
| `integration-tests-memory` | Black-box test suite | Verifies boot and CRUD through in-memory stores (`casehub-work-persistence-memory`) with dummy H2 datasource — no Flyway, schema auto-generated. All persistence via `@Alternative @Priority(100)`. |

---

## Key Abstractions

### WorkItem Entity

10-status lifecycle from creation through terminal states (pending, assigned, in-progress, completed, cancelled, expired, delegated, rejected, on-hold, claim-expired).

`DELEGATED` is a pre-acceptance state — item forwarded to a named actor who must explicitly accept (`PUT /workitems/{id}/accept-delegation?claimant=X`) or decline (`PUT /workitems/{id}/decline-delegation?actor=X`); non-terminal (`isTerminal()` = false, `isActive()` = true; can expire). On decline, `DELEGATION_DECLINED` fires the `AssignmentTrigger` and the item returns to `PENDING` (POOL) or `ASSIGNED` (DELEGATOR) per `DeclineTarget` scope preference (`casehub.work.delegation.decline-target`: POOL/DELEGATOR, default POOL). `EXPIRED` and `ESCALATED` are both terminal.

**Key fields:**
- `scope VARCHAR(255)` (V31 migration) — hierarchical scope path for SLA preference resolution via `casehub-platform-api`'s `Path` type; null = org root. Set by callers; propagated from casehub-engine via `HumanTaskTarget.scope` (engine#330).
- `types: List<String>` (work#291) — hierarchical type classification (replaces legacy `category` String). REST queries accept `type` param for filtering; responses include `types` and `typePaths` (CSV). `WorkItemLifecycleEvent` carries `types`. Migration from `category` complete across all modules (notifications, AI, reports, queues, MongoDB). `WorkItemCreateRequest.types` is `List<String>`; `SelectionContext` also uses `List<String> types`.

See `docs/ARC42STORIES.MD` for status enumeration and field model.

### Core Services

Services cover: WorkItem lifecycle management (create, claim, complete, delegate, expire, cancel) with schema validation against templates; template CRUD and instantiation with payload override support; worker assignment via pluggable selection strategies; conflict-of-interest exclusion policy; M-of-N parallel group completion coordination; child spawning with idempotency; label-based filter routing; and SLA compliance reporting.

See `docs/ARC42STORIES.MD` for service class structure and the M-of-N coordination model.

**Inbox query:** `WorkItemStore.scanRoots(assignee, candidateUser, candidateGroups)` — three independent OR predicates; returns root WorkItems (no `parentId`) including parents of visible children.

### Conditional Outcomes (work#177)

`Outcome` is now a 3-arg record: `Outcome(String name, String displayName, String condition)`. The `condition` field is a nullable JEXL expression evaluated at completion/rejection. `WorkItem.permittedOutcomes` stores full `Outcome` objects (not plain name strings); legacy rows are decoded transparently via format detection. `OutcomeValidator` (`runtime/service/`) encapsulates outcome name + condition validation, injected into `WorkItemService`. REST responses `WorkItemResponse.permittedOutcomes` and `WorkItemWithAuditResponse.permittedOutcomes` are now `List<Outcome>` (was `List<String>`).

### REST API (casehub-work-rest module)

REST endpoints live in the `rest/` module (`casehub-work-rest`) — opt-in via explicit dependency (work#292). Covers: WorkItem inbox and creation, lifecycle transitions (start, complete, cancel, delegate, accept-delegation, decline-delegation), audit history, child instance queries with group progress, SLA compliance reports, dynamic filter rules, and child WorkItem spawning.

**`PATCH /workitem-templates/{id}`** (work#199) — merge-patch endpoint (`Content-Type: application/merge-patch+json`, RFC 7396). Absent fields are unchanged; null clears.

See `docs/DESIGN.md` for the full endpoint inventory.

### WorkItem SPI Types (work#275)

`WorkItemRef` — lightweight reference to a WorkItem carrying template, callerRef, payload, and `tenancyId`. Used as the creation argument for `WorkItemCreator.create()` — decouples callers from the full `WorkItem` entity.

`WorkItemEvent` — interface for WorkItem lifecycle events consumed by SPI implementations. Provides `ref()` (WorkItemRef), `eventType()` (WorkEventType), `occurredAt()`, `actor()`, `detail()`, plus default methods delegating to ref: `workItemId()`, `status()`, `callerRef()`, `assigneeId()`, `resolution()`, `candidateGroups()`, `outcome()`, `tenancyId()`.

`WorkItemStatusEvent` — record carrying the SPI-visible subset: eventType, workItemId, status, actor, detail, callerRef, assigneeId, candidateGroups, outcome, tenancyId, occurredAt. This is what `WorkItemObserver.onStatusChange()` receives.

`WorkEventType` — enum with 24+ values including: CREATED, ASSIGNED, STARTED, COMPLETED, REJECTED, FAULTED, DELEGATED, DELEGATION_ACCEPTED, DELEGATION_DECLINED, RELEASED, SUSPENDED, RESUMED, CANCELLED, OBSOLETE, EXPIRED, CLAIM_EXPIRED, SPAWNED, ESCALATED, DEADLINE_EXTENDED, SLA_REASSIGNED, SLA_EXTENDED, SIGNAL_RECEIVED, MANUALLY_ESCALATED, PROGRESS_UPDATE, LABEL_ADDED, LABEL_REMOVED.

`WorkItemSpiAdapter` — adapter that bridges `WorkItemCreator` and `WorkItemLifecycle` SPI calls to the runtime `WorkItemService`. Lives in runtime; SPI consumers depend on `casehub-work-api` only. Template creation unified via `createFromTemplate()`.

### CDI Events

A lifecycle event fires on every status transition, carrying the transition details and an optional named outcome (the named completion classification from the WorkItem's template). The outcome field lets downstream adapters switch on completion type without parsing the resolution payload.

See `docs/DESIGN.md` for event payload shape.

### GroupStatus Lifecycle (`casehub-work-api`)

`GroupStatus` enum — aggregate lifecycle for multi-instance WorkItem groups:
- `IN_PROGRESS` — group still accepting completions, threshold not yet reached
- `COMPLETED` — threshold reached with majority approval
- `REJECTED` — threshold reached with majority rejection or escalation

`isTerminal()` (COMPLETED or REJECTED), `isActive()` (IN_PROGRESS). Used by `WorkItemGroupLifecycleEvent` which carries: parentId, groupId, instanceCount, requiredCount, completedCount, rejectedCount, groupStatus, callerRef, tenancyId, occurredAt. Persisted on `WorkItemSpawnGroup`.

### Queue Trend Data (`casehub-work-queues`)

Periodic queue snapshot system for historical trend analysis:

- `QueueSnapshot` — JPA entity (`queue_snapshot` table): id, tenancyId, queueViewId, memberCount, snapshotAt
- `QueueSnapshotJob` — Quartz-scheduled (5m cycle, 30s delay). Per tenant: reads all queues, takes snapshot if enough time elapsed since last (configurable interval via `QueueSnapshotInterval` preference, default 1h), deletes snapshots older than retention period (`QueueTrendRetention` preference, default 7d).
- REST endpoints:
  - `GET /queues/{id}/summary` — real-time summary of queue contents
  - `GET /queues/{id}/trend?period=24h` — historical trend data from snapshots. `QueueTrendResponse` with `List<DataPoint>` (snapshotAt + memberCount). Supports `24h`, `7d`, or ISO Duration `PT24H`.
  - `GET /queues/{id}/events` — SSE stream of queue membership events (ADDED/REMOVED/CHANGED)

### Template Versioning

`WorkItemCreateRequest.templateVersion` (`Long`) — version of the template used at instantiation; null for non-template WorkItems. Enables template evolution tracking: consumers can determine which template version was active when a WorkItem was created.

### SPI Reference (casehub-work-api — 17 interfaces in `io.casehub.work.api.spi`)

| SPI | Method | Description |
|---|---|---|
| `WorkerSelectionStrategy` | `select(SelectionContext, List<WorkerCandidate>)` | Pluggable routing — LeastLoaded (default), ClaimFirst, RoundRobin built-in. **Extends `NamedStrategy`** (id selects active strategy, default: "least-loaded"). |
| `WorkerRegistry` | `resolveGroup(String)` | Resolves candidateGroup names to `WorkerCandidate` objects |
| `WorkloadProvider` | `getActiveWorkCount(String)` | Active WorkItem count per worker (used by LeastLoaded) |
| `SlaBreachPolicy` | `onBreach(SlaBreachContext) → BreachDecision` | SLA breach handling: returns `Fail`, `EscalateTo(groups, deadline)`, `Extend(by)`, `Chained`, or `Exhausted(String reason)` (all Chained branches fail — sets `WorkItemStatus.ESCALATED` terminal). **Extends `NamedStrategy`** (default: "no-op"). `SlaBreachContext` carries `BreachType` (CLAIM_EXPIRED / COMPLETION_EXPIRED), `BreachedTask`, `Path scope`, and `Preferences`. `SLA_ESCALATED` trigger fires after `EscalateTo` execution. |
| `ClaimSlaPolicy` | `computeClaimDeadline(...)` | Computes pool-phase deadline. **Extends `NamedStrategy`** (default: "continuation"). |
| `InstanceAssignmentStrategy` | `assign(...)` | Multi-instance assignment. **Extends `NamedStrategy`** (default: "pool"). |
| `ExclusionPolicy` | `check(userId, excludedUsers) → PolicyDecision` | Conflict-of-interest user exclusion |
| `SpawnPort` | `spawn(SpawnRequest) → SpawnResult` | Child WorkItem creation with idempotency |
| `AssignmentTrigger` | enum | Values: `CREATED`, `RELEASED`, `DELEGATED`, `SLA_ESCALATED`, `DELEGATION_DECLINED` — strategies subscribe via `triggers()` |
| `WorkItemCreator` | `create(WorkItemCreateRequest)`, `findByCallerRef(String)`, `findActiveByCallerRef(String)`, `obsoleteByCallerRef(String)` | WorkItem creation and caller reference lookup SPI. `callerRef` is NOT unique across lifecycle; find methods return most recent match. `obsoleteByCallerRef` marks as OBSOLETE (idempotent). |
| `WorkItemLifecycle` | `cancel(UUID)`, `complete(UUID, ...)` | WorkItem lifecycle transition SPI |
| `WorkItemObserver` | `onStatusChange(WorkItemStatusEvent)` | Lifecycle event observation SPI — called synchronously in the emitter's transaction context. Multiple observers may be registered. Lives in work-api to avoid circular dependencies. |
| `BusinessCalendar` | `addBusinessDuration(...)`, `isBusinessHour(...)` | Business-hours-aware deadline calculation |
| `HolidayCalendar` | `isHoliday(...)` | Sub-SPI for holiday data |
| `CapabilityRegistry` | (vocabulary validation) | Capability vocabulary validation |
| `SkillMatcher` | `score(...)` | Scores worker skill profiles against work items |
| `SkillProfileProvider` | `profile(...)` | Builds a worker's SkillProfile |
| `NotificationChannel` | `channelType()`, `send(...)` | Outbound notification delivery |

**NamedStrategy pattern:** Four SPIs extend `io.casehub.platform.api.routing.NamedStrategy` — `WorkerSelectionStrategy`, `SlaBreachPolicy`, `ClaimSlaPolicy`, `InstanceAssignmentStrategy`. The `WorkStrategyContributor` in engine-adapter registers all four with `EngineStrategyResolver` at startup, working around Quarkus ARC's inability to resolve transitive NamedStrategy relationships.

---

## Depends On

- `casehub-platform-api` — production dep in `casehub-work-api` for `Path`, `Preferences`, `ActorType`, and `ActorTypeResolver`. Zero-dep pure-Java; does not force Quarkus on consumers. `ActorType`/`ActorTypeResolver` moved here from `casehub-ledger` in ledger#88 — any module using these types must import from `io.casehub.platform.api.identity`, not `io.casehub.ledger.api.model`.
- `casehub-platform` (mock module) — `test` scope in library/extension modules; `runtime` scope in application modules running `quarkus:build`. Provides `MockPreferenceProvider @DefaultBean` so `@QuarkusTest` augmentation satisfies the `PreferenceProvider` CDI dep. Must be Jandex-indexed.
- `casehub-ledger` — optional only, via `casehub-work-ledger` module. Core has zero other casehubio deps.

## Depended On By

| Repo | How |
|---|---|
| `casehub-engine` | `casehub-work-api` (compile — `CaseSignalSink`, `WorkItemCreator`, `WorkItemLifecycle` injection). The engine-adapter bridge module now lives in this repo (`casehub-work-engine-adapter`) rather than in engine. Routing no longer uses `casehub-work-core`/`WorkBroker` — engine uses its own `AgentRoutingStrategy` SPI (engine#337). Receives `WorkItemEvent` and `WorkItemGroupLifecycleEvent` via CDI adapter to drive plan-item transitions. |
| `claudony` | Future, via `casehub-work-casehub` adapter (currently blocked on CaseHub stability) |
| `casehub-clinical` | Layer 2 — adverse event WorkItems with GCP SLA (24h Grade>=3, 1h Grade 5); first consumer of `SlaBreachPolicy` with DSMB escalation |

---

## What This Repo Explicitly Does NOT Do

- Orchestrate — it fires events and provides primitives. It does not decide what completing a WorkItem means.
- **Heterogeneous plan-item completion** — whether named plan items A, B, and C have all completed to advance a Stage; that is CaseHub (see LAYERING.md). Homogeneous M-of-N group completion IS casehub-work (multi-instance coordinator).
- Interpret `callerRef` — stored and echoed opaquely. **Convention:** `casehub-work-engine-adapter` uses `CallerRef` sealed interface with two formats: `PlanItemCallerRef` (`case:{caseId}/pi:{planItemId}`) and `GateCallerRef` (`case:{caseId}/gate:{gateId}`). `WorkItemCallerRef.parseCaseId()` in `casehub-work-api` is the canonical parser.
- Provision or manage AI agents (that is CaseHub/Claudony).
- Know when to spawn child WorkItems (callers drive spawn via `SpawnPort`).

---

## The Core/Runtime Split (Critical for casehub-engine)

`casehub-work-core` is a Jandex library (not a Quarkus extension) containing only `WorkBroker` and selection strategies. casehub-engine depends on this module — it gets worker routing without pulling in WorkItem entities, Flyway migrations, or datasource requirements. REST is now a separate opt-in module (`casehub-work-rest`) — the separation is explicit rather than implicit (work#292).

The `WorkBroker` is generic: it routes any work unit, not just WorkItems.

**Engine adapter relocation:** The two-way bridge between engine PlanItems and work WorkItems (`casehub-engine-work-adapter`) was relocated from the engine repo to this repo as `casehub-work-engine-adapter` (`engine-adapter/`). This places the bridge with the module that owns the WorkItem entity and transaction boundaries, while keeping the engine repo focused on coordination primitives.

---

## Notification Concern

`casehub-work-notifications` currently ships Slack/Teams/webhook directly. This overlaps with `casehub-connectors`. Future direction: delegate to `casehub-connectors` connector SPI rather than maintaining a parallel implementation.

---

## Flyway Version Ranges

Each optional module owns a dedicated V-number range to prevent collision when multiple modules are loaded together:

| Range | Module |
|---|---|
| V1–V999 | `runtime` (sequential) |
| V2000–V2999 | `casehub-work-queues` and `casehub-work-ledger` |
| V3000–V3999 | `casehub-work-notifications` |
| V4000–V4999 | `casehub-work-ai` |
| V5000–V5999 | `casehub-work-issue-tracker` |
| V6000+ | next new optional module |

**casehub-ledger#95 note:** ledger base migrations now live at `classpath:db/ledger/migration/` (not `db/migration/`). Any module consuming `casehub-work-ledger` must configure `quarkus.flyway.locations=db/migration,db/ledger/migration` in test `application.properties`.

---

## Current State

- Core lifecycle, SPI extraction, MongoDB persistence, queue trends, engine-adapter: done
- NamedStrategy retrofit on 4 work SPIs: done
- WorkItemObserver SPI: done
- Template versioning: done
- Pending: `casehub-work-qhorus` adapter (MCP tools for agent-driven approval flows)

---

## Design Documents

- [docs/ARC42STORIES.MD](https://raw.githubusercontent.com/casehubio/work/main/docs/ARC42STORIES.MD) — module graph, domain model, SPI contracts, status enumeration, service class structure (migrated from DESIGN.md + ARCHITECTURE.md in work#246)
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/work/main/adr/INDEX.md) — architectural decision records
