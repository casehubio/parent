# QuarkMind

**GitHub:** [casehubio/quarkmind](https://github.com/casehubio/quarkmind)
**Tier:** Application — Living Lab
**Status:** Active — SC2 layer through replay-accurate multi-base mining model (828 unit/integration tests + 288 Playwright E2E); harness layer documentation in progress
**Note:** Transferred from `mdproctor/quarkmind` to `casehubio/quarkmind`. A personal project using the CaseHub pattern — does not participate in the casehubio CI pipeline.

## What It Is

A StarCraft II game AI application built on the CaseHub agentic harness. Coordinates plugin agents (strategy, economics, tactics, scouting) via CaseHub's case engine and blackboard, with Drools for rule-based reasoning and Quarkus Flow for durable task execution. Explicitly a living lab — a testbed for CaseHub, Drools, and Quarkus Flow integration patterns in a real-time domain.

The SC2 game loop is domain-specific. The CaseHub harness underneath — CaseFile blackboard, plugin coordination, adaptive agent selection — is the same foundation as AML, clinical, and devtown. QuarkMind demonstrates that the harness holds outside regulated enterprise domains, across diverse timing characteristics (game AI operates at millisecond tick granularity vs days for case management).

Its primary value in the application family is as a **proof of generality**: the same harness pattern that coordinates AML investigation specialists and clinical trial monitors also coordinates real-time game AI agents — without changing the foundation.

## What It Owns

- SC2 domain model: game state, units, buildings, actions, intents; `SC2Data` — all game constants (costs, timings, ranges, armour, attributes)
- Plugin seam interfaces: `StrategyTask`, `EconomicsTask`, `TacticsTask`, `ScoutingTask` — each extends CaseHub's `TaskDefinition`
- Active plugin implementations: `DroolsStrategyTask`, `FlowEconomicsTask`, `DroolsTacticsTask`, `DroolsScoutingTask`; competing strategy implementations (L6): `EarlyPressureStrategyTask`, `EconomicExpansionStrategyTask`
- `QuarkMindCaseFile` — all CaseFile key constants; never use raw string keys
- SC2 engine seam: `IntentQueue`, `GameStarted`/`GameStopped` events, sealed `Intent` interface (switch exhaustiveness at compile time)
- Mock, emulated, replay, and real SC2 profiles
- `EmulatedGame` — full physics simulation: probe-driven mining (per-base, saturation model), parallel training queues, sub-tick train timing (`TimedIntent`, `completesAt`), building cost deduction, vespene harvesting, combat (damage, armour, Hardened Shield), blink mechanics, auto-engage, enemy AI (`EnemyBehavior`, `TechTree`, `ReactiveStrategy`)
- **EmulatedSC2Server (quarkmind#171):** SC2 protocol wrapper over `EmulatedGame` — bidirectional translators (`GameStateToProtobuf`, `ProtobufToIntent`), walkability bitmap encoding, full `ResponseObservation` round-trip. Enables ocraft-based clients to drive `EmulatedGame` via SC2 protocol.
- `ReplayValidationHarness` — replay ground truth vs `EmulatedGame` per-tick economic divergence; `run(SimulatedGame groundTruth, List<TimedIntent> intents, int tickLimit)` overload accepts any `SimulatedGame` subclass as ground truth (binary `.SC2Replay` overload delegates to it); `assertInitialStateMatch` allows ±1 unit tolerance (SC2EGSet loop-0 quirk)
- `IEM10CommandExtractor` — extracts `List<TimedIntent>` from SC2EGSet JSON `gameEvents` using 2016 IEM10-era abilLink constants; building-tag format matches `IEM10JsonSimulatedGame` j-index-recycle convention
- `IEM10MultiGameValidationTest` — runs all 30 IEM10 games through `ReplayValidationHarness` via `IEM10CommandExtractor`; reports aggregate per-tick divergence stats across PvT, PvZ, PvP matchups
- `IEM10AbilityDiscoveryTest` — verifies 2016 IEM10-era abilLink constants by asserting expected command mappings against known `gameEvents` samples; serves as living documentation of constant derivation
- `SC2TrainTimeCalibrationTest` — range-bounded modal calibration from replay datasets; cross-validated against IEM10 JSON parser via `IEM10MultiGameValidationTest` (#150)
- `TerrainGrid` (HIGH/LOW/RAMP/WALL height model), `AStarPathfinder`, `MovementStrategy`
- Three.js 3D visualiser: 65+ unit/building sprites across all 3 races, fog of war, terrain shading, click-to-inspect panel, replay scrub control, Electron wrapper
- Electron visualiser for replay and emulated mode
- **Hierarchical event summarisation (quarkmind#182):** Generic framework (`io.casehub.blocks.summarisation`) with four-level temporal abstraction: raw ticks → intel → moments → phases → arcs. `EventLevel`, `LevelEvent`, `WindowPolicy`, `EventAccumulator`, `EventStreamBus`, `Summariser`, `SummarisationRunner`. SC2 bindings: `MomentDetectionTask` (Drools CEP L1→L2), `GamePhaseSummariser`, `GameArcSummariser`, `MomentBroker` (Qhorus channel), `SummarisationLifecycle`. `DroolsStrategyTask` consumes L2 moments and L3 phases. Pre-positioned for `casehub-blocks` migration.
- **LLM advisory team (quarkmind#180):** 6 `AgentDescriptor` configurations (crisis/strategic/economic roles × 2) with eidos disposition traits. `DispositionAwareRoutingStrategy` composes trust with game-context disposition scoring. `AdvisoryWorkerFactory` creates Workers backed by langchain4j `ChatModel`. Two-signal dispatch: sync tick settles, async advisory fire-and-forget. Multi-dimensional trust: latency (normalised per-role), deferred recommendation quality (200-frame delta), game-outcome (flat per-advisor). `quarkmind-advisory` Qhorus channel for audit. HIL coaching `ChannelBackend`. `QuarkMindTrustRoutingPolicyProvider` with per-capability quality floors.
- **casehub-engine Phase 2 migration (quarkmind#207):** `QuarkMindCaseHub extends CaseHub` with `signalAndAwaitSync` per tick. `TickOrchestratorWorker` chains plugins via `WorkerFunction.Sync`. `MutableMapCaseContext` provides writable context with delta tracking. `casehub-poc` dependency removed (−5134 lines).
- **Layer 6 — Trust-weighted strategy routing (quarkmind#158):** `StrategyTrustRouter` — four-phase Bayesian Beta maturity model (BOOTSTRAP/QUALIFIED/BORDERLINE/EXCLUDED) routing among competing `StrategyTask` implementations using `casehub-ledger` trust scores keyed by opponent context. `StrategySelector` — per-game volatile selection state. `GameOutcomeRecorder` — writes trust attestations to ledger on `@Observes GameStopped` (sync). `EnemyPostureClassifiedEvent` — CDI event for mid-game strategy checkpoint. `LedgerLifecycleAdapter` removed (was clearing ledger between games, breaking trust accumulation). Config required: `casehub.ledger.trust-score.{enabled,incremental.enabled,materialization.enabled}=true`. Note: `casehub-engine-ledger` NOT used — QuarkMind uses `casehub-ledger` core directly, not via engine-ledger. Known: records SOUND for all games until win/loss detection ships (quarkmind#189).

## Agentic Harness Structure

| Layer | CaseHub primitive | QuarkMind expression |
|-------|-------------------|---------------------|
| Agent coordination | `casehub-engine` CaseFile blackboard | `AgentOrchestrator` dispatches plugins via case engine per tick |
| Plugin tasks | `TaskDefinition` | `StrategyTask`, `EconomicsTask`, `TacticsTask`, `ScoutingTask` |
| Adaptive selection | Binding conditions | Plugin selection based on game state in CaseFile |
| Durable execution | Quarkus Flow | `FlowEconomicsTask` — build order execution with retry |
| Rule-based reasoning | Drools | `DroolsStrategyTask`, `DroolsTacticsTask`, `DroolsScoutingTask` |
| Typed advisory channel | `casehub-qhorus` | `ScoutingIntelBroker` publishes to `quarkmind-scouting-intel`; LLM advisors subscribe as `MessageObserver`. Dual-stack: synchronous in-memory broker (for plugins) + async advisory channel (for LLM advisors — quarkmind#180/#181) |
| Trust-weighted strategy routing | `casehub-ledger` | `StrategyTrustRouter` — four-phase Bayesian Beta maturity (BOOTSTRAP/QUALIFIED/BORDERLINE/EXCLUDED); `GameOutcomeRecorder` writes trust attestations on `GameStopped`; opponent-context keyed trust scores; `StrategySelector` volatile per-game state (quarkmind#158) |

## Layer Taxonomy

The layered structure applies to the agentic harness — not to the SC2 emulation layer, which is domain-specific. An LLM or developer studying the harness pattern can follow the layers independent of SC2 knowledge.

Architecture record: `ARC42STORIES.MD` in the quarkmind repo (LAYER-LOG.md retired in quarkmind#166).

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive game loop — direct plugin calls, no CaseHub | Baseline: no adaptive coordination, no blackboard | complete (conceptual) |
| 2 | casehub-engine blackboard | No shared state between plugins; each plugin is an island | complete |
| 3 | casehub-qhorus | No typed inter-plugin communication | complete (dual-stack) |
| 4 | casehub-ledger | No audit trail for agent decisions | complete |
| 5 | Adaptive plugin selection | Fixed plugin dispatch; no binding conditions | complete |
| 6 | Trust routing | No plugin performance tracking; no routing based on outcome history | complete (quarkmind#158) — `StrategyTrustRouter` four-phase Bayesian Beta; `GameOutcomeRecorder`; known: SOUND recorded for all outcomes until win/loss detection (quarkmind#189) |
| 7 | Comparison vs naive game AI — vs L1 naive loop and ocraft/SC2 API; no tutorial README | — | ✅ complete (quarkmind#159, 2026-06-16) |

## Dependencies

```
quarkmind
  → casehub-engine   (CaseFile blackboard, TaskDefinition, adaptive plugin dispatch)
  → casehub-persistence-memory (in-memory store for fast game-loop ticks)
  → Drools           (rule-based strategy, tactics, scouting)
  → Quarkus Flow     (durable economics build order execution)
  → casehub-qhorus   (advisory channel for LLM observers; persistence-memory for @QuarkusTest isolation)
  → casehub-ledger   (L6: trust-weighted strategy routing — StrategyTrustRouter, GameOutcomeRecorder; casehub-ledger core only, not casehub-engine-ledger)
```

## Current State

828 unit/integration tests passing (288 Playwright E2E excluded from default surefire run). The SC2 emulation layer is substantially complete for the Protoss vs Protoss / Terran matchup:

**Emulation accuracy (post-Phase 6 calibration):**
- Sub-tick train timing: `TimedIntent` with `completesAt` derived from `SC2Data.trainTimeInLoops` (integer-loop rounding calibrated from replays — #149); `firstUnitDivergenceTick ≥ 80`, `maxUnitDelta ≤ 2`; cross-validated across all 30 IEM10 games (#150)
- Per-base probe mining: saturation model (#141) + per-base `miningProbesPerBase` auto-computed in `tick()` with one-shot harness override (#152, #143); sqrt→squared distance fix (#153)
- Vespene income: synced from ground truth for gas-unit training in `ReplayValidationHarness` (#148)
- Building cost + mineral timing: `injectReplayBuildingWithCost` for replay harness accuracy (#146)
- Parallel training queues: per-building queues with supply reservation and `drainBuildingQueues` per tick (#128)
- Auto-engage: all units fire at enemies in range without an explicit `AttackIntent` (#129)
- Enemy AI: `EnemyBehavior` with `TechTree` prerequisite gating and `ReactiveStrategy` — counter-picks dominant player unit every 50 frames

**Visualiser (emulated + replay profiles):**
- Three.js 3D terrain with height shading, fog of war, mineral patches, geysers, creep
- 65+ canvas sprites across all 3 races; directional facing, teamColour decals
- Click-to-inspect unit/building panel; HP/shield bars; replay scrub control
- `ReplayVisualizerIT` pixel tests; Playwright end-to-end suite (288 tests)
- **Phase 5 visualiser additions (quarkmind#131):**
  - Mineral HUD: comma-formatted mineral count + colour tiers (< 50 critical red, 50–149 amber, 150+ normal)
  - Probe/unit spread: `applyUnitSpread()` distributes co-located sprites in a ring around the centroid (prevents sprite stacking)
  - Canvas sprites: `makeResourceMaterial()` factory — mineral patches (blue with cross) and geysers (teal with X) replacing solid-colour placeholders
  - Time-based tests: `window.__test.gameTimeSeconds()` + `tickForSeconds()` helper enabling `mineralIncomeScalesWithGameTime` and similar time-anchored assertions

**Harness layer:** `AgentOrchestrator` dispatches plugins via `casehub-engine` CaseFile per tick. Layers 1–7 complete. Architecture record is `ARC42STORIES.MD` in the quarkmind repo (LAYER-LOG.md retired in quarkmind#166).

**IEM10 JSON validation (#150):** `IEM10CommandExtractor` enables `ReplayValidationHarness` runs across all 30 IEM10 games, providing statistical coverage of training patterns (queued, non-queued, cross-type) across PvT, PvZ, PvP matchups. Cross-validates calibration results from the scelight binary parser against the SC2EGSet JSON parser.

## What It Does NOT Own

Everything below belongs in the foundation:
- Trust scoring computation (casehub-ledger — L6 complete for strategy routing; L4 full audit trail pending)
- Commitment lifecycle (casehub-qhorus — pending)
- Human task inbox (casehub-work — not applicable at game AI tick granularity)
