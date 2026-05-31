---
id: PP-20260529-35f3bd
title: "Foundation extension LLM pass must have a format-specific structural fallback"
type: rule
scope: platform
applies_to: "Any casehub Foundation extension that adds an optional LLM enrichment step to a rendering or generation SPI"
severity: important
refs:
  - ../../repos/casehub-eidos.md
violation_hint: "Structural path always produces CLAUDE_MD-structured output regardless of the requested RenderFormat, or structural path is removed entirely, making the extension non-functional without a configured LLM."
created: 2026-05-28
---

When a Foundation extension adds an optional LLM enrichment pass to a rendering SPI (e.g. `SystemPromptRenderer`, `CapabilityNarrativeGenerator`), the structural fallback path must produce correct, format-specific output for every declared output format — not just the primary format. The LLM pass is an enhancement; the extension must function correctly without any LLM configured, and the structural output must honour the caller's requested format. Extensions that produce CLAUDE_MD-structured output regardless of format when no LLM is present are violating this rule.
