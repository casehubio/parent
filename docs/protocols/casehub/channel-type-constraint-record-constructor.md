---
id: PP-20260604-c19f7c
title: "All channel type constraints (allowedTypes / deniedTypes) must be validated in ChannelCreateRequest's compact constructor"
type: rule
scope: repo
applies_to: "casehub-qhorus — any code path that creates a channel with type restrictions"
severity: important
refs:
  - docs/specs/2026-06-03-denied-types-enforcement-design.md
violation_hint: "A caller (ChannelService overload, MCP tool, AutoChannelPolicy, test helper) validates allowedTypes or deniedTypes outside the ChannelCreateRequest compact constructor — e.g. via a static validateNoOverlap() call, a service-layer check, or an inline validation before calling the service."
created: 2026-06-04
---

`ChannelCreateRequest`'s compact constructor is the single enforcement gate (D1) for channel message-type constraints: type names are validated via `MessageType.parseTypes()` (throws `IllegalArgumentException` on unknown names) and the intersection `allowedTypes ∩ deniedTypes` is asserted empty. This gate fires on every construction path — MCP tools, `ChannelService` named-param overloads, `ReactiveChannelService`, `ConnectorChannelBackend.tryAutoCreate()`, and tests — with no caller bypass. Adding validation in a caller is always wrong: it creates a parallel code path that will drift, and any future caller added without copying the check will silently skip it. Package-cycle constraints make it impossible to centralise this logic in `StoredMessageTypePolicy` (which already imports `runtime/channel/Channel`) — the compact constructor is the only location that is reachable from all creation paths without introducing cycles.
