---
id: PP-20260521-1ca0c8
title: "Trust-routing applications must implement the four-phase maturity model — never block on cold-start"
type: principle
scope: application
applies_to: "Any casehub harness that uses trust-based worker routing (RoutingPolicy, WorkerSelectionStrategy)"
severity: important
refs:
  - casehubio/devtown#9
  - casehubio/ledger#76
violation_hint: "New installation blocks or silently routes nothing on day-1 because no agent has trust history. Or: trust routing activates without a fallback, leaving some capability with no eligible workers."
created: 2026-05-21
---

Any CaseHub application using trust-based routing faces a cold-start problem: on day-1 of a fresh installation, no agent has trust history. Without an explicit maturity model, trust routing either blocks all work or is silently bypassed. The four-phase model below solves this — the system always routes; trust influence increases automatically as evidence accumulates.

## The Four Phases

| Phase | Name | Trust data | Routing mode |
|-------|------|-----------|--------------|
| 0 | Bootstrap | None | Availability — identical to GUPP/Gastown (random eligible agent) |
| 1 | Emerging | Sparse | Threshold routing for agents above `minimumObservations`; availability for new agents |
| 2 | Active | Sufficient | Full threshold + borderline uncertainty detection (→ HumanOversight) |
| 3 | Adaptive | Rich | Per-capability quality floors (requires `CAPABILITY_DIMENSION` scores — ledger#76) |

Transitions are automatic and driven by `RoutingPolicy.minimumObservations` per agent per capability. No configuration change or operator intervention is required at any transition point.

## Core Invariants

**Never block.** Phase 0 is always available — if no agent has crossed the `minimumObservations` threshold, fall back to availability routing. The system is never in a state where it has work and no routing path.

**Always degrade gracefully.** Every capability must declare a `fallbackType` in its `RoutingPolicy` — what to do when no agent qualifies (e.g. `AVAILABILITY`, `HUMAN_OVERSIGHT`, `ESCALATE`). "Do nothing silently" is not a valid fallback.

**Phase detection is per agent per capability**, not global. An application can be in Phase 2 for some capabilities and Phase 0 for others simultaneously.

## Phase Detection API (canonical — devtown)

```java
// In RoutingPolicy
boolean isBootstrap(int agentObservations) {
    return agentObservations < minimumObservations;
}

boolean isBorderline(double trustScore) {
    return Math.abs(trustScore - threshold) <= borderlineMargin;
}
```

- `isBootstrap()` → route by availability, not trust
- `isBorderline()` → route to `HumanOversight` (uncertain outcome; human verification required)
- Neither → route by trust score against `threshold`

## Why Phase 0 = Gastown Parity

Phase 0 availability routing is intentionally identical to Gastown's GUPP (Generic Uniform Probability Protocol). This means:
- Day-1 experience is no worse than a non-CaseHub system
- Trust routing is additive — it never degrades baseline capability
- The upgrade path from Gastown → CaseHub trust routing is seamless for operators

## Implementation Notes

The canonical implementation is in `casehub-devtown`: `RoutingPolicy.java` (phase detection), `DevtownCapabilityRegistry.java` (per-capability policies with `minimumObservations`, `threshold`, `borderlineMargin`, `fallbackType`).

Phase 3 (`CAPABILITY_DIMENSION` scores) requires `casehub-ledger#76` (composite trust score types). Implement Phases 0–2 first; Phase 3 is a forward-compatible extension — no structural changes needed to the `RoutingPolicy` API when Phase 3 is added.

## What NOT to do

- Do not seed artificial trust scores to skip Phase 0 — this defeats the purpose and creates false routing confidence.
- Do not implement trust routing without a `fallbackType` — some capability will eventually have no eligible agents (agent unavailable, new hire, new capability tag).
- Do not make `minimumObservations` a hardcoded constant — it is a tunable per-capability policy value; put it in `RoutingPolicy` or the `CapabilityRegistry`.
