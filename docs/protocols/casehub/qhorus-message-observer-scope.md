---
id: PP-20260518-837246
title: "MessageObserver implementations must be @ApplicationScoped, never @Dependent"
type: rule
scope: repo
applies_to: "casehub-qhorus — any class implementing MessageObserver"
severity: important
refs:
  - docs/repos/casehub-qhorus.md
violation_hint: "@Dependent MessageObserver bean obtained via Instance<MessageObserver> is never destroyed — leaks on every message persisted."
created: 2026-05-18
---

`MessageObserver` implementations registered as CDI beans must use `@ApplicationScoped` (or another normal scope). The `MessageObserverDispatcher` iterates `Instance<MessageObserver>` without calling `Instance.handles()` or `Instance.destroy()`, so `@Dependent` beans obtained during iteration are never destroyed and accumulate indefinitely — one leaked bean instance per persisted message. Proper lifecycle management via `Instance.handles()` is tracked in qhorus#167 and deferred; until it ships, `@ApplicationScoped` is the required scope for all observers. This applies to `InProcessMessageBus` (already correct) and any consumer-supplied observer.
