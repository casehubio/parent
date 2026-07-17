# casehub-desiredstate

**GitHub:** [casehubio/casehub-desiredstate](https://github.com/casehubio/casehub-desiredstate)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Generic desired-state management runtime for the CaseHub ecosystem. Declares what should exist (a DAG of typed nodes), observes what actually exists, and continuously reconciles the two via a per-tenant event-driven reconciliation loop. Domain-agnostic: the framework provides graph management, topological transition planning, fault policy, and reconciliation orchestration. Domain-specific concerns (what a "node" means, how to provision it, how to observe its state) are injected via SPIs.

The design follows the Kubernetes controller pattern: desired state is declarative, actual state is observed, and the runtime closes the gap automatically. But unlike Kubernetes, nodes can require human approval or human provisioning, and transition plans can be delegated to casehub-engine as CaseDefinitions with Serverless Workflow phases.

---

## Module Structure

| Module | artifactId | Contents |
|--------|-----------|----------|
| `api/` | `casehub-desiredstate-api` | Core SPIs and domain types. Pure Java + Mutiny `provided`. No CDI, no framework. |
| `runtime/` | `casehub-desiredstate` | CDI runtime: `ImmutableDesiredStateGraph`, `TransitionPlanner`, `ReconciliationLoop`, `SimpleTransitionExecutor`, `FaultPolicyEngine`. `@ApplicationScoped` beans. OpenTelemetry instrumented. |
| `testing/` | `casehub-desiredstate-testing` | `MockNodeProvisioner`, `MockActualStateAdapter`, `MockPendingApprovalHandler`, `CannedEventSource`. Test scope only. |
| `engine-adapter/` | `casehub-desiredstate-engine` | Bridges to casehub-engine: `CaseTransitionExecutor` (displaces `SimpleTransitionExecutor`), `TransitionWorkflowGenerator` (Serverless Workflow from steps), `DesiredStateWorkerFunction` (wraps `NodeProvisioner` as engine worker). |
| `work-adapter/` | `casehub-desiredstate-work` | Bridges to casehub-work: `WorkItemHumanNodeHandler` implements `HumanNodeHandler` — creates WorkItems for nodes that require human provisioning. |
| `ras-adapter/` | `casehub-desiredstate-ras` | Bridges to casehub-ras: `NodeFaultGanglion` (detects node faults — NODE_FAULTED → detected, NODE_RECOVERED → anti), `PersistentDriftGanglion` (detects persistent drift), `DesiredStateSituationDefinitionProvider` (3 situations: repeated-failure via Streak(3), persistent-drift via Count(3), zone-degradation via Rate(60%, 10)), `DesiredStateCorrelationKeyExtractor` (extracts `parentNodeId` for zone-level aggregation). |
| `examples/dungeon/` | — | Dungeon domain example: rooms, creatures, traps as nodes; `GoblinProvisioner`, `HeroRaidFaultPolicy`, `DungeonGoalCompiler`, `DungeonVisualizer`. |
| `examples/pipeline/` | — | Data pipeline domain example: medallion-layered data pipeline (sources, cleansers, enrichers, transformers, validators, sinks, AI review, human review) with `PipelineGoalCompiler`, multiple fault policies (`SchemaDriftFaultPolicy`, `QuarantineFaultPolicy`, `ProvisionEscalationFaultPolicy`), and `PipelineVisualizer`. Also demonstrates engine-adapter integration via `PipelineCaseTransitionTest`. |
| `examples/spatial/` | — | Battlefield-themed spatial/vector POC. Graph sufficiency research exploring how desired-state reconciliation handles spatial domains: `TerrainGrid`/`TerrainCell`/`TerrainType`, `FogOfWar` (vision-based reveal), `BattlefieldWorld` (units, scouts, zone activation), `AttackGoalCompiler`, `DefenseGoalCompiler`, `DistributionGoalCompiler`, `ZoneRebalanceFaultPolicy`, `GridRenderer`. Tests include situation detection, force distribution, fog-of-war, defense posture. |
| `examples/expansion/` | — | Build-then-defend lifecycle scenario — primary test vehicle for `CompilationResult.Lifecycle` phase transitions. `ExpansionGoalCompiler` produces lifecycle with "build" phase (probe → nexus → pylon → cannon) and "defend" phase (`CompletionCondition.never()`). `ExpansionSituationRecompiler` escalates defense posture to FORTIFY on situation. Node types: PROBE, NEXUS, PYLON, CANNON, PATROL, MONITOR, RESPONSE. |

---

## Key Abstractions

### DesiredStateGraph

Immutable directed acyclic graph of `DesiredNode` instances connected by `Dependency` edges. Core operations: `withNode()`, `withoutNode()`, `withDependency()`, `withMutation()`, `overlay()` (merge graphs), `connect()` (join graphs). Navigation: `dependenciesOf(nodeId)`, `dependentsOf(nodeId)`, `roots()`, `leaves()`. Versioned (`version()`) for optimistic concurrency. `ImmutableDesiredStateGraph` is the runtime implementation — all mutations return new instances.

### DesiredNode

Record: `(NodeId id, NodeType type, NodeSpec spec, boolean requiresHuman)`. `NodeType` is an open string classifier (e.g. `"vm"`, `"dns-record"`, `"human-task"`, `"data-source"`) — the runtime does not constrain it. `NodeSpec` is a marker interface — each domain provides its own implementations (e.g. `DungeonRoomSpec`, `DataSourceSpec`, `SchemaSpec`). `requiresHuman` marks nodes that need `HumanNodeHandler` instead of automated provisioning.

### GoalCompiler\<G\>

SPI: `compile(G goals, DesiredStateGraphFactory factory) → DesiredStateGraph`. Translates domain-specific goals (a dungeon blueprint, a pipeline configuration) into the generic graph representation. Each domain implements one.

### NodeProvisioner / ReactiveNodeProvisioner

SPIs for provisioning and deprovisioning nodes. `provision(DesiredNode, ProvisionContext) → ProvisionResult` returns `Success`, `Failed`, or `PendingApproval`. `PendingApproval` triggers a re-entry protocol: the runtime calls `provision()` again with `context.approval()` populated after human approval. `ReactiveNodeProvisioner` is the Mutiny-based variant.

### ActualStateAdapter

SPI: `readActual(DesiredStateGraph, tenancyId) → ActualState`. Returns a snapshot of observed status (`PRESENT`, `ABSENT`, `DRIFTED`, `UNKNOWN`) for each node. Called at the start of every reconciliation cycle.

### TransitionPlanner

Compares desired graph to actual state. Produces a `TransitionPlan` with topologically ordered additions (roots before leaves, Kahn's algorithm) and removals (orphaned nodes). Plans are deterministic given the same inputs.

### TransitionExecutor

SPI: `execute(TransitionPlan, tenancyId) → Uni<TransitionResult>`. Two implementations:
- `SimpleTransitionExecutor` (`@DefaultBean`) — sequential in-process execution using `NodeProvisioner` directly. Handles `PendingApproval` re-entry and `HumanNodeHandler` delegation.
- `CaseTransitionExecutor` (engine-adapter) — translates the plan into a casehub-engine `CaseDefinition` with prune/grow worker phases and human task bindings, then starts it via `CaseHubRuntime`.

### FaultPolicy / FaultPolicyEngine

SPI: `onFault(FaultEvent, DesiredStateGraph) → List<GraphMutation>`. Called when provisioning fails, nodes drift, approvals are rejected, or human nodes time out. Policies return graph mutations that the reconciliation loop applies to the desired graph. `FaultType` enum: `NODE_DESTROYED`, `NODE_DEGRADED`, `PROVISION_FAILED`, `DEPROVISION_FAILED`, `HUMAN_NODE_TIMEOUT`, `DEPENDENCY_UNAVAILABLE`, `APPROVAL_REJECTED`.

### GraphMutation

Sealed interface with five variants: `AddNode`, `RemoveNode`, `UpdateNode`, `AddDependency`, `RemoveDependency`. Used by fault policies and for programmatic graph modification.

### ReconciliationLoop

Per-tenant event-driven reconciliation engine (`@ApplicationScoped`). Two trigger paths: event-driven (subscribes to `EventSource.stream()` with debouncing) and periodic re-sync (default 5 minutes). Each cycle: read actual state, detect drift, plan transitions, execute, apply fault feedback, match CBR outcomes. The loop never dies on exception — a dead loop is worse than a failed cycle.

**OpenTelemetry tracing:** Comprehensive span tree per cycle using `GlobalOpenTelemetry.getTracer("io.casehub.desiredstate")`. Spans: `reconcile` (full-graph or type-filtered with `desiredstate.reconcile.types`), `readActual` (with `desiredstate.node.count`), `detectDrift` (with `desiredstate.drift.count`), `plan` (with `desiredstate.additions`, `desiredstate.removals`), `execute`, `faultFeedback` (with `desiredstate.fault.count`, `desiredstate.mutation.count`). Errors set `StatusCode.ERROR` and call `recordException()`.

Multi-provisioner support: `computeIntervalGroups()` creates separate scheduled timers per resync interval — `reconcileTypes(Set<NodeType>)` filters the graph to matching types only.

### Case-Based Reasoning (CBR)

Full CBR pipeline for fault and situation response:

**API types:** `CbrConfiguration` (retrieval/adaptation confidence gates + maxCandidates), `CbrProposal` (sourceId, CbrPath, affectedNodeIds, timestamp), `CbrOutcomeData` (per-node outcomes, success/failure counts, success rate), `CbrPath` enum (`FAULT`, `SITUATION`), `CbrEventTypes` (`CBR_OUTCOME` CloudEvent type).

**API SPIs:** `ConfigurationRetriever` (retrieve past configurations by context), `ConfigurationAdapter` (adapt retrieved config to current context), `RetrievalContext` (factory methods `forSituation()` and `forFault()`).

**Runtime:** `CbrSituationRecompiler` (implements `SituationRecompiler` — retrieves, filters by confidence, adapts, tracks via `CbrProposalTracker`), `CbrFaultPolicy` (implements `FaultPolicy` — same pipeline for fault events).

**CBR Revise (outcome feedback):** `CbrProposalTracker.matchOutcomes()` — called from `ReconciliationLoop` after execution completes. Maps affected nodeIds to outcomes (SUCCEEDED, FAILED, SKIPPED, REJECTED, SUPERSEDED, ALREADY_PRESENT), computes success rate, returns `CbrOutcomeData` records. Emitted as `io.casehub.cbr.outcome` CloudEvents with extensions for tenancyId, cbrPath, and successRate — closing the feedback loop.

### Multi-Provisioner Dispatch

`NodeProvisionerRouter` (API interface) / `DefaultNodeProvisionerRouter` (runtime impl): each `NodeProvisioner` declares `handledTypes()` and `resyncInterval()`. The router builds a `Map<NodeType, NodeProvisioner>` lookup table, enforcing no NodeType is claimed by two provisioners. Dispatches `provision()`/`deprovision()` by node type.

`ReconciliationLoop` uses `computeIntervalGroups()` to group node types by resync interval and creates **separate `ScheduledFuture` timers per interval group**. Each timer fires `reconcileTypes(Set<NodeType>)` which filters the desired graph and reconciles only matching types — different node types can have different reconciliation frequencies.

### Lifecycle Manager

`LifecycleManager` manages multi-phase `CompilationResult.Lifecycle` deployments. Internal `TenantLifecycle` record tracks `(List<Phase>, phaseIndex)`. On `onCycleCompleted()`: checks if current phase's `completionCondition.isComplete()` against actual state, computes next phase index, and advances via **dual CAS**: `lifecycles.replace(tenancyId, current, next)` on the ConcurrentHashMap entry + `loop.compareAndSetDesired(tenancyId, desired, nextPhase.graph())` on the AtomicReference. If either CAS fails (concurrent update), rolls back. `casRetryMutations()` also uses a CAS retry loop for fault-policy mutations.

### SituationRecompiler

SPI: `SituationRecompiler.recompile(ActiveSituation, DesiredStateGraph) → List<GraphMutation>`. Chain-of-responsibility pattern via `SituationRecompilerEngine` in runtime. The ras-adapter module provides `NodeFaultGanglion` and `PersistentDriftGanglion` as situation detectors; `CbrSituationRecompiler` provides CBR-based recompilation.

### HumanNodeHandler vs PendingApprovalHandler

Two distinct human-in-the-loop patterns:
- `HumanNodeHandler` — replaces the provisioner entirely for nodes with `requiresHuman=true`. The work-adapter provides `WorkItemHumanNodeHandler` which creates casehub-work `WorkItem` instances.
- `PendingApprovalHandler` — wraps the provisioner for automated nodes that need human approval before the machine provisions. Handles `check()` (is approval already granted?), `recordPending()` (record that approval is needed), and `acknowledgeRejection()`.

### EventSource

SPI: `stream() → Multi<StateEvent>`. The reconciliation loop subscribes to this for event-driven triggers. `StateEvent` carries `nodeId`, `newStatus`, and optional `detail`.

---

## Engine Adapter Architecture

When `casehub-desiredstate-engine` is on the classpath, `CaseTransitionExecutor` displaces `SimpleTransitionExecutor`. Transition plans become casehub-engine cases:

1. **Prune phase** — removals become a Serverless Workflow where each step calls `desiredstate:dispatch` with `action=DEPROVISION`. Executed as a `FlowWorkerFunction` in a `Worker`.
2. **Grow phase** — automated additions become a separate workflow with `action=PROVISION`.
3. **Human tasks** — additions with `requiresHuman=true` become `HumanTaskTarget` bindings in the case definition.

`TransitionWorkflowGenerator` generates Serverless Workflow 1.0 definitions. `DesiredStateWorkerFunction` wraps `NodeProvisioner` calls for engine dispatch.

V1 reports outcomes optimistically — proper case completion observation is a follow-up.

---

## Depends On

| Repo | Module | How |
|------|--------|-----|
| `casehub-platform` | `platform-api` | Via parent BOM. Tenancy, governance types. |
| `casehub-engine` | `engine-api`, `engine-common`, `engine-flow` | Engine-adapter only: `CaseHubRuntime`, `CaseDefinition`, `FlowWorkerFunction`, `Worker`, `Binding`. |
| `casehub-worker` | `worker-api` | Engine-adapter only: `Worker`, `Capability`. |
| `casehub-work` | `work-api` | Work-adapter only: `WorkItemCreator`, `WorkItemCreateRequest`, `WorkItemRef`. |
| `casehub-ras` | `ras-api` | RAS-adapter only: `Ganglion`, `JavaSwitchGanglion`, `SituationDefinitionProvider`, `CorrelationKeyExtractor`. |

## Depended On By

| Repo | What it uses |
|------|-------------|
| `casehub-ops` | `desiredstate-api` — deployment desired-state domain (ops module uses the graph SPIs) |

---

## Does NOT Do

- Persist desired-state graphs — no JPA module yet; graphs are in-memory per tenant
- Define domain-specific node types — consumers implement `NodeSpec` and `GoalCompiler`
- Schedule or time work items — that is `casehub-work` and `casehub-engine`
- Provide stream infrastructure (Kafka, AMQP) — `EventSource` is an SPI; stream adapters live elsewhere
- Multi-cluster orchestration — single-runtime reconciliation only
- Constrain `NodeType` vocabulary — open string, domain-defined
- Detect situations — that is `casehub-ras`; the ras-adapter bridges RAS detections to graph mutations

---

## Current State

- Core framework complete: API, runtime, testing, engine-adapter, work-adapter, ras-adapter all on main.
- Four working examples (dungeon, pipeline, spatial, expansion) demonstrating the full SPI surface including lifecycle phases and spatial graph sufficiency.
- Engine-adapter integration demonstrated in `PipelineCaseTransitionTest`.
- CBR pipeline complete: retrieve, adapt, apply, outcome feedback via CloudEvents.
- Multi-provisioner dispatch with per-type reconciliation scheduling.
- `LifecycleManager` for multi-phase deployments with dual CAS phase transitions.
- `SituationRecompiler` SPI with CBR and RAS-adapter implementations.
- Comprehensive OTel tracing on all reconciliation phases.
- No persistence module — graphs are in-memory only.
- `CaseTransitionExecutor` reports outcomes optimistically (V1); proper case completion observation is a follow-up.
