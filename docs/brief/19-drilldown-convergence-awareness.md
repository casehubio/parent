# Drill-Down — Convergence & Situational Awareness

*SPI quad contracts, topological planning, ganglion algebra, and
the runtime mechanics of domain-agnostic reconciliation and
composable signal detection.*

---

## Architecture Overview

Convergence and Awareness span three repos that compose into the
platform's feedback loop:

- **DesiredState** (37 modules, 566 Java source files) provides the
  reconciliation engine — declare target state as a graph, observe
  actual state, reconcile continuously. Framework-neutral core
  (`runtime-core`, 24 classes with zero CDI/Spring imports) runs
  identically on Quarkus and Spring Boot.
- **RAS** (9 modules, 122 Java source files) provides situation
  detection — route CloudEvents to pluggable ganglia, accumulate
  evidence, trigger cases. Five ganglion types cover stateless
  pattern matching through Bayesian classification to full CEP.
- **Ops** (10 modules, 316 Java source files) proves the model by
  running the engine's case definitions against the platform's own
  infrastructure.

The composition: RAS detects drift → triggers case creation via
engine → engine dispatches workers → workers execute reconciliation
via desiredstate. Outcomes feed back into RAS (tuning parameters,
CBR learning) and desiredstate (fault policy adaptation). The loop
closes.

---

## SPI Contracts

### The SPI Quad (DesiredState)

Every reconciliation domain implements four interfaces — the SPI
quad that makes reconciliation domain-agnostic:

| SPI | Contract | What It Does |
|-----|----------|-------------|
| `GoalCompiler<G>` | `compile(G goal)` → `CompilationResult` | Translates domain intent into a desired-state graph |
| `NodeProvisioner` | `provision(NodeSpec)` / `deprovision(NodeSpec)` | Drives reality toward desired state |
| `ActualStateAdapter` | `observe(NodeSpec)` → actual state | Reads current reality |
| `FaultPolicyProducer` | `faultPolicy(NodeSpec)` → `FaultPolicy` | Decides recovery strategy on failure |

Type parameter `G` on `GoalCompiler` preserves domain type safety
through cross-domain composition — infrastructure goals and
compliance goals compile independently.

`CompilationResult` carries:
- `DesiredStateGraph` — DAG of `NodeSpec` instances with dependency
  edges
- Optional `Lifecycle` — sequence of phases with completion
  conditions
- Optional `provides` / `requires` — cross-domain dependency
  declarations

### SPI Quad Implementations

| Domain | GoalCompiler | NodeProvisioner | ActualStateAdapter |
|--------|-------------|----------------|-------------------|
| Agent Topology (ops) | `TopologyGoalCompiler` | 5 provision handlers | 5 drift checkers |
| Infrastructure (ops) | `InfraGoalCompiler` | Standalone/Terraform/Ansible | Cloud-specific adapters |
| Compliance (ops) | `ComplianceGoalCompiler` | Evidence collection | Framework posture check |
| Container (ops) | `ContainerGoalCompiler` | PodmanClient REST | Container event stream |
| K8s Ops (ops) | `DeploymentGoalCompiler` | fabric8 K8s client | Watch API drift detection |
| Org Model (desiredstate) | `OrgGoalCompiler` | Org structure provisioner | Eidos org API |
| IoT (iot) | `IoTGoalCompiler` | Device provisioner | HA/OpenHAB adapters |

### Ganglion SPI (RAS)

`Ganglion` is the core detection primitive. Five sealed variants:

| Variant | Detection Model | Statefulness |
|---------|----------------|-------------|
| `JavaSwitchGanglion` | Pattern matching on event payload | Stateless |
| `ExpressionRulesGanglion` | JQ/MVEL expressions over event fields | Stateless |
| `NaiveBayesGanglion` | Incremental Bayesian classification | Stateful (priors) |
| `DroolsCepGanglion` | Drools CEP stream-mode processing | Stateful (sessions) |
| `SituationWatcherGanglion` | Observes child situation lifecycle events | Stateful (subscriptions) |

Each ganglion evaluates to a `TriggerDecision` — one of six
outcomes: TRIGGER, NO_TRIGGER, SUPPRESS, DEFER, ESCALATE,
INSUFFICIENT_DATA.

---

## Data Model

### Desired-State Graph

```
DesiredStateGraph
├── nodes: Map<NodeId, NodeSpec>     — typed node specifications
├── edges: Set<DependencyEdge>       — directed dependency links
└── metadata: GraphMetadata          — domain, tenant, compilation time

NodeSpec (per-domain sealed hierarchies)
├── nodeId: NodeId                   — unique within graph
├── nodeType: NodeTypeId             — registered type identifier
├── desiredProperties: Map           — target state
├── gating: GatingMode               — NONE / PROVISION_ONLY / DEPROVISION_ONLY / ALL
└── domainSpecific: T                — typed domain payload
```

The `TransitionPlanner` computes transitions using Kahn's
topological sort:
1. Compute delta: actual vs. desired for each node
2. Build transition graph: prune (remove) before grow (add)
3. Resolve orphan specs from previous desired graph
4. Validate: no cycles, no dangling dependencies
5. Output: ordered `TransitionPlan` with per-node actions

Two execution models:
- `SimpleTransitionExecutor` — sequential, single-threaded
- `ParallelTransitionExecutor` — layer-based virtual threads with
  per-NodeType semaphore rate limiting

### Three-Surface Graph Declaration

All three surfaces produce the same `GoalCompiler` beans:

**Annotations:**
```
@DesiredState → marks a goal compiler class
@Node → declares a node type
@DeclareNode → declares a specific node instance
@DependsOn → dependency edge
@GraphRule → pattern matching with:
    @Match → node pattern
    @DirectDep → direct dependency constraint
    @Reaches → transitive reachability
    @NotExists → absence constraint
    cardinality constraints
@GraphInvariant → universal quantification
```

**YAML:** `META-INF/desiredstate/*.yaml` with `NodeSpecRegistry`,
`VariableResolver`, reusable modules with parameters and cross-
module references.

**TypeScript (POC):** `defineGraph()` / `defineLifecycle()` /
`node()` helpers producing JSON envelopes consumed by the Java
runtime.

Cross-surface rules: Java `@GraphRule` annotations apply to
TypeScript-defined graphs.

Build-time validation on all surfaces: unknown types, dangling
dependencies, cycles.

### ChainMode — Sealed Signal Algebra (RAS)

Seven sealed variants compose ganglion signals:

```
ChainMode (sealed)
├── And       — all child signals must fire
├── Or        — any child signal fires
├── Threshold — M-of-N children fire
├── Sequence  — children fire in declared order
├── Count     — N occurrences within time window
├── Streak    — N consecutive occurrences
└── Rate      — N of last M occurrences
```

Each is composable: a Sequence of Thresholds, a Rate of Streaks,
an And of Sequences. The sealed hierarchy enforces exhaustive
pattern matching at compile time.

### Situation Definition (YAML)

```yaml
situations:
  - id: repeated-failure
    description: "Node has failed 3 times"
    ganglion:
      type: expression-rules
      expression: "event.type == 'NODE_FAULT'"
    chain-mode:
      type: streak
      count: 3
    trigger-action:
      type: case-creation
      case-definition: fault-response
    evidence-template:
      fields: [nodeId, faultType, timestamp]
    confidence-expression: "0.6 + (count * 0.1)"
```

Situation templates support parameter substitution for reusable
definitions.

---

## Runtime Behaviour

### Reconciliation Loop

The `ReconciliationLoop` runs per-tenant with two trigger modes:

1. **Event-driven** — CDI events from state changes trigger
   immediate reconciliation
2. **Periodic resync** — configurable interval (5-minute safety-net
   default in ops)

Loop execution:

1. `GoalCompiler.compile()` → desired-state graph
2. `ActualStateAdapter.observe()` per node → actual state
3. Delta computation: desired vs. actual
4. `TransitionPlanner.plan()` → ordered transitions (Kahn's sort)
5. Gating check: PROVISION_ONLY / DEPROVISION_ONLY / ALL → create
   work items for human approval if gated
6. Execute transitions: `NodeProvisioner.provision()` or
   `.deprovision()`
7. On failure: `FaultPolicyProducer.faultPolicy()` → recovery
8. Record outcome → CBR feedback via CloudEvents
9. Debounce — suppress rapid re-evaluation from event storms

Per-NodeType scheduling allows different node types to reconcile at
different intervals within the same loop. OTel tracing on all phases.

### CBR Fault Learning Cycle

When reconciliation fails:

1. **Retrieve** — `CbrFaultPolicy` queries CBR store for similar
   past fault configurations
2. **Adapt** — adjust recovery strategy to current context (node
   type, fault type, environment)
3. **Apply** — execute adapted strategy
4. **Revise** — track outcome via `CbrProposalTracker`:
   SUCCEEDED, FAILED, SKIPPED, REJECTED, SUPERSEDED,
   ALREADY_PRESENT

Multi-tier escalation via `ThresholdFaultPolicy`:
- Tier 1: retry with backoff
- Tier 2: AI review (graph-presence guard: only if AI agent node
  exists in graph)
- Tier 3: human review (create work item)

Each tier's outcomes feed the CBR store. The system learns not
just what to do, but when to escalate.

`CbrSituationRecompiler` extends the learning loop to situation-
triggered replanning: when RAS detects a condition, CBR retrieves
similar past situations and proposes adapted lifecycle sequences.

### Multi-Phase Lifecycle Management

`CompilationResult.Lifecycle` carries a sequence of phases:

1. Each phase has a `DesiredStateGraph` and a `CompletionCondition`
2. `LifecycleManager` orchestrates phase transitions
3. Dual CAS (phase map + reconciliation loop desired graph) prevents
   concurrent update corruption
4. `SituationRecompiler` can replace the entire lifecycle sequence
   mid-execution
5. Per-domain lifecycle tracking in cross-domain composition

Built-in `CompletionCondition` implementations: `allPresent`
(all nodes reconciled), `never` (manual advancement).

### Cross-Domain Composition

`CrossDomainCompositionEngine` orchestrates multi-domain
reconciliation:

1. Each domain registers via `DomainRegistration` (provides,
   requires, readinessCondition, situationRecompilers)
2. Validation: duplicate provides, unsatisfied requires, circular
   deps (Kahn's), node ID collisions
3. Three composition modes:
   - **Flattened** — single merged graph
   - **Hierarchical** — meta-graph with domain-level nodes
   - **Passthrough** — 0-1 domains, no overhead
4. Domain-specific `SituationRecompiler`s receive only their
   domain graph — isolation preserved
5. `TenantCompositionState` immutable record with `recomposeLock`
   serialisation

### Situation Detection Pipeline (RAS)

CloudEvent processing through the detection engine:

1. Event arrives (Kafka, AMQP, webhook, Camel — clean event-only
   boundary, no transport imports)
2. Route to matching situation definitions by event type
3. Ganglion evaluation: `ganglion.evaluate(event)` → signal
4. ChainMode composition: compose signals per definition
5. Evidence accumulation across time windows
6. `TriggerDecision` evaluation: TRIGGER / NO_TRIGGER / SUPPRESS /
   DEFER / ESCALATE / INSUFFICIENT_DATA
7. On TRIGGER: case creation via engine SPI, notification dispatch
8. Clustered conflict resolution: dual-layer OCC (application
   storeVersion + JPA @Version), CAS-based claim mechanism

**Clustered processing:** Two-phase (detect-once, apply-with-retry).
Bifurcated claim path: new situations use save-before-claim,
existing situations use claim-before-save. Deferred cleanup via
`SituationExpiryJob`. No distributed locks — purpose-built OCC.

### Feedback-Driven Detection Tuning

Three-layer architecture:

1. **Ingestion** — case outcomes arrive as CloudEvents.
   `CaseOutcomeObserver` maps outcomes to detection instances.
2. **Analysis** — drift classification:
   OVER_SENSITIVE, UNDER_SENSITIVE, BOTH_DRIFTING, STABLE,
   INSUFFICIENT_DATA
3. **Application** — two modes:
   - **Advisory** — suppression + quality metrics only
   - **Tuning** — automatic parameter adjustment with guards

Per-ganglion quality metrics: precision, noise rate, recall.
NaiveBayes prior recalibration from outcome-to-outcome mapping.
Threshold adjustment for Threshold and Rate chain modes.
External missed-detection API (POST /api/ras/feedback/missed)
with ganglion attribution.

Guard against counter-productive auto-tuning: drift direction
must be stable before automatic adjustment applies.

---

## Extension Points

| Extension | SPI | Pattern |
|-----------|-----|---------|
| New reconciliation domain | SPI quad (4 interfaces) | CDI `@ApplicationScoped` |
| Custom node type | `@NodeTypeId` registration | Build-time validated |
| YAML plugin resource | Plugin YAML file | No Java required |
| Custom fault policy | `FaultPolicy` | CDI priority ordering |
| Custom completion condition | `CompletionCondition` | CDI bean |
| Custom ganglion type | `Ganglion` | CDI auto-discovery |
| Custom chain mode | Extend `ChainMode` sealed hierarchy | — |
| Custom evidence collector | Strategy key routing | ops compliance module |
| Custom situation recompiler | `SituationRecompiler` | Per-domain registration |
| Custom graph rule | `@GraphRule` annotations | Build-time pattern matching |
| Plugin test infrastructure | `PluginTestExtension` | JUnit5 + WireMock |

---

## Module Map

### DesiredState

| Module | Provides | Key Types |
|--------|----------|-----------|
| `desiredstate-api` | SPI quad, graph model | `GoalCompiler`, `NodeProvisioner`, `ActualStateAdapter`, `FaultPolicyProducer` |
| `desiredstate-runtime-core` | Framework-neutral engine (24 classes) | `ReconciliationLoop`, `TransitionPlanner`, `LifecycleManager` |
| `desiredstate-runtime` | Quarkus CDI wiring | CDI bridges to core |
| `desiredstate-runtime-spring` | Spring auto-config | Discovery classes |
| `desiredstate-annotations` | Java declaration surface | `@DesiredState`, `@Node`, `@GraphRule`, `@GraphInvariant` |
| `desiredstate-yaml` | YAML declaration surface | `NodeSpecRegistry`, `VariableResolver` |
| `desiredstate-ts-dsl` | TypeScript surface (POC) | `defineGraph()`, `defineLifecycle()` |
| `desiredstate-plugins` | YAML plugin system | `PluginModel`, `PluginParser`, `YamlPluginProvisioner` |
| `desiredstate-cbr` | CBR fault learning | `CbrFaultPolicy`, `CbrProposalTracker` |
| `desiredstate-engine-adapter` | Engine bridge | `CaseTransitionExecutor`, human task gating |
| `desiredstate-ras-adapter` | RAS bridge | `NodeFaultGanglion`, `PersistentDriftGanglion` |
| `desiredstate-eidos` | Org model bridge | `OrgGoalCompiler`, `OrgUnitNodeSpec` |
| `desiredstate-persistence-*` | JPA (Quarkus + Spring) | Graph persistence entities |

### RAS

| Module | Provides | Key Types |
|--------|----------|-----------|
| `ras-api` | Ganglion SPI, situation model | `Ganglion`, `SituationDefinition`, `ChainMode`, `TriggerDecision` |
| `ras-runtime` | Detection engine | `SituationEvaluator`, `FeedbackTuningStrategy`, `OutcomeLedger` |
| `ras-persistence-memory` | In-memory store | Development/testing |
| `ras-persistence-jpa` | JPA persistence | Flyway V1-V10 |
| `ras-drools` | Drools CEP ganglion | `DroolsCepGanglion`, stream-mode |
| `ras-drools-reliability` | Drools session persistence | Write-ahead log (planned) |
| `ras-testing` | Test fixtures | Replay, deterministic time |

### Ops

| Module | Provides | Key Types |
|--------|----------|-----------|
| `ops-api` | Domain node specs | 10 sealed InfraNodeSpec types |
| `ops-deployment` | Agent topology | `TopologyGoalCompiler`, adaptive recompiler |
| `ops-infra` | Infrastructure provisioning | Standalone/Terraform/Ansible backends |
| `ops-compliance` | Regulatory posture | 6 frameworks, 4 evidence strategies |
| `ops-container` | Container lifecycle | `PodmanClient`, 4 container node types |
| `ops-app` | K8s operations console | 7 case descriptors, 37 ganglia, 29 @McpDomain ops |
| `ops-topology-tests` | Deployment pattern proofs | 14 YAML exemplars, 5×4 matrix |
