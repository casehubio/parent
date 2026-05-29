---
id: PP-20260529-68c422
title: "Fleet HTTP clients must register FleetKeyClientFilter on RestClientBuilder, not via @RegisterProvider"
type: rule
scope: repo
applies_to: "claudony-app; any code building a PeerClient via RestClientBuilder.newBuilder()"
severity: important
refs:
  - docs/superpowers/specs/2026-05-29-fleet-channel-backend-delivery-design.md
violation_hint: "RestClientBuilder.newBuilder() call that does not explicitly call .register(FleetKeyClientFilter.class) before .build()"
created: 2026-05-29
---

Every peer-to-peer HTTP call in Claudony that needs fleet authentication must register `FleetKeyClientFilter` explicitly on the builder: `.register(FleetKeyClientFilter.class)`. `@RegisterProvider(FleetKeyClientFilter.class)` on the `PeerClient` interface is silently ignored by `RestClientBuilder.newBuilder()` — the filter annotation only applies to CDI-managed injection, not to dynamically constructed clients. Without explicit registration, the `X-Fleet-Key` header is never added and the peer returns 401. See garden entry GE-20260415-dfa8ba.
