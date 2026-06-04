# Platform Doc Sync Batch — #83, #85, #86, #87, #88

**Date:** 2026-05-29
**Branch:** issue-83-doc-sync-batch
**Issues:** casehubio/parent#83, #85, #86, #87, #88

---

## Scope

Five documentation sync issues covering recent implementation work. No code changes. Each section is self-contained — implementation is sequential file edits followed by a single commit per file.

---

## #83 — quarkmind.md (mdproctor/quarkmind#150)

### What changed in the repo

`IEM10CommandExtractor` — new class extracting `List<TimedIntent>` from SC2EGSet JSON `gameEvents` using 2016 IEM10 abilLink constants and j-index-recycle building-tag format matching `IEM10JsonSimulatedGame`.

`ReplayValidationHarness` generalised — new overload `run(SimulatedGame groundTruth, List<TimedIntent> intents, int tickLimit)` accepts any `SimulatedGame` subclass as ground truth; binary `.SC2Replay` overload delegates to it. `assertInitialStateMatch` carries ±1 unit tolerance for SC2EGSet loop-0 quirk.

New tests: `IEM10MultiGameValidationTest` (all 30 IEM10 games via `IEM10CommandExtractor`), `IEM10AbilityDiscoveryTest` (documents abilLink constant derivation).

### Changes to docs/repos/quarkmind.md

**What It Owns:**
- Update `ReplayValidationHarness` bullet: add "`run(SimulatedGame, List<TimedIntent>, int)` overload — accepts any `SimulatedGame` as ground truth; binary `.SC2Replay` overload delegates. `assertInitialStateMatch` allows ±1 unit tolerance (SC2EGSet loop-0 quirk)."
- Add `IEM10CommandExtractor` — extracts `List<TimedIntent>` from SC2EGSet JSON `gameEvents`; uses 2016 patch-specific abilLink constants; building-tag format matches `IEM10JsonSimulatedGame` j-index-recycle convention.
- Add `IEM10MultiGameValidationTest` — runs all 30 IEM10 games through `ReplayValidationHarness`; reports aggregate divergence stats.
- Add `IEM10AbilityDiscoveryTest` — documents how 2016 abilLink constants were derived.

**Current State:**
- Note quarkmind#150 completed: IEM10 JSON validation now covers 30 games via `IEM10CommandExtractor`.
- Sub-tick train timing bullet: mention cross-validation via `IEM10MultiGameValidationTest` (#150).

---

## #85 — casehub-platform.md (platform#27)

### What changed in the repo

`CaseMemoryStore` SPI + value types (`MemoryInput`, `Memory`, `MemoryQuery`, `EraseRequest`, `MemoryDomain`) + `MemoryPermissions` static utility — all in `platform-api`.

`NoOpCaseMemoryStore @DefaultBean` in `platform/` — returns empty results; zero overhead when no backend installed.

`ReactiveCaseMemoryStore` interface + `BlockingToReactiveBridge @DefaultBean` in `platform/` — wraps blocking adapters transparently; native async adapters override as `@Alternative @Priority(N)`.

Adapter implementations (Memori, Mem0, Graphiti) live in the separate `casehub-memory` repo (`casehubio/memory`).

### Changes to docs/repos/casehub-platform.md

**New section — CaseMemoryStore** (after Identity):

Document the SPI contract: permission-aware recall enforced at the SPI layer (not delegated to backends), domain isolation (`MemoryDomain` scopes facts — health/finance/household do not cross), fact emission via CDI observer pattern (mechanism shared with ledger capture).

Document the two `@DefaultBean` patterns explicitly (this is an important design distinction):
- **Configurable mock** (`PreferenceProvider`, `CurrentPrincipal`): returns SmallRye Config values or fixed test values — the system makes business decisions based on them. Wrong values produce wrong behaviour. The mock must be explicit.
- **Silent no-op** (`CaseMemoryStore`): returns empty results — the system functions correctly without memory, just without recall. Zero overhead. This is right when an absent backend is a valid production configuration.

Document `BlockingToReactiveBridge` — the standard pattern for wrapping blocking adapters as reactive; native async adapters override with `@Alternative @Priority(N)`. This is the same pattern used elsewhere in the platform.

Note `casehub-memory` repo: adapter implementations activate by classpath presence (no config needed).

**Module Roadmap:** add `memory/` row: status shipped (platform#27); note adapters in casehub-memory repo.

---

## #86 — casehub-life.md (life#3)

### What changed in the repo

Layer 2 (casehub-work) implemented and merged 2026-05-27 (casehubio/life#3):
- Domain model corrected: `HouseholdTask`, `LifeGoal`, `LifeEvent` removed — duplicated foundation primitives (`WorkItem`, case definitions, and ledger entries respectively)
- `LifeTaskContext` added as domain supplement entity — holds life-specific fields alongside the foundation `WorkItem`
- `POST /life-tasks` — creates `WorkItem` + `LifeTaskContext` atomically via `WorkItemTemplate` lookup
- `LifeSlaBreachPolicy` — implements `casehub-work` `SlaBreachPolicy` SPI; stateless two-tier escalation (first: escalate to `household-admin`; second: fail)
- Engine deps temporarily removed from pom.xml — SNAPSHOT build broken (engine#379, engine#380); will be re-added in Layer 5 branch
- Flyway path: `classpath:db/life/migration/` (PP-20260525-607b33)

### Changes to docs/repos/casehub-life.md

**Status header:** `Layer 1 complete` → `Layer 2 complete (2026-05-27)`

**Tutorial Layers table:**
- Layer 1: status `**complete** (casehubio/life#2)` (unchanged, confirm ref)
- Layer 2: status `pending` → `**complete** (casehubio/life#3)`

**What It Owns:**
- Remove: `HouseholdTask`, `LifeGoal`, `LifeEvent` (removed — duplicated foundation primitives)
- Add: `LifeTaskContext` — domain supplement entity; `WorkItem` is the foundation record, `LifeTaskContext` holds life-specific fields
- Add: `POST /life-tasks` — creates `WorkItem` + `LifeTaskContext` atomically via `WorkItemTemplate` lookup
- Add: `LifeSlaBreachPolicy` — `SlaBreachPolicy` SPI impl; stateless two-tier escalation

**New subsection or inline note — Current State:**
Engine deps temporarily removed (pom.xml); SNAPSHOT build broken (engine#379, engine#380). Will be restored in Layer 5 branch.

**Dependencies block:**
Flyway path: `classpath:db/life/migration/` (PP-20260525-607b33 compliant).

---

## #87 + #88 — PLATFORM.md capability table

### What changed in the repos

engine#337: `WorkOrchestrator` now resolves routing via `@Any Instance<AgentRoutingStrategy>` (CDI priority resolution), not `WorkerSelectionStrategy` from `casehub-work-core`. Engine runtime has no routing dep on casehub-work-core.

engine#336: `TrustWeightedAgentStrategy` shipped in `casehub-engine-ledger` (`@Alternative @Priority(1)`).

engine#376: `casehub-engine-ai` optional module — `AgentEmbeddingProvider` SPI + `SemanticAgentRoutingStrategy` (`@Alternative @Priority(2)` — overrides trust-weighted strategy when on classpath).

### Changes to docs/PLATFORM.md

**Capability Ownership table:**

Replace stale entry:
> Worker routing / selection strategies | casehub-work-core | WorkBroker, WorkerSelectionStrategy SPI — also used by casehub-engine

With two entries:

| Capability | Owner | Notes |
|---|---|---|
| Human task routing / selection | `casehub-work-core` | `WorkBroker`, `WorkerSelectionStrategy` SPI; `SemanticWorkerSelectionStrategy` in `casehub-work-ai` (`@Alternative @Priority(1)`) |
| Agent routing / selection | `casehub-engine-api` | `AgentRoutingStrategy` SPI; CDI priority resolution in `WorkOrchestrator`. Implementations: `LeastLoadedAgentStrategy` (engine runtime, default), `TrustWeightedAgentStrategy` (casehub-engine-ledger, `@Priority(1)`), `SemanticAgentRoutingStrategy` (casehub-engine-ai, `@Priority(2)`, optional) |
| Agent embedding vector provider | `casehub-engine-ai` | `AgentEmbeddingProvider` SPI — required by `SemanticAgentRoutingStrategy`; activates semantic routing when on classpath |

**Build / Dependency Order:** add `casehub-engine-ai (optional — SemanticAgentRoutingStrategy, AgentEmbeddingProvider)` under `casehub-engine`.

**casehub-engine.md module table:** add row for `casehub-engine-ai`.

---

## Implementation Order

1. quarkmind.md — standalone, no cross-file deps
2. casehub-platform.md — standalone
3. casehub-life.md — standalone
4. PLATFORM.md + casehub-engine.md — batched (both touch engine routing; one commit)

Each file committed separately referencing its issue(s).
