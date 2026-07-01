# Case-Based Reasoning (CBR) in CaseHub

> **Status:** Foundational capability gap — building blocks exist, coordination layer is missing.
> This document defines the target architecture and identifies what each repo must provide.
> Read this before implementing any retrieval, adaptation, or strategy-selection feature in any harness application.

---

## Why CBR

CaseHub is named for *cases* — but until recently, it did very little true Case-Based Reasoning. The trust routing in casehub-ledger is the first fragment: it records outcomes (Retain) and replays them as weights (Reuse). But it skips the two steps that give CBR its power:

- **Retrieve**: given a new situation, find the *k* most similar past cases — not by exact key match, but by feature-vector similarity
- **Revise**: adapt the retrieved solution to the current context — a retrieved plan is a starting point, not a final answer

Without Retrieve and Revise, the system is a lookup table with credence decay. With them, it learns from analogous experience and adapts plans rather than selecting from a fixed menu.

Every harness application is a natural CBR system:
- AML: an investigation that looks like past confirmed fraud cases should inherit their escalation structure
- Clinical: a trial adverse event similar to a past serious event should trigger the same safety protocol, adapted for the current arm
- QuarkMind: a Zerg roach-rush game should inherit strategy from similar past Zerg all-in games, not from a static DRL rule

---

## The Four CBR Steps and CaseHub Ownership

### 1. Retain — store the outcome as a retrievable case

**Owner:** `casehub-ledger` + `casehub-platform` (`CaseMemoryStore`)

Two complementary stores:

| Store | What it holds | Use for CBR |
|-------|--------------|-------------|
| `casehub-ledger` | Tamper-evident outcome attestations, trust scores (Bayesian Beta), decision records | Trust credence — "this strategy won 70% of similar games" |
| `CaseMemoryStore` (platform) | Queryable, permission-aware case memories; adapters: `memory-jpa`, `memory-mem0`, `memory-graphiti` | Full case representation — problem features + solution + outcome, retrievable by semantic similarity |

Both are needed. The ledger provides the compliance record and trust signal; the memory store provides the rich case representation for retrieval.

**Current state:** `casehub-ledger` is used by QuarkMind (L6 trust routing). `CaseMemoryStore` is not yet used by any harness application for CBR case storage. This is the first gap to close.

**What to do:** When a case closes with an outcome, write both a ledger attestation (already done where ledger is wired) AND a memory entry capturing the full problem description (key features from the CaseFile at decision time) + the solution (which plan/strategy was chosen) + the outcome (win/loss, accepted/rejected, resolved/escalated).

---

### 2. Retrieve — find similar past cases

**Owner:** `casehub-neocortex` — `CaseRetriever` / `ReactiveCaseRetriever` SPIs

`CaseRetriever` performs similarity-based retrieval against the `CaseMemoryStore`. It is already declared in `casehub-neocortex` (see `casehub-neocortex-rag-api`) and marked for future engine integration (PLATFORM.md cross-dependency table, entry: "fact space prompt compiler context injection, future, #154").

Similarity functions are domain-specific and pluggable:
- QuarkMind: feature vector = `[opponent_race, detected_build_order, enemy_posture, game_phase, army_size_ratio]`
- AML: feature vector = `[transaction_pattern_cluster, entity_risk_tier, prior_outcomes_on_similar_profiles]`
- Clinical: feature vector = `[adverse_event_type, trial_arm, patient_risk_profile, protocol_phase]`

**Current state:** `CaseRetriever` SPI exists but is not yet used by any harness for CBR retrieval. This is the second gap to close.

**What to do:** At decision time (new case arrives, plan must be chosen), invoke `CaseRetriever` with the current CaseFile's feature vector to retrieve the top-k most similar past cases. The retrieved cases inform — but do not replace — the routing decision.

---

### 3. Reuse — select a solution from retrieved cases

**Owner:** Two distinct sub-problems, two distinct owners.

#### 3a. Routing between competing implementations

**Current gap.** When multiple `TaskDefinition` implementations register for the same capability (e.g. `DroolsStrategyTask`, `EarlyPressureStrategyTask`, `EconomicExpansionStrategyTask` all implementing `StrategyTask`), the engine currently runs all of them (every `canActivate()` returning true gets a PlanItem).

Application-tier workaround (QuarkMind L6): `StrategyTrustRouter` + `StrategySelector` select the winner and gate the others via `canActivate()`. This belongs in the engine, not the application.

**Target:** `casehub-engine` should provide an `ImplementationRoutingStrategy` SPI — symmetric to `AgentRoutingStrategy` but operating over competing `TaskDefinition` implementations rather than competing agent workers. The trust-maturity four-phase model (BOOTSTRAP / BORDERLINE / QUALIFIED / EXCLUDED) applies identically.

See `casehub/garden: docs/protocols/casehub/trust-maturity-model.md` for the four-phase model. The same model governs both agent selection and implementation selection.

#### 3b. Routing a task to a trusted worker

**Already implemented.** `AgentRoutingStrategy` SPI in `casehub-engine-api`; `TrustWeightedAgentStrategy` in `casehub-engine-ledger` at `@Priority(1)`. Activates by classpath presence. See PLATFORM.md Capability Ownership — "Agent routing / selection."

---

### 4. Revise — adapt the retrieved solution to the current context

**Owner:** `casehub-engine` (target) — `PlanningStrategy` equivalent in the full engine stack.

**Current gap.** Today, strategy selection is binary: one implementation is chosen, it runs its full plan. There is no mechanism to take a retrieved past solution and *adapt* it — blend parameters from the top-k retrievals, weight sub-tasks differently based on context, or parameterise a plan template.

**Target:** Adaptive plan templates — plan instances that are parameterised at runtime rather than fixed at compile time. The adaptation function is domain-specific (pluggable SPI) and operates on the retrieved cases to produce a concrete plan.

For QuarkMind, adaptation might mean: given that the top-3 similar past games used `EarlyPressure` (2 wins, 1 loss) and `Economic` (3 wins), blend their opening build orders weighted by outcome. Rather than choosing one strategy, parameterise a hybrid. This cannot be expressed in static DRL files.

This is the most ambitious gap — it requires adaptive plan templates, which do not yet exist anywhere in the platform.

---

## Component Map

```
Problem description (CaseFile features)
        │
        ▼
┌──────────────────────────────────────┐
│  casehub-neocortex / CaseRetriever │  ← RETRIEVE: similarity search
│  (CaseMemoryStore backend)           │
└──────────────────────────────────────┘
        │  top-k similar past cases
        ▼
┌──────────────────────────────────────┐
│  casehub-engine                      │  ← REUSE: select / weight solutions
│  ImplementationRoutingStrategy (gap) │
│  TrustWeightedAgentStrategy ✅        │
└──────────────────────────────────────┘
        │  chosen plan / implementation
        ▼
┌──────────────────────────────────────┐
│  casehub-engine (gap)                │  ← REVISE: adapt plan to context
│  Adaptive plan templates             │
└──────────────────────────────────────┘
        │  execution + outcome
        ▼
┌──────────────────────────────────────┐
│  casehub-ledger + CaseMemoryStore    │  ← RETAIN: record for future retrieval
│  Trust scoring, outcome attestation  │
└──────────────────────────────────────┘
```

---

## Degenerate CBR — What Exists Today

Most harness applications are currently running degenerate CBR with only Reuse and Retain:

| Step | Current implementation | Gap |
|------|----------------------|-----|
| Retain | `casehub-ledger` trust scores by exact `(actorId, contextKey)` | No full case representation stored for similarity retrieval |
| Retrieve | Exact key match only (`opponentContext` string in QuarkMind) | No feature-vector similarity; analogous cases with different keys are invisible |
| Reuse | `TrustWeightedAgentStrategy` (workers) ✅; application-layer workarounds for implementations | `ImplementationRoutingStrategy` missing from engine |
| Revise | Not implemented | Adaptive plan templates not defined |

The trust four-phase model (BOOTSTRAP → BORDERLINE → QUALIFIED → EXCLUDED) is a credence-update mechanism, not true retrieval. It improves with repetition of the *same* problem type; it cannot generalise across *similar* problem types. Full CBR closes that gap.

---

## Reference Implementation — QuarkMind

QuarkMind is the first and most demanding CBR test case: millisecond game-loop granularity, real win/loss feedback from the SC2 API, and multiple competing strategy implementations with measurable outcomes. It demonstrates that CBR is viable at game-speed latency, not just at human-timescale case management.

Current state in QuarkMind:

| CBR step | QuarkMind status |
|----------|-----------------|
| Retain | ✅ L6 — ledger outcome recording, trust scoring via `TrustGateService` |
| Retrieve | ❌ Exact match only (`opponentContext` = PvT/PvZ/PvP) |
| Reuse (implementation) | ❌ Application-layer workaround: `StrategyTrustRouter` + `StrategySelector` |
| Reuse (worker) | N/A — QuarkMind has no human/AI worker routing |
| Revise | ❌ Not implemented |

Target state (tracked via QuarkMind GitHub issues):

| CBR step | QuarkMind target |
|----------|----------------|
| Retain | Add `CaseMemoryStore` writes at game end capturing full game context (opponent features, strategy chosen, outcome) |
| Retrieve | Implement `CaseRetriever` integration — retrieve top-k similar past games by feature vector |
| Reuse (implementation) | Migrate `StrategyTrustRouter` logic to `casehub-engine ImplementationRoutingStrategy` |
| Revise | Parameterise strategy selection from retrieved case blend (long-term) |

---

## Migration Note — casehub-poc Retirement

`casehub-poc` (GroupId: `io.casehub`, artifactId: `casehub-core:1.0.0-SNAPSHOT`) is **retiring — no new features**. See PLATFORM.md repository map.

QuarkMind currently depends on casehub-poc. CBR capabilities belong in `casehub-engine` (casehubio/engine), not in casehub-poc. Before CBR retrieval or implementation routing can be properly wired, QuarkMind must migrate its `CaseEngine` dependency from casehub-poc to `casehub-engine`.

This migration is tracked separately. Do not implement new CBR capabilities in casehub-poc.

---

## What Each Repo Should Do

| Repo | CBR responsibility | Status |
|------|--------------------|--------|
| `casehub-ledger` | Retain: outcome attestation, trust scoring | ✅ Done — extend to full case representation when CaseMemoryStore is wired |
| `casehub-platform` | Retain: `CaseMemoryStore` adapters (jpa, mem0, graphiti) | ✅ Adapters exist — no harness has wired for CBR yet |
| `casehub-neocortex` | Retrieve: `CaseRetriever` SPI + RAG implementation | ⏳ SPI declared, not yet wired to CBR retrieval |
| `casehub-engine` | Reuse: `ImplementationRoutingStrategy` SPI — route among competing `TaskDefinition` implementations | ❌ Gap — to be filed as engine issue |
| `casehub-engine` | Revise: adaptive plan templates | ❌ Gap — long-term |
| `casehub-aml` | CBR over AML investigation patterns — retrieve similar past investigations at case open | ❌ Not started |
| `casehub-clinical` | CBR over adverse event history — retrieve similar past AEs at safety review | ❌ Not started |
| `casehub-devtown` | CBR over PR review patterns — retrieve similar past reviews for context | ❌ Not started |
| `quarkmind` | CBR reference implementation at game-loop granularity | 🔲 L6 Retain ✅; Retrieve/Reuse/Revise pending |
