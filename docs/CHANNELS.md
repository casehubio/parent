# CaseHub Channel Taxonomy

Channels are the communication primitive of the CaseHub platform. Every agent interaction,
human decision, domain event, and infrastructure signal flows through a Qhorus channel.
This document names and classifies the channel types that have emerged from practice,
and describes the open design space for new channel patterns.

---

## Channel Taxonomy

### 1. Coordination Channels — the agent mesh

The normative pattern for any agent participating in the CaseHub mesh. Three channels per
agent case, declared by `CaseChannelLayout` SPI, `allowedTypes` enforced at the Qhorus layer.

| Channel suffix | Purpose | Participants | Speech acts (allowedTypes) |
|----------------|---------|-------------|--------------------------|
| `/work` | Task assignment and completion | Agent ↔ engine | COMMAND, RESPONSE, DONE, DECLINE |
| `/observe` | Passive state broadcast | Engine → agents (read-only) | EVENT, INFORM |
| `/oversight` | Human governance gate | Engine → human, human → engine | COMMAND, RESPONSE |

**Current home:** `CaseChannelLayout` in `claudony-casehub`.
**Planned:** extract to `casehub-engine-api` so any agent implementation (claudony, openclaw, future) shares the canonical definition. See parent#93.

---

### 2. Deliberation Channels — structured reasoning

Channels for multi-participant reasoning about content, decisions, or plans. Not about
task coordination — about reaching a conclusion through structured discourse.

#### 2a. Debate — multi-agent, multi-turn, document-scoped
- **Home:** `casehub-drafthouse`
- **Naming:** `drafthouse/debate/d-{UUID}`
- **Participants:** REV, IMP, SUPERVISOR, MODERATOR, SELECTOR roles
- **Turn structure:** round-based, explicit round numbers per message
- **Constraints:** protocol-layer (entry types encoded via `DebateProtocol.META_SENTINEL`), not Qhorus `allowedTypes`
- **Entry types:** RAISE, AGREE, COUNTER, DISPUTE, QUALIFY, FLAG_HUMAN, MEMO, SUB_TASK_REQUEST
- **Lifecycle:** session-scoped (start_debate → end_debate)
- **Link to coordination:** standalone today; optionally triggerable from a /work COMMAND

#### 2b. Review — single reviewer, reactive, document-scoped
- **Home:** `casehub-drafthouse`
- **Participants:** one human, one LLM reviewer (auto-responds via `ReviewerChannelBackend`)
- **Turn structure:** reactive — `ReviewerChannelBackend` auto-invokes LLM on QUERY
- **Lifecycle:** session-scoped (start_review → end_review)

**Open design space:** negotiation channels (agents agreeing on a plan), consensus channels
(M-of-N agreement), planning channels (structured decomposition of a goal into tasks).

---

### 3. Signal Channels — case state mutation

Channels used to deliver state-change signals into running case instances.

- **Home:** `casehub-engine` (`QhorusMessageSignalBridge`, `CaseSignalSink`)
- **Direction:** Qhorus message event → case context mutation
- **Turn structure:** one-way, no response expected
- **Lifecycle:** ephemeral (signal fired, case context updated, channel message consumed)
- **Examples:** SLA escalation → `CaseSignalSink.signal()`; Qhorus RESPONSE → `QhorusMessageSignalBridge`

---

### 4. Notification Channels — external boundary

Channels bridging the external world into the platform (inbound) or the platform out to
external systems (outbound).

- **Home:** `casehub-connectors`, `casehub-qhorus` (connector-backend module)
- **Examples:**
  - Slack webhook → `InboundMessage` → `ConnectorChannelBackend` → case signal
  - Watchdog alert → `WatchdogAlertEvent` → `ConnectorService.send()`
  - CloudEvent from `casehub-iot` / `casehub-qhorus` / `casehub-connectors` → `casehub-ras`

---

### 5. Infrastructure Channels — platform plumbing

Channels used internally for platform coordination, not visible to domain agents.

- **Fleet relay (claudony):** cross-node SSE tick delivery via `FleetMessageRelayObserver`.
  Each Qhorus message dispatch is relayed to all healthy fleet peers.
- **Channel sync (claudony):** `POST /sync` registers `ClaudonyChannelBackend`; `POST /notify`
  relays cross-node ticks. Internal to claudony fleet operation.

---

## Discriminator Dimensions

| Dimension | Values |
|-----------|--------|
| **Purpose** | coordination · deliberation · governance · signal · notification · infrastructure |
| **Participants** | agent↔agent · human↔agent · agent→broadcast · system |
| **Turn structure** | unstructured · round-based · reactive (auto-respond) · one-way |
| **Constraint enforcement** | Qhorus `allowedTypes` · protocol-layer · none |
| **Lifecycle** | long-lived (task) · session-scoped (debate) · ephemeral (signal) |
| **Initiation** | COMMAND on /work · MCP tool · CDI event · external webhook |

---

## Open Design Space

These channel patterns are implied by existing use cases but not yet formalised:

| Pattern | Description | First likely consumer |
|---------|-------------|----------------------|
| **Negotiation** | Two agents reach agreement on a plan or resource allocation | Multi-agent planning in casehub-engine |
| **Consensus** | M-of-N agents must agree before proceeding | Human+AI approval gates, clinical DSMB |
| **Planning** | Structured decomposition of a goal into an ordered task graph | Supervisor pattern in casehub-engine |
| **Audit trail** | Append-only channel as tamper-evident decision record | Already approximated by Qhorus + ledger |
| **Broadcast** | Platform-wide event fan-out to all interested consumers | casehub-ras situational awareness |

See parent#294 (Reusable Platform Primitives epic) for the broader initiative.

---

## References

- `docs/LIFECYCLE.md` — state machine taxonomy (companion document)
- `docs/PLATFORM.md` — Capability Ownership table (CloudEvents, channel SPIs)
- parent#93 — extract normative coordination channel layout to casehub-engine-api
- `casehub/garden: docs/protocols/casehub/qhorus-consumer-integration-pattern.md`
