---
id: PP-20260519-1f5e2c
title: "Unsatisfied reactive CDI beans from library deps must be satisfied via @DefaultBean test stub, not by disabling the library"
type: rule
scope: platform
applies_to: "All casehub extension modules using @QuarkusTest with non-reactive H2 datasources"
severity: important
refs:
  - runtime/src/test/java/io/casehub/qhorus/runtime/ledger/StubReactiveLedgerEntryRepository.java
violation_hint: "All @QuarkusTest tests fail at CDI discovery with 'UnsatisfiedResolutionException' for a reactive repository type"
created: 2026-05-19
---

When a casehub library module (e.g. casehub-ledger) declares a CDI bean that injects a reactive repository or reactive service — and the consuming extension runs tests with a non-reactive H2 datasource (`quarkus.datasource.reactive=false`) — the real reactive implementation is gated by `@IfBuildProperty` and absent, leaving the library's bean unsatisfied. The fix: add a `@DefaultBean @ApplicationScoped` stub implementing the unsatisfied interface in the consuming module's test sources. All stub methods throw `UnsupportedOperationException` — they are not expected to be called in non-reactive tests. Do NOT disable the library (`casehub.ledger.enabled=false`) as a workaround; that removes coverage for the library's non-reactive beans. The stub is build-time transparent and yields to any real implementation. See `StubReactiveLedgerEntryRepository` in casehub-qhorus for the reference implementation.
