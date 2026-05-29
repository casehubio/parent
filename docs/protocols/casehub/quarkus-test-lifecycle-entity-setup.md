---
id: PP-20260529-fa9cbf
title: "@QuarkusTest lifecycle tests for @ObservesAsync services must persist entities in @BeforeEach @Transactional"
type: rule
scope: application
applies_to: "@QuarkusTest integration tests where the service under test calls Panache.findById() in an @ObservesAsync handler"
severity: important
refs:
  - ../repos/casehub-clinical.md
violation_hint: "Service observer logs 'entity not found — skipping' in tests, or returns null from Phase 1 without any assertion failure, because @BeforeEach created UUIDs but never persisted the entities"
created: 2026-05-29
---

When testing an `@ObservesAsync` service that calls `Panache.findById()` on a domain entity (e.g. in a three-phase refactor's Phase 1), the `@BeforeEach setup()` method must be annotated `@Transactional` and must persist a minimal entity using the same UUID that will be passed in the CDI event. Without this, Phase 1 finds no entity, logs a warning, returns null, and skips all subsequent phases — silently making the test pass for the wrong reasons. Add a `@Transactional` helper method (`findAe()`, `findDeviation()`, etc.) that reads the entity from the DB for use in assertions. Reference implementations: `AeEscalationLifecycleTest`, `IrbGateLifecycleTest`, `DsmbRollupTest` in `casehub-clinical`.
