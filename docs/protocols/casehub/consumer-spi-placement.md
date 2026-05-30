---
id: consumer-spi-placement
title: Consumer-Facing SPI Placement — api/spi/ vs runtime/
scope: casehub
applies-to: any casehubio extension or library module defining an SPI interface
---

## Rule

Any `@FunctionalInterface` or plain interface that an external consumer (Claudony,
an application repo, or any module that is NOT the defining extension) is expected
to implement MUST live in `api/spi/`.

Placing it in `runtime/` forces consumers to declare the full extension as a
dependency just to implement the interface — pulling in JPA entities, CDI beans,
Quarkus build-time dependencies, and transitive runtime deps they do not need.
The `api/` module is intentionally lightweight (pure Java, no JPA, no Quarkus
runtime deps) so consumers can depend on it alone.

## The Criterion

Ask: **will any module other than this extension's own runtime provide an implementation?**

| Answer | Placement |
|--------|-----------|
| Yes — Claudony, an app repo, or any external module implements this | `api/spi/` |
| No — only the runtime provides implementations | `runtime/<domain>/` (acceptable) |
| Unsure | Default to `api/spi/` — a misplaced SPI forces migration later; premature placement costs nothing |

## Interface vs Default Implementation

The SPI **interface** always follows the rule above.

The `@DefaultBean` **default implementation** placement depends on its dependencies:

| Default impl has… | Placement |
|-------------------|-----------|
| No deps (identity function, constant) | Can live in `api/spi/` alongside the interface, or in `runtime/` — either is fine |
| JPA, `@ConfigMapping`, or Quarkus service injection | `runtime/<domain>/` — these are inherently runtime concerns |

## Correct Placements (reference)

| SPI | Location | Default impl location | Consumer |
|-----|----------|-----------------------|---------|
| `InstanceActorIdProvider` | `api/spi/` | `runtime/ledger/` (trivial no-op; could be inline) | Claudony (session→persona mapping) |
| `CommitmentAttestationPolicy` | `api/spi/` | `runtime/ledger/` (injects `QhorusConfig`) | Future consumers |
| `MessageObserver` | `api/gateway/` | `runtime/gateway/InProcessMessageBus` | Any module observing channel messages |
| `InboundNormaliser` | `api/gateway/` | `runtime/gateway/DefaultInboundNormaliser` | Custom inbound normalisation |
| `ObligorTrustPolicy` | `api/spi/` | `runtime/message/DefaultObligorTrustPolicy` | Claudony (capability-scoped trust) |

## When Is a Violation Justified?

Almost never. The only case where keeping an interface in `runtime/` is legitimate is
when the **interface parameter or return types themselves are runtime-only** (JPA entities,
Quarkus service types) and cannot be extracted to a plain Java type.

In practice this is a design smell — if you cannot write the interface signature using
only `java.*`, `api/` module types, and other foundational `*-api` types, the interface
is leaking implementation details. Fix the interface first; the placement question then
answers itself.

If a genuine justified exception exists, document it inline on the interface:

```java
// Kept in runtime/ because [concrete reason].
// Consumers requiring this SPI must depend on runtime; this is intentional.
```

## Anti-pattern

```
runtime/
  message/
    MyConsumerFacingSpi.java     ← WRONG: external consumer cannot depend on api/ only
    DefaultMyConsumerFacingSpi.java  ← OK: @DefaultBean with JPA/config deps
```

```
api/spi/
  MyConsumerFacingSpi.java       ← CORRECT
runtime/
  message/
    DefaultMyConsumerFacingSpi.java  ← CORRECT: @DefaultBean with JPA/config deps
```

## Refs

- Protocol surfaced during casehub-qhorus#213 (ObligorTrustPolicy SPI)
- `api/spi/` is the dedicated subdirectory for SPI interfaces within the `api` module;
  other `api/<domain>/` packages hold records, events, and enums that are not SPIs
