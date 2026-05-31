---
id: PP-20260530-b7b3be
title: "Both eidos renderers must inject ReactiveRenderedPromptCache — not RenderedPromptCache"
type: rule
scope: repo
applies_to: "EidosSystemPromptRenderer, DefaultReactiveSystemPromptRenderer, any future SystemPromptRenderer implementation in casehub-eidos"
severity: important
refs:
  - ../../repos/casehub-eidos.md
violation_hint: "A renderer injects RenderedPromptCache directly. When the user provides an @Alternative @Priority(1) ReactiveRenderedPromptCache (e.g. Redis), the renderer that still uses RenderedPromptCache sees a different backing store — cache entries written by one path are invisible to the other."
created: 2026-05-30
---

`ReactiveRenderedPromptCache` is the canonical cache SPI in casehub-eidos. Both `EidosSystemPromptRenderer` (blocking) and `DefaultReactiveSystemPromptRenderer` (reactive) must inject `ReactiveRenderedPromptCache` directly. The blocking renderer calls `.await().atMost(Duration.ofSeconds(5))` on it — safe, because it runs on the worker pool. `RenderedPromptCache` (blocking) stays in `api/` as a convenience SPI for simple implementations; a `BlockingToReactiveRenderedPromptCacheAdapter @DefaultBean` bridges it automatically. This guarantees that when a user provides an alternative cache implementation (in-memory LRU, Redis), both renderers see the same backing store. A renderer that bypasses this by injecting `RenderedPromptCache` directly creates a split-brain cache when any `@Alternative ReactiveRenderedPromptCache` is installed.
