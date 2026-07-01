# casehub-connectors

**GitHub:** [casehubio/connectors](https://github.com/casehubio/connectors)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Outbound and inbound message connector library for the casehubio platform. Provides a `Connector` CDI SPI (outbound) and `InboundConnector`/`WebhookInboundConnector` SPIs (inbound) with built-in implementations for Slack, Teams, Twilio SMS, WhatsApp, email (outbound), and email inbound (IMAP polling). Also provides a `ChatPlatform` SPI for structured interaction with chat systems (channels, threads, reactions, presence, members, channel management, member management, message history) with graceful degradation across platforms. No Camel, no vendor SDKs — pure `java.net.http.HttpClient`.

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

### ChatPlatform SPI (`chat-spi`)

Structured interface for chat-system interactions beyond simple message delivery. Defines capability interfaces: `Messaging`, `Threading`, `Discovery`, `Reactions`, `Presence`, `Members`, `ChannelManagement`, `MemberManagement`, `MessageHistory`. Each platform declares which capabilities it supports; unsupported capabilities degrade gracefully (no-op or fallback). Implementations: `chat-ref` (in-memory reference), `chat-irc`, `chat-discord` (8 native capabilities), `chat-slack` (9 native capabilities — most complete).

### RichCard (`chat-spi`)

Platform-agnostic rich content model. Record with title, description, url, color (decimal RGB), fields (name/value/inline), thumbnailUrl, imageUrl, footer, author — plus a Builder. `ChatContent.cards()` carries `List<RichCard>`. Outbound: translators render RichCard to platform-native formats (Discord embeds, Slack Block Kit blocks). Inbound: translators parse platform-native rich content (Discord embeds, Slack blocks) back into RichCard objects. `Channel` includes `memberCount` (nullable Integer) populated from guild/workspace metadata.

### Module Structure

| Module | Contents |
|--------|----------|
| `casehub-connectors` (`casehub-connectors-core`) | `Connector` SPI + Slack, Teams, Twilio SMS, WhatsApp outbound impls; `InboundConnector` SPI + `InboundConnectorService` polling engine; `WebhookInboundConnector` abstract base. `ConnectorDiscovery` SPI (connectors#16) — optional interface CDI beans implement when their targets are discoverable (e.g. Slack channels via `conversations.list`); `connectorId()` + `discover() → List<DiscoveredTarget>`. `ConnectorsCloudEventAdapter` — CDI adapter observing `@ObservesAsync InboundMessage`, fires `Event<CloudEvent>.fireAsync()` with type `io.casehub.connectors.inbound.<connectorType>`. Follows canonical CloudEvent adapter pattern (GE-20260621-629712). |
| `casehub-connectors-email` | SMTP outbound via `quarkus-mailer` |
| `casehub-connectors-email-inbound` | `EmailInboundConnector` — IMAP polling, `EmailInboundAccountProvider` SPI |
| `casehub-connectors-mcp` | MCP tool surface: `send_slack`, `send_teams`, `send_sms`, `send_whatsapp`, `send_email`, `send_chat` (cross-platform chat via ChatPlatformService — replaces per-platform tools for chat, supports RichCard and multi-card), `list_channels` (aggregates ConnectorDiscovery), `list_chat_channels` (ChatPlatform Discovery with rich Channel detail including memberCount). Integrates with Qhorus via `ConnectorMeshBridge` SPI. |
| `casehub-connectors-slack-bot` | `SlackBotClient` — pure `java.net.http` client for the Slack Web API (14 methods: messaging, channel listing, reactions, presence, members, users, channel management, member management, message history). Block Kit `blocks` parameter on `postMessage`. `ConversationInfo` includes `numMembers`. Paginating methods use generic `paginateGet<T>` helper with fail-soft partial results. |
| `casehub-connectors-discord` | `DiscordClient` (REST API v10 + Gateway WebSocket + CDN attachment download with SSRF defense + rich embed serialization). `DiscordGuild` with nullable `approximateMemberCount`. Pure `java.net.http`. |
| `casehub-connectors-chat-spi` | ChatPlatform SPI, capability interfaces, `RichCard` model with Builder, `ChatContent`, `Channel` (with `memberCount`), `ReceivedMessage`. |
| `casehub-connectors-chat-ref` | In-memory reference ChatPlatform implementation for testing. |
| `casehub-connectors-chat-discord` | Discord ChatPlatform — 8 native capabilities. RichCard → DiscordEmbed translation (outbound), embed → RichCard parsing (inbound). |
| `casehub-connectors-chat-slack` | Slack ChatPlatform — 9 native capabilities (most complete). RichCard → Block Kit translation (outbound), blocks → RichCard parsing (inbound). Batch user fetch for members, full ts-precision message history. |
| `casehub-connectors-chat-irc` | IRC ChatPlatform — 3 native capabilities. |
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

Nothing in the casehubio ecosystem. Core module: `java.net.http.HttpClient`, `cloudevents-core` (CNCF CloudEvents SDK), `jackson-databind`. Optional modules: `quarkus-mailer` (email outbound), `jakarta.mail` (email inbound).

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
