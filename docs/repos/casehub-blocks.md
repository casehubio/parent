# casehub-blocks

**GitHub:** [casehubio/blocks](https://github.com/casehubio/blocks)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Reusable building blocks for CaseHub applications — composed from qhorus, engine, and work primitives. Foundation-adjacent library that sits between the foundation tier and application tier. Single module, single artifact: `casehub-blocks`.

**What blocks does:** packages recurring cross-application patterns that require LLM integration, classical AI, or foundational API composition. Now includes a full agentic orchestration framework with DAG-based execution plans, hybrid (static + LLM) task decomposition, and composable routing/aggregation/termination strategies.

**What blocks does NOT do:** generic utilities (backoff, rate limiters), pure SPI unifications (those stay in API modules), or domain-specific logic that happens to be duplicated but doesn't involve AI or foundational integration.

---

## Scope Criteria

A pattern belongs in blocks if it meets at least one of these criteria:
1. **Needs an LLM in the loop** — the pattern involves LLM invocation, prompt construction, or LLM-driven decision-making
2. **Uses classical AI** — classical planning, Bayesian reasoning, CEP (complex event processing), or similar
3. **Requires integration across foundational platform parts that the consuming module does not already depend on** — the pattern composes across qhorus, engine, work, or eidos APIs in combinations that would otherwise force every consumer to take on new cross-module dependencies. If all dependencies are already available in the consuming module's API tier, the type belongs in that API module, not blocks.

**The test:** if removing the LLM/AI/integration aspect leaves a generic utility, it belongs in platform. If removing the domain-specific aspect leaves a reusable AI-integration pattern, it belongs in blocks.

---

## Module Structure

Single module — `casehub-blocks` is a flat library, not a multi-module reactor.

| Module | Artifact | Contents |
|--------|----------|----------|
| (root) | `casehub-blocks` | Six packages: channel, agentic (nine sub-packages), conversation, routing, routing.agent, summarisation |

---

## Package: `io.casehub.blocks.channel`

Channel utility blocks — message metadata encoding, context tracking, bounded projection, and agent dispatch coordination.

| Class | What it does |
|-------|-------------|
| `ChannelMessageMeta` | Sentinel-prefixed key=value metadata headers in message bodies. Apps choose their own sentinel. Methods: `parseMeta()`, `bodyContent()`, `encode()`, `parseInt()` |
| `ContextTracker` | Incremental LLM context window usage tracking via atomic counters. Thread-safe. |
| `ContextSnapshot` | Immutable record of context state: contribution chars, window size, effective %, threshold exceeded |
| `BoundedProjectionDecorator<S>` | Generic decorator wrapping any qhorus `ChannelProjection<S>` — skips messages past a configurable bound. Consumer supplies the value extraction function. |
| `ChannelAgentHandler` | SPI interface for sub-task handlers: `handles()`, `prepareTask()`, `buildResponse()`. First-match routing. |
| `ChannelAgentDispatcher` | First-match handler routing + agent invocation. Takes `Function<AgentTask, String>` (agent provider) and `Consumer<MessageDispatch>` (message sink). Subclass to override `onError()`. |
| `ChannelAgentRequest` | Record: channelId, correlationId, message (the sub-task trigger) |
| `AgentTask` | Record: systemPrompt, assembledInput (what to send to the LLM) |
| `ChannelEventAdapter` | `MessageObserver` bridge — extracts events from qhorus channel messages via configurable extractor function, publishes to `EventStreamBus`. Optional channel name filtering. |
| `ChannelEventPublisher` | Reverse bridge — subscribes to `EventStreamBus`, dispatches events back to qhorus channels via `MessageDispatcher` with configurable message building. |
| `AgentResultParseException` | Unchecked exception for handler parse failures |

---

## Package: `io.casehub.blocks.conversation`

Structured conversation protocol — reusable infrastructure for multi-agent deliberation channels. Extracted from drafthouse via casehubio/drafthouse#79, #80, #81, #83.

| Class | What it does |
|-------|-------------|
| `ConversationProtocol` | Sentinel-based metadata encoding/decoding for structured conversation messages. Defines entry types, round markers, status transitions. |
| `ConversationProjection` | Abstract base class for conversation-style channel projections. Folds channel messages into `ConversationState` by dispatching on metadata entry types. Infrastructure types (MEMO, SUB_TASK_*, FLAG_HUMAN, RESTART_CONTEXT) handled by base; domain entry types dispatched via three hook methods: `sentinel()`, `isPointInitiator(entryType)`, `statusAfter(entryType)` — configurable vocabulary per consumer. |
| `ConversationFold` | Fold operations for typed-message projections — accumulates conversation state from a message stream. |
| `ConversationState` | Immutable snapshot of conversation state: points by thread, round boundaries, flags, sub-task status. |
| `ConversationPoint` | Individual point in a conversation thread — classification, priority, content, agent attribution. |
| `ConversationRenderer` | Pluggable markdown rendering of conversation state — round-by-round or thread-by-thread views. |
| `ConversationRendererConfig` | Configuration for renderer: section ordering, inclusion filters, format options. |
| `ThreadEntry` | Entry within a conversation thread — point + responses + sub-task findings. |
| `PointClassification` | Open type system for classifying conversation points (replaces drafthouse's closed `EntryType` enum). |
| `Priority` | Priority level for conversation points — used in rendering and attention ordering. |
| `RoundMemo` | Summary memo for a completed conversation round — key outcomes, unresolved points. |
| `FlagEntry` | Flag raised during conversation — attention markers for moderators or supervisors. |
| `SubTaskFinding` | Result from a sub-agent task (verify, analyse, etc.) attached to a conversation point. Uses `TaskStatus` (from `io.casehub.api.model`) — `SubTaskStatus` removed, migrated to `TaskStatus`. |

---

## Package: `io.casehub.blocks.agentic`

Compositional agentic orchestration framework — nine sub-packages implementing five SPIs for routing, decomposition, activation, aggregation, and termination, plus execution plans, execution drivers, and pre-composed pattern builders.

| Sub-package | What it contains |
|-------------|-----------------|
| `agentic` | Foundation types: `AgentRef` (sealed, extends `ExecutorRef`: WorkerAgent, ChannelAgent, HumanAgent, ExternalAgent, ComposedAgent), `AgentResult`, `RoutingCandidate`, `FailurePolicy`, `AgentCardSupport` (LLM-readable agent description builder for routing prompts) |
| `agentic.routing` | Routing SPI: `RoutingStrategy<T>`, `RoutingDecision` (sealed: Selected, Unresolvable, Escalate), `RoutingContext`, `Routing` (factory), `FirstMatchRouting`, `RoundRobinRouting`, `SequentialRouting`, `LlmSelectedRouting`, `StageGate` (interface for staged binding visibility), `StageAwareCandidateSupplier` (filters candidates by active staged bindings) |
| `agentic.decomposition` | Decomposition SPI: `DecompositionStrategy<T>` (returns `Uni<ExecutionPlan<T>>`), `DecompositionContext<T>` (state + agents + depth), `Decomposition` (factory), `TaskNode` (sealed: `LeafTask` extends `TaskDescriptor` / `CompoundTask`), `LeafTask` (sealed: `PrimitiveTask` / `PlannedTask` — both use `AgentRef` as executor, report `TaskStatus`), `DecompositionMethod`, `IdentityDecomposition`, `StaticDecomposition`, `LlmDecomposition` (LLM-driven task planning from goal + state + agent cards), `HybridDecomposition` (static-first with LLM fallback — ChatHTN-style), `NoMethodMatchedException` |
| `agentic.plan` | `ExecutionPlan<T>` — DAG record expressing task dependencies with `ExecutionNode<T>` (id, task, dependsOn, `JoinType` ALL_OF/ANY_OF). Validated: no cycles, all references exist, at least one entry node. Methods: `entryNodeIds()`, `exitNodeIds()`, `topologicalSort()`. Factory methods: `singleton()`, `sequence()`, `parallel()`, `fromList()`, `sequentialMerge()` |
| `agentic.activation` | Activation SPI: `ActivationRule<T>`, `ActivationContext`, `Activation` (factory), `OnExplicitDispatch`, `MaxIterationsGuard` |
| `agentic.aggregation` | Aggregation SPI: `AggregationStrategy<T>`, `AggregationContext`, `AggregationResult` (sealed: Resolved, Partial, Deadlocked), `Aggregation` (factory), `PassThrough`, `CollectAll`, `MajorityVote` |
| `agentic.termination` | Termination SPI: `TerminationCondition<T>`, `TerminationContext`, `TerminationDecision` (sealed: Continue, Complete, Failed, Escalate), `Termination` (factory), `GoalReached`, `MaxIterationsTermination`, `JudgeConvergence` |
| `agentic.model` | Execution model: `ExecutionModel<T>`, `ExecutionDriver<T>`, `AbstractExecutionDriver`, `OrchestratedDriver`, `ChoreographedDriver`, `AgentInvoker<T>`, `ExecutionResult` (sealed: Completed, Failed, Escalated, Cancelled), `ExecutionState` (sealed: Idle, Running, WaitingForAgent, WaitingForEvent, Complete, Faulted, Cancelled), `ExecutionEventListener` |
| `agentic.listener` | Accountability listeners: `OrchestrationEventType`, `EventLogListener` (operational audit via EventSink), `LedgerExecutionListener` (compliance audit via LedgerSink), `MetricsListener` (OTel metrics via Meter) |
| `agentic.pattern` | Pattern DSL: `Patterns` entry point, `AbstractPatternBuilder`, 8 builders (Supervisor, Sequence, Loop, Parallel, Voting, Debate, Conditional, HTN) |

---

## Package: `io.casehub.blocks.routing`

Trust routing audit types — compliance records for trust-weighted routing decisions. Preference-to-policy utilities (`TrustRoutingPolicyKeys`, `TrustRoutingPolicyResolver`, `DoublePreference`, `IntPreference`) moved to engine-api — domain repos now implement `TrustRoutingPolicyProvider` directly.

| Class | What it does |
|-------|-------------|
| `RoutingDecisionRecord` | Compliance audit record for trust-weighted routing decisions: capabilityTag, workerId, trustScoreAtRouting, thresholdApplied, evidenceEntryId. |
| `TrustRoutingRequirement` | Compliance evidence wrapper: requirementId, citation, mechanism, status, decisions. |
| `RequirementStatus` | Enum: CLOSED, PARTIAL, BREACHED, GAP. |

---

## Package: `io.casehub.blocks.routing.agent`

AI-powered `AgentRoutingStrategy` implementations for the engine's routing pipeline, plus composable prompt enrichment, plan composition analysis, and outcome recording infrastructure. Strategies are selected by name via `StrategyResolver` (engine#634). Optional trust classification via `Instance<T>` — activates when engine-ledger is on the consumer's classpath.

| Class | What it does |
|-------|-------------|
| `LlmAgentRoutingStrategy` | `AgentRoutingStrategy` (id: `"llm"`). Asks an LLM via `AgentProvider` to reason about which candidate best fits the task. Delegates to `RoutingPromptAssembler` for composable prompt enrichment (CBR history, future signal sources). Optional trust classification. Worker pool offloading. |
| `CbrAgentRoutingStrategy` | `AgentRoutingStrategy` (id: `"cbr"`). Uses `CbrCaseMemoryStore` to retrieve similar past cases and analyse worker success rates from `PlanTrace` entries. Signal assembly via `RoutingSignalAssembler`. Falls back to `AgentGraphQuery.topAgentsByOutcome()` when CBR store unavailable. Optional trust classification. |
| `CbrRoutingPromptSection` | `RoutingPromptSection` implementation — renders historical CBR evidence (agent success rates + case details) into the LLM routing prompt. Filters to eligible agents only. |
| `PlanCompositionAnalyser` | `@ApplicationScoped` `RoutingSignalProvider` — scores candidates based on case-level outcomes in multi-step plans. Examines `planTrace.size() >= 2`, weights by `CbrCaseOutcomeWeights` and similarity score. Returns per-candidate `RoutingSignal`. |
| `CbrCaseOutcomeWeights` | SPI for case-level outcome weights used by `PlanCompositionAnalyser`. Domain repos override `DefaultCbrCaseOutcomeWeights` (`@DefaultBean`) to tune how COMPLETED/FAULTED/CANCELLED outcomes influence plan-fit scoring. |
| `DefaultCbrCaseOutcomeWeights` | `@DefaultBean @ApplicationScoped` default weights: COMPLETED=1.0, FAULTED=0.2, CANCELLED=0.0. |
| `CbrOutcomeWeights` | SPI for step-level outcome weights. Used by `CbrAgentRoutingStrategy`. |
| `DefaultCbrOutcomeWeights` | `@DefaultBean @ApplicationScoped` default step-level outcome weights. |
| `RoutingSupport` | Package-private utility — shared prompt building, response parsing, `AgentProvider` invocation, and trust classification extraction (`TrustFilterOutcome` sealed interface). Used by both `LlmAgentRoutingStrategy` and `CbrAgentRoutingStrategy`. |

---

## Package: `io.casehub.blocks.summarisation`

Layered event summarisation framework — temporal event accumulation with configurable window policies and pluggable summarisation strategies. Extracted from quarkmind via blocks#27.

| Class | What it does |
|-------|-------------|
| `EventLevel` | Enum defining temporal granularity levels for event accumulation |
| `LevelEvent` | Event at a specific temporal level — carries content and metadata |
| `WindowPolicy` | Configurable window boundaries for event accumulation (time-based, count-based) |
| `EventAccumulator` | Accumulates events within a window policy, triggers summarisation at window boundaries |
| `EventStreamBus` | CDI event bus for streaming events through the summarisation pipeline |
| `Summariser` | SPI for pluggable summarisation strategies — consumers implement domain-specific summarisation |
| `SummarisationRunner` | Orchestrates the summarisation pipeline: accumulate → summarise → emit higher-level events |
| `KeyedAccumulator` | Keyed event accumulator — groups events by key (via extractor function), drains groups when a completion test passes or a stale timeout elapses. Thread-safe. Supports bidirectional channel bridges. |
| `KeyedSummarisationRunner` | Keyed variant of `SummarisationRunner` — uses `KeyedAccumulator` to group events, then summarises each group independently. Tick-driven (call `tick(now)` on a schedule). |

---

## Trust Routing Architecture

The trust routing system spans four layers — blocks owns AI-powered routing strategies and compliance audit types.

| Layer | Owner | What it does |
|-------|-------|-------------|
| Score computation | **ledger** | `TrustScoreRoutingPublisher` computes trust scores from ledger entries and publishes them. The `trust-score-routing` package owns all score payloads and events. |
| Policy configuration | **engine-api** | `TrustRoutingPolicyProvider` SPI + `TrustRoutingPolicyKeys` + `TrustRoutingPolicyResolver` (moved from blocks). Domain repos implement `TrustRoutingPolicyProvider` using these utilities. |
| Classical strategy execution | **engine** | `TrustWeightedAgentStrategy` (engine-ledger) applies trust scores. `SemanticAgentRoutingStrategy` (engine-ai) adds embedding-based re-ranking. Strategies stay where their differentiating dependency lives. |
| AI-powered strategy execution | **blocks** (routing.agent package) | `LlmAgentRoutingStrategy` (LLM reasoning with composable prompt enrichment), `CbrAgentRoutingStrategy` (case-based evidence with signal assembly), and `PlanCompositionAnalyser` (multi-step plan scoring). All optionally compose with trust classification via `Instance<TrustCandidateClassifier>`. |
| Compliance audit types | **blocks** (routing package) | `RoutingDecisionRecord`, `TrustRoutingRequirement`, `RequirementStatus` — audit trail records for trust-weighted decisions. |

Domain repos (aml, devtown, clinical, life, ops) implement `TrustRoutingPolicyProvider` from engine-api — they configure policy parameters, not compute scores or execute routing.

---

## Consolidation Epic

Epic #28 tracks extraction of shared patterns from domain repos into blocks. Each child issue covers a distinct pattern duplicated across 2+ repos.

| # | Title | Scale | Complexity | Ready? | Destination | Migrates from | Downstream consumers |
|---|-------|-------|------------|--------|-------------|---------------|---------------------|
| #17 | Trust routing YAML | M | Med | **Done → moved to engine-api** | engine-api | aml, devtown, clinical, life, ops, soc | aml, devtown, clinical, life, ops, soc, fsitrading |
| #22 | Debate channel infrastructure | L | High | **Done** | blocks | drafthouse | drafthouse, devtown, clinical, aml, claudony |
| #23 | Oversight gate lifecycle + risk classification | L | High | **Done → moved to engine-api** | engine-api | openclaw, engine-api | openclaw, aml, soc, life, devtown, clinical, iot, claudony |
| #24 | Universal pluggable routing strategy | L | High | **Moved → engine#634** | engine | engine, work | engine, work, qhorus, eidos |
| #30 | AI routing strategy impls (trust, LLM, CBR) | M | Med | **Done** | blocks | — | engine, domain repos |
| #25 | Worker data coordination (DataExchange/DataChannel) | L | High | **Moved → engine#633** | engine | engine | engine, workers, desiredstate |
| #27 | Layered event summarisation | M | Med | **Done** | blocks | quarkmind | quarkmind, iot, aml, clinical |

---

## Depends On

**Compile:** `casehub-qhorus-api`, `casehub-work-api`, `casehub-engine-api`, `casehub-worker-api`, `org.jspecify:jspecify`, `com.fasterxml.jackson.core:jackson-databind`

**Provided:** `io.smallrye.reactive:mutiny`, `casehub-platform-agent-api`, `casehub-platform-api`, `casehub-ledger-api`, `casehub-neocortex-memory-api`, `io.opentelemetry:opentelemetry-api`

**Test:** `casehub-qhorus`, `casehub-qhorus-testing`, `casehub-engine`, `casehub-engine-testing`, `assertj`, `mockito`, `awaitility`, `io.opentelemetry:opentelemetry-sdk-testing`

---

## Depended On By

| Repo | What it uses |
|------|-------------|
| casehub-drafthouse | Channel + conversation blocks — DebateProtocol delegates to `ConversationProtocol`, DebateChannelProjection extends `ConversationProjection` (abstract fold with configurable vocabulary), ReviewChannelProjection uses `ConversationFold`/`ConversationState`, `ChannelAgentDispatcher` subclass with debate-specific error dispatch, `BoundedProjectionDecorator` for round bounding, `ContextTracker` for LLM window tracking |
| casehub-engine | Agentic: `ExecutionPlan`, `ExecutionDriver`, `AgentInvoker`, `StageGate`, `StageAwareCandidateSupplier` for stage-gated routing |
| casehub-aml | Routing agent: `CbrRoutingPromptSection`, `PlanCompositionAnalyser`. Summarisation: `KeyedAccumulator`, `ChannelEventAdapter` |
| casehub-devtown | Routing agent: `CbrRoutingPromptSection` |
| casehub-clinical | Routing agent: `CbrRoutingPromptSection` |
| casehub-quarkmind | Summarisation: `KeyedAccumulator`, `KeyedSummarisationRunner`, `EventStreamBus` |

---

## Configuration

No runtime configuration — blocks is a pure library, not a Quarkus extension. All configuration happens via code (SPI implementations, CDI beans).
