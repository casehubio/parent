---
id: consumer-spi-placement
title: Consumer-Facing SPI Placement — api/ vs runtime/
scope: casehub
applies-to: any casehubio extension or library module defining an SPI interface
---

## Rule

Any `@FunctionalInterface` or plain interface that an external consumer (Claudony,
an application repo, or any module that is NOT the defining extension) is expected
to implement MUST live in `api/<domain>/`, not `runtime/`.

Placing a consumer-facing SPI in `runtime/` forces consumers to declare the full
extension as a dependency just to implement the interface — pulling in JPA entities,
CDI beans, Quarkus build-time dependencies, and transitive runtime deps they do not
need. The `api/` module is intentionally lightweight (pure Java, no JPA, no Quarkus
runtime deps) so consumers can depend on it alone.

## The Criterion

Ask: **will any module other than this extension's own runtime provide an implementation?**

| Answer | Placement |
|--------|-----------|
| Yes — Claudony, an app repo, or any external module implements this | `api/<domain>/` |
| No — only the runtime provides implementations; no external consumer will override it | `runtime/<domain>/` (acceptable) |
| Unsure | Default to `api/` — a misplaced SPI forces migration later; a prematurely moved one costs nothing |

## Interface vs Default Implementation

The SPI **interface** always follows the rule above.

The `@DefaultBean` **default implementation** may stay in `runtime/` if it injects
runtime dependencies (JPA repositories, `@ConfigMapping`, Quarkus services). The
interface being in `api/` is sufficient — consumers see the contract; the default
wiring is an extension concern.

## Known Violations (cleanup tracked in qhorus#223)

| SPI | Current location | Correct location | Consumer |
|-----|-----------------|-----------------|---------|
| `InstanceActorIdProvider` | `runtime/ledger/` | `api/message/` (or `api/ledger/`) | Claudony (session→persona mapping) |
| `CommitmentAttestationPolicy` | `runtime/ledger/` | `api/message/` | Potential future consumer |

## Correct Placements (reference)

| SPI | Location | Consumer |
|-----|----------|---------|
| `MessageObserver` | `api/gateway/` | Any module observing channel messages |
| `InboundNormaliser` | `api/gateway/` | Custom inbound normalisation |
| `ObligorTrustPolicy` | `api/message/` | Claudony (capability-scoped trust) |

## Anti-pattern

```
runtime/
  message/
    MyConsumerFacingSpi.java     ← WRONG — external consumer can't depend on api/ only
    DefaultMyConsumerFacingSpi.java  ← OK — default impl may stay here if it has runtime deps
```

```
api/
  message/
    MyConsumerFacingSpi.java     ← CORRECT
runtime/
  message/
    DefaultMyConsumerFacingSpi.java  ← CORRECT — @DefaultBean with JPA/config deps
```

## Refs

- Protocol surfaced during casehub-qhorus#213 (ObligorTrustPolicy SPI)
- Cleanup: casehub-qhorus#223
- Module tier structure: [`universal/module-tier-structure.md`](../universal/module-tier-structure.md) (if it exists)
