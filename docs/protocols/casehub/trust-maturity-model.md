---
id: trust-maturity-model
title: Trust Routing Cold-Start and Maturity Model
scope: casehub
applies-to: any application using TrustWeightedAgentStrategy from casehub-engine-ledger
---

## Rule

Every application that activates trust-based routing MUST implement the four-phase maturity
model. Never block on missing trust data. Phase 0 is Gastown parity — availability routing.

## The Four Phases

| Phase | Condition | Routing |
|---|---|---|
| 0/1 BOOTSTRAP | `decisionCount < minimumObservations` OR no CAPABILITY score | Availability: `1/(1+runningJobs)` |
| 2 QUALIFIED | score ≥ threshold AND NOT borderline AND passes quality floors | Blended: `trust×blendFactor + workload×(1-blendFactor)` |
| 2a BORDERLINE | `Math.abs(score - threshold) <= borderlineMargin` | Score 0.0; if ALL non-bootstrap candidates are borderline → `EscalateToOversight` |
| 3 EXCLUDED | score < threshold (Phase 2b) OR quality floor failed (Phase 3) | Score 0.0; not escalated |

## Bootstrap > Borderline

A BOOTSTRAP candidate (positive availability score) always outscores a BORDERLINE candidate
(score 0.0). New agents with no decision history are preferred over established agents with
borderline trust. Operators who want to prevent unknown agents from executing sensitive
operations must configure the Qhorus trust gate (`casehub.qhorus.commitment.min-obligor-trust`).

## Quality Floors

`qualityFloors` maps dimension name → minimum required score. If a candidate's score for a
dimension is present in the ledger AND below the floor, it is EXCLUDED_PHASE3. If the
dimension data is absent, no penalty is applied — absence does not count as failure.

## Dimension Convention

All trust dimensions MUST be stored as higher = better (0.0–1.0). Dimensions with inverted
natural semantics (e.g. false-positive-rate) MUST be stored as their complement (precision =
1 - FPR). Storing a dimension as higher = worse makes quality floor logic semantically
inverted and silently wrong.

## Consumer Obligations

1. Declare a `RoutingPolicy` for every trust-sensitive capability in the domain registry.
2. Every capability with a routing policy MUST declare a `fallbackType` (the human oversight
   type to escalate to when the all-borderline pool condition is met).
3. Never hard-code trust thresholds — use YAML config via `casehub-platform-config` +
   `PreferenceKey` per field. See `DevtownTrustRoutingPolicyProvider` as the reference impl.

## Reference

- `TrustWeightedAgentStrategy` in `casehub-engine-ledger`
- `TrustCandidateClassifier` — classification and outcome decision logic
- `TrustRoutingPolicy` — the policy record (`threshold`, `minimumObservations`,
  `borderlineMargin`, `blendFactor`, `qualityFloors`)
- devtown#57 — first consumer; reference implementation of `TrustRoutingPolicyProvider`
