---
id: PP-20260529-3ffe28
title: "Engine case start requires three-phase @Transactional split — never join() inside a transaction"
type: rule
scope: application
applies_to: "Any harness service that calls CaseHubRuntime.startCase() or YamlCaseHub.startCase()"
severity: critical
refs:
  - ../../repos/casehub-clinical.md
  - ../../repos/casehub-engine.md
violation_hint: "Service method annotated @Transactional calls startCase().join() — Agroal pool deadlock under load; or service writes entity status before and after join() in a single transaction — pool exhaustion silently prevents status from being persisted"
created: 2026-05-29
---

Any service that calls `startCase().toCompletableFuture().join()` must split into four phases: Phase 1 `@Transactional` (validate, update domain status, build initial context), Phase 2 non-transactional (`startCase().join()`), Phase 3 `@Transactional` (persist the returned `caseId` on the domain entity), Phase 4 `@Transactional markFailed()` called from a `try-catch` around Phase 2–3 (writes FAILED status if `join()` throws). Holding an open DB connection across `join()` deadlocks the Agroal pool when the engine's JPA persistence also needs a connection from the same pool. Phase 4 must itself be wrapped in a `try-catch` to prevent a secondary DB failure from masking the original failure. Reference implementation: `TrialActivationService`, `AeEscalationCaseService`, `IrbDeviationCaseService` in `casehub-clinical`.
