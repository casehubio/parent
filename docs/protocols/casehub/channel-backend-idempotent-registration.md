---
id: PP-20260601-4fa0b2
title: "ChannelBackend implementations must deregister before registering in ChannelInitialisedEvent observer"
type: rule
scope: platform
applies_to: "Any class implementing ChannelBackend and observing ChannelInitialisedEvent to self-register"
severity: important
refs:
  - docs/protocols/casehub/claudony-channel-backend-registration-path.md
violation_hint: "Calling gateway.registerBackend() without a preceding gateway.deregisterBackend() in an @Observes ChannelInitialisedEvent method — causes duplicate backend entries if initChannel() is called more than once for the same channel (e.g. startup recovery + channel re-init)"
created: 2026-06-01
---

`ChannelInitialisedEvent` fires on every `ChannelGateway.initChannel()` call — at startup recovery (all persisted channels) and on new channel creation or re-binding. Any `ChannelBackend` that self-registers via `@Observes ChannelInitialisedEvent` must call `gateway.deregisterBackend(channelId, BACKEND_ID)` before `gateway.registerBackend(...)`. The deregister is a no-op when the backend isn't registered yet, making the pattern safe on first registration and idempotent on all subsequent calls. Skipping the deregister causes the backend to accumulate duplicate entries in the `ChannelGateway` registry, leading to fan-out delivering the same message multiple times.
