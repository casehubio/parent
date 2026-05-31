---
id: PP-20260529-8e5948
title: "InboundMessage.connectorId must be the connector type string — never an account-level or instance-level id"
type: rule
scope: repo
applies_to: "casehub-connectors — all InboundConnector and WebhookInboundConnector implementations"
severity: important
refs:
  - inbound-connector-type-separation.md
  - ../../repos/casehub-connectors.md
violation_hint: "An InboundConnector implementation that sets connectorId to an account id, mailbox name, or any value that varies across instances of the same connector type (e.g. 'email-inbound-support' instead of 'email-inbound')"
created: 2026-05-29
---

`InboundMessage.connectorId` is a connector type discriminator — it identifies which connector class produced the message, not which account or instance. Observers branch on `connectorId` (e.g. `connectorId.equals("email-inbound")`) to select their handler; a per-account id would require prefix-matching and silently miss messages from accounts with unexpected naming. When a connector manages multiple accounts (e.g. `EmailInboundConnector` polling multiple IMAP mailboxes), `connectorId` remains the connector type string (e.g. `"email-inbound"`), and per-account identity is carried in `InboundMessage.metadata["account-id"]`. This rule extends PP-20260529-7b94ab (pull-based vs webhook type separation) to cover the connectorId field contract.
