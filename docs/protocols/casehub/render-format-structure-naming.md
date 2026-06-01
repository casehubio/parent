---
id: PP-20260531-60dc12
title: "RenderFormat enum values must name output structure, not LLM provider"
type: rule
scope: repo
applies_to: "SystemPromptRenderer.RenderFormat in casehub-eidos-api; any future output format enum in casehub-eidos"
severity: important
refs:
  - ../../repos/casehub-eidos.md
violation_hint: "A format value is named after a provider (e.g. CLAUDE_MD, OPENAI_SYSTEM, GEMINI) rather than output structure — or two format values produce structurally identical output and differ only by a micro-styling choice."
created: 2026-05-31
---

`RenderFormat` enum members describe the structure of the rendered output, not the LLM provider consuming it: `MARKDOWN` (rich markdown), `PROSE` (dense flowing paragraphs), `A2A_CARD` (JSON). Provider-named values (CLAUDE_MD, OPENAI_SYSTEM, GEMINI) cause enum explosion — every new LLM target requires a new member even when it produces structurally identical output to an existing one. Provider-specific rendering differences (rubric strictness, resource citation format) belong in the assembly method or evaluator prompt, not in the format type. When a proposed new format value is structurally identical to an existing one except for a micro-styling detail, collapse them into the existing value and handle the detail in the implementation. Sub-labels (e.g. `PROSE_OPENAI`) may be added if and only if concrete structural differences — not cosmetic ones — emerge.
