---
id: PP-20260529-368527
title: "Format-specific LLM enrichment concerns belong in a dedicated step with their own schema"
type: rule
scope: platform
applies_to: "Any casehub renderer that runs an LLM enrichment step shared across multiple output formats"
severity: important
refs:
  - llm-pass-structural-fallback.md
  - renderer-cache-key-includes-format.md
  - ../casehub-eidos.md
violation_hint: "A format-specific output field (e.g. per-capability prose only needed for A2A cards) is added to the shared enrichment schema, causing the LLM to generate and discard that content on every render of unrelated formats."
created: 2026-05-29
---

When a rendering SPI has a shared LLM enrichment step used across multiple output formats, format-specific enrichment fields must not be added to the shared schema. Adding such fields forces the LLM to generate content that is discarded for all formats that do not use it — wasting tokens and latency proportional to agent capability count on every render. The fix: create a dedicated enrichment step with its own schema, its own prompt template, and a payload scoped to the data the format actually needs (e.g. descriptor-only for A2A cards, which are context-independent). Each enrichment concern is a distinct step; the shared step covers only what every format uses. Complements `llm-pass-structural-fallback` (PP-20260529-35f3bd) and `renderer-cache-key-includes-format` (PP-20260529-5c883f).
