---
id: PP-20260606-ef909e
title: "Snapshot template-defined constraints onto WorkItem at instantiation, never re-read at completion"
type: principle
scope: platform
applies_to: "casehub-work WorkItemService.create(), all instantiation paths (WorkItemTemplateService, MultiInstanceSpawnService, WorkItemSpawnService)"
severity: important
refs:
  - ../../../casehub/work/docs/GOTCHAS.md
  - ../../../casehub/work/docs/MODULES.md
created: 2026-06-05
---

Template-defined constraints — `inputDataSchema`, `outputDataSchema`, and `permittedOutcomes` (including any JEXL conditions on each outcome) — must be copied onto the `WorkItem` entity at instantiation time, not re-read from the `WorkItemTemplate` at completion or rejection time. This ensures that a WorkItem is validated against the constraint set that was in effect when it was created: changing a template's schema or outcomes after instantiation has no retroactive effect on in-flight WorkItems. Any new constraint added to `WorkItemTemplate` that affects completion behaviour must follow this snapshotting pattern and be propagated through all instantiation call sites (`WorkItemTemplateService.instantiate()`, `MultiInstanceSpawnService.buildParentRequest()`, `MultiInstanceSpawnService.buildChildRequest()`, `WorkItemSpawnService.buildCreateRequest()`).
