---
id: PP-20260519-5f6d9f
title: "Claudony SPI implementations must use reactive variants when casehub-engine provides them"
type: rule
scope: repo
applies_to: "claudony-casehub — all WorkerContextProvider, WorkerProvisioner, CaseChannelProvider implementations"
severity: critical
refs:
  - plans/2026-05-18-io-thread-safety.md
violation_hint: "Implementing WorkerContextProvider (blocking) instead of ReactiveWorkerContextProvider when CaseContextChangedEventHandler.tryProvision() runs on the Vert.x IO thread — causes BlockingOperationNotAllowedException in production"
created: 2026-05-19
---

casehub-engine's `CaseContextChangedEventHandler` runs on the Vert.x IO thread via `@ConsumeEvent`. It injects `ReactiveWorkerContextProvider` and `ReactiveWorkerProvisioner` (the reactive SPIs). Any Claudony implementation of the blocking variants (`WorkerContextProvider`, `WorkerProvisioner`, `CaseChannelProvider`) will never be called by the engine — and if they are called from any IO thread context they will throw `BlockingOperationNotAllowedException`. Claudony must implement the `Reactive*` SPI interfaces, offloading blocking work (JPA, tmux `ProcessBuilder`, Qhorus service calls) to `Infrastructure.getDefaultWorkerPool()` via `runSubscriptionOn()`. See `ClaudonyReactiveWorkerContextProvider`, `ClaudonyReactiveWorkerProvisioner`, `ClaudonyReactiveCaseChannelProvider` as reference implementations from #115.
