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
- Active plugin implementations: `DroolsStrategyTask`, `FlowEconomicsTask`, `DroolsTacticsTask`, `DroolsScoutingTask`
- `QuarkMindCaseFile` — all CaseFile key constants; never use raw string keys
- SC2 engine seam: `IntentQueue`, `GameStarted`/`GameStopped` events, sealed `Intent` interface (switch exhaustiveness at compile time)
- Mock, emulated, replay, and real SC2 profiles
- `EmulatedGame` — full physics simulation: probe-driven mining (per-base, saturation model), parallel training queues, sub-tick train timing (`TimedIntent`, `completesAt`), building cost deduction, vespene harvesting, combat (damage, armour, Hardened Shield), blink mechanics, auto-engage, enemy AI (`EnemyBehavior`, `TechTree`, `ReactiveStrategy`)
- `ReplayValidationHarness` — replay ground truth vs `EmulatedGame` per-tick economic divergence; `run(SimulatedGame groundTruth, List<TimedIntent> intents, int tickLimit)` overload accepts any `SimulatedGame` subclass as ground truth (binary `.SC2Replay` overload delegates to it); `assertInitialStateMatch` allows ±1 unit tolerance (SC2EGSet loop-0 quirk)
- `IEM10CommandExtractor` — extracts `List<TimedIntent>` from SC2EGSet JSON `gameEvents` using 2016 IEM10-era abilLink constants; building-tag format matches `IEM10JsonSimulatedGame` j-index-recycle convention
- `IEM10MultiGameValidationTest` — runs all 30 IEM10 games through `ReplayValidationHarness` via `IEM10CommandExtractor`; reports aggregate per-tick divergence stats across PvT, PvZ, PvP matchups
- `IEM10AbilityDiscoveryTest` — verifies 2016 IEM10-era abilLink constants by asserting expected command mappings against known `gameEvents` samples; serves as living documentation of constant derivation
- `SC2TrainTimeCalibrationTest` — range-bounded modal calibration from replay datasets; cross-validated against IEM10 JSON parser via `IEM10MultiGameValidationTest` (#150)
- `TerrainGrid` (HIGH/LOW/RAMP/WALL height model), `AStarPathfinder`, `MovementStrategy`
- Three.js 3D visualiser: 65+ unit/building sprites across all 3 races, fog of war, terrain shading, click-to-inspect panel, replay scrub control, Electron wrapper
- Electron visualiser for replay and emulated mode

## Agentic Harness Structure

| Layer | CaseHub primitive | QuarkMind expression |
|-------|-------------------|---------------------|
| Agent coordination | `casehub-engine` CaseFile blackboard | `AgentOrchestrator` dispatches plugins via case engine per tick |
| Plugin tasks | `TaskDefinition` | `StrategyTask`, `EconomicsTask`, `TacticsTask`, `ScoutingTask` |
| Adaptive selection | Binding conditions | Plugin selection based on game state in CaseFile |
| Durable execution | Quarkus Flow | `FlowEconomicsTask` — build order execution with retry |
| Rule-based reasoning | Drools | `DroolsStrategyTask`, `DroolsTacticsTask`, `DroolsScoutingTask` |

## Tutorial Layers

The layered structure applies to the agentic harness — not to the SC2 emulation layer, which is domain-specific. An LLM or developer studying the harness pattern can follow the layers independent of SC2 knowledge.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive game loop — direct plugin calls, no CaseHub | Baseline: no adaptive coordination, no blackboard | pending documentation |
| 2 | casehub-engine blackboard | No shared state between plugins; each plugin is an island | in use (active) |
| 3 | casehub-qhorus | No typed inter-plugin communication | pending |
| 4 | casehub-ledger | No audit trail for agent decisions | pending |
| 5 | Adaptive plugin selection | Fixed plugin dispatch; no binding conditions | pending |
| 6 | Trust routing | No plugin performance tracking; no routing based on outcome history | pending |
| 7 | Comparison vs naive game AI | — | pending |

## Dependencies

```
quarkmind
  → casehub-engine   (CaseFile blackboard, TaskDefinition, adaptive plugin dispatch)
  → casehub-persistence-memory (in-memory store for fast game-loop ticks)
  → Drools           (rule-based strategy, tactics, scouting)
  → Quarkus Flow     (durable economics build order execution)
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

**Harness layer (Layer 2 active):** `AgentOrchestrator` dispatches plugins via `casehub-engine` CaseFile per tick. Layer-by-layer tutorial documentation in progress — Layer 1 (conceptual baseline) and Layer 2 (casehub-engine blackboard) are documented in `LAYER-LOG.md`. Layers 3–7 tracked in quarkmind#155–#159.

**IEM10 JSON validation (#150):** `IEM10CommandExtractor` enables `ReplayValidationHarness` runs across all 30 IEM10 games, providing statistical coverage of training patterns (queued, non-queued, cross-type) across PvT, PvZ, PvP matchups. Cross-validates calibration results from the scelight binary parser against the SC2EGSet JSON parser.

## What It Does NOT Own

Everything below belongs in the foundation:
- Trust scoring computation (casehub-ledger — pending)
- Commitment lifecycle (casehub-qhorus — pending)
- Human task inbox (casehub-work — not applicable at game AI tick granularity)
