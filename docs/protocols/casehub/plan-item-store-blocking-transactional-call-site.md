---
id: PP-20260518-78f8b7
title: "PlanItemStore.save() must be called from a blocking @Transactional context"
type: rule
scope: repo
applies_to: "casehub-engine-work-adapter — any handler or service that writes PlanItem status via PlanItemStore"
severity: critical
refs:
  - casehub-engine.md
violation_hint: "PlanItemStore.save() called from DefaultCasePlanModel.addPlanItem() or any reactive call chain — the write silently no-ops or throws TransactionRequiredException; the durable status record is never created"
created: 2026-05-18
---

`PlanItemStore.save()` and `PlanItemStore.updateStatus()` must only be called from a blocking thread with an active JTA context. The production call path through `DefaultCasePlanModel.addPlanItem()` runs on the Vert.x IO thread (inside the reactive `PlanningStrategy` chain) and has no JTA context — calling the JPA blocking store there silently fails or throws `TransactionRequiredException`. The correct call site is `HumanTaskScheduleHandler`, which is annotated `@ConsumeEvent(blocking=true) @Transactional`; both `PlanItemStore.save()` and `WorkItemService.create()` join that single JTA transaction, making WorkItem creation and PlanItem status durable atomically. Any future handler that needs to record PlanItem status must similarly run on a blocking thread inside a `@Transactional` boundary. See engine#273 for the root cause analysis.
