---
id: PP-20260529-f67675
title: "Harness @QuarkusTest must supply @DefaultBean WorkloadProvider stub"
type: rule
scope: application
applies_to: "Any harness application including casehub-engine in @QuarkusTest scope"
severity: critical
refs:
  - ../../repos/casehub-clinical.md
violation_hint: "UnsatisfiedResolutionException for io.casehub.work.api.WorkloadProvider at @QuarkusTest CDI startup — JpaWorkloadProvider is excluded but no DefaultBean substitute exists"
created: 2026-05-29
---

Any harness application that includes `casehub-engine` in `@QuarkusTest` must provide a `@DefaultBean @ApplicationScoped` stub implementing `io.casehub.work.api.WorkloadProvider` that returns 0 for all methods. The engine's internal bridge (`CasehubWorkloadProvider`) was deleted in engine#378 as part of the AgentRoutingStrategy refactor; `JpaWorkloadProvider` from `casehub-work` is excluded via `quarkus.arc.exclude-types` to avoid DB schema issues. Without a stub, CDI startup fails with an unsatisfied dependency. The stub must live in `src/test/java` under a `support/` package alongside other test infrastructure beans. See `StubWorkloadProvider` in `casehub-clinical` for the reference implementation. Track engine#393 — if the engine ships a replacement default, this stub may become redundant.
