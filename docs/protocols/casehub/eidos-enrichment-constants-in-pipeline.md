---
id: PP-20260529-b83bf1
title: "Enrichment step constants shared between blocking and reactive paths belong in EidosRenderPipeline"
type: rule
scope: repo
applies_to: "Any new enrichment step added to casehub-eidos (blocking or reactive)"
severity: important
refs:
  - ../casehub-eidos.md
violation_hint: "A new enrichment step declares its own PROMPT_TEMPLATE, RESPONSE_FORMAT, or STREAMING_TIMEOUT_SECONDS constant instead of referencing EidosRenderPipeline.*."
created: 2026-05-29
---

`EidosRenderPipeline` is the single source of truth for all enrichment constants shared between blocking and reactive implementations: `PROMPT_TEMPLATE`, `TEMPLATE_HASH`, `RESPONSE_FORMAT`, `A2A_PROMPT_TEMPLATE`, `A2A_RESPONSE_FORMAT`, and `STREAMING_TIMEOUT_SECONDS`. When adding a new enrichment step (blocking or reactive), reference `EidosRenderPipeline.CONSTANT_NAME` — never declare a local copy. Duplication between `SemanticEnrichmentStep` / `ReactiveSemanticEnrichmentStep` (and A2A equivalents) caused drift risk that was eliminated in eidos#17; any new enrichment concern must follow the same pattern.
