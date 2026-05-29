---
id: PP-20260529-ca7b89
title: "Reactive @QuarkusTest entity setup for named-PU services: use QuarkusTransaction.requiringNew() with blocking service"
type: rule
scope: platform
applies_to: "@QuarkusTest integration tests for reactive services backed by a named Quarkus datasource (e.g. 'qhorus') where test setup must pre-seed entities before a reactive dispatch"
severity: important
refs:
  - reactive-pg-devservices-test-profile.md
violation_hint: "persistChannel() or test helper calls Panache.withTransaction('qhorus', () -> ...) from a JUnit5 test thread, causing 'No current Vert.x context found' or deadlock on await()"
created: 2026-05-29
---

When a `@QuarkusTest` for a reactive service needs pre-seeded entities before a reactive dispatch, the test setup helper must use `QuarkusTransaction.requiringNew().run(() -> blockingService.create(...))` — not `Panache.withTransaction("qhorus", () -> ...)`. JUnit test threads have no Vert.x event loop context; the reactive Panache API throws "No current Vert.x context found". `QuarkusTransaction.requiringNew()` uses JTA/JDBC which is not thread-constrained: the entity commits in a separate JTA transaction and is visible to the reactive service's own reactive session when it starts. Established in casehubio/qhorus#193 via `ReactiveMessageServiceTest.persistChannel()`.
