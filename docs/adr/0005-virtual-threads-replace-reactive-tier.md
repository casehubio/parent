# 0005 — Virtual threads replace reactive (Mutiny) tier as default concurrency model

Date: 2026-07-20
Status: Accepted

## Context and Problem Statement

CaseHub adopted Mutiny Uni/Multi as the reactive programming model for I/O concurrency,
leading to a dual-tier architecture: every SPI ships blocking + reactive beans, gated by
`@IfBuildProperty`, with ArchUnit tests enforcing bidirectional method parity. This spans
~21 repos, 561 Java files, and ~20 garden protocols.

With Java 21, virtual threads eliminate the original motivation for reactive wrappers —
a blocked virtual thread is nearly free. An ecosystem-wide audit found:

- **The wrapper pattern dominates.** Most reactive code wraps blocking JPA/JDBC with
  `Uni.createFrom().item(() -> blocking.method())` — not true non-blocking I/O.
- **REST is already imperative.** Zero repos use reactive REST exclusively.
- **The engine's core handler (`CaseContextChangedEventHandler`) runs `@ConsumeEvent(blocking = true)`
  yet uses Uni composition throughout.** The reactive chain is structural convenience, not IO-thread
  safety.
- **42 `@Blocking` annotations in qhorus** — reactive code fighting against blocking reality.
- **Only 4 `@RunOnVirtualThread` in the entire ecosystem** despite Java 21 being the target.

The dual-tier architecture (separate beans, build-time gating, parity tests, Reactive* naming,
consumer contracts) carries significant accidental complexity for limited benefit.

## Decision

Default to virtual threads + synchronous code. Retire the reactive tier except where streaming,
backpressure, or event-driven APIs structurally require it.

## What Changes

| Layer | Before | After |
|-------|--------|-------|
| SPIs | `FooStore` + `ReactiveFooStore` (two beans, build-time gated) | `FooStore` only |
| Services | `FooService` + `ReactiveFooService` | `FooService` only |
| Event handlers | `@ConsumeEvent(blocking=true)` + `Uni<Void>` chains | Virtual thread, `void`, sequential |
| Worker execution | `Uni.createFrom().item(blocking).runSubscriptionOn(vt)` | Synchronous on virtual thread |
| Fan-out | `Uni.combine().all().unis(list)` | `StructuredTaskScope` |
| Timeout | `Uni.ifNoItem().after(duration).fail()` | `Future.get(timeout)` or `StructuredTaskScope` |
| Error recovery | `.onFailure().recoverWithUni()` | try-catch |
| DB access | Hibernate Reactive + standard JPA (dual) | Standard JPA only |
| Build-time gating | `@IfBuildProperty(casehub.*.reactive.enabled)` | Removed |
| Parity tests | `BlockingReactiveParityTest` (ArchUnit) | Removed |

## What Stays Reactive

| Pattern | Why |
|---------|-----|
| Reactive Messaging channels (Kafka, AMQP) | SmallRye Reactive Messaging API is `Multi<T>` by design |
| `Multi<T>` streaming with backpressure | No virtual thread equivalent |
| Postgres LISTEN/NOTIFY broadcasters | Event-driven pub/sub — reactive PG client is correct |
| SSE endpoints | Already `@RunOnVirtualThread` — no change needed |

## What Gets Deleted

- All `Reactive*Service` / `Reactive*Store` classes (~10 repos)
- All `@IfBuildProperty` / `@UnlessBuildProperty` reactive gating
- All `BlockingReactiveParityTest` ArchUnit tests
- `quarkus-hibernate-reactive` dependency from non-broadcaster modules
- ~20 garden protocols about reactive patterns (replaced by single protocol)

## Consequences

**Positive:**
- Dramatic codebase simplification — one bean per service, no gating, no parity tests
- Simpler onboarding — new contributors write synchronous Java, not Uni chains
- Fewer Vert.x threading errors — no more `BlockingOperationNotAllowedException`
- Hibernate ORM is better documented and tooled than Hibernate Reactive

**Negative:**
- Large migration scope (~21 repos, 561 files)
- Reactive Messaging (Kafka/AMQP) still uses Mutiny — mixed model at boundaries
- `StructuredTaskScope` is preview in Java 21 (stable in 25) — may need `--enable-preview`

**Neutral:**
- Worker SPI (`WorkerFunctionHandler.execute()`) return type changes from `Uni<WorkerResult>` to
  `WorkerResult` — breaking API change, but all implementations are internal
