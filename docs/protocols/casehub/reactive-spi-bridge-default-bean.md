---
id: PP-20260529-5745c1
title: "Reactive SPI bridge defaults must be @DefaultBean without @IfBuildProperty"
type: rule
scope: platform
applies_to: "Any casehub Foundation module that adds a reactive SPI bridge implementation"
severity: important
refs:
  - ../casehub-eidos.md
  - alternative-extension-patterns.md
violation_hint: "@DefaultBean reactive bridge is gated with @IfBuildProperty even though it has no Hibernate Reactive dependency — it is vetoed under the default profile and callers get UnsatisfiedResolutionException."
created: 2026-05-29
---

A reactive SPI bridge (an impl that wraps a blocking delegate via `Uni.createFrom().item(supplier).runSubscriptionOn(workerPool)`) must be annotated `@DefaultBean @ApplicationScoped` with no `@IfBuildProperty` gate. The `@IfBuildProperty` gate belongs only on implementations that actually depend on Hibernate Reactive. Bridges have no such dependency — they are safe to activate unconditionally and must be active under all profiles so the SPI injection point is always satisfied. The pattern: no-op / bridge impl → `@DefaultBean`; JPA blocking impl → `@IfBuildProperty(enableIfMissing=true)`; JPA reactive impl → `@IfBuildProperty(reactive=true)`; InMemory → `@Alternative @Priority(1)`.
