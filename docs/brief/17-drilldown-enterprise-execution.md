# Drill-Down — Enterprise Execution

*SPIs, sealed types, and runtime mechanics behind case lifecycle,
worker dispatch, and human task management.*

---

## Architecture Overview

Enterprise Execution is four repos converging on one execution model:

- **Engine** (68 modules) owns case lifecycle, planning, and routing.
  The core split: `engine-api` defines contracts, `engine-core`
  implements framework-neutral logic, `engine-runtime` wires CDI.
  Spring Boot mirrors with `-core` / `-spring` modules.
- **Worker** (3 modules) defines the typed execution primitive —
  `WorkerFunction<T,R>` with sealed outcomes.
- **Workers** (19 modules) provides transport backends. Each backend
  follows a three-class pattern: `*Runtime`, `*Resolver`,
  `*ExecutionManager`.
- **Work** (38 modules) delivers human task management as a
  standalone product with its own SPI surface, persistence, and API.

The engine dispatches work through `CompositeWorkerExecutionManager`,
which delegates to transport-specific managers. Routing signals score
candidates before dispatch. Oversight gates intercept before
execution. The ledger records after completion. Every step is CDI-
evented and OTel-traced.

---

## SPI Contracts

### Routing Signal Providers

`RoutingSignalProvider` is the core routing SPI. Each provider scores
worker candidates independently; a compositor computes weighted sums.

| Provider | SPI Interface | Input | Output |
|----------|--------------|-------|--------|
| Workload | `WorkloadSignalProvider` | Current active dispatch count | Load score (lower is better) |
| Trust | `TrustSignalProvider` | Bayesian trust from ledger | Reliability score (higher is better) |
| Experience | `CbrSignalProvider` | Case similarity from neocortex CBR | Past-performance score |
| Personality | `PersonalitySignalProvider` | JPAF profile from eidos | Task-fit score |
| Semantic | `SemanticSignalProvider` | Embedding similarity | Skill-match score |

The compositor is configurable per case definition — YAML declares
signal weights. Strategy SPIs extend routing for specific contexts:

- `AgentRoutingStrategy` — agent-to-case assignment
- `ImplementationRoutingStrategy` — worker implementation selection
- `HumanTaskRoutingStrategy` — human task assignment
- `CandidateMatchingStrategy` — pre-filter before scoring
- `DecompositionStrategy` — HTN method selection

All strategies resolve via the platform's `NamedStrategy` convention.

### Worker Function Variants

`WorkerFunction<T,R>` has four sealed variants:

| Variant | Contract | Use Case |
|---------|----------|----------|
| `Sync` | `R execute(T input, WorkerScope scope)` | One-shot agent, service call |
| `Persistent` | Event-loop with `PersistentScope` | Long-running conversation, stateful agent |
| `ExchangeProcessor` | `Exchange<R> process(Exchange<T>)` with `andThen()` | Pipeline composition |
| `None` | External proxy — no local execution | K8s Job, GitHub Actions, MCP server |

`WorkerScope` is the execution context parameter. Engine casts it to
`WorkerRuntime` for engine-specific methods (case context access,
binding metadata, credential resolution). This design avoids circular
dependencies between `casehub-worker-api` and `engine-api`.

### Dispatch Handler Types

The engine supports six handler types for worker dispatch:

| Handler | How It Works |
|---------|-------------|
| Sync Agent | Direct `WorkerFunction.execute()` invocation |
| Flow | Quarkus-Flow workflow DSL — imperative step chains |
| A2A | Google Agent-to-Agent protocol dispatch |
| MCP | Model Context Protocol tool invocation |
| ReAct | Reasoning + Acting loop with tool use |
| Pattern (Blocks) | Blocks adapter — supervisor, debate, voting patterns |

### Oversight Gate SPI

`ActionRiskClassifier` CDI beans evaluate whether an action requires
human approval. Multiple classifiers compose with most-restrictive-wins
semantics. The gate lifecycle:

1. Classifier chain evaluates risk → `RiskLevel` (NONE, LOW, MEDIUM,
   HIGH, CRITICAL)
2. If gated: serialise context as Properties into Qhorus COMMAND
   message → crash-safe persistence
3. M-of-N approvers respond via speech act RESPONSE messages
4. Quorum reached → gate releases → execution proceeds
5. Gate outcome recorded in tamper-evident ledger

Edge case design: fail-open on infrastructure errors (unreachable gate
must not deadlock), fail-safe on classifier errors (unknown risk
treated as high risk).

---

## Data Model

### WorkerOutcome — Sealed 5-Variant Hierarchy

```
WorkerOutcome<R>
├── Success<R>        — result + optional PlannedAction + reasoning
├── Declined          — worker says "not me" → triggers re-routing
├── Failed            — exception with context → fault pipeline
├── Expired           — timeout (distinct from exception)
└── Completed         — clean shutdown of persistent worker
```

Pattern matching is exhaustive. Every outcome carries an optional
`reasoning` field — `withReasoning(String)` on results,
`reasoning()` on `PersistentScope`. Designed for LLM workers
recording chain-of-thought.

### SLA Breach Decision — Sealed Hierarchy

```
SlaBreachDecision
├── Fail              — mark work item as FAILED
├── EscalateTo        — route to specified escalation target
├── Extend            — grant additional time
├── Exhausted         — all options consumed
└── Chained           — compose multiple decisions in sequence
```

`Chained` enables complex escalation policies: try EscalateTo(L2),
then EscalateTo(L3), then Fail. Business calendar support (static
holidays + iCal feeds) and per-tenant SLA overrides via the platform
preference hierarchy.

### WorkItem Status — 12-State Lifecycle

```
PENDING → ASSIGNED → IN_PROGRESS → COMPLETED
                                  → FAILED
                                  → CANCELLED
                   → DELEGATED    → (re-enters PENDING)
                   → SUSPENDED    → (re-enters ASSIGNED)
         → ESCALATED
         → EXPIRED
         → OBSOLETE
```

Every status has `isTerminal()` and `isActive()` predicates. Every
transition emits a typed `WorkItemLifecycleEvent` with CloudEvent URI.
26 lifecycle event types total.

### DAG Plan — Immutable Validated Graph

`DagPlan` is immutable after construction. Nodes carry state:
Pending → Dispatched → Completed / Failed / Skipped / Cancelled.
Validation catches cycles, dangling dependencies, and missing nodes
at plan creation time. Streaming or barrier dispatch modes. Contingency
nodes fire on predecessor failure.

---

## Runtime Behaviour

### Blackboard Handler Lifecycle

The engine is a Blackboard Architecture. Handlers (bindings) react
to context change on a shared blackboard, not to graph edges:

1. **Case activated** — case context initialised, initial bindings
   evaluated
2. **Context change** — any update to the working layer
   (`context.layer(ContextLayer.WORKING)`)
3. **Binding evaluation** — JQ/MVEL/Lambda expressions evaluate
   against the working layer. Matching bindings become eligible.
4. **Dispatch budget check** — case-level + external `DispatchBudget`
   SPI enforce concurrency limits
5. **Routing** — composable signal providers score eligible workers
6. **Oversight gate** — risk classifiers evaluate; gate opens if
   required
7. **Dispatch** — transport-specific `WorkerExecutionManager` sends
   work
8. **Completion** — `WorkerOutcome` applied to context → triggers
   re-evaluation at step 2
9. **Goal evaluation** — completion semantics (All, M-of-N, FirstWins)
   checked after each completion

This is reactive choreography: the execution path emerges from
context state, not from a predefined graph. Orchestrated dispatch
(DAG mode) is available when determinism is needed.

### Worker Dispatch Through 7 Transport Backends

All transports implement `WorkerRuntime` and `WorkerExecutionManager`.
The dispatch path:

1. **Capability resolution** — 3-tier: SPI beans → config → tenant-
   aware `EndpointRegistry`
2. **Credential minting** — case-scoped credentials with auto-ACL
3. **Dispatch** — transport-specific (HTTP POST, K8s Job create,
   MCP tools/call, etc.)
4. **Completion tracking** — synchronous return or
   `AsyncWorkerCompletionRegistry` with TTL
5. **Fault classification** — transport-specific semantics:
   - HTTP 429 → RetryAfter
   - K8s OOMKilled → Permanent
   - MCP session expiry → retryable + session invalidation
   - GitHub Actions 422 → RetryAfter(60s)
6. **Retry** — 3 backoff strategies (FIXED, EXPONENTIAL,
   EXPONENTIAL_WITH_JITTER)
7. **Result** — `WorkerOutcome` flows back to engine

CaseHub owns all retry decisions. K8s Jobs: `backoffLimit=0`,
`restartPolicy=Never`. K8s restart recovery reconstructs dispatch
state from Job labels — no external database.

### MCP Session Lifecycle

MCP transport uses Streamable HTTP (2025-06-18 spec). Session init
ordering is critical: `onFailure` before `memoize` to avoid caching
failed sessions. Parallel server initialization via
`Uni.join().all()`. Session invalidation on 404. `tools/list`
discovery with allowlist filtering. SSE multi-event parsing finds
JSON-RPC responses by request ID. `structuredContent` extraction
preferred over `content`.

---

## Extension Points

| Extension | SPI | Pattern |
|-----------|-----|---------|
| Custom routing signal | `RoutingSignalProvider` | `@ApplicationScoped` CDI bean |
| Custom risk classifier | `ActionRiskClassifier` | CDI bean, compose with chain |
| Custom planning strategy | `DecompositionStrategy` | `NamedStrategy` resolution |
| Custom worker transport | `WorkerRuntime` + `WorkerExecutionManager` | CDI auto-discovery |
| Custom dispatch budget | `DispatchBudget` | CDI bean, global or per-case |
| Custom SLA breach policy | `SlaBreachDecision` | Compose via `Chained` |
| Custom assignment strategy | `WorkItemAssignmentStrategy` | 4 built-ins + custom |
| Custom conflict-of-interest | `ConflictOfInterestPolicy` | Pluggable ALLOW/deny |
| Step plugin | `@StepHandler` annotation | APT code generation |
| Playbook decorator | `DecoratorChain` | 13-layer pipeline |

All extensions follow the platform's `@DefaultBean` displacement
pattern — provide an `@ApplicationScoped` implementation to replace
the default. `@Alternative @Priority` for ordering.

---

## Module Map

| Module | Provides | Key Types |
|--------|----------|-----------|
| `engine-api` | Contracts, SPIs, events | `CaseDefinition`, `CaseLifecycleEvent`, `WorkerRuntime` |
| `engine-core` | Framework-neutral logic | `BlackboardEngine`, `TransitionPlanner`, `RoutingCompositor` |
| `engine-runtime` | Quarkus CDI wiring | `CaseLifecycleManager`, `CompositeWorkerExecutionManager` |
| `engine-persistence-jpa` | JPA persistence | Case instance entities, RLS |
| `engine-planning` | GOAP, HTN, DAG | `DagPlan`, `DecompositionStrategy`, `GoalEvaluator` |
| `engine-routing` | 5 signal providers | `WorkloadSignalProvider`, `TrustSignalProvider` |
| `engine-yaml-core` | YAML compilation | `CaseDefinitionCompiler`, `BindingResolver` |
| `engine-yaml-cbr` | CBR-playbook bridge | `CbrPlanStepConverter`, `PlaybookExperienceAdapter` |
| `engine-eidos-routing` | Personality routing | `PersonalitySignalProvider`, `AgentSelector` |
| `casehub-worker-api` | Worker primitive | `WorkerFunction<T,R>`, `WorkerOutcome`, `WorkerScope` |
| `casehub-worker-testing` | Test support | `MockWorkerExecutor` |
| `workers-http` | HTTP transport | `HttpWorkerRuntime`, async completion |
| `workers-mcp` | MCP transport | `McpWorkerRuntime`, session management |
| `workers-k8s` | K8s Job transport | `K8sJobBuilder`, `K8sJobInformerManager` |
| `workers-camel` | Camel transport | Convention auto-discovery from routes |
| `workers-github-actions` | GitHub Actions | Workflow dispatch, RetryAfter |
| `workers-script` | Script transport | Local script execution |
| `workers-scenario` | Scenario automation | Pages GraphQL bridge |
| `casehub-work-api` | Work item contracts | `WorkItem`, 42 SPI interfaces |
| `casehub-work-runtime` | Task lifecycle | SLA breach algebra, delegation, M-of-N |
| `casehub-work-progress` | Progress tracking | 6-module subsystem, hierarchical rollup |
| `casehub-work-saga` | Saga compensation | Compensation bindings, YAML schema |
