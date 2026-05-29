---
id: PP-20260529-457e5f
title: "ClaudonyChannelBackend registration must go through ChannelInitialisedEvent"
type: rule
scope: repo
applies_to: "claudony-app; any code that registers ClaudonyChannelBackend in ChannelGateway"
severity: important
refs:
  - docs/superpowers/specs/2026-05-29-fleet-channel-backend-delivery-design.md
violation_hint: "Direct gateway.registerBackend() or gateway.deregisterBackend() calls targeting ClaudonyChannelBackend.BACKEND_ID outside of the observer method"
created: 2026-05-29
---

`ClaudonyChannelBackend` must self-register via `@Observes ChannelInitialisedEvent` exclusively. No other code path should call `gateway.registerBackend()` for this backend. `ChannelInitialisedEvent` fires whenever `gateway.initChannel()` is called — at startup (all persisted channels) and on new channel creation — giving a single, idempotent registration path. Direct `registerBackend()` calls bypass fleet propagation: when Node A registers explicitly, Node B's gateway never learns about the channel; when Node A uses `initChannel()`, the event fires, the observer runs, and `ChannelSyncResource` propagates it to peers.
