---
id: PP-20260531-32efe8
title: "Numeric InboundMessage metadata keys must always be present — never absent when zero"
type: rule
scope: repo
applies_to: "casehub-connectors — all InboundConnector and WebhookInboundConnector implementations that write numeric metadata"
severity: important
refs:
  - ../../repos/casehub-connectors.md
  - inbound-connector-id-is-type-not-account.md
violation_hint: "A connector that omits 'attachment-count' when there are no attachments, requiring observers to use containsKey() rather than parsing the value directly"
created: 2026-05-31
---

`InboundMessage.metadata` keys with numeric/countable semantics must always be written as parseable string integers, even when the value is zero (e.g. `"attachment-count" → "0"`). Keys must never be omitted to signal "zero" — absence must not carry semantic meaning for numeric keys. This gives observers a consistent contract: `Integer.parseInt(metadata.get("attachment-count"))` always works without a prior `containsKey()` check, and routing logic can branch on the count value rather than its presence. The reference case is `attachment-count` written by `EmailInboundConnector.buildMetadata()` for every message regardless of whether attachments are present.
