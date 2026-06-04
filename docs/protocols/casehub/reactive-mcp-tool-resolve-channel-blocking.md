---
id: PP-20260604-995096
title: "Reactive @Tool methods that call resolveChannel() must carry @Blocking"
type: rule
scope: repo
applies_to: "casehub-qhorus — ReactiveQhorusMcpTools and any future reactive MCP tool class that inherits QhorusMcpToolsBase"
severity: important
refs:
  - docs/protocols/casehub/qhorus-channel-dual-identity.md
violation_hint: "A reactive @Tool method returns Uni<T> without @Blocking, but calls resolveChannel() in its body — either directly or via a pattern like 'UUID channelId = resolveChannel(channel)'. No compile error or runtime exception; symptom is Vert.x blocked-thread warning in logs and latency stall under load."
created: 2026-06-04
garden_ref: "GE-20260604-96d82a"
---

`QhorusMcpToolsBase.resolveChannel(String channel)` performs blocking JPA lookups (`ChannelService.findById()` / `findByName()`) to accept either UUID or channel name. quarkus-mcp-server dispatches `@Tool` methods on the Vert.x I/O thread by default — calling a blocking JPA method from the I/O thread stalls it silently (no exception; only a Vert.x blocked-thread warning). Any reactive `@Tool` method in `ReactiveQhorusMcpTools` (or any subclass of `QhorusMcpToolsBase`) that calls `resolveChannel()` must carry `@Blocking` to ensure the method executes on a worker thread where JPA is safe. The `Uni<T>` return type is still correct — `@Blocking` does not change the return type, only the dispatch thread. Reference implementations: `project_channel` and `set_channel_type_constraints` in `ReactiveQhorusMcpTools`. See GE-20260604-96d82a for the gotcha diagnosis.
