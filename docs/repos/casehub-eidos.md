# casehub-eidos — Platform Deep Dive

**GitHub:** [casehubio/eidos](https://github.com/casehubio/eidos) (local: `~/claude/casehub/eidos`)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Structured agent identity for LLM agents on the CaseHub platform. Any Quarkus app that depends on `casehub-eidos` can register agents with four-layer descriptors (identity, slot, capabilities, disposition), discover agents by slot or capability, probe whether a declared capability is currently operable, and render system prompts from descriptors.

---

## Module Structure

| Module | artifactId | Type | Purpose |
|---|---|---|---|
| `api/` | `casehub-eidos-api` | Pure Java, no CDI | SPIs and domain types — `AgentDescriptor`, `AgentRegistry`, `CapabilityHealth`, `VocabularyRegistry`, `SystemPromptRenderer`, `AgentStateStore`; top-level types: `AgentPromptContext`, `DegradationReason`, `GoalContext`, `Resource`; vocabulary types: `VocabularyTerm` (interface — replaced record), `VocabularyRegistrar` (@FunctionalInterface CDI SPI), `VocabularyMetadata` (annotation on enum classes), `DispositionAxis` (enum: SOCIAL_ORIENTATION, RULE_FOLLOWING, RISK_APPETITE, AUTONOMY, CONFLICT_MODE — 5th axis added in eidos#38; `jsonKey()` → camelCase JSON key for LLM responses; `description()` → human-readable axis description for judge prompts) |
| `runtime/` | `casehub-eidos` | Quarkus extension | CDI registry, health implementations, renderer; `@DefaultBean` for all SPIs; `runtime/renderer/` — `EidosSystemPromptRenderer`; `runtime/health/` — `NoOpAgentStateStore` |
| `persistence-memory/` | `casehub-eidos-memory` | Optional module | `InMemoryAgentRegistry` + `InMemoryAgentStateStore` — `@Alternative @Priority(1)`; activate by adding as dep |
| `deployment/` | `casehub-eidos-deployment` | Quarkus build step | `EidosProcessor` + `EidosBuildTimeConfig` |
| `vocab/` | `casehub-eidos-vocab` | Optional module | Well-known vocabularies: `SvoTerm`, `ConscientiousnessTerm`, `CasehubSlotTerm`, `BelbinTerm` (9 Belbin team roles, slot vocab), `DiscTerm` (4 DISC types, disposition vocab, `axisExactMatch` → Conscientiousness + TK), `ThomasKilmannTerm` (5 conflict modes, disposition vocab for `CONFLICT_MODE` axis) enums with bidirectional `exactMatch()`; each accompanied by a `VocabularyRegistrar` bean; Jandex-indexed for CDI discovery |
| `graph/` | `casehub-eidos-graph` | Optional module (Jandex library) | Phase 4 knowledge graph — `AgentGraphStore` SPI (write), `AgentGraphQuery` SPI (read), `AgentGraphBackfill` SPI (ledger ingestion), `TaskSemanticEnricher` SPI (application-tier enrichment at query time). Activates by classpath presence. `AgentOutcome.observedAt: Instant` added (eidos#36) — business time of observation (not persistence time); compact constructor validates all four required fields including NaN guard on confidence. `ReactiveAgentGraphQuery`: not build-gated — `BlockingToReactiveGraphBridge @DefaultBean @ApplicationScoped` always active by classpath presence. |
| `eval/` | `casehub-eidos-eval` | Test-only, not deployed | Offline quality evaluation harness: `EvalCase` sealed interface (`SyntheticEvalCase` + `ProfiledEvalCase`), `EvalDataset`, `PromptJudge`, `ProximityJudge`, `VocabularyExpressivenessJudge`, `TraitExpressionJudge`, `PairContrastJudge`, `BehavioralJudge` (Phase 3 — eidos#46); `AgentProviderChatModel` bridge (`ChatModel → AgentProvider` SPI, `@DefaultBean`); 8 YAML agent profiles (eidos#23). `VariantPair` carries `DispositionAxis primaryAxis` + `List<String> scenarioQuestions`; `PairContrastResult.primaryAxis` is `DispositionAxis`. All compute-path types migrated from `String` to `DispositionAxis` (eidos#46). `RenderCacheEntry` record (`caseName`, `format`, `content`) with `toRenderedPrompt()` — used by `evaluateWithIndependentJudge()` diagnostic method for self-evaluation bias detection (eidos#51). |
| `examples/agent-scenarios/` | — | Test-only | `@QuarkusTest` integration examples covering team, cross-vocab, epistemic, tenancy, disposition |

---

## Key Abstractions

### AgentDescriptor

Four-layer record: identity (`id`, `name`, `agentId`), slot (open `String` — domain-defined, e.g. `"planner"` or `"reviewer"`), capabilities (`AgentCapability` list with `qualityHint` and `epistemicDomains`), disposition (`AgentDisposition` with open-String axes + boolean `delegation`).

`tenancyId` is always required. `domainVocabulary` sets the default vocabulary URI for all fields; per-field overrides: `slotVocabulary`, `dispositionVocabulary`.

**Slot is deliberately open** — platform never constrains. `casehub-eidos-vocab` provides starting-point vocabularies (SVO, Conscientiousness, CasehubSlot) but they are entirely optional.

**Validation (compact constructor):** validates all required fields (`agentId`, `name`, `slot`, `tenancyId`) and all optional string fields (`version`/`provider`/`modelFamily`/`modelVersion` ≤200, `weightsFingerprint` ≤255, vocabulary URIs ≤500, `jurisdiction`/`dataHandlingPolicy` ≤1000). All fields reject C0/C1 control chars, BiDi direction overrides, and zero-width chars. Validation is at construction time — no invalid descriptor can exist in any context. Throws `AgentValidationException` on violation.

### AgentCapability

Declares a named capability with an optional `qualityHint` (Double, 0–1) and `epistemicDomains` map (domain → confidence, e.g. `{"java": 0.95, "rust": 0.42}`). The `epistemicDomains` map qualifies *how well* the agent handles the declared capability in specific subject domains — it is not a list of separate capabilities.

**Validation (compact constructor):** `name` required ≤100; `costHint` optional ≤200; list items in `inputTypes`/`outputTypes`/`tags` ≤200 each; `epistemicDomains` keys ≤200. Same character-set rules as `AgentDescriptor`. Throws `AgentValidationException` on violation.

### AgentDisposition

Open-string axes describing behavioural profile: `socialOrient`, `ruleFollowing`, `riskAppetite`, `autonomy`. All axes are optional. `delegation` is a separate boolean field (not an axis) — indicates whether the agent may delegate tasks. `get(DispositionAxis)` — exhaustive switch method mapping `DispositionAxis` enum value to the corresponding field (eidos#40).

**Validation (compact constructor):** all axes null-permissive (absent is valid), blank-rejecting, ≤200 chars, no banned characters (C0/C1, BiDi, zero-width). Throws `AgentValidationException` on violation.

### AgentRegistry / ReactiveAgentRegistry

SPIs for register, findById, and find(AgentQuery). `AgentQuery` carries: `slot`, `capabilityName`, and `tenancyId` (required — all queries are tenancy-scoped). `JpaAgentRegistry` is the `@ApplicationScoped` default; `JpaReactiveAgentRegistry` is build-gated via `casehub.eidos.reactive.enabled`. `InMemoryAgentRegistry` activates from `casehub-eidos-memory`.

### CapabilityHealth / ReactiveCapabilityHealth

SPI: `probe(AgentDescriptor, capabilityTag, ProbeContext)` → `CapabilityStatus`. Four statuses: `Ready`, `Degraded`, `Unavailable`, `EpistemicallyWeak`. `DegradationReason` is a top-level type in `casehub-eidos-api` — not nested inside `CapabilityHealth`.

`DefaultCapabilityHealth` checks `AgentStateStore` first (degraded state takes precedence), then declared capabilities + compares `ProbeContext.taskDomain` against `epistemicDomains`; fires `EpistemicallyWeak` when confidence is below `casehub.eidos.epistemic.weak-threshold` (default 0.3).

**ProbeContext:** `taskDomain` is the *subject domain* of the task — e.g. `"rust"` within a `"code-review"` capability. It is semantically distinct from `capabilityTag`. Conflating them prevents `EpistemicallyWeak` from triggering. `taskMetadata` carries additional task context.

**Engine integration:** `WorkOrchestrator` calls `probe()` at dispatch time for workers where `Worker.hasDescriptor()` is true. Workers without a descriptor skip the probe and are assumed capable. Engine provides `NoOpCapabilityHealth @DefaultBean` — deployments without eidos receive no filtering.

### VocabularyRegistry

SPI for term registration, resolution, and cross-vocabulary equivalence. Vocabularies are Java enums implementing `VocabularyTerm` interface (not records). `CdiVocabularyRegistry` (`@DefaultBean`) discovers `Instance<VocabularyRegistrar>` CDI beans at startup. Axis-aware overload: `equivalentValues(fromUri, value, toUri, DispositionAxis)` — typed bypass registration (eidos#40).

**Vocabulary design reference:** `docs/personality-frameworks.md` maps 11 personality and team-role frameworks (Belbin, Big Five, DISC, Thomas-Kilmann, O*NET, SFIA, etc.) to `AgentDescriptor` fields. Prerequisite for eidos#26 (Belbin/DISC vocabulary module) and the authoritative source for vocabulary term design decisions.

**DISC types are disposition vocabulary** — not slot vocabulary. eidos#29 made this architectural call explicit: DISC axes map to `AgentDisposition` fields, never to `AgentCapability.slot`.

**Open design decisions:** minor robustness gaps (eidos#42).

**Resolved:** `conflictMode` as 5th disposition axis — eidos#38 CLOSED, implemented as `DispositionAxis.CONFLICT_MODE` + `AgentDisposition.conflictMode` field. Open Map vs. fixed fields — eidos#39 CLOSED, fixed fields kept with `DispositionAxis` enum as extensibility point (ADR-0004). Per-axis vocabulary override: `AgentDescriptor.axisVocabularies(Map<DispositionAxis, String>)` + `vocabUriForAxis(DispositionAxis)` (3-step resolution: axis override → dispositionVocabulary → domainVocabulary) — eidos#40 **closed, implemented**. Belbin/DISC vocabulary — eidos#26 CLOSED, shipped in `casehub-eidos-vocab` alongside `ThomasKilmannTerm` for `CONFLICT_MODE` axis.

### SystemPromptRenderer (Phase 3 — complete)

SPI: `render(AgentDescriptor, AgentPromptContext)` → `RenderedPrompt`. `EidosSystemPromptRenderer @DefaultBean` — two-step pipeline: structural assembly → optional LangChain4j `ChatModel` semantic pass. Three output formats: `MARKDOWN`, `PROSE`, `A2A_CARD`. Falls back to structural output when no `ChatModel` is available. `AgentPromptContext` carries `Optional<GoalContext>`, `List<Resource>`, `situationalContext`, `RenderFormat` — re-renderable as agent context evolves. Works without LLM (structural-only). Hashes enable cache invalidation. Capability rendering is format-discriminated (PP-20260611-228599, eidos#49): PROSE and MARKDOWN surface capability names and `inputTypes`/`outputTypes` only; `A2A_CARD` carries full routing signals — `qualityHint`, `latencyHintP50Ms`, `costHint`, `epistemicDomains`, `inputTypes`, `outputTypes` — for casehub-engine dispatch.

**`RenderFormat`** — 3 values: `MARKDOWN` (was `CLAUDE_MD`), `PROSE` (consolidates `OPENAI_SYSTEM` + `GEMINI` — structurally identical), `A2A_CARD`. `A2A_CARD` exposes `slot` (with vocabularyUri/vocabularyName), per-axis `disposition` objects with vocabulary context, and a `frameworks` array — deduplicated index of actively-instantiated vocabulary URIs enabling machine-to-machine capability negotiation. Separate `A2ASemanticEnrichmentStep` handles per-capability descriptions in `A2A_CARD` format (eidos#45). `A2A_CARD` capability objects include full routing signals: `qualityHint` (Double, 0–1), `latencyHintP50Ms` (Long), `costHint` (String), `epistemicDomains` (Map<String,Double>), `inputTypes`/`outputTypes` (String lists). PROSE and MARKDOWN suppress all numeric routing signals (PP-20260611-228599). `vocabUriForSlot()` on `AgentDescriptor` — `slotVocabulary → domainVocabulary` two-step fallback, alongside `vocabUriForAxis()`.

### AgentStateStore (Phase 3 — complete)

SPI: `record(agentId, DegradationReason, expiresAt)`, `query(agentId)` → `Optional<AgentState>`. `NoOpAgentStateStore @DefaultBean` (no tracking). `InMemoryAgentStateStore @Alternative @Priority(1)` in `casehub-eidos-memory` — TTL-based ConcurrentHashMap, entries expire on `query()`. `DefaultCapabilityHealth` checks store first at probe time — degraded state takes precedence over Ready/EpistemicallyWeak. `DegradationReason` is a top-level type in `casehub-eidos-api`, not nested inside `CapabilityHealth`. JPA persistence deferred (eidos#7).

---

## Depends On

| Repo | How |
|---|---|
| `casehub-ledger` | Runtime dep — `casehub-eidos` (runtime) depends on it; `casehub-eidos-api` depends on nothing |
| `dev.langchain4j:langchain4j-core:1.14.1` | `casehub-eidos` (runtime) — `ChatModel` interface used by `ClaudeMarkdownRenderer` for optional LLM semantic pass |

## Depended On By

| Repo | Module | Nature |
|---|---|---|
| `casehub-engine` | `engine-api` | Optional compile dep — `AgentDescriptor` on `Worker`; `CapabilityHealth.probe()` in `WorkOrchestrator` |

---

## What This Repo Explicitly Does NOT Do

- Trust scoring — that is `casehub-ledger`
- Agent-to-agent messaging — that is `casehub-qhorus`
- Work item or case orchestration — that is `casehub-engine`
- Constrain slot or disposition vocabulary — consumers define their own; `casehub-eidos-vocab` is optional
- Put `AgentDescriptor` or vocabulary types in `casehub-platform-api` — descriptor types are Eidos domain types; repos that need them depend on `casehub-eidos-api` directly

---

## Reactive Build Gating

Both `ReactiveAgentRegistry` and `ReactiveCapabilityHealth` are gated on `casehub.eidos.reactive.enabled=true` (build-time config in `deployment/`). Default false — blocking-only consumers pay no Hibernate Reactive cost.

`ReactiveAgentGraphQuery` is **not** build-gated. `BlockingToReactiveGraphBridge @DefaultBean @ApplicationScoped` wraps `JpaAgentGraphQuery` via `Uni.createFrom().item(Supplier).runSubscriptionOn(Infrastructure.getDefaultWorkerPool())` and is always active by classpath presence, regardless of `casehub.eidos.reactive.enabled`.

Pattern mirrors the platform-wide reactive build gating protocol.

---

## Tenancy

`AgentDescriptor.tenancyId` is always required. All registry queries are tenancy-scoped — `AgentQuery.tenancyId` is mandatory. The registry never returns descriptors across tenancy boundaries.

---

## Schema Management

JPA/Flyway — version range V1–V999 in `classpath:db/eidos/migration`. No Flyway migrations created yet (no deployed instances). All schema changes go directly into base migration files — treat every change as clean-slate design.

---

## Current State

- Phases 1 and 2 complete and merged to main (96 tests across 7 modules, all green).
- Phase 3 — `SystemPromptRenderer` + `ClaudeMarkdownRenderer` + `AgentStateStore` + `InMemoryAgentStateStore` — complete (eidos#5). Structural rendering + optional LangChain4j semantic pass.
- eidos#23 — Real-world agent profile library — complete. 8 YAML profiles (Belbin/DISC grounded), `AgentProfileLoader` with Stage 0 pair isolation validation, `ProximityJudge` (semantic proximity scoring), three-stage personality preservation measurement (`VocabularyExpressivenessJudge` / `TraitExpressionJudge` / `PairContrastJudge`).
- Phase 4 (knowledge graph) — complete. `casehub-eidos-graph` module: `AgentGraphStore` / `AgentGraphQuery` / `AgentGraphBackfill` SPIs + `TaskSemanticEnricher` SPI (application-tier extension point, eidos pulls at query time). Activates by classpath presence (Jandex library pattern). Refs eidos#32.
- Engine integration (`Worker.agentDescriptor`, `NoOpCapabilityHealth`, `WorkOrchestrator` probe dispatch) — engine#341, design agreed.
- eidos#45 — A2A card framework references — complete. `A2A_CARD` format now includes `slot`, per-axis `disposition`, and `frameworks` array; `A2ASemanticEnrichmentStep`; `AgentDescriptor.vocabUriForSlot()` added.
- eidos#46 — Eval baseline and behavioral validation — in progress. Phase 1 (structural baseline judges: `PromptJudge`, `ProximityJudge`, `VocabularyExpressivenessJudge`, `TraitExpressionJudge`) and Phase 3 (pair-contrast behavioral judge via `AgentProviderChatModel` bridge to Claude CLI: `PairContrastJudge`, `BehavioralJudge`) implemented. `DispositionAxis.jsonKey()` and `description()` added to api. All compute-path migrations from `String` to `DispositionAxis` complete. Eval execution phases tracked in eidos#48 (Phase 1) and eidos#51 (Phase 2).
- eidos#48 — Eval Phase 1 execution — complete. `evaluateAllScenarios()` run against Claude; `SCORE_FLOORS` calibrated from observed per-format output; baseline committed as `eval-baseline-2026-06-10.json`. Multi-backend eval support added: Ollama, Jlama NEON (Apple Silicon), GPULlama3-Metal (TornadoVM). All backend run commands documented in CLAUDE.md.
- eidos#49 — A2A_CARD capability routing signals — complete. `A2A_CARD` format now carries full routing signals: `qualityHint`, `latencyHintP50Ms`, `costHint`, `epistemicDomains`, `inputTypes`/`outputTypes`. Capability rendering is format-discriminated (PP-20260611-228599): PROSE/MARKDOWN suppress all numeric routing signals; `buildDescriptorPayload()` is format-discriminated accordingly.
- eidos#50 — TEMPLATE_HASH scope fix — complete. TEMPLATE_HASH now covers `PROMPT_TEMPLATE`, `A2A_PROMPT_TEMPLATE`, and all `RESPONSE_FORMAT`/`A2A_RESPONSE_FORMAT` schema description strings. Schema descriptions extracted into named `List<String>` constants used both in `ResponseFormat` builders and in the hash fingerprint input (PP-20260614-templatehash).
- eidos#51 — Eval Phase 2 + independent judge — in progress. Phase 2a: `evaluateRealWorldScenarios()` completed with Qwen 3 8B; `PROXIMITY_FLOOR=3.0` confirmed (min=3, mean=3.5 across 16 cases). `AgentProviderChatModel` await bounded to 7 min (eidos#52 filed for root cause). Phase 2b: `evaluateWithIndependentJudge()` added — loads `target/renders-cache.json` and re-judges with any configured `ChatModel` to detect self-evaluation bias. `RenderCacheEntry` record (`caseName`, `format`, `content`) with `toRenderedPrompt()`.

---

## Design Documents

- [CLAUDE.md](https://raw.githubusercontent.com/casehubio/eidos/main/CLAUDE.md) — stack, module coordinates, key design decisions
- [examples/README.md](https://raw.githubusercontent.com/casehubio/eidos/main/examples/README.md) — capability coverage table across test scenarios
