---
id: PP-20260529-7b94ab
title: "Pull-based and webhook-based inbound connectors must use distinct types — no unified SPI"
type: rule
scope: repo
applies_to: "casehub-connectors — any module implementing inbound message transport"
severity: important
refs:
  - ../../repos/casehub-connectors.md
  - ../../docs/specs/2026-05-29-inbound-connector-spi-design.md
violation_hint: "A webhook connector that implements InboundConnector and overrides start()/stop() as no-ops, or a pull connector that extends WebhookInboundConnector"
created: 2026-05-29
---

Pull-based connectors (IMAP polling, any transport that actively fetches messages on a schedule) implement `InboundConnector` — the interface carries `start(InboundMessageSink)` and `stop()` lifecycle methods managed by `InboundConnectorService` at Quarkus startup/shutdown. Webhook-based connectors (Slack, Teams, WhatsApp, Twilio SMS) extend `WebhookInboundConnector` — a standalone abstract class with no lifecycle methods, whose lifecycle is JAX-RS. The two types must not be unified: a unified interface would require webhook connectors to implement no-op `start()`/`stop()` methods, making the interface contract misleading and the `InboundConnectorService.onStart()` call semantically incorrect for webhook connectors. CDI discovers them through separate `@All List<InboundConnector>` and `@All List<WebhookInboundConnector>` injection points — this type-safe separation is intentional and must not be collapsed.
