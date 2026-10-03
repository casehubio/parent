# Drill-Down — Agentic Orchestration

*Five composable SPIs, two execution drivers, and a communications mesh that makes every message an accountable act.*

---

## Architecture Overview

Agentic orchestration in CaseHub is split across three repositories,
each owning a distinct architectural layer:

- **blocks** (25 modules, 903 source files) — pattern framework:
  composable SPIs, execution drivers, BDI primitives, social
  cognition, conversation protocol, summarisation, prompt
  optimisation.
- **qhorus** (23 modules, 29 store interfaces) — communications
  mesh: speech act messaging, commitment lifecycle, channel
  architecture, dispatch pipeline, protocol enforcement, watchdogs,
  A2A bridge.
- **claudony** (4 modules) / **openclaw** (3 modules) — fleet
  management: LLM session pools, remote terminal orchestration,
  agent execution bridge, commitment lifecycle MCP surface.

The engine consumes all three through adapter modules. `ExecutionModel`,
`ExecutionDriver`, `AgentRef`, and `RoutingCandidate` flow from blocks
into the engine's worker dispatch pipeline. Qhorus channels carry
commitment-tracked messages between agents. Fleet managers provision
and lifecycle LLM sessions.

---

## SPI Contracts

### Five Orchestration SPIs (blocks)

These SPIs are independently composable. Swap any one without
touching the others.

| SPI | Interface | Key methods | Governs |
|-----|-----------|-------------|---------|
| **Routing** | `RoutingStrategy` | `route(AgentRef[] candidates, RoutingContext ctx)` | Which agent handles which task |
| **Decomposition** | `DecompositionStrategy` | `decompose(Task task, DecompositionContext ctx)` → `DagPlan` | How tasks break into sub-tasks |
| **Activation** | `ActivationStrategy` | `shouldActivate(Task task, ActivationContext ctx)` | When a sub-task is ready to execute |
| **Aggregation** | `AggregationStrategy` | `aggregate(List<ExecutionResult> results, AggregationContext ctx)` | How sub-task results combine |
| **Termination** | `TerminationCondition` | `shouldTerminate(ExecutionState state)` | When orchestration stops |

**Routing strategy implementations:** 4 built-in (round-robin,
capability-match, weighted-random, priority-based) + LLM-selected
(prompt-based candidate evaluation) + CBR-evidence (experience-
weighted scoring from neocortex).

**Decomposition strategy implementations:** 9 strategies — identity
(no decomposition), flat (one level), hierarchical, GOAP
(backward-chaining from goal to preconditions), SHOP-style
(forward reasoning), HTN (hierarchical task networks with DAG
cycle validation), plan-based, LLM-generated, custom.

**Termination condition implementations:** 4 built-in (max-iterations,
timeout, all-complete, first-complete) + judge-convergence (LLM
evaluates whether output is sufficient).

### Execution Drivers (blocks)

| Driver | Model | Behaviour |
|--------|-------|-----------|
| `OrchestratedDriver` | Imperative while-loop | Central controller drives the decompose → route → activate → execute → aggregate → terminate cycle. Deterministic, auditable. |
| `ChoreographedDriver` | Event-reactive | Agents react to blackboard state changes. No central controller. Bindings fire on context mutation, not graph edges. |

Both drivers implement the same `ExecutionDriver` interface and use
the same SPI contracts. A case definition switches between them via
the `dispatchMode` field (`ORCHESTRATED` / `CHOREOGRAPHED`).

### Pattern Builders (blocks)

Eight pattern builders compose SPIs into named topologies:

| Pattern | Builder | Routing | Aggregation | Termination |
|---------|---------|---------|-------------|-------------|
| Supervisor | `SupervisorPatternBuilder` | LLM or capability-match | Single result | Explicit completion |
| Sequence | `SequencePatternBuilder` | Ordered | Chain (pass-through) | All complete |
| Loop | `LoopPatternBuilder` | Same agent | Accumulate | Condition or max-iterations |
| Parallel | `ParallelPatternBuilder` | Fan-out | Merge all | All complete |
| Voting | `VotingPatternBuilder` | Broadcast | Tally | Majority or unanimous |
| Debate | `DebatePatternBuilder` | Alternating | Convergence analysis | Judge convergence |
| HTN | `HtnPatternBuilder` | Capability-match per sub-task | DAG merge | DAG complete |
| Custom | `CustomPatternBuilder` | Any | Any | Any |

All extend `AbstractPatternBuilder` and are available in both Java
DSL and YAML.

### Dispatch Gate Pipeline (qhorus)

The 12-step pipeline enforces policy on every message. No bypass path.

| Step | Gate | Effect |
|------|------|--------|
| 1 | Paused check | Reject if channel is paused |
| 2 | ACL | Verify sender has write permission |
| 3 | Rate limiting | Token bucket per sender per channel |
| 4 | Capability routing | Route to agents matching required capabilities |
| 5 | Trust gate | Reject if sender trust score below channel threshold |
| 6 | Type policy | Enforce allowed message types per channel |
| 7 | Correlation integrity | Verify correlation chains are valid |
| 8 | Protocol evaluation | Evaluate against channel protocol rules |
| 9 | Enforcement gate | Advisory / blocking / quarantine based on violations |
| 10 | Overwrite | Handle LAST_WRITE channel semantics |
| 11 | Ledger | Create tamper-evident Merkle hash-chained audit entry |
| 12 | Fan-out | Deliver to all channel members via backend |

### Commitment Lifecycle (qhorus)

State machine for normative obligations:

```
OPEN → ACKNOWLEDGED → FULFILLED
                   → FAILED
                   → DECLINED
                   → DELEGATED
                   → EXPIRED (automatic deadline enforcement)
```

Each transition produces a CDI event consumed by engine orchestration,
ledger audit, and watchdog monitoring.

---

## Data Model

### Speech Act Types (qhorus)

10-type message taxonomy rooted in speech act theory:

| Type | Semantic obligation | Creates commitment? |
|------|--------------------|--------------------|
| `QUERY` | Request for information | No |
| `COMMAND` | Directive to act | Yes |
| `RESPONSE` | Answer to a query | No |
| `STATUS` | Progress update | No |
| `DECLINE` | Refusal of a command | Terminates commitment |
| `HANDOFF` | Transfer of responsibility | Delegates commitment |
| `DONE` | Task completion signal | Fulfils commitment |
| `FAILURE` | Task failure signal | Fails commitment |
| `PROPOSE` | Negotiation offer | Opens negotiation |
| `EVENT` | Broadcast notification | No |

### BDI Primitives (blocks)

| Type | Purpose | Key classes |
|------|---------|-------------|
| Belief | Structured agent beliefs | `Belief`, `BeliefSet`, `ConsistencyChecker` |
| Desire | Goal-directed intentions | `JointIntention`, `IntentionMonitor`, `ReconsiderationSignal` |
| Intention | Coalition formation | `CoalitionEvaluator`, `CapabilityCoverageEvaluator` |
| Judgment | Consensus decisions | `JudgmentDispatcher`, 5 `AgreementPolicy` variants, `CompositeVerifier` |

### Social Cognition Type Hierarchy (blocks)

90+ types across social sub-packages:

| Domain | Types | Renders as |
|--------|-------|------------|
| Mood | PAD model (Pleasure, Arousal, Dominance) | `MoodPromptSection` |
| Drives | 4 axes: curiosity, competence, affiliation, autonomy | `DrivePromptSection` |
| Personality evolution | Trait drift tracking, calibration feedback | `PersonalityPromptSection` |
| Mental model | BDI Theory of Mind per observed agent | `MentalModelPromptSection` |
| User model | Familiarity, relationship stages | `UserModelPromptSection` |
| Strategy learning | Strategy effectiveness tracking | `StrategyPromptSection` |
| Inner life | Proactive initiation from drives | `InnerLifePromptSection` |
| Narrative identity | First-person autobiography construction | `NarrativePromptSection` |
| Goal proposal | Drive-to-goal mapping with escalation | `GoalPromptSection` |
| Social emergence | Norm detection, collective goal formation | `EmergencePromptSection` |

The entire stack renders as `PromptSection` implementations for LLM
agent consumption. Social cognition is infrastructure — orchestration
patterns access it through CDI injection, not custom wiring.

### Conversation State (blocks)

| Type | Purpose |
|------|---------|
| `ConversationProjection` | Folds channel messages into `ConversationState` |
| `EpistemicCommonGround` | Tracks established / pending / disputed facts |
| `ConvergenceState` | 5 states: PROGRESSING → NARROWING → STABILISING → CONVERGED / DEADLOCK |
| `NegotiationProjection` | Bilateral / multilateral with acceptance policies |
| `TurnPolicy` | 4 variants: round-robin, addressed, point-addressed, free |

---

## Runtime Behaviour

### Orchestrated Execution Cycle

```
OrchestratedDriver.execute(task)
    │
    ├── DecompositionStrategy.decompose(task) → DagPlan
    │
    ├── for each sub-task in DagPlan:
    │     ├── ActivationStrategy.shouldActivate(sub-task)
    │     ├── RoutingStrategy.route(candidates, context)
    │     ├── ExecutionDriver.dispatch(sub-task, agent)
    │     └── collect ExecutionResult
    │
    ├── AggregationStrategy.aggregate(results)
    │
    └── TerminationCondition.shouldTerminate(state)
          ├── true  → return aggregated result
          └── false → loop
```

Virtual threads throughout. No reactive Mutiny pipelines, no
`CompletableFuture` chains.

### Fleet Management Lifecycle (claudony)

LLM session pools with suspend/resume semantics. Three-representation
parity: fluent Java DSL, YAML, and `@PoolDefinition` annotations with
APT code generation.

| Component | Type | Purpose |
|-----------|------|---------|
| `AgentPoolDefinition` | Model | Capacity, model, scaling policy, eviction policy |
| `AgentSessionManager` | Runtime | Session provisioning, suspend/resume via tmux |
| `ScalingScheduler` | Control | 3 policies: step thresholds, target-tracking, custom |
| `EvictionPolicy` SPI | Extension | Pluggable eviction strategies |
| `PoolMetricsRegistrar` | Observability | Micrometer + IoTDB time-series bridge |

Sessions survive across tasks — suspend/resume preserves
conversation context. No competing platform manages LLM CLI sessions
as persistent, pooled resources.

---

## Extension Points

| Extension | Mechanism | Effect |
|-----------|-----------|--------|
| Custom routing strategy | Implement `RoutingStrategy` CDI bean | Available in pattern builders and YAML |
| Custom decomposition | Implement `DecompositionStrategy` CDI bean | Available for HTN, GOAP, or custom patterns |
| Custom termination | Implement `TerminationCondition` CDI bean | Available in all patterns |
| Custom channel protocol | Implement protocol evaluator, register in qhorus | Enforced by dispatch pipeline step 8 |
| Custom watchdog condition | Implement `WatchdogCondition` CDI bean | Monitored alongside 11 built-in types |
| Custom scaling policy | Implement `ScalingPolicy` SPI | Available for claudony pool definitions |
| Custom eviction policy | Implement `EvictionPolicy` SPI | Available for claudony pool definitions |
| Custom speech pipeline | Implement `SpeechProvider` SPI (STT/TTS) | Pluggable alongside sherpa-onnx |

---

## Module Map

### blocks (25 modules)

| Module | Provides | Key types |
|--------|----------|-----------|
| `blocks-api` | SPI contracts | `RoutingStrategy`, `DecompositionStrategy`, `ActivationStrategy`, `AggregationStrategy`, `TerminationCondition` |
| `blocks-core` | Execution drivers | `OrchestratedDriver`, `ChoreographedDriver`, `AbstractPatternBuilder` |
| `blocks-bdi` | BDI primitives | `Belief`, `JointIntention`, `CoalitionEvaluator`, `JudgmentDispatcher` |
| `blocks-conversation` | Conversation protocol | `ConversationProjection`, `EpistemicCommonGround`, `ConvergenceState` |
| `blocks-social` | Social cognition (90+ types) | `MoodOrchestrator`, `DriveOrchestrator`, `NarrativeOrchestrator` |
| `blocks-summarisation` | Temporal event summarisation | `EventAccumulator`, `Compactor`, `Summariser` |
| `blocks-routing` | AI-powered routing | `LlmRoutingStrategy`, `CbrRoutingStrategy`, 5 signal providers |
| `blocks-prompt` | Prompt optimisation | `InstructionOptimiser`, `FewShotOptimiser`, `VariantStore` |
| `blocks-memory` | Memory hygiene | `MemoryHygieneOrchestrator`, confidence scorers, integrity checkers |
| `blocks-speech` | Speech pipeline | `SpeechProvider` SPI, sherpa-onnx FFM, `AvatarCognition` |
| `blocks-stigmergy` | Stigmergic coordination | `SignalSpace`, `RuleSpace`, `NeighborSpace`, `ConvergenceDetector` |

### qhorus (23 modules)

| Module | Provides | Key types |
|--------|----------|-----------|
| `qhorus-api` | Speech act model | 10 message types, `Commitment`, `Channel`, `Space` |
| `qhorus-core` | Dispatch pipeline | 12-step gate pipeline, `DispatchGateChain` |
| `qhorus-protocol` | Protocol enforcement | `ProtocolEvaluator`, advisory/blocking/quarantine modes |
| `qhorus-watchdog` | Coordination monitoring | 11 `WatchdogCondition` types |
| `qhorus-compliance` | EU AI Act evidence | Render → sign → store pipeline, 4 export formats |
| `qhorus-a2a` | A2A protocol bridge | Agent card, task messaging, SSE streaming, JWS signing |
| `qhorus-gateway` | Channel fan-out | 3 backend types, AT_LEAST_ONCE delivery, cursor tracking |

### Fleet Management (claudony + openclaw)

| Module | Provides | Key types |
|--------|----------|-----------|
| `claudony-core` | Terminal orchestration | `TmuxService`, `SessionRegistry`, fleet federation |
| `claudony-casehub` | CaseHub worker integration | `WorkerProvisioner`, `WorkerExecutionManager`, signal drain |
| `claudony-fleet` | LLM pool management | `AgentPoolDefinition`, `AgentSessionManager`, `ScalingScheduler` |
| `openclaw-core` | Agent execution bridge | `DirectCallBridge`, `ChannelContextWindowObserver` |
| `openclaw-casehub` | CaseHub SPI implementations | 8 SPI impls: `WorkerProvisioner`, `AgentProvider`, `OversightGateService` |
