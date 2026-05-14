---
id: PP-20260513-ecabd7
title: "Use native M-of-N counting for simple threshold coordination; delegate complex orchestration to quarkus-flow"
type: principle
scope: platform
applies_to: "casehub-engine blackboard module; any future orchestration feature involving parallel sub-case or worker coordination"
severity: important
refs:
  - specs/2026-05-12-subcase-mofn-coordination-design.md
violation_hint: "Building a custom sequential/conditional state machine for sub-case coordination instead of using quarkus-flow; or using quarkus-flow for a simple M-of-N counter"
created: 2026-05-13
---

When coordinating parallel sub-cases or workers, choose the mechanism based on complexity: if the coordination is purely threshold counting (completedCount ≥ requiredCount), implement it natively with a persisted counter + policyTriggered flag behind a repository SPI — this is lighter, faster, and avoids a quarkus-flow dependency. If the coordination requires conditional sequencing, branching on intermediate results, or dependency between sub-cases (e.g. "if site A fails, spawn fallback site B"), express the logic as a quarkus-flow workflow. The implementation must always be hidden behind an SPI so the choice can be replaced without changing callers.
