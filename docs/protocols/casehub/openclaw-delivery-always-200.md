---
id: PP-20260603-d52060
title: "OpenClaw delivery endpoints always return 200 — never let the agent runtime retry"
type: rule
scope: repo
applies_to: "casehub-openclaw — any @Path('/openclaw/delivery/*') or '/openclaw/plugin/*' endpoint"
severity: important
refs:
  - docs/specs/openclaw-integration.md
violation_hint: "A delivery endpoint returns 4xx or 5xx on exception — OpenClaw retries, causing double dispatch to Qhorus or a partially-fulfilled gate to be re-attempted."
created: 2026-06-03
---

Every HTTP endpoint that receives an OpenClaw callback (`/openclaw/delivery/channel/{channelId}`, `/openclaw/delivery/oversight/{gateId}`, `/openclaw/plugin/commit`, `/openclaw/plugin/done`) must return HTTP 200 on all paths, including processing failures. OpenClaw treats any non-200 response as a delivery failure and retries — on a gate endpoint this would re-invoke `OversightGateService.fulfill()` on a Commitment that may already be partially processed; on a channel endpoint it would dispatch a duplicate message to Qhorus. Implementations achieve this by wrapping all processing in a `try/catch` that logs the exception and returns `Response.ok()` rather than propagating to Quarkus's default exception mapper.
