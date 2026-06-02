---
id: PP-20260602-b748c9
title: "Event-log left-fold projection — derive channel read-models as a pure fold"
type: rule
scope: platform
applies_to: "Any casehubio consumer building a read-model, summary, or digest from Qhorus channel message history"
severity: guidance
refs:
  - ../../repos/casehub-qhorus.md
violation_hint: "Consumer implements its own channel-reading loop, file-based parser, or ad-hoc messageStore.scan() iteration instead of ChannelProjection<S>"
created: 2026-06-02
---

Use `ProjectionService.project(channelId, ChannelProjection<S>)` to derive a deterministic
read-model from a channel's message history. A `ChannelProjection<S>` is a pure left-fold:
`identity()` returns a fresh empty state; `apply(S, MessageView)` folds one message and
returns the next state. The result is a `ProjectionResult<S>` carrying the materialised state
and a cursor (`lastMessageId`) for incremental re-projection — pass it back as `previous` to
fold only new messages without replaying the full history. Consumers that write ad-hoc channel
readers, local file parsers, or manual scan loops bypass the fold abstraction and should
migrate to `ChannelProjection<S>` when Qhorus is on the classpath.
