---
id: PP-20260514-engine-spi-noops-defaultbean
title: "Engine SPI no-op defaults must use @DefaultBean, not bare @ApplicationScoped"
type: rule
scope: platform
applies_to: "casehub-engine runtime — all no-op SPI default implementations"
severity: error
refs:
  - GE-20260428-9311f8
violation_hint: "NoOp* bean is @ApplicationScoped without @DefaultBean — collides with consumer implementations when casehub-engine is indexed alongside a consumer (e.g. via casehub-testing)"
created: 2026-05-14
---

Every no-op SPI default in casehub-engine must be annotated `@DefaultBean @ApplicationScoped`,
not bare `@ApplicationScoped`. A bare `@ApplicationScoped` no-op collides with consumer
implementations (e.g. Claudony's `ClaudonyWorkerProvisioner`) when the engine runtime is indexed
alongside a consumer repo's `@QuarkusTest` classpath, causing CDI ambiguity errors that fail
the entire test suite.

`@DefaultBean` yields automatically to any non-default qualifying bean — the correct semantic
for a platform fallback that exists only when no real implementation is provided.

## Beans to fix

In `casehub-engine/runtime/src/main/java/io/casehub/engine/internal/worker/`:

| Class | Current | Required |
|---|---|---|
| `NoOpWorkerProvisioner` | `@ApplicationScoped` | `@DefaultBean @ApplicationScoped` |
| `NoOpCaseChannelProvider` | `@ApplicationScoped` | `@DefaultBean @ApplicationScoped` |
| `NoOpWorkerStatusListener` | `@ApplicationScoped` | `@DefaultBean @ApplicationScoped` |

In `casehub-engine/runtime/src/main/java/io/casehub/engine/internal/diff/`:

| Class | Current | Required |
|---|---|---|
| `NoOpContextDiffStrategy` | `@ApplicationScoped` | `@DefaultBean @ApplicationScoped` |

The reactive variants (`NoOpReactiveWorkerProvisioner`, `NoOpReactiveCaseChannelProvider`,
`NoOpReactiveWorkerStatusListener`) currently use `@Alternative` which avoids the collision,
but should migrate to `@DefaultBean` for consistency — `@Alternative` requires explicit
activation, whereas `@DefaultBean` is active by default and clearly communicates "I am the
fallback, replace me."

## Why this matters

Consumer repos (Claudony, devtown, etc.) that depend on `casehub-testing` for integration
tests index the engine runtime transitively. Without `@DefaultBean`, CDI sees two beans
implementing the same SPI interface — the engine's no-op and the consumer's real implementation
— and fails with an unsatisfied/ambiguous dependency error. The workaround (listing each no-op
in `quarkus.arc.exclude-types` per consumer) is fragile: it breaks silently when new no-ops are
added to the engine.

## See also

Garden entry `GE-20260428-9311f8` — "@ApplicationScoped no-op SPI beans collide with consumer
implementations when engine is indexed".
