# Enterprise Execution

*How work gets done — case lifecycle, intelligent planning, worker
dispatch, and human task management across 128 modules.*

---

## What This Is

Enterprise Execution is the engine room of CaseHub. It covers the
complete path from "this case needs work done" to "the work is done,
the outcome is recorded, and the next step is evaluated." Four repos
contribute:

- **Engine** (68 modules) — case lifecycle, planning strategies,
  routing, and dispatch coordination
- **Worker** (3 modules) — the typed execution primitive: input,
  output, fault tolerance, reasoning capture
- **Workers** (19 modules) — 7 transport backends behind one SPI
- **Work** (38 modules) — human task management as a standalone product

Together they deliver a unified execution model where AI agents,
external services, Kubernetes jobs, and humans participate through the
same worker contract — dispatched by the same routing infrastructure,
governed by the same oversight gates, and recorded in the same audit
trail.

---

## Key Capabilities

### Case Lifecycle Engine

CaseHub implements a **Blackboard Architecture** (Hayes-Roth, 1985),
not a directed-acyclic-graph workflow. The difference matters:

- **DAG workflows** (Camunda, Step Functions, Temporal) execute a
  pre-defined graph of steps. Execution paths are known at design time.
  Emergent behaviour requires redesigning the graph.
- **Blackboard Architecture** uses reactive choreography — handlers
  respond to state changes on a shared blackboard. The case definition
  declares *what could happen*; the runtime determines *what does happen*
  based on context. New handlers can fire in response to outcomes of
  earlier handlers, enabling execution patterns that emerge from the
  situation rather than being pre-planned.

Orchestration is available when you want it — synchronous dispatch
with dependency ordering, DAG parallel execution on virtual threads,
sub-case orchestration with grouped M-of-N threshold logic. But the
default is choreography: bindings fire on context change, not on graph
edges.

CMMN terminology throughout. Case definitions support progressive
complexity — from a flat YAML file with three bindings to a directory
convention with dozens of workers, goal expressions, and compound
hierarchies.

### Planning Strategies

Three planning paradigms, selectable per case:

| Strategy | What it does | When to use it |
|----------|-------------|----------------|
| **GOAP** | Goal-Oriented Action Planning — search for action sequences that achieve goal states | Agent autonomy: "achieve this outcome" |
| **HTN** | Hierarchical Task Network — decompose high-level tasks into concrete sub-tasks via method selection | Complex operations: "break this problem down" |
| **DAG** | Dependency-graph execution — validated immutable plans with streaming or barrier dispatch | Deterministic pipelines: "run these steps in order" |

DAG plans execute on virtual threads with node state tracking
(Pending → Dispatched → Completed / Failed / Skipped / Cancelled).
HTN decomposition uses `DecompositionStrategy` SPIs — methods
produce DagPlans of sub-tasks, enabling recursive decomposition.
Contingency support on failure nodes.

### Composable Signal Routing

Worker selection is not a simple assignment. CaseHub's routing
architecture composes independent signals into a weighted routing
decision:

| Signal Provider | What it scores |
|----------------|---------------|
| **Workload** | Current load across active workers — avoid overloading |
| **Trust** | Bayesian trust score from the ledger — prefer reliable workers |
| **Experience (CBR)** | Case-based reasoning: how well has this worker performed on similar work? |
| **Personality (JPAF)** | Agent personality fit for the task context |
| **Semantic** | Embedding-based skill matching — semantic similarity between task requirements and worker capabilities |

Each `RoutingSignalProvider` scores candidates independently. A
compositor computes weighted sums. The result: intelligent, context-
aware dispatch that improves with use — because trust scores update
from outcomes, and CBR learns from experience.

Strategy SPIs extend routing for specific contexts: agent routing,
implementation routing, human task routing, candidate matching, and
decomposition. Every strategy resolves via the platform's shared
`NamedStrategy` convention.

### Worker Dispatch

7 transport backends behind one `WorkerRuntime` SPI:

| Transport | What it dispatches to | Key capability |
|-----------|----------------------|---------------|
| **HTTP** | REST endpoints | Async completion with callback security |
| **Camel** | 300+ Apache Camel connectors | Convention auto-discovery from CamelContext routes |
| **MCP** | Model Context Protocol servers | Streamable HTTP, session management, tool discovery |
| **K8s Job** | Kubernetes clusters | Restart recovery from Job labels, Pod log capture |
| **GitHub Actions** | CI/CD workflows | Retry-After on 422 trigger caching |
| **Script** | Local script execution | Direct invocation |
| **Playbook** | Scenario automation (pages) | Browser + API multi-step automation |

Transport is a deployment choice, not a code change. The same worker
capability declaration works across all backends. Each transport
implements the same three-class pattern (Runtime, Resolver,
ExecutionManager) with framework-neutral `-core` modules and separate
Quarkus/Spring wiring.

**Unified fault pipeline.** Every transport feeds into one fault
classification system. Transport-specific semantics are preserved:
HTTP 429 → RetryAfter. K8s OOMKilled → Permanent. MCP session
expiry → retryable with session invalidation. GitHub Actions 422 →
RetryAfter(60s) for trigger caching. Three backoff strategies (fixed,
exponential, exponential with jitter). CaseHub owns all retry
decisions — K8s `backoffLimit=0`, `restartPolicy=Never`.

**Async completion.** Long-running dispatches register in an
`AsyncCompletionRegistry` with TTL expiry. External systems call back
via a REST endpoint with constant-time token validation (timing-attack
resistant). K8s adds restart recovery — dispatch state reconstructed
from Job labels after application restart, no external database needed.

**Tenant-aware capability resolution.** Three-tier endpoint
resolution: SPI beans (programmatic, highest priority) → config
properties → `EndpointRegistry` (tenant-aware runtime resolution).
The same capability tag resolves to different endpoints per tenant.

**Worker rights and scoped credentials.** Workers receive
case-scoped credentials at dispatch time — security boundary per
case, not per service. Auto-managed ACL grants mean each worker
sees only the data it needs for its specific case step. Differential
revocation for shared service accounts ensures credentials are
withdrawn when the case step completes, even if the underlying
service account is shared across tenants.

**DataChannel for inter-worker communication.** `DataChannel<T>`
provides typed, bidirectional streaming between workers within a
case. `Exchange<T>` enables worker-to-worker composition via
`andThen()` — chain workers into pipelines where the output of one
feeds directly into the next without serialisation to case context.

### Case-to-Playbook Dispatch

`StepFileCallableDispatcher` bridges the case engine to the playbook
system. Cases dispatch playbook step files as callable work —
a case binding can reference a `.step` file, and the engine executes
it as a worker invocation with full lifecycle tracking. This connects
declaration (playbook steps), execution (worker dispatch), and the
application surface (ARIA-based automation) in a single dispatch
path.

### Execution Resilience

**Circuit breaker with event-sourced recovery.** Circuit breaker
state survives application restarts via EventLog event-sourcing.
State transitions (CLOSED → OPEN → HALF_OPEN) are persisted as
events, meaning a restart doesn't reset protection thresholds.

**Dead letter queue.** Failed dispatches move to a DLQ with
PoisonPill detection — messages that repeatedly fail are quarantined
rather than blocking the queue. Configurable backoff strategies and
auto-replay policies. Integration with the notifications pipeline
for operator alerts.

### Work Item Management

Not a checkbox feature — a standalone product. 38 modules, 196 API
types, 42 SPI interfaces, 4 persistence backends. Includes work
queues for prioritised dispatch, queue-based assignment, and
queue-level SLA policies.

**12-status lifecycle.** PENDING → ASSIGNED → IN_PROGRESS → terminal
states including DELEGATED, SUSPENDED, ESCALATED, and OBSOLETE. Every
transition emits a typed lifecycle event with CloudEvent URI. Status
semantics are precise — `isTerminal()` and `isActive()` on every state.

**SLA breach decision algebra.** Not just "escalate on timeout." A
sealed decision hierarchy: Fail, EscalateTo, Extend, Exhausted,
Chained. Policies compose — Chained enables sequences of escalation
strategies. Business calendar support with holidays (static + iCal)
and per-tenant SLA overrides via the platform preference hierarchy.

**M-of-N group completion.** Multi-instance WorkItems with
configurable threshold. 4 assignment strategies: pool, round-robin,
explicit, composite. Threshold-reached policies: KEEP remaining
active or CANCEL_REMAINING. Conflict-of-interest exclusion with
pluggable policies returning ALLOW / deny-with-reason.

**Delegation chains.** Pre-acceptance delegation with accept/decline
workflow. Configurable decline routing (back to POOL or back to
DELEGATOR). Full delegation history tracking.

**Progress tracking.** A 6-module subsystem that isn't coupled to
WorkItems. Any scope type gets hierarchical progress with 3 rollup
strategies, step-based tracking, event-sourced state, and SSE
broadcasting. Scope-generic infrastructure.

**AI-augmented routing.** Semantic skill matching via embeddings,
confidence scoring, learning-ready routing context (`candidateScores`
and `routingExperiences`) threaded through the entire lifecycle.

**Saga compensation.** Reversible task chains with compensation
bindings declared in YAML. Engine-work bridge, ledger supplement for
audit, notifications on compensation, and visualization support.

**Annotation-driven human oversight.** Add `@HumanApproval` to any
worker and it automatically gets human oversight — no workflow
redesign, no plumbing code. `@RequiresQuorum(3)` gates execution
behind multi-approver consensus. `@Escalate` declares escalation
paths. `@SkillMatch` routes to humans with specific expertise.
These annotations bridge Declaration and Execution: a domain expert
adds one line to a YAML binding, and the platform wires up the
full human-in-the-loop lifecycle — task creation, inbox routing,
SLA enforcement, approval tracking, and audit trail.

**Issue tracker SPI.** Work items bridge to external issue trackers
(GitHub, Jira) via webhooks. CloudEvent bridge enables distributed
task creation — an event from an external system creates a tracked
work item with full SLA and lifecycle management. Quarkus-Flow
workflow DSL provides an alternative imperative declaration
approach for complex approval chains.

### Evolution Conductor

Gated agent improvement streams. Agent capabilities evolve through
controlled phases — not unconstrained self-modification. Each
evolution phase defines entry criteria, success metrics, and
rollback conditions. The conductor manages promotion across phases,
ensuring agents improve measurably before gaining broader
responsibilities.

Surface in the UI via the Evolution Conductor dashboard (blocks-ui
component). First consumer: DevTown for PR review agent improvement.

### Oversight Gates

Consequential worker actions require approval before execution.
M-of-N multi-approver quorum. Composable risk classification via
`ActionRiskClassifier` chain — "most restrictive wins" composition.
Gate lifecycle events. Configurable per binding in YAML.

Crash-safe gate persistence. If the application restarts during an
approval, the gate state survives. Approval decisions are recorded
in the tamper-evident ledger, creating an unbroken accountability
chain from risk classification through approval to execution.

---

## What Makes It Different

### Not a DAG — a Blackboard

Most workflow engines (Camunda, Temporal, Step Functions, Airflow)
assume execution is a directed acyclic graph. CaseHub's Blackboard
Architecture is fundamentally different — handlers react to state,
not to graph edges. This enables emergent execution patterns that
DAGs cannot express: handlers that fire in response to combinations
of outcomes, parallel exploration paths that converge based on
content rather than structure, and cases that adapt their execution
path based on what they discover during execution.

Orchestration is available when appropriate — DAG plans, sub-case
coordination, barrier-based synchronisation. But orchestration is a
tool within the architecture, not the architecture itself.

### Intelligent Dispatch, Not Assignment

Worker selection in most platforms is a lookup table: capability →
endpoint. CaseHub's composable signal routing blends five independent
scoring dimensions into a single weighted decision. Trust scores
update from outcomes. CBR learns from experience. Personality fit
adapts as agent identity evolves. The routing decision improves
every time work completes.

### Work Items Are a Product, Not a Feature

Most platforms offer a human task queue as an afterthought — create,
assign, complete. CaseHub's Work Item Management is 38 modules with
its own SLA breach algebra, delegation chains, saga compensation,
and a 6-module progress tracking subsystem. It has its own REST API,
its own persistence layer, and its own federation model. It could
ship as a standalone product.

### Sealed Outcome Algebra

Workers return one of five discriminated outcomes: Success, Declined,
Failed, Expired, Completed. Not success/error. Declined enables
graceful routing — a worker saying "not me" triggers re-routing, not
failure. Expired separates timeout from exception. Pattern matching
is exhaustive. Every outcome carries an optional reasoning field for
chain-of-thought capture — designed for LLM workers but useful for
any worker that needs to explain its decision.

---

## How Deep It Goes

| Dimension | Measure |
|-----------|---------|
| Total modules | ~128 across 4 repos |
| Engine modules | 68 (44 non-example) |
| Work modules | 38 (22 active in reactor) |
| Workers modules | 19 |
| Worker modules | 3 (pure API + testing) |
| Transport backends | 7 |
| Routing signal providers | 5 |
| WorkItem statuses | 12 |
| Worker function variants | 4 (Sync, Persistent, ExchangeProcessor, None) |
| Worker outcomes | 5 (sealed) |
| Work SPI interfaces | 42 (17 core + progress + issue-tracker) |
| Engine SPIs | 15+ |
| Persistence backends (work) | 4 (JPA/Postgres, MongoDB/Quarkus, MongoDB/Spring, in-memory) |
| Persistence backends (engine) | 5 (in-memory, Hibernate/Panache, Spring Data JPA, H2, PostgreSQL with RLS) |
| Planning strategies | 3 (GOAP, HTN, DAG) |
| Dispatch handler types | 6 (sync agent, flow, A2A, MCP, ReAct, pattern-based) |
| Framework support | Dual (Quarkus + Spring Boot) |
| REST endpoints (engine) | 20+ |
| REST resources (work, MCP-annotated) | 25+ |

---

## Consistency Benefit

Enterprise Execution doesn't operate in isolation. Because it shares
the platform's CDI model, event system, tenancy model, and audit
trail:

- **Worker dispatch uses platform agent infrastructure** for LLM
  backends — the same AgentProvider SPI, the same rate limiting, the
  same credential resolution
- **Routing uses ledger trust scores** — Bayesian EigenTrust feeds
  directly into the trust signal provider without an integration layer
- **CBR experience** feeds from neocortex — the same CaseRetriever
  used for knowledge retrieval powers the experience signal provider
- **Human tasks share tenancy and ACL** — the same `CurrentPrincipal`,
  the same tenant-scoped repositories, the same ACL grants
- **Lifecycle events flow through the platform** — `CaseLifecycleEvent`
  and `WorkItemLifecycleEvent` are CDI events that integrate with
  ledger (audit), qhorus (communication), and notifications without
  coupling
- **Expression engine delegates to platform** — same JQ/MVEL/JEXL
  registry everywhere, including binding expressions, SLA conditions,
  and outcome evaluation
- **SLA overrides use platform preferences** — per-tenant configuration
  through the shared preference hierarchy

---

## Connections to Other Areas

| Area | Connection |
|------|-----------|
| [Declaration Surface](01-declaration-surface.md) | Case definitions in YAML or annotations declare bindings, workers, and planning strategies. The engine compiles them into runtime execution plans. |
| [Agentic Orchestration](02-agentic-orchestration.md) | Blocks patterns (supervisor, debate, voting) execute as pattern-based worker handlers within the engine. Orchestration patterns compose with case lifecycle. |
| [AI Knowledge & Learning](03-ai-knowledge-learning.md) | CBR provides experience signals for routing. RAG provides knowledge context for workers. Agent memory persists across case executions. |
| [Accountability & Governance](05-accountability-governance.md) | Oversight gates enforce approval before execution. Every dispatch produces a ledger entry. Trust scores feed routing. Protocol enforcement governs agent communication during execution. |
| [Convergence & Situational Awareness](06-convergence-awareness.md) | Desired-state reconciliation uses workers for node provisioning. RAS situation detection triggers new cases. The ops module uses the engine to manage its own infrastructure. |
| [Agent Identity & Cognition](07-agent-identity-cognition.md) | Agent descriptors feed personality routing signals. Social cognition renders during multi-agent coordination within cases. BDI beliefs influence orchestration decisions. |
| [The Shared Foundation](08-shared-foundation.md) | Platform identity, expressions, notifications, ACL, credentials, and agent infrastructure are all consumed by the execution layer. |
| [The Application Surface](09-application-surface.md) | Domain components render case state, work item inboxes, progress tracking, and trust-augmented routing decisions. Playbook automation integrates as a worker transport. |

---

## Architecture

![Enterprise Execution Architecture](images/brief/enterprise-execution.svg)

*Case definitions compile into runtime plans. The planning layer
selects strategies (GOAP, HTN, DAG). Composable signal routing scores
worker candidates across five dimensions. Dispatch sends work to any
of seven transport backends. Workers return sealed outcomes. Oversight
gates intercept consequential actions. The entire path is audited.*

---

## Vision

- **Spring completeness** — 11 CDI modules awaiting core extraction
  for Spring Boot deployment parity
- **Auto-bootstrap** — auto-discover YAML case definitions from the
  classpath without explicit registration
- **Multi-cluster K8s** — dispatch Jobs to multiple Kubernetes clusters
- **Federation** — cross-cluster WorkItem distribution (module active,
  implementation in progress)
- **CBR-to-playbook mapping** — convert CBR plan traces into
  executable playbook steps
