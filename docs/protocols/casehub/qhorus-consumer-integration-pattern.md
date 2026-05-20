---
id: PP-20260520-mesh-dashboard
title: "Qhorus consumer integration: use QhorusDashboardService for dashboard consumers, not raw entity services"
type: rule
scope: platform
applies_to: "Any REST resource, scheduled task, or service in a consumer repo (claudony, devtown, aml, clinical) that reads or writes to Qhorus channels, instances, or messages"
severity: critical
refs:
  - claudony#119
  - qhorus#175
  - qhorus#176
created: 2026-05-20
---

## Rule

Do not call `QhorusMcpTools` or `ReactiveQhorusMcpTools` from consumer service code.
Do not inject `ReactiveChannelService` / `ReactiveMessageService` directly for dashboard-style operations.

Inject `QhorusDashboardService` instead.

## Why the rule exists

`QhorusMcpTools` is the MCP protocol dispatch layer for Claude Code. Calling it from internal service code:
- Exposes `@WrapBusinessError` exception semantics (`ToolCallException` wrapping), forcing consumers to catch and unwrap
- Creates coupling to an external protocol layer that may evolve independently

"Inject entity services directly" sounds like the correct fix but is also wrong for dashboard consumers:
- `ReactiveChannelService.listAll()` returns raw `Channel` entities without message counts
- To build `ChannelView` (with count), the consumer must inject `ReactiveMessageStore` (store layer) directly — bypassing the service layer and creating a worse cross-layer coupling

## The three correct integration points

| Consumer type | Integration point |
|---|---|
| Dashboard / UI (needs composed views: count, tags, timeline) | `QhorusDashboardService` |
| Service-layer integration (SPI impls, background workers needing raw entities) | `ReactiveChannelService` / `ReactiveMessageService` |
| Reactive event-driven (reacting to new messages on a channel) | `ChannelBackend` or `MessageObserver` SPI |

## Violation hint

A REST resource or service bean imports from `io.casehub.qhorus.runtime.mcp.*` and calls `.await()` or uses `@Blocking` on tool methods — or injects `ReactiveMessageStore` alongside `ReactiveChannelService` to assemble composed views.

## Follow-on

- qhorus#175: move `ChannelView`, `InstanceView`, `HumanMessageResult` DTO types to `casehub-qhorus-api`
- qhorus#176: extract `toTimelineEntry` / `toChannelDetail` mapping to a shared `QhorusEntityMapper`
