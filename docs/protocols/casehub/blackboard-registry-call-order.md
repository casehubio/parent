---
id: PP-20260519-006f35
title: "Call BlackboardRegistry.getOrCreate() before markConfigured() or indexWorkerForCompletion() for the same caseId"
type: rule
scope: repo
applies_to: "casehub-blackboard — any caller of BlackboardRegistry"
severity: important
refs:
  - blackboard/src/main/java/io/casehub/blackboard/registry/BlackboardRegistry.java
  - blackboard/src/main/java/io/casehub/blackboard/control/PlanningStrategyLoopControl.java
violation_hint: "Calling markConfigured() or indexWorkerForCompletion() on a caseId with no prior getOrCreate() silently no-ops — no exception, no log. Symptom: BlackboardPlanConfigurer fires more than once per case, or completion index is empty when PlanItemCompletionHandler looks up a worker."
created: 2026-05-19
---

`BlackboardRegistry.markConfigured()` and `indexWorkerForCompletion()` use `entries.get()` internally and silently no-op when no entry exists for the given caseId. `getOrCreate(caseId)` must have been called first to materialise the `CaseEntry`. The production call site in `PlanningStrategyLoopControl` always calls `getOrCreate()` before either method; this ordering is the contract, not a coincidence. Violating it produces no error but drops the configured flag (causing configurers to run more than once) or leaves the completion index empty (causing `getPlanItemId()` to return empty on worker completion). See engine#292 for the internal consolidation that introduced this constraint.
