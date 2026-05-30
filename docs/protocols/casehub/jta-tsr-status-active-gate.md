---
id: PP-20260530-332d70
title: "Check STATUS_ACTIVE before registering JTA synchronizations"
type: rule
scope: repo
applies_to: "casehub-qhorus — any @Transactional service class that defers post-commit side effects via TransactionSynchronizationRegistry"
severity: important
refs:
  - runtime/src/main/java/io/casehub/qhorus/runtime/message/MessageObserverDispatcher.java
violation_hint: "Calling tsr.registerInterposedSynchronization() without checking status first silently breaks in @TestTransaction tests where a prior exception has marked the TX ROLLBACK_ONLY — error surfaces as Narayana IllegalStateException 'state 1' wrapped in ToolCallException"
created: 2026-05-30
---

Any code that calls `tsr.registerInterposedSynchronization()` must first verify `tsr.getTransactionStatus() == jakarta.transaction.Status.STATUS_ACTIVE`. Narayana (Quarkus JTA) rejects synchronization registration on ROLLBACK_ONLY transactions with an opaque internal error ("state 1") — not a JTA spec constant. In `@TestTransaction` tests a prior `@Transactional` call that throws an unchecked exception marks the outer TX ROLLBACK_ONLY; subsequent deferral attempts in the same test then fail. When the status check fails or TSR is null, fall back to synchronous dispatch immediately rather than propagating the registration error. See `MessageObserverDispatcher.dispatch()` for the canonical implementation.
