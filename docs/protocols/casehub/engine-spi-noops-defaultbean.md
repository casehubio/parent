---
id: PP-20260514-engine-spi-noops-defaultbean
title: "Engine SPI no-op defaults must use @DefaultBean, not bare @ApplicationScoped"
type: rule
scope: platform
applies_to: "casehub-engine runtime — all no-op SPI default implementations"
severity: critical
refs:
  - GE-20260428-9311f8
created: 2026-05-14
---

Every no-op SPI default in casehub-engine must be annotated `@DefaultBean @ApplicationScoped`,
not bare `@ApplicationScoped` or `@Alternative @ApplicationScoped`. A bare `@ApplicationScoped`
no-op collides with consumer implementations (e.g. Claudony's `ClaudonyWorkerProvisioner`) when
the engine runtime is indexed alongside a consumer repo's `@QuarkusTest` classpath, causing CDI
ambiguity errors that fail the entire test suite.

`@DefaultBean` is `io.quarkus.arc.DefaultBean` — a Quarkus Arc annotation, not standard CDI.
It yields automatically to any non-default qualifying bean — the correct semantic for a platform
fallback that exists only when no real implementation is provided.

## Beans

All in `casehub-engine/runtime/src/main/java/io/casehub/engine/internal/`:

| Class | Package | Annotation |
|-------|---------|-----------|
| `NoOpWorkerProvisioner` | `worker/` | `@DefaultBean @ApplicationScoped` |
| `NoOpCaseChannelProvider` | `worker/` | `@DefaultBean @ApplicationScoped` |
| `NoOpWorkerStatusListener` | `worker/` | `@DefaultBean @ApplicationScoped` |
| `EmptyWorkerContextProvider` | `worker/` | `@DefaultBean @ApplicationScoped` |
| `EmptyReactiveWorkerContextProvider` | `worker/` | `@DefaultBean @ApplicationScoped` |
| `NoOpReactiveWorkerProvisioner` | `worker/` | `@DefaultBean @ApplicationScoped` |
| `NoOpReactiveCaseChannelProvider` | `worker/` | `@DefaultBean @ApplicationScoped` |
| `NoOpReactiveWorkerStatusListener` | `worker/` | `@DefaultBean @ApplicationScoped` |

## Why this matters

Consumer repos (Claudony, devtown, etc.) that depend on `casehub-testing` for integration
tests index the engine runtime transitively. Without `@DefaultBean`, CDI sees two beans
implementing the same SPI interface — the engine's no-op and the consumer's real implementation
— and fails with an unsatisfied/ambiguous dependency error. The workaround (listing each no-op
in `quarkus.arc.exclude-types` per consumer) is fragile: it breaks silently when new no-ops are
added to the engine.

## Adding a new no-op default

When adding a new SPI no-op to `casehub-engine`:
1. Annotate it `@DefaultBean @ApplicationScoped` from the start — use `io.quarkus.arc.DefaultBean`
2. Add it to the table above
3. Verify no consumer repo needs updating (no `exclude-types` entries to clean up)

## Two patterns: consumer-replaceable SPI vs. engine-internal selection

`@DefaultBean` applies to two distinct situations in the engine:

**Consumer-replaceable SPI** (the 8 worker/channel beans above): The engine ships a no-op
fallback. A consumer deployment provides a real `@ApplicationScoped` implementation
(e.g. `ClaudonyWorkerProvisioner`) and the no-op yields automatically.

**Engine-internal strategy selection** (`ContextDiffStrategy`): The engine ships multiple
real implementations and selects one via config (`casehub.engine.diff-strategy`). A
`@Produces @DefaultBean @ApplicationScoped` method on `ContextDiffStrategyProducer` produces
the chosen instance. A consumer `@ApplicationScoped` implementation still wins over the
produced default. The individual strategy classes (`NoOpContextDiffStrategy` etc.) are plain
POJOs — no CDI annotations — instantiated directly by the producer.

Do not apply the single-class `@DefaultBean` pattern to engine-internal strategy groups.
Use a config-driven producer instead.

## See also

Garden entry `GE-20260428-9311f8` — "@ApplicationScoped no-op SPI beans collide with consumer
implementations when engine is indexed".
