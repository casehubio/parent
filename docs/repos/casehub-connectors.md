# casehub-connectors

**GitHub:** [casehubio/connectors](https://github.com/casehubio/connectors)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Outbound and inbound message connector library for the casehubio platform. Provides a `Connector` CDI SPI (outbound) and `InboundConnector`/`WebhookInboundConnector` SPIs (inbound) with built-in implementations for Slack, Teams, Twilio SMS, WhatsApp, email (outbound), and email inbound (IMAP polling). No Camel, no vendor SDKs — pure `java.net.http.HttpClient`.

This is the **canonical notification infrastructure** for the platform. Any repo that needs to send outbound messages (escalations, alerts, notifications) or receive inbound messages must use these SPIs rather than implementing its own connectors.

---

## Key Abstractions

### Outbound SPI — `Connector`

The `Connector` CDI SPI has two methods: an id accessor and a send method that takes a message with destination, title, and body. Custom connectors implement it as CDI beans — auto-discovered. See docs/DESIGN.md for method signatures and the ConnectorMessage type.

### ConnectorMeshBridge SPI (in `casehub-connectors-core`)

Called by MCP tools after successful delivery. No-op `@DefaultBean @Unremovable` default. Qhorus bridge implementation activates by classpath presence (qhorus#249) and posts `EVENT` to the active observe channel. Contract: must return quickly, never throw, tolerate absent case context.

### Inbound SPI — `InboundConnector` / `WebhookInboundConnector`

Two inbound SPIs:

- **`InboundConnector`** — pull-based polling (e.g. IMAP). `InboundConnectorService` polls all registered `InboundConnector` implementations on a configurable schedule and fires `Event<InboundMessage>` via **`fireAsync()`** — NOT `fire()`. At-least-once delivery. **Breaking contract:** observers MUST use `@ObservesAsync InboundMessage` — a synchronous `@Observes` observer will not receive events.
- **`WebhookInboundConnector`** — push-based webhook reception. Abstract base class; implementations register an HTTP endpoint that receives webhook payloads and normalises them to `InboundMessage`. Also fires via `Event.fireAsync()` — `@ObservesAsync` required.

Consumers observe `Event<InboundMessage>` and react accordingly — they never call inbound SPIs directly.

### Module Structure

| Module | Contents |
|--------|----------|
| `casehub-connectors` (`casehub-connectors-core`) | `Connector` SPI + Slack, Teams, Twilio SMS, WhatsApp outbound impls; `InboundConnector` SPI + `InboundConnectorService` polling engine; `WebhookInboundConnector` abstract base. `ConnectorDiscovery` SPI (connectors#16) — optional interface CDI beans implement when their targets are discoverable (e.g. Slack channels via `conversations.list`); `connectorId()` + `discover() → List<DiscoveredTarget>`. |
| `casehub-connectors-email` | SMTP outbound via `quarkus-mailer` |
| `casehub-connectors-email-inbound` | `EmailInboundConnector` — IMAP polling, `EmailInboundAccountProvider` SPI |
| `casehub-connectors-mcp` | MCP tool surface: `send_slack`, `send_teams`, `send_sms`, `send_whatsapp`, `send_email`, `send_slack_bot` (bot-token Slack posting via `SlackBotClient`, returns `ts` for thread replies), `list_channels` (aggregates all registered `ConnectorDiscovery` beans). Depends on `core` + `email` + `quarkus-mcp-server-core:1.11.1`. Consuming apps add `quarkus-mcp-server-http` for transport. Integrates with Qhorus via `ConnectorMeshBridge` SPI when `connector-backend` is on classpath (qhorus#249). |
| `casehub-connectors-slack-bot` | `SlackBotClient` — pure `java.net.http` client for the Slack Web API (`chat.postMessage`). Implements `ConnectorDiscovery` via `conversations.list` — registers Slack channels as discoverable targets for `list_channels` MCP tool. Config: `casehub.connectors.slack-bot.token` (bot token). No Slack SDK dependency (connectors#2). Also adds `InboundConnectorIds.SLACK_INBOUND = "slack-inbound"` constant and `slack-ts` / `slack-thread-ts` metadata fields to `casehub-connectors-core`. |
| `casehub-connectors-qhorus` | Optional — `WatchdogAlertEvent → ConnectorService.send()` bridge (Qhorus → connectors); activates by classpath presence |
| *(qhorus-side)* `casehub-qhorus-connector-backend` | Optional — `InboundMessage → ConnectorChannelBackend` bridge (connectors → Qhorus); lives in casehub-qhorus repo; activates by classpath presence |

### Built-in Implementations

**Outbound:**

| ID | Module | Auth |
|---|---|---|
| `slack` | `casehub-connectors` | Webhook URL in `destination` |
| `teams` | `casehub-connectors` | Webhook URL in `destination` |
| `twilio-sms` | `casehub-connectors` | Account SID + Auth Token in config |
| `whatsapp` | `casehub-connectors` | API Token + Phone Number ID in config. Template messages: `ConnectorMessage.attributes("templateName")` + `attributes("templateLanguage")` (default `en_US`). MCP surface exposes both as optional parameters. |
| `email` | `casehub-connectors-email` | SMTP via `quarkus-mailer` |

**Inbound:**

| ID | Module | Auth |
|---|---|---|
| `email-inbound` | `casehub-connectors-email-inbound` | IMAP username/password in MP Config |

### Configuration

Twilio and WhatsApp require account credentials in config. Slack and Teams webhook: no config — webhook URL is passed as the destination at call time. Email inbound: IMAP host, port, username, and password via MP Config.

| Property | Module | Purpose |
|---|---|---|
| `casehub.connectors.slack-bot.token` | `casehub-connectors-slack-bot` | Bot OAuth token for `chat.postMessage` and `conversations.list` |

---

## Depends On

Nothing in the casehubio ecosystem. Pure Java (`java.net.http.HttpClient`) + optional `quarkus-mailer` for email outbound + standard IMAP (`jakarta.mail`) for email inbound.

## Depended On By

| Repo | Expected usage |
|---|---|
| `casehub-engine` | Escalation and notification paths (not yet wired) |
| `casehub-work-notifications` | Should delegate to `casehub-connectors` rather than maintain its own Slack/Teams implementations |
| `casehub-qhorus` | Optional — `WatchdogAlertEvent → ConnectorService.send()` bridge activates by classpath presence |
| `casehub-life` | Household and care notifications (contractor alerts, carer escalations) |
| `casehub-qhorus` | `casehub-qhorus-slack-channel` (pending) — will depend on `casehub-connectors-slack-bot` for `SlackBotClient` |

---

## What This Repo Explicitly Does NOT Do

- Provide domain logic — purely delivery infrastructure
- Route or schedule notifications — callers decide when and what to send
- Depend on casehub-work, casehub-ledger, or casehub-engine

---

## Notification Consolidation Rule

**Do not implement a new Slack, Teams, SMS, email, or inbound connector in any other repo.** All outbound and inbound messaging routes through these SPIs. If a new channel type is needed, add it here.

`casehub-work-notifications` currently has parallel Slack/Teams implementations — this is a known overlap risk and should be resolved by delegating to `casehub-connectors`.

---

## Current State

- Multiple shipped epics — connectors#4 (webhook inbound SPI), connectors#7 (email inbound)
- Published to GitHub Packages at `0.2-SNAPSHOT`
- GroupId: `io.casehub`
- Not yet wired into casehub-engine or casehub-work escalation paths
