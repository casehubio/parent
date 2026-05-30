---
id: PP-20260530-096e7a
title: "Local SPI placeholders must have a contract identical to the planned engine-api SPI — import-swap migration only"
type: rule
scope: platform
applies_to: "casehub integration repos (casehub-openclaw, casehub-claudony, etc.) when defining a local interface that will later be promoted to casehub-engine-api"
severity: important
refs:
  - docs/specs/2026-05-30-epic6-bidirectional-wiring-design.md
violation_hint: "A local placeholder interface diverges from the engine-api SPI contract (different method signature, different type names, or different override pattern) — causing callers to require code changes beyond a simple import update at migration time"
created: 2026-05-30
---

When a casehub integration repo needs a capability that belongs in `casehub-engine-api` but the SPI hasn't shipped yet, define a local interface in the repo's library module (`casehub/`) with a contract that is **identical** to what the engine SPI will define: same method signature, same type names, same `@Alternative @Priority(1)` override mechanism. The default `@ApplicationScoped` bean implements the Phase 1 no-op. Javadoc on the interface must explicitly state: (1) this is a local placeholder for `casehubio/engine#N`; (2) when that SPI ships, migration is a pure import swap with no contract change. The filed cross-repo issue must reference the local interface as the intended contract. Precedents: `ActionRiskClassifier` (casehub-openclaw, engine#402), `SpeechActClassifier` (casehub-openclaw, openclaw#10).
