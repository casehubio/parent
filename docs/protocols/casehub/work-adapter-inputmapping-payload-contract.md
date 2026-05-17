---
id: PP-20260517-0093f8
title: "Engine adapters must propagate HumanTaskTarget inputMapping output to WorkItem payload"
type: rule
scope: repo
applies_to: "casehub-engine-work-adapter — all outbound handlers creating WorkItems from HumanTaskTarget bindings"
severity: important
refs:
  - casehub-engine.md
violation_hint: "inputData passed as empty/null when it has content, or serializePayload() not called — inputMapping silently discarded, WorkItem missing case context"
created: 2026-05-17
---

`HumanTaskTarget` explicitly contracts that both inline and template modes support
`inputMapping` (context → task payload). Any outbound handler that creates a WorkItem
from a `HumanTaskTarget` binding must honour this: serialize `event.inputData()` and
pass it as the WorkItem `payload` (inline mode via `WorkItemCreateRequest`) or as
`payloadOverride` (template mode via `WorkItemTemplateService.instantiate`). If
`inputData` is null or empty, the template's `defaultPayload` is used as fallback.
Silently ignoring `inputData` when it contains content violates the published contract
and discards case context the plan author explicitly configured.
