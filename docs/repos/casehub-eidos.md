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
| `api/` | `casehub-eidos-api` | Pure Java, no CDI | SPIs and domain types — `AgentDescriptor`, `AgentRegistry`, `CapabilityHealth`, `VocabularyRegistry`, `SystemPromptRenderer`, `AgentStateStore`; top-level types: `AgentPromptContext`, `DegradationReason`, `GoalContext`, `Resource` |
| `runtime/` | `casehub-eidos` | Quarkus extension | CDI registry, health implementations, renderer; `@DefaultBean` for all SPIs; `runtime/renderer/` — `ClaudeMarkdownRenderer`; `runtime/health/` — `NoOpAgentStateStore` |
| `persistence-memory/` | `casehub-eidos-memory` | Optional module | `InMemoryAgentRegistry` + `InMemoryAgentStateStore` — `@Alternative @Priority(1)`; activate by adding as dep |
| `deployment/` | `casehub-eidos-deployment` | Quarkus build step | `EidosProcessor` + `EidosBuildTimeConfig` |
| `vocab/` | `casehub-eidos-vocab` | Optional module | Well-known vocabularies: SVO, Conscientiousness, CasehubSlot |
| `eval/` | `casehub-eidos-eval` | Test-only, not deployed | Offline quality evaluation harness: `EvalCase` sealed interface (`SyntheticEvalCase` + `ProfiledEvalCase`), `EvalDataset`, `PromptJudge`, `ProximityJudge`, `VocabularyExpressivenessJudge`, `TraitExpressionJudge`, `PairContrastJudge`; real-world agent profile library (8 YAML profiles grounded in O*NET and practitioner sources); three-stage personality preservation measurement system |
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

Open-string axes describing behavioural profile: `socialOrient`, `ruleFollowing`, `riskAppetite`, `autonomy`. All axes are optional. `delegation` is a separate boolean field (not an axis) — indicates whether the agent may delegate tasks.

**Validation (compact constructor):** all axes null-permissive (absent is valid), blank-rejecting, ≤200 chars, no banned characters (C0/C1, BiDi, zero-width). Throws `AgentValidationException` on violation.

### AgentRegistry / ReactiveAgentRegistry

SPIs for register, findById, and find(AgentQuery). `AgentQuery` carries: `slot`, `capabilityName`, and `tenancyId` (required — all queries are tenancy-scoped). `JpaAgentRegistry` is the `@ApplicationScoped` default; `JpaReactiveAgentRegistry` is build-gated via `casehub.eidos.reactive.enabled`. `InMemoryAgentRegistry` activates from `casehub-eidos-memory`.

### CapabilityHealth / ReactiveCapabilityHealth

SPI: `probe(AgentDescriptor, capabilityTag, ProbeContext)` → `CapabilityStatus`. Four statuses: `Ready`, `Degraded`, `Unavailable`, `EpistemicallyWeak`. `DegradationReason` is a top-level type in `casehub-eidos-api` — not nested inside `CapabilityHealth`.

`DefaultCapabilityHealth` checks `AgentStateStore` first (degraded state takes precedence), then declared capabilities + compares `ProbeContext.taskDomain` against `epistemicDomains`; fires `EpistemicallyWeak` when confidence is below `casehub.eidos.epistemic.weak-threshold` (default 0.3).

**ProbeContext:** `taskDomain` is the *subject domain* of the task — e.g. `"rust"` within a `"code-review"` capability. It is semantically distinct from `capabilityTag`. Conflating them prevents `EpistemicallyWeak` from triggering. `taskMetadata` carries additional task context.

**Engine integration:** `WorkOrchestrator` calls `probe()` at dispatch time for workers where `Worker.hasDescriptor()` is true. Workers without a descriptor skip the probe and are assumed capable. Engine provides `NoOpCapabilityHealth @DefaultBean` — deployments without eidos receive no filtering.

### VocabularyRegistry

SPI for term registration, resolution, and cross-vocabulary equivalence. `CdiVocabularyRegistry` (`@DefaultBean`) discovers `Instance<Vocabulary>` CDI beans at startup — any bean that implements `Vocabulary` is auto-discovered.

### SystemPromptRenderer (Phase 3 — complete)

SPI: `render(AgentDescriptor, AgentPromptContext)` → `RenderedPrompt`. `ClaudeMarkdownRenderer @DefaultBean` implements a two-step pipeline: structural YAML serialization → optional LangChain4j `ChatModel` semantic pass → markdown assembly. `AgentPromptContext` carries `Optional<GoalContext>`, `List<Resource>`, `situationalContext`, `RenderFormat` — re-renderable as agent context evolves. Works without LLM (structural-only). Hashes enable cache invalidation.

**`RenderFormat`** — 3 values: `MARKDOWN` (was `CLAUDE_MD`), `PROSE` (consolidates `OPENAI_SYSTEM` + `GEMINI` — structurally identical), `A2A_CARD`.

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

Both `ReactiveAgentRegistry` and `ReactiveCapabilityHealth` are gated on `casehub.eidos.reactive.enabled=true` (build-time config in `deployment/`). Default false — blocking-only consumers pay no Hibernate Reactive cost. Pattern mirrors the platform-wide reactive build gating protocol.

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
- Phase 4 (knowledge graph) — next.
- Engine integration (`Worker.agentDescriptor`, `NoOpCapabilityHealth`, `WorkOrchestrator` probe dispatch) — engine#341, design agreed.

---

## Design Documents

- [CLAUDE.md](https://raw.githubusercontent.com/casehubio/eidos/main/CLAUDE.md) — stack, module coordinates, key design decisions
- [examples/README.md](https://raw.githubusercontent.com/casehubio/eidos/main/examples/README.md) — capability coverage table across test scenarios
