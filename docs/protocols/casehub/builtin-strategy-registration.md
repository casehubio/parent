---
id: PP-20260521-903472
title: "Register new built-in WorkerSelectionStrategy in three places atomically"
type: rule
scope: repo
applies_to: "casehub-work — WorkItemAssignmentService, WorkItemsConfig"
severity: important
refs:
  - runtime/src/main/java/io/casehub/work/runtime/service/WorkItemAssignmentService.java
  - runtime/src/main/java/io/casehub/work/runtime/config/WorkItemsConfig.java
violation_hint: "New strategy activates via @Alternative but not via config key, or config key works but strategy appears in CDI override path (treated as external alternative)."
created: 2026-05-21
---

When adding a new built-in `WorkerSelectionStrategy` to casehub-work, three locations must be updated in the same commit: (1) `WorkItemAssignmentService.activeStrategy()` — add a case to the switch so the config key activates the strategy; (2) the `@Alternative` exclusion filter in the same method — add `&& !(s instanceof NewStrategy)` so CDI does not pick it up as an external override when it is the configured built-in; (3) `WorkItemsConfig.RoutingConfig.strategy()` Javadoc — document the new config value and any infrastructure it requires. Missing any one of these causes silent behaviour inconsistencies: the strategy either activates for all config values (filter gap) or activates for none (switch gap).
