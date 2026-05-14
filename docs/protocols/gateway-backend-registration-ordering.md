---
id: PP-20260514-c80d4c
title: "Call open() before registerBackend() when registering a ChannelBackend"
type: rule
scope: repo
applies_to: "Any code that calls ChannelGateway.registerBackend() directly — e.g. A2AChannelBackend.ensureRegistered(), custom backend wiring"
severity: important
refs:
  - runtime/src/main/java/io/casehub/qhorus/runtime/gateway/ChannelGateway.java
  - runtime/src/main/java/io/casehub/qhorus/runtime/api/A2AChannelBackend.java
violation_hint: "registerBackend() called before open() — fanOut() may dispatch to the backend before it has completed initialisation"
created: 2026-05-14
---

When manually registering a ChannelBackend via `gateway.registerBackend()`, always
call `backend.open(ref, metadata)` first. This matches the ordering in
`ChannelGateway.initChannel()`, which calls `agentBackend.open()` before adding the
backend to the registry. Reversing the order creates a window where `fanOut()` can
dispatch to the backend before `open()` has completed — safe today because `open()`
is a no-op for most backends, but a latent hazard for any backend that uses `open()`
for real initialisation (e.g. establishing a connection, registering SSE listeners).
