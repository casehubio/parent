# casehub-engine — Platform Deep Dive

**GitHub:** [casehubio/engine](https://github.com/casehubio/engine) (local: `casehub-engine`)
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Hybrid choreography+orchestration coordination engine for multi-agent work. Implements the Blackboard Architecture (Hayes-Roth, 1985) with CMMN terminology. Coordinates workers (AI agents, humans) via case definitions, binding rules, and optional synchronous orchestration.

---

## Module Structure

| Module | Folder | Type | Purpose |
|---|---|---|---|
| `casehub-engine-api` | `api` | Pure Java + langchain4j | SPI interfaces, domain model (`Worker`, `Binding`, `Capability`, `HumanTaskTarget`), `Agent` wrapper, `AgentRoutingStrategy` SPI |
| `casehub-engine-common` | `common` | Pure Java (no CDI) | Domain objects (`CaseMetaModel`, `CaseInstance`), persistence SPIs, `JQEvaluator`, `EventLog` |
| `casehub-engine` | `runtime` | Quarkus module | Choreography handlers, orchestration, worker scheduling, expression engine |
| `casehub-engine-blackboard` | `blackboard` | Optional module | CMMN/Blackboard orchestration — `BlackboardRegistry`, `PlanItem`, `SubCase` lifecycle |
| `casehub-engine-work-adapter` | `work-adapter` | Module | Bridges casehub-work WorkItem lifecycle to blackboard PlanItem transitions |
| `casehub-engine-resilience` | `resilience` | Optional module | Dead Letter Queue, PoisonPill detection, backoff strategies, case timeout |
| `casehub-engine-ledger` | `ledger` | Optional module | Tamper-evident case lifecycle ledger; extends `casehub-ledger` entry model; `TrustWeightedAgentStrategy` (`@Alternative @Priority(1)`) |
| `casehub-engine-ai` | `ai` | Optional module | `AgentEmbeddingProvider` SPI + `SemanticAgentRoutingStrategy` (`@Alternative @Priority(2)`) — activates semantic agent routing by classpath presence. `AgentEmbeddingProvider` SPI lives here (not in `casehub-engine-api`) deliberately: the whole semantic routing feature — SPI + implementation — is opt-in together; placing the SPI in `casehub-engine-api` would force all deployments to declare an embedding provider even when no semantic routing is needed. |
| `casehub-engine-actor-state` | `actor-state` | Optional module | Unified actor workload view (`GET /actors/{actorId}/state`) — aggregates active cases, open WorkItems, and open Qhorus obligations via `ActorStateContributor` SPI; both blocking and reactive aggregation paths |
| `casehub-engine-scheduler-quartz` | `scheduler-quartz` | Module | Quartz-based worker execution (RAM store) |
| `casehub-engine-schema` | `schema` | Build-time | `CaseDefinition.yaml` JSON Schema → generated Java model via jsonschema2pojo |
| `casehub-engine-persistence-hibernate` | `persistence-hibernate` | Module | JPA/Panache persistence (PostgreSQL) |
| `casehub-engine-persistence-memory` | `persistence-memory` | Test module | In-memory thread-safe persistence for `@QuarkusTest` without Docker |
| `casehub-engine-codegen` | `codegen` | Build-time | Code generation utilities |
| `casehub-engine-flow` | `flow` | Optional module | Enables `Worker(Workflow)` to dispatch casehub workers from Serverless Workflow steps and await results reactively. `FlowWorkerExecutor @ApplicationScoped` wins over `NoOpWorkflowExecutor @DefaultBean` fallback in runtime by classpath presence. Depends on `casehub-engine-common` only (not runtime). Provides: `FlowWorkerExecutor`, `FlowExecutionRegistry`, `CasehubDispatch`, `CasehubCallableTaskBuilder` (`call: casehub:dispatch` YAML steps via Java SPI), `CasehubFlow` (FuncDSL helper, blocks on cached thread pool). |
| `casehub-engine-testing` | `testing` | Test module | Shared test utilities |

---

## Key Abstractions

### YAML DSL (`CaseDefinition.yaml`)

Cases are defined declaratively: namespace, name, version, capabilities, workers, bindings, goals, milestones, completion conditions. `CaseDefinitionYamlMapper` converts the JSON Schema–generated model to the runtime API model.

**Binding target types** (mutually exclusive per binding):
- `capability` — routes to a worker by capability match
- `subCase` — spawns a child case
- `humanTask` — creates a WorkItem in casehub-work (inline or template mode). Supports `scope` (hierarchical path for SLA preference resolution), `inputMapping`/`outputMapping` (JQ), `candidateGroups`, `candidateUsers`, `expiresIn`.

**Trigger types:** `contextChange` (with optional `filter` and binding-level `when` guard), `schedule`/`timer`.

### Engine Handlers

Two execution paths: choreography (evaluates bindings on context change) and orchestration (suspends case, awaits worker completion, resumes).

- `CaseContextChangedEventHandler` — evaluates `contextChange.filter` AND `binding.when()` to find eligible bindings for RUNNING and WAITING cases, selects via `LoopControl` (which owns state eligibility), dispatches by target type. `PlanningStrategyLoopControl` handles WAITING by filtering already-dispatched (RUNNING/DELEGATED) bindings; `ChoreographyLoopControl` restricts to RUNNING only.
- `WorkerScheduleEventHandler` — opens channel, builds `CommandContent`, dispatches via `postToChannel` with `correlationId` and `deadline` as first-class SPI params
- `WorkOrchestrator` (interface in `common/spi/`, implemented by `DefaultWorkOrchestrator` in runtime; `common/spi/` placement avoids circular dep since it uses `CaseInstance`) — synchronous dispatch path; integrates `CapabilityHealth` probe to filter/sort agent-backed candidates before selection; routing delegated to `AgentRoutingStrategy` SPI. `Worker(Workflow)` execution uses a non-blocking path: Quartz fires `workflowExecutor.execute()` and returns immediately; success/failure communicated via event bus (`WORKER_EXECUTION_FINISHED` / `WorkflowExecutionFailed`).

### AgentRoutingStrategy SPI (`api/spi/`)

Engine's own routing abstraction — replaces the borrowed `WorkerSelectionStrategy` from `casehub-work`. Types: `AgentRoutingStrategy`, `AgentRoutingContext`, `AgentCandidate` (with `AgentHealth` enum), `AgentAssignment`. `WorkOrchestrator` resolves the active strategy via `@Any Instance<AgentRoutingStrategy>` CDI priority resolution (engine#337).

| Implementation | Module | Priority | When active |
|---|---|---|---|
| `LeastLoadedAgentStrategy` | engine runtime | 0 (default) | Always — base fallback |
| `TrustWeightedAgentStrategy` | casehub-engine-ledger | `@Priority(1)` | When casehub-engine-ledger on classpath; implements trust maturity phases 0–3 via `TrustScoreCache` |
| `SemanticAgentRoutingStrategy` | casehub-engine-ai | `@Priority(2)` | When casehub-engine-ai on classpath; uses `AgentEmbeddingProvider` for embedding-based candidate matching |

### Worker Provisioner SPIs (`api/spi/`)

Eight operational SPIs (4 blocking + 4 reactive mirrors):

| SPI | Purpose |
|---|---|
| `WorkerProvisioner` / `ReactiveWorkerProvisioner` | Provision and terminate workers |
| `WorkerStatusListener` / `ReactiveWorkerStatusListener` | Worker lifecycle callbacks (started, completed, stalled) |
| `CaseChannelProvider` / `ReactiveCaseChannelProvider` | Open/close/post to backend-agnostic channels. `postToChannel` is 6-param: `(channel, from, content, MessageType, correlationId, deadline)` |
| `WorkerContextProvider` / `ReactiveWorkerContextProvider` | Build worker startup context from ledger lineage |

All eight ship with `@DefaultBean @ApplicationScoped` no-op defaults that yield automatically to consumer-provided implementations.

**`WorkerExecutionManager.getActiveCaseIds(String workerId): List<UUID>`** — `default` method returning Quartz job case UUIDs currently scheduled for the given worker. Added in engine#56 for the actor state view; consumers that implement `WorkerExecutionManager` inherit the default unless they override it.

**`CaseChannel.parseCaseId(String channelName): UUID`** — static utility in `casehub-engine-api` that parses a `case-{caseId}/{purpose}` channel name and returns the embedded `caseId`. Returns `null` for non-case channel names. Used by the actor-state module to resolve channels back to their originating case.

### ActionRiskClassifier SPI (`api/spi/` — engine#402)

Platform-level oversight gate for consequential worker actions. Workers return `WorkerResult` (breaking change — replaced `Map<String,Object>`) containing an optional `PlannedAction`. If `PlannedAction` is present, the engine gates via a WorkItem before advancing the case.

Key facts:
- `Agent.execute()` returns `WorkerResult`
- `@RiskClassifier @ApplicationScoped` for consumer implementations (e.g. `TextClassifier` from `casehub-neural-text`)
- Gate resolved via `WorkItem` in casehub-work — requires `casehub-engine-work-adapter` on classpath
- `pendingActionGate` is in-memory only in v1 — a server restart loses pending gates (tracked engine#433)
- Gate approval re-fires `WorkflowExecutionCompleted(plannedAction=null)` — normal completion path

Consumer exploration issues: aml#42, clinical#47, devtown#56, life#20, openclaw#6.

### Blackboard / PlanItem Lifecycle

`BlackboardRegistry` tracks `CasePlanModel` per case. Each binding creates a `PlanItem` that transitions through: `PENDING` → `DELEGATED` (control handed to external system, e.g. human task) or `RUNNING` (Quartz-executed capability worker) → terminal.

`SubCase` lifecycle: parent PlanItem stays `DELEGATED` until child case completes; `SubCaseCompletionService` handles the callback.

### Work Adapter (`casehub-work-adapter`)

Two-way bridge:
- **Outbound** (`HumanTaskScheduleHandler`) — creates WorkItems from `HumanTaskTarget` bindings (inline or template mode), sets `callerRef`, `scope`, `payload`. Atomicity: WorkItem creation + `planItemStore.save(DELEGATED)` + `markDelegated()` in single `@Transactional`.
- **Inbound** (`WorkItemLifecycleAdapter`) — translates `WorkItemLifecycleEvent` (COMPLETED, REJECTED, CANCELLED, EXPIRED — ESCALATED excluded as non-terminal) to PlanItem transitions, evaluates `outputMapping`, fires `CONTEXT_CHANGED`. Also observes `WorkItemGroupLifecycleEvent` for M-of-N SpawnGroup outcomes.

### CaseSignalSink SPI (`casehub-work-api`)

`CaseSignalSink` — SPI interface defined in `casehub-work-api`; implemented by `casehub-engine-work-adapter`. Called by `casehub-work` when SLA escalation fires — translates the escalation into a `CaseHubRuntime.signal()` call that unblocks a WAITING case. The `work-adapter` module depends on `casehub-work-api` for this interface only (compile scope, not a runtime routing dep).

Three external signal entry points that reach a running case:
1. **SLA escalation** — `casehub-work` calls `CaseSignalSink.signal()` → engine `work-adapter` → `CaseHubRuntime.signal()`
2. **Qhorus messages** — `QhorusMessageSignalBridge` (see below)
3. **Direct REST** — `CaseHubRuntime.signal()` from any engine consumer with direct engine access

### Qhorus Message Signal Bridge

`QhorusMessageSignalBridge` — CDI `@ObservesAsync` observer for `MessageReceivedEvent`; bridges commitment-resolving Qhorus messages (RESPONSE, DONE, DECLINE, FAILURE) on `case-{caseId}/{purpose}` channels to `CaseHubRuntime.signal()`. Enables human channel messages to unblock WAITING cases. Protocol: `PP-20260526-case-channel-message-signal`.

### Tenancy Enforcement (persistence-hibernate)

All JPA repositories in `casehub-engine-persistence-hibernate` extend `TenantAwareRepository`, which injects `SET LOCAL "casehub.tenancy_id"` into every reactive transaction for PostgreSQL Row Level Security (RLS).

**Helpers:** `withTenantTransaction()` (RLS enforced) / `withCrossTenantTransaction()` (BYPASSRLS role — platform-internal only).

**Config:** `casehub.rls.enabled` (default false). When true, `RlsPolicyApplicator` creates the `casehub_crosstenancy` BYPASSRLS role at startup and applies RLS policies.

**Cross-tenant repository:** `JpaCrosstenantEventLogRepository` is a separate class from `JpaEventLogRepository` — queries without tenancy constraint. Produced with `@CrossTenant` CDI qualifier (see below).

**Cross-tenant test setup:** `quarkus.datasource.devservices.init-script-path=db/init-crosstenancy-role.sql` pattern — creates the BYPASSRLS role in the test database.

### @CrossTenant CDI Qualifier

`@CrossTenant` qualifier (in `common/qualifier/`) gates access to cross-tenant SPIs. `CrossTenantProducer` (in `runtime/internal/identity/`) produces:
- `@CrossTenant CrossTenantEventLogRepository`
- `@CrossTenant CrossTenantCaseInstanceRepository`

`SystemCurrentPrincipal` (`@ApplicationScoped @EngineSystem`) serves as the interim platform system actor until `casehub-platform` ships a system-actor principal. All 6 cross-tenant injection sites are updated with the `@CrossTenant` qualifier.

### CaseDefinitionRegistry uses CaseKey record

`DefaultCaseDefinitionRegistry` stores definitions in `Map<CaseKey, RegistryEntry>` where `CaseKey` is an immutable record `(namespace, name, version)`. Eliminates the mutable-hashCode map key bug (engine#410). `RegistryEntry` is an inner record `(CaseDefinition, CaseMetaModel)`.

### CapabilityHealth Integration

Optional integration with `casehub-eidos-api`. `WorkOrchestrator` probes agent-backed workers via `CapabilityHealth.probe()` before candidate selection:
- `Unavailable` → hard filter (removed from candidates)
- `EpistemicallyWeak` → preference demotion (sorted last, not removed)
- `Degraded` → keep, sort after `Ready`
- No descriptor → skip probe, assume capable

`NoOpCapabilityHealth` `@DefaultBean` returns `Ready` for all probes when eidos is not on the classpath.

---

## Depends On

| Repo | How |
|---|---|
| `casehub-ledger` | Optional, via `casehub-engine-ledger` module |
| `casehub-qhorus-api` | `MessageType` enum for channel messaging |
| `casehub-platform-api` | `ActorType`, `PreferenceProvider`, `Path` (transitive via ledger) |
| `casehub-platform-expression` | `JQEvaluator` for expression evaluation |
| `casehub-eidos-api` | Optional — `AgentDescriptor`, `CapabilityHealth` for agent health probing |
| `casehub-work-api` | Compile scope — `CaseSignalSink` injection via work-adapter only; NOT a runtime routing dep |

## Depended On By

| Repo | Module | How |
|---|---|---|
| `claudony` | `claudony-casehub` | Implements the 4 worker provisioner SPIs, provides `ClaudonyReactiveCaseChannelProvider` |
| `devtown` | `app` | Runtime dep — `casehub-engine-work-adapter` + `casehub-engine-blackboard` for HITL |
| `casehub-clinical` | `runtime` | Runtime dep — adverse event case coordination |

---

## What This Repo Explicitly Does NOT Do

- Manage human task inboxes (that is casehub-work)
- Handle agent-to-agent messaging protocols (that is casehub-qhorus)
- Provide a terminal/session UI (that is claudony)
- Implement worker provisioner SPIs — only defines the contracts
- Agent identity/discovery/vocabulary (that is casehub-eidos)

---

## Schema Management

No Flyway for engine tables — Hibernate `drop-and-create` only (no prod instances to migrate). `casehub-engine-ledger` uses Flyway migrations from `casehub-ledger` (`db/ledger/migration/V1000+`) plus its own `V2000__case_ledger_entry.sql`. Quartz uses RAM store, not JDBC.

---

## Agent Mesh — Layer 4 (Enforcement)

casehub-engine is Layer 4 (Enforcement) in the Qhorus normative accountability framework. It reacts to commitment outcomes published as CDI events by Qhorus and takes orchestration decisions:

- `FULFILLED` commitment → case continues to the next worker or step
- `FAILED` / `EXPIRED` commitment → recovery policy triggers (escalation, reprovision, cancel)

**`sessionMeta` caseId propagation:** Every worker session must carry the `caseId` in its `sessionMeta` for cross-repo ledger correlation and Claudony dashboard correlation.

---

## Current State

- Core choreography and orchestration: done
- WAITING state durability (restart-safe): done
- `casehub-ledger` integration: merged
- Human worker integration (`humanTask` YAML binding): done — inline + template modes, `scope` for SLA preference routing
- `casehub-work-adapter`: done — two-way bridge with atomicity guarantees
- `CapabilityHealth` integration: in progress (engine#341)
- `AgentRoutingStrategy` SPI: done — `casehub-work-core` removed from engine runtime routing; `TrustWeightedAgentStrategy` in ledger module (engine#337, engine#336)
- `ActionRiskClassifier` SPI — platform-level oversight gate for consequential worker actions: done (engine#402)
- Resilience module (DLQ, PoisonPill, timeout): done
- Worker↔Session↔Channel triple correlation: not yet stored
- Escalation rules, lineage-driven planning: ahead

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/engine/main/docs/DESIGN.md) — choreography+orchestration models, worker SPI contracts, blackboard lifecycle
- [docs/adr/INDEX.md](https://raw.githubusercontent.com/casehubio/engine/main/docs/adr/INDEX.md) — architectural decision records
