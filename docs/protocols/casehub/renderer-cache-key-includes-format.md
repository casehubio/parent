---
id: PP-20260529-5c883f
title: "Renderer cache keys must include the output format dimension"
type: rule
scope: platform
applies_to: "Any casehub component that caches format-specific rendered output (system prompts, A2A cards, OpenAI system messages)"
severity: important
refs:
  - ../../repos/casehub-eidos.md
violation_hint: "Cache key is derived from descriptor + context alone. Two render calls with the same descriptor and context but different RenderFormat values return the same cache entry, serving the wrong format to one caller."
created: 2026-05-28
---

When a renderer caches output that is format-specific (CLAUDE_MD, OPENAI_SYSTEM, A2A_CARD, etc.), the cache key must include the `RenderFormat` dimension. A key that encodes only the semantic input (descriptor hash, context hash, template version) is insufficient: the same semantic input produces structurally different output for each format. Callers requesting OPENAI_SYSTEM must not receive cached CLAUDE_MD content. The canonical cache key is: `descriptorHash + ":" + contextHash + ":" + format.name() + ":" + templateVersion`.
