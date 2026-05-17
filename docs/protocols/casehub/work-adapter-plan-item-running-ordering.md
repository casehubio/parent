---
id: PP-20260517-cbf836
title: "PlanItem must not be marked RUNNING until all resolution and validation steps succeed"
type: rule
scope: repo
applies_to: "casehub-engine-work-adapter — all outbound handlers (HumanTaskScheduleHandler and any future handlers)"
severity: critical
refs:
  - casehub-engine.md
violation_hint: "markRunning() called before template resolution or other pre-condition check — PlanItem ends up RUNNING with no WorkItem to complete it; case stuck indefinitely"
created: 2026-05-17
---

Any outbound handler in `casehub-work-adapter` that creates a WorkItem for a `PlanItem`
must gate `item.markRunning()` behind all resolution and validation steps. If template
lookup fails, the ref is ambiguous, or any other pre-condition is not satisfied, the
handler must return without calling `markRunning()` — leaving the PlanItem PENDING so
the binding remains eligible for re-evaluation on the next `CONTEXT_CHANGED` tick. A
PlanItem advanced to RUNNING before its WorkItem is created cannot self-recover: the
engine will not reschedule it, and the case is stuck.
