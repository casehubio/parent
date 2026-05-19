---
id: PP-20260518-837246
title: "MessageObserver implementations — any normal CDI scope is valid"
type: rule
scope: repo
applies_to: "casehub-qhorus — any class implementing MessageObserver"
severity: info
refs:
  - docs/repos/casehub-qhorus.md
resolved: 2026-05-19
resolved_by: qhorus#167
---

**Resolved in qhorus#167 (2026-05-19).** `MessageObserverDispatcher` now calls
`observers.handles()` and closes each `Instance.Handle` in a `finally` block.
`@Dependent`-scoped implementations are correctly destroyed after each dispatch.
Any normal CDI scope (`@ApplicationScoped`, `@RequestScoped`, `@Dependent`, etc.)
is valid for `MessageObserver` implementations.

The former constraint (`@ApplicationScoped` required) is retired.
