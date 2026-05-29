---
id: PP-20260529-e418f0
title: "Fleet key must grant fleet role, not user role"
type: rule
scope: repo
applies_to: "claudony-app; ApiKeyAuthMechanism"
severity: critical
refs:
  - docs/superpowers/specs/2026-05-29-fleet-channel-backend-delivery-design.md
violation_hint: "ApiKeyAuthMechanism fleet key branch calling addRole(\"user\") instead of addRole(\"fleet\")"
created: 2026-05-29
---

`ApiKeyAuthMechanism` must grant `addRole("fleet")` — not `addRole("user")` — when the fleet key authenticates. The `fleet` role gates fleet-internal endpoints (`@RolesAllowed("fleet")`, e.g. `ChannelSyncResource`) while keeping peers out of human-session endpoints that use `@Authenticated` with a `user` role expectation. Granting `user` to fleet callers would allow a peer node to call any human-session endpoint as if it were a human operator, violating the trust boundary between peer-to-peer fleet calls and browser/agent sessions.
