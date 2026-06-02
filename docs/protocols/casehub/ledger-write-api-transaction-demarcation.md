---
id: PP-20260602-a44c4e
title: "casehub-ledger write API outer methods must not be @Transactional — delegate to a separate @Transactional service"
type: rule
scope: repo
applies_to: "casehub-ledger — any combined write API (OutcomeRecorder, future incremental write APIs)"
severity: important
refs:
  - ../../repos/casehub-ledger.md
  - https://github.com/casehubio/ledger/issues/115
violation_hint: "A @DefaultBean @ApplicationScoped write service annotated @Transactional on its public record()/write() method — the transaction commits too late; async CDI observers fire before the writes are visible, producing silent data races."
created: 2026-06-02
---

Any combined write API in casehub-ledger (e.g. `OutcomeRecorder.record()`) must be implemented as a non-`@Transactional` outer method on a `@DefaultBean @ApplicationScoped` class, with the actual write logic delegated to a separate package-private `@ApplicationScoped @Transactional` service. The outer method owns the post-commit hook point — future async trust update observers (casehubio/ledger#115) will be invoked there, after the writes are committed. If `@Transactional` were placed on the outer method, the transaction would commit only when that method returns; any `Event.fire()` or post-write hook invoked before the return would read uncommitted data. The separate-service pattern ensures the commit point is precisely controlled: `delegate.save()` returning means the transaction is committed, and the outer method can safely invoke downstream CDI events or observers.
