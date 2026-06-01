---
id: PP-20260601-e368ea
title: "CDI SPI event records that carry tenancyId must place it as the 2nd component after caseId"
type: rule
scope: platform
applies_to: "casehub-engine-common/spi/event/ — any new SPI event record that carries tenancyId"
severity: important
refs:
  - ../../repos/casehub-engine.md
violation_hint: "New SPI event record has tenancyId at position 3+ instead of position 2 (e.g. after workerId or traceId)"
created: 2026-06-01
---

All CDI SPI event records in `casehub-engine-common/spi/event/` that include a `tenancyId` component must place it immediately after `caseId` — matching the `CaseLifecycleEvent` ordering: `(UUID caseId, String tenancyId, ...)`. This is enforced so observers can destructure events consistently and so the pattern is immediately recognisable when reading fire sites. The traceId is always last; tenancyId is always second. See `WorkerDecisionEvent` (engine#407) and `CaseLifecycleEvent` (engine#299) for the canonical pattern.
