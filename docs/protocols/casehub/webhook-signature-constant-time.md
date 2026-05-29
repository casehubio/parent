---
id: PP-20260529-b7765c
title: "All webhook HMAC signature verification must use MessageDigest.isEqual() — never String.equals() or Arrays.equals()"
type: rule
scope: platform
applies_to: "Any casehub module that verifies inbound webhook signatures (casehub-connectors-webhook and any future webhook-receiving module)"
severity: critical
refs:
  - ../../docs/specs/2026-05-29-inbound-connector-spi-design.md
violation_hint: "signature.equals(computed) or Arrays.equals(expected, actual) in any HMAC verification path"
created: 2026-05-29
---

HMAC signature verification for inbound webhooks (Slack, Teams, WhatsApp, Twilio, or any future platform) must use `MessageDigest.isEqual(expected, actual)` for byte array comparison. `String.equals()` and `Arrays.equals()` return early on the first mismatch, leaking comparison time proportional to the number of matching bytes — a timing attack that allows an adversary to recover the expected HMAC incrementally by measuring response latency. `MessageDigest.isEqual()` runs in constant time regardless of where the first mismatch occurs. Both sides must be byte arrays of the same encoding before comparison; avoid converting to hex strings for comparison unless using a constant-time hex equality function. This rule applies to all four current connectors (Slack HMAC-SHA256, Teams HMAC-SHA256, WhatsApp X-Hub-Signature-256, Twilio HMAC-SHA1) and any connector added in future. Complements `ledger-algorithm-transparent-signing.md` (which governs algorithm derivation for signing, not verification comparison).
