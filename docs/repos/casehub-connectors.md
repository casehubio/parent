# casehub-connectors — Platform Deep Dive

**GitHub:** [casehubio/casehub-connectors](https://github.com/casehubio/casehub-connectors)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/PLATFORM.md)

---

## Purpose

Lightweight outbound message connectors for the casehubio platform. Provides a unified `Connector` CDI SPI with built-in implementations for Slack, Teams, Twilio SMS, WhatsApp, and email. No Camel, no vendor SDKs — pure `java.net.http.HttpClient`.

This is the **canonical outbound notification infrastructure** for the platform. Any repo that needs to send outbound messages (escalations, alerts, notifications) must use this SPI rather than implementing its own connector.

---

## Key Abstractions

### SPI

```java
public interface Connector {
    String id();                      // "slack", "teams", "twilio-sms", etc.
    void send(ConnectorMessage msg);
}

public record ConnectorMessage(
    String destination,   // webhook URL, phone number, etc.
    String title,
    String body
) {}
```

Custom connectors implement `Connector` as `@ApplicationScoped` CDI beans — auto-discovered.

### Built-in Implementations

| ID | Module | Auth |
|---|---|---|
| `slack` | `casehub-connectors` | Webhook URL in `destination` |
| `teams` | `casehub-connectors` | Webhook URL in `destination` |
| `twilio-sms` | `casehub-connectors` | Account SID + Auth Token in config |
| `whatsapp` | `casehub-connectors` | API Token + Phone Number ID in config |
| `email` | `casehub-connectors-email` | SMTP via `quarkus-mailer` |

### Configuration

```properties
casehub.connectors.twilio.account-sid=ACxx...
casehub.connectors.twilio.auth-token=...
casehub.connectors.twilio.from=+14155552671

casehub.connectors.whatsapp.api-token=EAAxx...
casehub.connectors.whatsapp.phone-number-id=12345678901234
```

Slack and Teams: no config — webhook URL is the `destination` field.

---

## Depends On

Nothing in the casehubio ecosystem. Pure Java (`java.net.http.HttpClient`) + optional `quarkus-mailer` for email.

## Depended On By

| Repo | Expected usage |
|---|---|
| `casehub-engine` | Escalation and notification paths (not yet wired) |
| `quarkus-work-notifications` | Should delegate to `casehub-connectors` rather than maintain its own Slack/Teams implementations |

---

## What This Repo Explicitly Does NOT Do

- Provide domain logic — purely delivery infrastructure
- Route or schedule notifications — callers decide when and what to send
- Implement inbound message handling
- Depend on quarkus-work, quarkus-ledger, or casehub-engine

---

## Notification Consolidation Rule

**Do not implement a new Slack, Teams, SMS, or email connector in any other repo.** All outbound messaging routes through this SPI. If a new channel type is needed, add it here.

`quarkus-work-notifications` currently has parallel Slack/Teams implementations — this is a known overlap risk and should be resolved by delegating to `casehub-connectors`.

---

## Current State

- Lightweight and early-stage — no `CLAUDE.md` or `docs/DESIGN.md` yet
- Recently added to the ecosystem CI dashboards
- Published to GitHub Packages at `0.2-SNAPSHOT`
- GroupId: `io.casehubio` (not yet `io.quarkiverse.*`)
- Not yet wired into casehub-engine or quarkus-work escalation paths

---

## Usage

```java
@Inject @Any Instance<Connector> connectors;

connectors.stream()
    .filter(c -> "slack".equals(c.id()))
    .findFirst()
    .ifPresent(c -> c.send(new ConnectorMessage(
        "https://hooks.slack.com/services/...",
        "WorkItem Assigned",
        "Loan #1234 assigned to alice"
    )));
```
