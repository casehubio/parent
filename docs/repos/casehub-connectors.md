# casehub-connectors

**GitHub:** [casehubio/connectors](https://github.com/casehubio/connectors)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Lightweight outbound message connectors for the casehubio platform. Provides a unified `Connector` CDI SPI with built-in implementations for Slack, Teams, Twilio SMS, WhatsApp, and email. No Camel, no vendor SDKs — pure `java.net.http.HttpClient`.

This is the **canonical outbound notification infrastructure** for the platform. Any repo that needs to send outbound messages (escalations, alerts, notifications) must use this SPI rather than implementing its own connector.

---

## Key Abstractions

### SPI

The `Connector` CDI SPI has two methods: an id accessor and a send method that takes a message with destination, title, and body. Custom connectors implement it as CDI beans — auto-discovered. See docs/DESIGN.md for method signatures and the ConnectorMessage type.

### Built-in Implementations

| ID | Module | Auth |
|---|---|---|
| `slack` | `casehub-connectors` | Webhook URL in `destination` |
| `teams` | `casehub-connectors` | Webhook URL in `destination` |
| `twilio-sms` | `casehub-connectors` | Account SID + Auth Token in config |
| `whatsapp` | `casehub-connectors` | API Token + Phone Number ID in config |
| `email` | `casehub-connectors-email` | SMTP via `quarkus-mailer` |

### Configuration

Twilio and WhatsApp require account credentials in config. Slack and Teams: no config — webhook URL is passed as the destination at call time. See docs/DESIGN.md for configuration property names.

---

## Depends On

Nothing in the casehubio ecosystem. Pure Java (`java.net.http.HttpClient`) + optional `quarkus-mailer` for email.

## Depended On By

| Repo | Expected usage |
|---|---|
| `casehub-engine` | Escalation and notification paths (not yet wired) |
| `casehub-work-notifications` | Should delegate to `casehub-connectors` rather than maintain its own Slack/Teams implementations |

---

## What This Repo Explicitly Does NOT Do

- Provide domain logic — purely delivery infrastructure
- Route or schedule notifications — callers decide when and what to send
- Implement inbound message handling
- Depend on casehub-work, casehub-ledger, or casehub-engine

---

## Notification Consolidation Rule

**Do not implement a new Slack, Teams, SMS, or email connector in any other repo.** All outbound messaging routes through this SPI. If a new channel type is needed, add it here.

`casehub-work-notifications` currently has parallel Slack/Teams implementations — this is a known overlap risk and should be resolved by delegating to `casehub-connectors`.

---

## Current State

- Lightweight and early-stage — no `CLAUDE.md` yet; `docs/DESIGN.md` stub exists
- Recently added to the ecosystem CI dashboards
- Published to GitHub Packages at `0.2-SNAPSHOT`
- GroupId: `io.casehub`
- Not yet wired into casehub-engine or casehub-work escalation paths

---

## Usage

Callers inject all `Connector` beans, filter by id, and call send with a destination, title, and body. See docs/DESIGN.md for a usage example.
