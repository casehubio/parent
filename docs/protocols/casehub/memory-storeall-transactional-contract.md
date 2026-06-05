---
id: PP-20260605-e63850
title: "CaseMemoryStore storeAll() must be single-transaction with per-item tenant assertion"
type: rule
scope: platform
applies_to: "All CaseMemoryStore adapter implementations — memory-jpa, memory-sqlite, memory-inmem, and any future adapters (memory-graphiti, etc.)"
severity: important
refs:
  - platform-api/src/main/java/io/casehub/platform/api/memory/CaseMemoryStore.java
  - docs/superpowers/specs/2026-06-05-memory-cdi-priority-and-emission-design.md
violation_hint: "storeAll() calls assertTenant() only on item 0 and uses N separate @Transactional calls — mixed-tenant input commits items before the violation is detected"
created: 2026-06-05
---

Any CaseMemoryStore adapter overriding `storeAll()` must wrap all N inserts in a single
`@Transactional(REQUIRED)` scope, call `MemoryPermissions.assertTenant()` per item inside
the batch (not just on the first item), and propagate `SecurityException` for any mismatch.
This guarantees atomicity: no entries are persisted if any item fails the tenant check.
The SPI default (`store() × N`) must not be used when partial-write safety is required —
it issues a separate transaction per call, committing earlier items before the violation
is detected. Exception type on mismatch must be `SecurityException` (from `assertTenant`),
not `IllegalArgumentException`, so callers can write adapter-neutral catch clauses.
