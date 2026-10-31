# Messaging vs Notifications — When to Use What

The platform has two communication systems that serve different purposes.
This document explains when to use each one.

## Qhorus Channels (agent-to-agent messaging)

**Use for:** structured communication between agents within a case.

Qhorus channels are case-scoped message streams with type enforcement
and obligation tracking. Messages are persistent, ordered, and carry
protocol semantics.

### Key capabilities

- **Message types:** QUERY, COMMAND, RESPONSE, STATUS, DECLINE, HANDOFF,
  DONE, FAILURE, PROPOSE, JUDGMENT, EVENT
- **Channel semantics:** APPEND, COLLECT, BARRIER, EPHEMERAL, LAST_WRITE,
  BROADCAST
- **Commitment tracking:** COMMAND messages create obligations
  (OPEN → ACKNOWLEDGED → FULFILLED/DECLINED/FAILED/DELEGATED/EXPIRED).
  STATUS replies acknowledge; DONE/DECLINE/FAILURE resolve.
- **Type enforcement:** channels restrict which MessageTypes are allowed
  (e.g., observe channel permits EVENT only)
- **Agent visibility:** `MessageType.isAgentVisible()` controls whether
  agents see a message. EVENT is invisible by default — use for telemetry,
  not for messages agents should react to.
- **Broadcast channels:** `BroadcastMembershipManager` auto-joins agents
  to `broadcast/<capability>` channels (semantic: BROADCAST). Only STATUS
  and EVENT types permitted.

### Engine integration

The engine accesses qhorus through `CaseChannelProvider` — never
`MessageDispatcher` directly. App-level bridges (Claudony, OpenClaw)
implement `CaseChannelProvider` and translate to qhorus
`MessageService.dispatch()`.

The `NormativeChannelLayout` defines four standard channels per case:

| Channel | Purpose | Type restrictions |
|---------|---------|-------------------|
| work | Primary coordination — all obligation-carrying types | unrestricted |
| observe | Telemetry | EVENT only |
| oversight | Human governance | no EVENT |
| coordination | Engine coordination | unrestricted |

### When to use qhorus

- Agent needs to tell another agent something within a case
- Message requires acknowledgement or obligation tracking
- Communication follows request/response patterns (QUERY → RESPONSE)
- Agents need to coordinate on shared work (COMMAND → DONE)
- Engine needs to broadcast state changes to case participants

## Platform Notifications (cross-cutting delivery)

**Use for:** delivering events to human or system targets outside the
agent mesh.

Platform notifications are a subscription-driven delivery pipeline.
Events match subscriptions; matched notifications route through
configurable delivery channels.

### Key capabilities

- **Delivery channels:** IN_APP (inbox), EMAIL, SMS, PUSH, WHATSAPP,
  CDI_EVENT
- **Target kinds:**
  - USER — full pipeline: preferences → suppression → quiet hours →
    digest buffering → channel routing → delivery + tracking
  - NON_USER — minimal pipeline: CDI event only, fire-and-forget
- **Inbox:** `InAppNotificationDeliverer` persists to `NotificationStore`.
  Real persistence, not ephemeral.
- **Engagement tracking:** OPENED, CLICKED, DISMISSED, REPLIED, CONVERTED.
  This is user engagement metrics — not protocol acknowledgement.
- **No obligation tracking.** A notification does not create a commitment.
  If you need "did they act on it?", use qhorus COMMAND + commitment
  lifecycle instead.

### When to use platform notifications

- A human needs to know something happened (case stalled, escalation)
- Delivery preference matters (email vs push vs inbox)
- Quiet hours, digest buffering, or suppression rules apply
- System/agent observers need fire-and-forget CDI events
- The event source is not within a qhorus channel

## They Do Not Overlap

| Concern | Qhorus | Platform notifications |
|---------|--------|-----------------------|
| Scope | Per-case, per-channel | Cross-cutting, any event source |
| Participants | Agents within a case | Humans, agents, systems |
| Persistence | Channel message log | Inbox (USER) or ephemeral (NON_USER) |
| Acknowledgement | Protocol-level (CommitmentState) | Engagement-level (OPENED/CLICKED) |
| Delivery routing | Channel semantic determines behavior | Subscription + preference matching |
| Engine access | `CaseChannelProvider` SPI | Not used by engine directly |

## Decision Checklist

1. **Is the recipient an agent in the same case?** → Qhorus channel
2. **Does the recipient need to acknowledge or act?** → Qhorus COMMAND
3. **Is the recipient a human?** → Platform notification
4. **Does the recipient have delivery preferences?** → Platform notification
5. **Is this telemetry/observability?** → Qhorus EVENT (agent-invisible)
   or platform notification (for human dashboards)
6. **Is this a state change agents should react to?** → Qhorus STATUS
   on the coordination channel (agent-visible)
