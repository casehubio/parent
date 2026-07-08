# casehub-blocks

**GitHub:** [casehubio/blocks](https://github.com/casehubio/blocks)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Reusable building blocks for CaseHub applications — composed from qhorus, engine, and work primitives. Foundation-adjacent library that sits between the foundation tier and application tier. Single module, single artifact: `casehub-blocks`.

**What blocks does:** packages recurring cross-application patterns that require LLM integration, classical AI, or foundational API composition.

**What blocks does NOT do:** generic utilities (backoff, rate limiters), pure SPI unifications (those stay in API modules), or domain-specific logic that happens to be duplicated but doesn't involve AI or foundational integration.

---

## Scope Criteria

A pattern belongs in blocks if it meets at least one of these criteria:
1. **Needs an LLM in the loop** — the pattern involves LLM invocation, prompt construction, or LLM-driven decision-making
2. **Uses classical AI** — classical planning, Bayesian reasoning, CEP (complex event processing), or similar
3. **Requires integration with foundational platform parts** — the pattern composes across qhorus, engine, work, or eidos APIs in a way that would otherwise be duplicated by every consumer

**The test:** if removing the LLM/AI/integration aspect leaves a generic utility, it belongs in platform. If removing the domain-specific aspect leaves a reusable AI-integration pattern, it belongs in blocks.

---

## Module Structure

Single module — `casehub-blocks` is a flat library, not a multi-module reactor.

| Module | Artifact | Contents |
|--------|----------|----------|
| (root) | `casehub-blocks` | Six packages: channel, agentic, conversation, oversight, routing, routing.agent |

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
| `AgentResultParseException` | Unchecked exception for handler parse failures |

---

## Package: `io.casehub.blocks.conversation`

Structured conversation protocol — reusable infrastructure for multi-agent deliberation channels. Extracted from drafthouse via casehubio/drafthouse#79, #80, #81, #83.

| Class | What it does |
|-------|-------------|
| `ConversationProtocol` | Sentinel-based metadata encoding/decoding for structured conversation messages. Defines entry types, round markers, status transitions. |
| `ConversationProjection` | Incremental projection over conversation messages — maintains fold state, tracks rounds, classifies points. |
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
| `SubTaskFinding` | Result from a sub-agent task (verify, analyse, etc.) attached to a conversation point. |
| `SubTaskStatus` | Status tracking for dispatched sub-agent tasks within a conversation. |

---

## Package: `io.casehub.blocks.oversight`

Oversight gate lifecycle and risk classification — SPIs for gating worker actions pending human approval. Extracted from engine-api via casehubio/engine (3cdb1f90) and casehubio/openclaw (37a7044).

| Class | What it does |
|-------|-------------|
| `ActionRiskClassifier` | Blocking SPI: classifies a worker's `PlannedAction` → `RiskDecision`. Annotate implementations with `@RiskClassifier @ApplicationScoped`. |
| `ReactiveActionRiskClassifier` | Reactive SPI: primary interface called by the engine. Consumers implement `ActionRiskClassifier` instead — the chain bridges blocking to reactive. |
| `RiskDecision` | Sealed interface (Autonomous, GateRequired). GateRequired carries reason, reversible flag, candidateGroups, expiresIn, scope. |
| `ClassificationContext` | Record: workerId, caseId, tenancyId, caseDefinitionName, capabilityName, bindingName. |
| `RiskClassifier` | CDI `@Qualifier` for `ActionRiskClassifier` implementations — prevents circular injection with the chain. |
| `ChainedReactiveActionRiskClassifier` | `@ApplicationScoped` CDI bean: discovers all `@RiskClassifier`-qualified classifiers, chains them, returns most-restrictive `RiskDecision`. Fail-safe: GateRequired on any exception. |
| `OversightGateService` | Blocking SPI: `openGate()` → `GateOutcome`, `fulfill()`. |
| `ReactiveOversightGateService` | Reactive SPI: `openGate()` → `Uni<GateOutcome>`, `fulfill()` → `Uni<Void>`. |
| `GateOutcome` | Sealed interface (Autonomous, GatePending). GatePending carries gateId + reason. |

---

## Package: `io.casehub.blocks.agentic`

Compositional agentic orchestration framework — eight sub-packages implementing five SPIs for routing, decomposition, activation, aggregation, and termination, plus execution drivers and pre-composed pattern builders.

| Sub-package | What it contains |
|-------------|-----------------|
| `agentic` | Foundation types: `AgentRef` (sealed: WorkerAgent, ChannelAgent, HumanAgent, ExternalAgent, ComposedAgent), `AgentResult`, `RoutingCandidate`, `FailurePolicy` |
| `agentic.routing` | Routing SPI: `RoutingStrategy<T>`, `RoutingDecision` (sealed: Selected, Unresolvable, Escalate), `FirstMatchRouting`, `RoundRobinRouting`, `SequentialRouting`, `LlmSelectedRouting` |
| `agentic.decomposition` | Decomposition SPI: `DecompositionStrategy<T>`, `TaskNode` (sealed: PrimitiveTask, CompoundTask), `DecompositionMethod`, `IdentityDecomposition`, `StaticDecomposition` |
| `agentic.activation` | Activation SPI: `ActivationRule<T>`, `ActivationContext`, `OnExplicitDispatch`, `MaxIterationsGuard` |
| `agentic.aggregation` | Aggregation SPI: `AggregationStrategy<T>`, `AggregationResult` (sealed: Resolved, Partial, Deadlocked), `PassThrough`, `CollectAll`, `MajorityVote` |
| `agentic.termination` | Termination SPI: `TerminationCondition<T>`, `TerminationDecision` (sealed: Continue, Complete, Failed, Escalate), `GoalReached`, `MaxIterationsTermination`, `JudgeConvergence` |
| `agentic.model` | Execution model: `ExecutionModel<T>`, `ExecutionDriver<T>`, `AbstractExecutionDriver`, `OrchestratedDriver`, `ChoreographedDriver`, `AgentInvoker<T>`, `ExecutionResult` (sealed: Completed, Failed, Escalated, Cancelled), `ExecutionState` (sealed: Idle, Running, WaitingForAgent, WaitingForEvent, Complete, Faulted, Cancelled), `ExecutionEventListener` |
| `agentic.listener` | Accountability listeners: `OrchestrationEventType`, `EventLogListener` (operational audit via EventSink), `LedgerExecutionListener` (compliance audit via LedgerSink), `MetricsListener` (OTel metrics via Meter) |
| `agentic.pattern` | Pattern DSL: `Patterns` entry point, `AbstractPatternBuilder`, 8 builders (Supervisor, Sequence, Loop, Parallel, Voting, Debate, Conditional, HTN) |

---

## Package: `io.casehub.blocks.routing`

Shared trust routing utilities — eliminates duplicated preference-to-policy boilerplate across domain repos.

| Class | What it does |
|-------|-------------|
| `DoublePreference` | `SingleValuePreference` record for double-typed preference values. Replaces copies in aml, devtown, life. |
| `IntPreference` | `SingleValuePreference` record for int-typed preference values. Replaces copies in aml, devtown. |
| `TrustRoutingPolicyKeys` | Parameterised `PreferenceKey` definitions — scope prefix + 4 universal keys (threshold, minimum-observations, borderline-margin, blend-factor) + builder for domain-specific quality floor keys. |
| `TrustRoutingPolicyResolver` | Stateless utility: `resolve(Preferences, TrustRoutingPolicyKeys)` → `TrustRoutingPolicy`. Also exposes `collectFloors()` for hybrid providers that read some fields from a domain registry. |
| `RoutingDecisionRecord` | Compliance audit record for trust-weighted routing decisions: capabilityTag, workerId, trustScoreAtRouting, thresholdApplied, evidenceEntryId. |
| `TrustRoutingRequirement` | Compliance evidence wrapper: requirementId, citation, mechanism, status, decisions. |
| `RequirementStatus` | Enum: CLOSED, PARTIAL, BREACHED, GAP. |

---

## Package: `io.casehub.blocks.routing.agent`

AI-powered `AgentRoutingStrategy` implementations for the engine's routing pipeline, plus composable prompt enrichment and outcome recording infrastructure. Strategies are selected by name via `StrategyResolver` (engine#634). Optional trust classification via `Instance<T>` — activates when engine-ledger is on the consumer's classpath.

| Class | What it does |
|-------|-------------|
| `LlmAgentRoutingStrategy` | `AgentRoutingStrategy` (id: `"llm"`). Asks an LLM via `AgentProvider` to reason about which candidate best fits the task. Delegates to `RoutingPromptAssembler` for composable prompt enrichment (CBR history, future signal sources). Optional trust classification. Worker pool offloading. |
| `CbrAgentRoutingStrategy` | `AgentRoutingStrategy` (id: `"cbr"`). Uses `CbrCaseMemoryStore` to retrieve similar past cases and analyse worker success rates from `PlanTrace` entries. Falls back to `AgentGraphQuery.topAgentsByOutcome()` when CBR store unavailable. Uses `RoutingFeatureExtractor` for query construction. Optional trust classification. |
| `RoutingPromptSection` | SPI for composable LLM prompt enrichment. CDI-discovered — all implementations render into the prompt. Returns null to skip. Not a `NamedStrategy`. |
| `RoutingPromptAssembler` | `@ApplicationScoped` bean that iterates all `RoutingPromptSection` implementations, sorts by `@Priority`, catches rendering failures, and concatenates non-null results. Used by `LlmAgentRoutingStrategy`. |
| `CbrRoutingPromptSection` | `RoutingPromptSection` implementation — queries `CbrCaseMemoryStore` for similar past cases and formats historical context (agent success rates + case details) for the LLM prompt. Filters to eligible agents only. |
| `RoutingFeatureExtractor` | SPI for extracting structured features and problem text from `AgentRoutingContext`. `@DefaultBean` `TextOnlyFeatureExtractor` uses `caseContext.toString()` for problem text and `Map.of()` for features. Domain repos override with `@ApplicationScoped` (displaces `@DefaultBean` automatically). |
| `TextOnlyFeatureExtractor` | `@DefaultBean` implementation of `RoutingFeatureExtractor` — text-only similarity, no structured features. |
| `CbrRoutingOutcomeRecorder` | Implements engine-api `RoutingOutcomeRecorder` — records routing outcomes as `PlanCbrCase` entries in the CBR store, creating a feedback loop. Uses `RoutingFeatureExtractor` for consistent feature vocabulary. |
| `RoutingSupport` | Package-private utility — shared prompt building, response parsing, `AgentProvider` invocation, and trust classification extraction (`TrustFilterOutcome` sealed interface). Used by both `LlmAgentRoutingStrategy` and `CbrAgentRoutingStrategy`. |

---

## Trust Routing Architecture

The trust routing system spans four layers — blocks owns policy configuration AND AI-powered routing strategies.

| Layer | Owner | What it does |
|-------|-------|-------------|
| Score computation | **ledger** | `TrustScoreRoutingPublisher` computes trust scores from ledger entries and publishes them. The `trust-score-routing` package owns all score payloads and events. |
| Policy configuration | **blocks** (routing package) + **engine-api** (`TrustRoutingPolicyProvider` SPI) | `TrustRoutingPolicyKeys` + `TrustRoutingPolicyResolver` provide the shared preference-to-policy loading. Domain repos implement `TrustRoutingPolicyProvider` using these utilities. |
| Classical strategy execution | **engine** | `TrustWeightedAgentStrategy` (engine-ledger) applies trust scores. `SemanticAgentRoutingStrategy` (engine-ai) adds embedding-based re-ranking. Strategies stay where their differentiating dependency lives. |
| AI-powered strategy execution | **blocks** (routing.agent package) | `LlmAgentRoutingStrategy` (LLM reasoning) and `CbrAgentRoutingStrategy` (case-based evidence). Both optionally compose with trust classification via `Instance<TrustCandidateClassifier>`. |

Domain repos (aml, devtown, clinical, life, ops) implement `TrustRoutingPolicyProvider` from engine-api — they configure policy parameters, not compute scores or execute routing.

---

## Consolidation Epic

Epic #28 tracks extraction of shared patterns from domain repos into blocks. Each child issue covers a distinct pattern duplicated across 2+ repos.

| # | Title | Scale | Complexity | Ready? | Destination | Migrates from | Downstream consumers |
|---|-------|-------|------------|--------|-------------|---------------|---------------------|
| #17 | Trust routing YAML | M | Med | **Done** | blocks | aml, devtown, clinical, life, ops, soc | aml, devtown, clinical, life, ops, soc, fsitrading |
| #22 | Debate channel infrastructure | L | High | **Done** | blocks | drafthouse | drafthouse, devtown, clinical, aml, claudony |
| #23 | Oversight gate lifecycle + risk classification | L | High | **Done** | blocks | openclaw, engine-api | openclaw, aml, soc, life, devtown, clinical, iot, claudony |
| #24 | Universal pluggable routing strategy | L | High | **Moved → engine#634** | engine | engine, work | engine, work, qhorus, eidos |
| #30 | AI routing strategy impls (trust, LLM, CBR) | M | Med | **Done** | blocks | — | engine, domain repos |
| #25 | Worker data coordination (DataExchange/DataChannel) | L | High | **Moved → engine#633** | engine | engine | engine, workers, desiredstate |
| #27 | Layered event summarisation | M | Med | Not yet — quarkmind still baking | blocks | quarkmind | quarkmind, iot, aml, clinical |

---

## Depends On

**Compile:** `casehub-qhorus-api`, `casehub-work-api`, `casehub-engine-api`, `casehub-eidos-api`, `casehub-worker-api`, `org.jspecify:jspecify`

**Provided:** `io.smallrye.reactive:mutiny`, `casehub-platform-agent-api`, `casehub-platform-api`, `casehub-engine-ledger`, `casehub-ledger-api`, `casehub-neocortex-memory-api`, `io.opentelemetry:opentelemetry-api`

**Test:** `casehub-qhorus`, `casehub-qhorus-testing`, `casehub-engine`, `casehub-engine-testing`, `assertj`, `mockito`, `awaitility`, `io.opentelemetry:opentelemetry-sdk-testing`

---

## Depended On By

| Repo | What it uses |
|------|-------------|
| casehub-drafthouse | Channel + conversation blocks — DebateProtocol delegates to `ConversationProtocol`, DebateChannelProjection extends `ConversationProjection`, ReviewChannelProjection uses `ConversationFold`/`ConversationState`, `ChannelAgentDispatcher` subclass with debate-specific error dispatch, `BoundedProjectionDecorator` for round bounding, `ContextTracker` for LLM window tracking |
| casehub-engine | Oversight: `GateOutcome`, `OversightGateService`, `ReactiveOversightGateService` (NoOp impls), `ReactiveActionRiskClassifier`, `RiskDecision`, `ClassificationContext` (handler + health check) |
| casehub-openclaw | Oversight: `ActionRiskClassifier`, `RiskClassifier`, `RiskDecision`, `ClassificationContext`, `GateOutcome` (concrete OversightGateService impl) |
| casehub-aml | Routing: `TrustRoutingPolicyKeys`, `TrustRoutingPolicyResolver`, `DoublePreference`, `IntPreference`, `AmlRoutingFeatureExtractor` (implements `RoutingFeatureExtractor`). Oversight: `ActionRiskClassifier`, `RiskClassifier`, `RiskDecision`, `ClassificationContext` |
| casehub-devtown | Routing: `TrustRoutingPolicyKeys`, `TrustRoutingPolicyResolver.collectFloors()`, `DoublePreference`. Oversight: `ActionRiskClassifier`, `RiskClassifier`, `RiskDecision`, `ClassificationContext` |
| casehub-life | Routing: `TrustRoutingPolicyKeys`, `TrustRoutingPolicyResolver.collectFloors()`, `DoublePreference`. Oversight: `ActionRiskClassifier`, `RiskClassifier`, `RiskDecision`, `ClassificationContext` |
| casehub-soc | Oversight: `ActionRiskClassifier`, `RiskClassifier`, `RiskDecision`, `ClassificationContext` |
| casehub-clinical | Routing: `ClinicalRoutingFeatureExtractor` (implements `RoutingFeatureExtractor`). Oversight: `ActionRiskClassifier`, `RiskClassifier`, `RiskDecision`, `ClassificationContext` |
| casehub-iot | Oversight: `ActionRiskClassifier`, `RiskClassifier`, `RiskDecision`, `ClassificationContext` |

---

## Configuration

No runtime configuration — blocks is a pure library, not a Quarkus extension. All configuration happens via code (SPI implementations, CDI beans).
