---
id: PP-20260605-0b4818
title: "AgentRoutingStrategy implementations must pre-screen guards before emitOn(workerPool)"
type: rule
scope: platform
applies_to: "Any AgentRoutingStrategy implementation (in casehub-engine-ledger, casehub-engine-ai, or consumer repos) that dispatches to a worker pool via emitOn()"
severity: important
refs:
  - trust-maturity-model.md
violation_hint: "A bootstrap guard, eligible-list filter, or any short-circuit check that avoids expensive computation is placed inside the emitOn() lambda rather than before it — paying the worker-pool dispatch cost even when the guard fires."
garden_ref: "GE-20260605-58f57c"
created: 2026-06-05
---

When an `AgentRoutingStrategy` implementation uses `emitOn(Infrastructure.getDefaultWorkerPool())` for expensive computation (embeddings, LLM inference, heavy scoring), any guard that might short-circuit the expensive path — including the `bootstrapEscalationRequired` pre-screen and any eligible-list computation — must be placed BEFORE the `emitOn()` call, not inside the lambda. The eligible list (e.g. BOOTSTRAP-stripped candidates) must be computed on the calling thread and captured by the lambda; the lambda then works on the pre-filtered list without re-computing. Violation wastes worker-pool threads and embedding compute budget on results that are immediately discarded. Reference implementation: `SemanticAgentRoutingStrategy.select()` in `casehub-engine-ai`.
