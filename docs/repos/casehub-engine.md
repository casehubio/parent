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
| `casehub-engine-ledger` | `ledger` | Optional module | Tamper-evident case lifecycle ledger; extends `casehub-ledger` entry model |
| `casehub-engine-scheduler-quartz` | `scheduler-quartz` | Module | Quartz-based worker execution (RAM store) |
| `casehub-engine-schema` | `schema` | Build-time | `CaseDefinition.yaml` JSON Schema → generated Java model via jsonschema2pojo |
| `casehub-engine-persistence-hibernate` | `persistence-hibernate` | Module | JPA/Panache persistence (PostgreSQL) |
| `casehub-engine-persistence-memory` | `persistence-memory` | Test module | In-memory thread-safe persistence for `@QuarkusTest` without Docker |
| `casehub-engine-codegen` | `codegen` | Build-time | Code generation utilities |
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
- `WorkOrchestrator` — synchronous dispatch path; integrates `CapabilityHealth` probe to filter/sort agent-backed candidates before selection; routing delegated to `AgentRoutingStrategy` SPI

### AgentRoutingStrategy SPI (`api/spi/`)

Engine's own routing abstraction — replaces the borrowed `WorkerSelectionStrategy` from `casehub-work`. Types: `AgentRoutingStrategy`, `AgentRoutingContext`, `AgentCandidate` (with `AgentHealth` enum), `AgentAssignment`. `TrustWeightedAgentStrategy` in `casehub-engine-ledger` implements trust maturity phases 0–3 via `TrustScoreCache`.

### Worker Provisioner SPIs (`api/spi/`)

Eight operational SPIs (4 blocking + 4 reactive mirrors):

| SPI | Purpose |
|---|---|
| `WorkerProvisioner` / `ReactiveWorkerProvisioner` | Provision and terminate workers |
| `WorkerStatusListener` / `ReactiveWorkerStatusListener` | Worker lifecycle callbacks (started, completed, stalled) |
| `CaseChannelProvider` / `ReactiveCaseChannelProvider` | Open/close/post to backend-agnostic channels. `postToChannel` is 6-param: `(channel, from, content, MessageType, correlationId, deadline)` |
| `WorkerContextProvider` / `ReactiveWorkerContextProvider` | Build worker startup context from ledger lineage |

All eight ship with `@DefaultBean @ApplicationScoped` no-op defaults that yield automatically to consumer-provided implementations.

### Blackboard / PlanItem Lifecycle

`BlackboardRegistry` tracks `CasePlanModel` per case. Each binding creates a `PlanItem` that transitions through: `PENDING` → `DELEGATED` (control handed to external system, e.g. human task) or `RUNNING` (Quartz-executed capability worker) → terminal.

`SubCase` lifecycle: parent PlanItem stays `DELEGATED` until child case completes; `SubCaseCompletionService` handles the callback.

### Work Adapter (`casehub-work-adapter`)

Two-way bridge:
- **Outbound** (`HumanTaskScheduleHandler`) — creates WorkItems from `HumanTaskTarget` bindings (inline or template mode), sets `callerRef`, `scope`, `payload`. Atomicity: WorkItem creation + `planItemStore.save(DELEGATED)` + `markDelegated()` in single `@Transactional`.
- **Inbound** (`WorkItemLifecycleAdapter`) — translates `WorkItemLifecycleEvent` (COMPLETED, REJECTED, CANCELLED, EXPIRED — ESCALATED excluded as non-terminal) to PlanItem transitions, evaluates `outputMapping`, fires `CONTEXT_CHANGED`. Also observes `WorkItemGroupLifecycleEvent` for M-of-N SpawnGroup outcomes.

### Qhorus Message Signal Bridge

`QhorusMessageSignalBridge` — CDI `@ObservesAsync` observer for `MessageReceivedEvent`; bridges commitment-resolving Qhorus messages (RESPONSE, DONE, DECLINE, FAILURE) on `case-{caseId}/{purpose}` channels to `CaseHubRuntime.signal()`. Enables human channel messages to unblock WAITING cases. Protocol: `PP-20260526-case-channel-message-signal`.

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
- Resilience module (DLQ, PoisonPill, timeout): done
- Worker↔Session↔Channel triple correlation: not yet stored
- Escalation rules, lineage-driven planning: ahead

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/engine/main/docs/DESIGN.md) — choreography+orchestration models, worker SPI contracts, blackboard lifecycle
- [docs/adr/INDEX.md](https://raw.githubusercontent.com/casehubio/engine/main/docs/adr/INDEX.md) — architectural decision records
