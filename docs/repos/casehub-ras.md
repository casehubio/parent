# casehub-ras

**GitHub:** [casehubio/casehub-ras](https://github.com/casehubio/casehub-ras)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Reticular Activating System -- situational awareness and reactive case creation for the CaseHub ecosystem. Observes CloudEvent CDI async events produced by platform stream modules (Kafka, AMQP, webhook, Camel), routes them to pluggable detection strategies (Ganglia), correlates composite events across time windows, and triggers case creation via casehub-engine when a situation threshold is crossed.

The biological metaphor is deliberate: a ganglion is a neural cluster that detects a specific signal pattern. Multiple ganglia compose via `ChainMode` (AND, OR, threshold, sequence, count) to detect complex situations from simple parts.

---

## Module Structure

| Module | artifactId | Contents |
|--------|-----------|----------|
| `api/` | `casehub-ras-api` | Core SPIs and domain types: `Ganglion`, `SituationStore`, `CaseTrigger`, `RasTriggerPolicy`; records: `SituationDefinition`, `SituationContext`, `DetectionResult`, `CaseTriggerConfig`; sealed `ChainMode` (5 variants); enums: `DetectionSignal`, `TriggerDecision`; base class: `JavaSwitchGanglion`. Depends on CloudEvents SDK + Mutiny. No CDI. |
| `runtime/` | `casehub-ras` | CDI runtime: `RasEngine` (CloudEvent observer), `SituationEvaluator` (two-phase detection + OCC retry), `SituationDefinitionRegistry`, `DefaultRasTriggerPolicy`, `DefaultCaseTrigger`, `YamlSituationDefinitionProvider`, `NaiveBayesGanglion`, scheduled expiry + buffer flush jobs. |
| `ras-drools/` | `casehub-ras-drools` | `DroolsGanglion` -- Drools CEP stream-mode ganglion with long-lived/ephemeral sessions, pseudo/realtime clock, hot rule reload, `DroolsObjectExtractor` SPI, `ResultCollectionStrategy` enum. |
| `ras-llm/` | `casehub-ras-llm` | POM-only placeholder. Intended: LLM-based ganglion via `casehub-platform-agent-api` for narrative and ambiguous signal detection. No source yet. |
| `persistence-memory/` | `casehub-ras-memory` | `InMemorySituationStore` (`@Alternative @Priority(100)`) -- ConcurrentHashMap-backed. Zero-config. |
| `persistence-jpa/` | `casehub-ras-jpa` | `JpaSituationStore` -- JPA-backed with dual-layer OCC (application-level `storeVersion` + JPA `@Version`). `SituationEntity` (table `ras_situation`, JSONB detections). Flyway V1-V2. |
| `testing/` | `casehub-ras-testing` | `MockGanglion`, `MockCaseTrigger`, `FixedDetectionResult`. Test scope only. |

---

## Key Abstractions

### Ganglion

The central detection SPI. Each ganglion handles a specific set of CloudEvent types and produces a `DetectionResult` for each event in the context of an accumulating situation.

Methods: `ganglionId()`, `handledEventTypes()`, `detect(CloudEvent, SituationContext) -> Uni<DetectionResult>`, `compact(SituationContext)` (optional -- compress accumulated detections), `close(situationId, correlationKey, tenancyId)` (lifecycle cleanup).

**Design invariant:** `DetectionResult` must be portable -- it may be applied to a different `SituationContext` than the one passed to `detect()` (e.g. after an OCC retry). Implementations must not base decisions on accumulated `context.detections()`.

Three built-in implementations:
- `JavaSwitchGanglion` -- abstract base for pure-Java detection. Wraps synchronous `evaluate()` in Uni. Provides factory methods: `detected(confidence)`, `weak(confidence)`, `noise()`, `anti(confidence)`.
- `NaiveBayesGanglion` -- incremental Naive Bayes classifier. Maintains per-situation-instance log-posterior state. Extracts features from CloudEvents, updates posteriors, maps probability to `DetectionSignal` via configurable thresholds.
- `DroolsGanglion` -- Drools CEP stream-mode engine. Rules write `DetectionResult` to a channel; `ResultCollectionStrategy` resolves multiple results.

### DetectionResult / DetectionSignal

`DetectionResult(ganglionId, confidence, signal, evidence)` -- confidence 0.0-1.0, evidence is `Map<String, Object>`.

`DetectionSignal` enum (ordinal ordering): `NOISE` (no signal), `ANTI` (counter-evidence), `WEAK` (possible but uncertain), `DETECTED` (confident). `isAtLeast(threshold)` enables signal-strength filtering.

### SituationDefinition

Record: `(situationId, eventTypes, correlationWindow, eventBufferDelay, chainMode, triggerConfig)`. Defines what CloudEvent types to watch, how long to correlate signals (`correlationWindow`), whether to buffer out-of-order events (`eventBufferDelay`), how ganglia combine (`chainMode`), and which case to create (`triggerConfig`).

### ChainMode

Sealed interface with 5 composition strategies. Each variant has `referencedGanglia()` returning the ganglion IDs involved.

| Variant | Semantics |
|---------|-----------|
| `And(requiredGanglia)` | All ganglia must produce at least one WEAK+ detection |
| `Or(ganglia)` | Any ganglion with WEAK+ detection suffices |
| `Threshold(ganglia, minConfidence)` | Sum of confidences (ANTI subtracts) must reach threshold |
| `Sequence(orderedGanglia)` | Ganglia must fire in temporal order |
| `Count(ganglionId, requiredCount)` | Single ganglion must fire N times |

### SituationContext

Immutable record accumulating detections for a correlation key: `(situationId, correlationKey, tenancyId, firstSignal, lastSignal, detections, storeVersion)`. `storeVersion` (`OptionalLong`) enables optimistic concurrency. `withDetection()` returns a new instance.

### RasEngine (Entry Point)

`@ApplicationScoped` CDI bean. Observes `CloudEvent` CDI async events via `@ObservesAsync`. For each event: extracts `tenancyid` extension (skips events without it), looks up matching `SituationRegistration`s by event type, extracts correlation key, delegates to `SituationEvaluator`.

### SituationEvaluator

Two-phase processing per event:
1. **Detect** (Phase 1, never retried) -- calls `ganglion.detect()` for all relevant ganglia.
2. **Apply + persist** (Phase 2, retried on `SituationConflictException` up to `ras.evaluator.max-conflict-retries=3`) -- applies detections to context, evaluates trigger policy, executes decision.

Decisions: `CREATE_CASE` fires `CaseTrigger` then removes the situation; `CONTINUE_ACCUMULATING` optionally compacts then saves; `DISCARD` removes.

Handles event reorder buffers (TreeMap-based, drains when watermark advances past `eventBufferDelay`) and correlation window expiry.

### SituationStore

Persistence SPI: `find()`, `save()`, `remove()`, `removeExpired(cutoff)`. All return `Uni<>`. Two implementations: `InMemorySituationStore` (ConcurrentHashMap) and `JpaSituationStore` (JPA with dual-layer OCC).

### CaseTrigger

SPI: `fire(CaseTriggerConfig, SituationContext) -> Uni<UUID>`. `DefaultCaseTrigger` resolves the case definition from `CaseHubRuntime` by namespace/name/version and starts it with input data containing all detections.

### DroolsGanglion

Drools CEP (Complex Event Processing) integration. Builds a `KieBase` with `EventProcessingOption.STREAM` from DRL rules (classpath or programmatic). Two session modes:
- `LONG_LIVED` -- stateful session keyed by (situation, correlation, tenancy), persisted in `DroolsSessionStore`. Sessions are lazily invalidated on rule reload (generation counter).
- `EPHEMERAL` -- new session per event, disposed after detection.

Two clock modes: `PSEUDO` (event-time driven, advances to event time, rejects out-of-order) and `REALTIME`.

`DroolsObjectExtractor` SPI allows domain-specific facts to be inserted alongside the CloudEvent. `ResultCollectionStrategy` resolves multiple rule-fired results: `HIGHEST_CONFIDENCE`, `FIRST_MATCH`, `LAST_WINS`, `ACCUMULATE`.

---

## CloudEvent Consumption Pattern

RAS is a pure CloudEvent consumer. Platform stream modules (Kafka, AMQP, webhook, Camel) produce CloudEvents and fire them as CDI async events. RAS observes via `@ObservesAsync CloudEvent`.

**CloudEvent fields used:**
- `type` -- routes to matching `SituationDefinition`s and `Ganglion`s
- `time` -- temporal ordering (reorder buffer, Drools pseudo clock)
- `subject` -- default correlation key (via `DefaultCorrelationKeyExtractor`, falls back to `"_singleton"`)
- extension `tenancyid` -- required; events without it are skipped

**RAS does not produce CloudEvents.** Its output is case creation via `CaseTrigger`.

---

## Depends On

| Repo | Module | How |
|------|--------|-----|
| `casehub-platform` | `platform-api` | CloudEvent types, CDI event infrastructure |
| `casehub-platform` | `platform` (runtime) | Full platform runtime (runtime module) |
| `casehub-engine` | `engine-api` | `CaseHub` SPI for case creation (via `DefaultCaseTrigger`) |
| Drools 10.1.0 | `drools-model-codegen` | ras-drools module only |

## Depended On By

| Repo | What it uses |
|------|-------------|
| Application-tier repos that need situational awareness | `casehub-ras-api` for Ganglion SPI; runtime + persistence module for CDI activation |

---

## Does NOT Do

- Stream infrastructure (Kafka, AMQP, webhook, Camel routes) -- platform stream modules handle ingestion; RAS observes CDI events
- Case lifecycle management -- only triggers creation; case state machines, milestones, tasks are casehub-engine
- REST/gRPC endpoints -- entirely event-driven via CDI async events
- ML model training -- `NaiveBayesGanglion` uses pre-configured priors and likelihood tables; no online learning
- LLM integration (yet) -- `ras-llm` is a POM placeholder with no source
- Event sourcing or audit trail -- situations are mutable state, deleted when case is created or discarded
- Distributed coordination -- uses in-process synchronized locks; clustered deployments rely on OCC
- Rule authoring UI -- DRL provided as classpath resources or programmatic strings

---

## Current State

- Core framework complete: API, runtime, persistence-memory, persistence-jpa, ras-drools, testing all on main.
- `NaiveBayesGanglion` built into runtime with full incremental Bayesian classification.
- `DroolsGanglion` supports CEP stream mode with long-lived sessions and hot rule reload.
- JPA persistence with dual-layer OCC (application + JPA `@Version`).
- YAML-based situation definition via `YamlSituationDefinitionProvider`.
- `ras-llm` module scaffolded (POM only, no source).
- API module publishes a test-jar with `AbstractGanglionContractTest` for implementation verification.
