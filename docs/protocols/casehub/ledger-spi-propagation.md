---
id: PP-20260511-ledger-spi
title: "When a LedgerEntryRepository SPI method is added, update all downstream implementations — including test no-ops"
type: principle
scope: platform
applies_to: "casehub-work, casehub-qhorus, casehub-engine (and any future ledger consumer)"
severity: required
refs: ["casehub-ledger#58", "casehub/work#163", "casehub/qhorus#143", "casehub/engine#242"]
violation_hint: "Compilation failure in downstream module with 'does not override abstract method' — often masked by stale .m2 jar producing a different error"
created: 2026-05-11
---

# Protocol: Ledger SPI Propagation — Update All Downstream Implementations

**Applies to:** Any session that adds an abstract method to `LedgerEntryRepository` or `ReactiveLedgerEntryRepository` in `casehub-ledger`  
**Severity:** Required — downstream modules will fail to compile

## Rule

When a new abstract method is added to `LedgerEntryRepository` (blocking) or `ReactiveLedgerEntryRepository` (reactive) in `casehub-ledger`, the following implementations must be updated **before the next full-stack build**:

| Module | Implementation | Type |
|--------|---------------|------|
| `casehub-work` | `JpaWorkItemLedgerEntryRepository` | main source |
| `casehub-qhorus` | `MessageLedgerEntryRepository` | main source |
| `casehub-qhorus` | `ReactiveMessageLedgerEntryRepository` | main source |
| `casehub-engine` | `NoOpLedgerEntryRepository` (×4) | **test source** |
| `casehub-engine` | `casehub-work-adapter/NoOpLedgerEntryRepository` | test source |
| `casehub-engine` | `casehub-blackboard/NoOpLedgerEntryRepository` | test source |
| `casehub-engine` | `casehub-resilience/NoOpLedgerEntryRepository` | test source |

Test no-ops return `List.of()` or `Uni.createFrom().item(List.of())` for reactive variants.

## Why test sources are the trap

Maven reports compilation failures in the **downstream** module (e.g. casehub-engine), not in the test source file where the actual error is. IntelliJ's `build_project` tool finds the true location. Always use `build_project` to diagnose unexplained compilation failures in engine.

## Checklist

When adding a method to `LedgerEntryRepository`:

- [ ] Add implementation to `JpaLedgerEntryRepository` in casehub-ledger (the canonical implementation)
- [ ] Add implementation to `JpaWorkItemLedgerEntryRepository` in casehub-work
- [ ] Add implementation to `MessageLedgerEntryRepository` in casehub-qhorus
- [ ] Add implementation to `ReactiveMessageLedgerEntryRepository` in casehub-qhorus
- [ ] Add no-op to all 4 `NoOpLedgerEntryRepository` test classes in casehub-engine
- [ ] Run `mvn install -f aggregator.xml` from casehub-parent to verify full-stack compiles

## Example

```java
// LedgerEntryRepository (casehub-ledger) — new method added:
List<LedgerEntry> findBySubjectIdAndTimeRange(UUID subjectId, Instant from, Instant to);

// All no-op test implementations:
@Override
public List<LedgerEntry> findBySubjectIdAndTimeRange(UUID subjectId, Instant from, Instant to) {
    return List.of();
}

// Reactive variant in casehub-qhorus:
@Override
public Uni<List<LedgerEntry>> findBySubjectIdAndTimeRange(UUID subjectId, Instant from, Instant to) {
    return repo.list("subjectId = ?1 AND occurredAt >= ?2 AND occurredAt <= ?3 ORDER BY occurredAt ASC",
        subjectId, from, to)
        .map(l -> (List<LedgerEntry>) (List<?>) l);
}
```
