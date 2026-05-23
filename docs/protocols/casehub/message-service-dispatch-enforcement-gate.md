---
id: PP-20260523-a08b97
title: "MessageService.dispatch() is the single enforcement gate for all channel writes — no caller may duplicate or bypass it"
type: rule
scope: repo
applies_to: "casehub-qhorus — any code that sends a message to a Qhorus channel"
severity: important
refs:
  - docs/specs/2026-05-23-dispatch-enforcement-design.md
violation_hint: "A caller (QhorusMcpTools, A2AChannelBackend, a new integration, a test) adds its own paused check, ACL check, rate-limit check, or fanOut call before or after calling dispatch(). Or a caller bypasses dispatch() entirely and calls messageStore.put() directly to avoid enforcement."
created: 2026-05-23
---

`MessageService.dispatch(MessageDispatch)` is the sole location for channel write enforcement in casehub-qhorus. Paused check, writer ACL (`AllowedWritersPolicy`), rate limiting (`RateLimiter`), LAST_WRITE overwrite semantics, and `ChannelGateway.fanOut()` all run inside `dispatch()` — in that order, before the message is persisted. Every caller — MCP tools, A2A backends, human backends, tests — calls `dispatch()` and receives full enforcement automatically. Adding enforcement in a caller is always wrong: it creates a parallel code path that will diverge, and any future caller added without copying the enforcement will silently bypass it. MCP-specific concerns (artefact lifecycle, deadline assignment, content format validation) are the only concerns that remain in `QhorusMcpTools.sendMessage()` — these are not enforcement, they are MCP-layer enrichment. See the referenced spec for the full enforcement sequence and the rationale for placing each concern in `dispatch()` rather than in callers.
