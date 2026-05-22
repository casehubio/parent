# QuarkMind

**GitHub:** [mdproctor/quarkmind](https://github.com/mdproctor/quarkmind)
**Tier:** Application — Living Lab
**Status:** Active — SC2 layer through Phase 6 (replay-accurate emulation); harness layer documentation in progress
**Note:** In the `mdproctor/` namespace, not `casehubio/` — a personal project using the CaseHub pattern. Does not participate in the casehubio CI pipeline.

## What It Is

A StarCraft II game AI application built on the CaseHub agentic harness. Coordinates plugin agents (strategy, economics, tactics, scouting) via CaseHub's case engine and blackboard, with Drools for rule-based reasoning and Quarkus Flow for durable task execution. Explicitly a living lab — a testbed for CaseHub, Drools, and Quarkus Flow integration patterns in a real-time domain.

The SC2 game loop is domain-specific. The CaseHub harness underneath — CaseFile blackboard, plugin coordination, adaptive agent selection — is the same foundation as AML, clinical, and devtown. QuarkMind demonstrates that the harness holds outside regulated enterprise domains, across diverse timing characteristics (game AI operates at millisecond tick granularity vs days for case management).

Its primary value in the application family is as a **proof of generality**: the same harness pattern that coordinates AML investigation specialists and clinical trial monitors also coordinates real-time game AI agents — without changing the foundation.

## What It Owns

- SC2 domain model: game state, units, buildings, actions, intents
- Plugin seam interfaces: `StrategyTask`, `EconomicsTask`, `TacticsTask`, `ScoutingTask` — each extends CaseHub's `TaskDefinition`
- Active plugin implementations: `DroolsStrategyTask`, `FlowEconomicsTask`, `DroolsTacticsTask`, `BasicScoutingTask`
- `QuarkMindCaseFile` — all CaseFile key constants; never use raw string keys
- SC2 engine seam: `IntentQueue`, `GameStarted`/`GameStopped` events
- Mock, emulated, replay, and real SC2 profiles
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

Phase 6 complete: replay-accurate `EmulatedGame` with sub-tick train-timing calibrated from replay ground truth (`SC2TrainTimeCalibrationTest` — range-bounded modal calibration from 29 AI Arena replays). `ReplayValidationHarness` shows `firstUnitDivergenceTick=150`; remaining gap is vespene income model (#148). Harness LAYER-LOG documentation pending.

## What It Does NOT Own

Everything below belongs in the foundation:
- Trust scoring computation (casehub-ledger — pending)
- Commitment lifecycle (casehub-qhorus — pending)
- Human task inbox (casehub-work — not applicable at game AI tick granularity)
