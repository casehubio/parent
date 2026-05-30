---
id: PP-20260530-40a73c
title: "BlackboardRegistry.get() callers in @ConsumeEvent must use blocking = true"
type: rule
scope: repo
applies_to: "casehub-engine-blackboard — any @ConsumeEvent handler that calls BlackboardRegistry.get()"
severity: critical
refs:
  - casehubio/engine#274
violation_hint: "@ConsumeEvent without blocking = true on a method calling registry.get() — silently makes a blocking JPA call on the Vert.x IO thread on the first event after a JVM restart"
created: 2026-05-30
---

`BlackboardRegistry.get()` performs a blocking JDBC call via `PlanItemStore.findDelegated()` on the first miss after a JVM restart (lazy hydration — engine#274). Any `@ConsumeEvent` handler that calls `registry.get()` must declare `blocking = true` so the handler runs on a worker thread, not the Vert.x IO thread. Current handlers covered: `PlanItemCompletionHandler` (two methods), `WorkerRetryExhaustionHandler`, `PlanItemFaultHandler`. Every new blackboard handler that calls `registry.get()` — directly or via a helper — must include this annotation; omitting it causes no compile error and no test failure but triggers the blocked-thread detector in production on the first post-restart event.
