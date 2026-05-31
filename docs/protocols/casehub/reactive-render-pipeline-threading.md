---
id: PP-20260529-cd4646
title: "Reactive eidos renderers must follow the three-stage threading pattern"
type: rule
scope: repo
applies_to: "Any reactive SystemPromptRenderer or ReactiveSystemPromptRenderer implementation in casehub-eidos"
severity: important
refs:
  - ../../repos/casehub-eidos.md
  - reactive-spi-bridge-default-bean.md
violation_hint: "Stage 1 (payload build / cache check) runs on the event loop thread instead of the worker pool; or Stage 3 (format assembly) runs on the streaming callback thread without emitOn."
created: 2026-05-29
---

Reactive rendering in casehub-eidos must decompose into three stages with explicit thread routing: **Stage 1** (payload building, cache check) runs on the worker pool via `runSubscriptionOn(Infrastructure.getDefaultWorkerPool())` — JSON serialisation is non-trivial CPU work that must not block the event loop. **Stage 2** (LLM enrichment) must not hold any thread — use `StreamingChatModel` bridged to `Uni` via `CompletableFuture.orTimeout()` + `Uni.createFrom().completionStage()`. **Stage 3** (format assembly, cache write) must return to the worker pool via `.emitOn(Infrastructure.getDefaultWorkerPool())` before `.map()` — the streaming callback thread must not perform heavy computation. When no `StreamingChatModel` is available, fall back to `Uni.createFrom().item(() -> blockingDelegate.render(...)).runSubscriptionOn(workerPool)`.
