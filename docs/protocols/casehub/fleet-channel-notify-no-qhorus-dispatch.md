---
id: PP-20260530-9d18a0
title: "Fleet channel notify endpoint must call ChannelEventBus.emit() directly — never re-enter Qhorus dispatch"
type: rule
scope: repo
applies_to: "claudony-app; any fleet endpoint that handles cross-node channel message delivery"
severity: critical
refs:
  - app/src/main/java/io/casehub/claudony/server/fleet/ChannelSyncResource.java
  - docs/superpowers/specs/2026-05-30-cluster-message-observer-fleet-tick-relay-design.md
violation_hint: "Fleet notify endpoint calling MessageService.dispatch() or ReactiveMessageService.dispatch() rather than channelEventBus.emit() directly"
created: 2026-05-30
---

The fleet tick relay loop invariant: when Node B's FleetMessageRelayObserver relays a channel-name tick to Node A via POST /api/internal/channels/notify, Node A's endpoint must call ChannelEventBus.emit() directly — never MessageService.dispatch() or any other Qhorus write path. Routing through Qhorus dispatch would fire Node A's own FleetMessageRelayObserver, which would relay back to Node B, creating an unbounded relay loop. ChannelEventBus.emit() is a pure in-process SSE tick with no observers — the loop cannot form.
