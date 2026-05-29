---
id: PP-20260529-eb19c3
title: "Qhorus service classes must query through store interfaces — never Panache static calls"
type: rule
scope: repo
applies_to: "casehub-qhorus — any @ApplicationScoped service that needs data from Channel, Message, Commitment, Instance, Watchdog, or SharedData entities"
severity: important
refs:
  - docs/specs/2026-05-28-watchdog-store-seam-design.md
violation_hint: "A service method calls Commitment.list(...), Instance.list(...), Message.count(...), or any other Panache entity static directly instead of injecting and calling the corresponding *Store interface."
created: 2026-05-29
---

Services in casehub-qhorus inject `*Store` interfaces (`CommitmentStore`, `InstanceStore`, `MessageStore`, `WatchdogStore`, `ChannelStore`, `DataStore`) and call their methods exclusively. Direct Panache static calls (`Entity.list(...)`, `Entity.count(...)`, `Entity.find(...)`) are forbidden in service classes. Direct calls bypass the persistence seam: `@Alternative @Priority(1)` InMemory stores are never invoked, so tests cannot swap the implementation, and the service is permanently coupled to JPA. The `testing` module's `InMemory*Store` beans only substitute cleanly when all data access flows through the interface.
