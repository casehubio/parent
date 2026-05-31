---
id: PP-20260531-ext-api-deep-dive
title: "External API surface belongs in the deep-dive, not deferred to DESIGN.md"
type: rule
scope: platform
applies_to: "Any casehubio repo whose deep-dive (docs/repos/<repo>.md in parent) defers API surface facts to an internal doc"
severity: important
refs:
  - ../../PLATFORM.md
violation_hint: "docs/repos/<repo>.md says 'See docs/DESIGN.md for message types / SPI contracts / tool names' without stating those facts directly"
created: 2026-05-31
---

DESIGN.md is an internal architecture document — it documents how a repo is built.
The deep-dive (`docs/repos/<repo>.md` in casehubio/parent) is the cross-repo discovery
document — it documents what a repo exposes.

Type vocabulary, SPI interface signatures, and MCP tool names must be enumerated directly
in the deep-dive. Pointers like "see DESIGN.md for message types" are not acceptable —
they require the reader to clone and open a separate repo.

Any branch that adds, renames, or removes an external API surface element (a `MessageType`
variant, an SPI method, a store SPI, an MCP tool name) must update the deep-dive before
closing. The implementation-doc-sync skill enforces this at session end.
