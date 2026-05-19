# casehub-qhorus — Platform Deep Dive

**GitHub:** [casehubio/qhorus](https://github.com/casehubio/qhorus)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Agent communication mesh and governance methodology for multi-agent AI systems. Gives every agent interaction the formal status of an accountable act — grounded in speech act theory, deontic logic, defeasible reasoning, and social commitment semantics. The LLM reasons; Qhorus enforces, records, and derives. Independently embeddable in any Quarkus app. CaseHub ecosystem agent communication mesh.

Designed after research into A2A, AutoGen, LangGraph, OpenAI Swarm, Letta, and CrewAI. See [docs/normative-layer.md](https://raw.githubusercontent.com/casehubio/qhorus/main/docs/normative-layer.md) for the theoretical framing.

---

## Key Abstractions

### Domain Model

| Entity | Purpose |
|---|---|
| Channel | Typed communication channel with configurable delivery semantics and access control. |
| Message | Speech-act message with a typed intent (query, command, response, etc.) — see ADR-0005. |
| Commitment | Obligation with a defined lifecycle from open through resolution states. |
| Instance | Agent registry entry with capability tags and multiple addressing modes. |
| SharedData + ArtefactClaim | Shared artefact store with claim/release lifecycle. |
| Watchdog | Condition-based alert registration. |

See docs/DESIGN.md for channel semantics, message types, commitment state machine, and addressing modes.

### Channel Gateway

Outbound messages are routed through a channel backend SPI that supports multiple backend types: agent-to-agent (default), human-participating, and human-observer. An inbound normaliser SPI translates external human messages into the canonical message format before they enter the system. Fan-out to non-default backends is asynchronous and non-fatal. The default backend is always registered and handles all standard agent messaging.

See docs/DESIGN.md for gateway class structure and SPI contracts.

### Ledger Integration

Every message sent — regardless of type — is recorded as a tamper-evident ledger entry extending `casehub-ledger`. The ledger is the complete, immutable channel history. Telemetry data from structured event messages is extracted and indexed for aggregation queries.

See docs/DESIGN.md for ledger entry structure and query capabilities.

### MCP Tool Surface

Qhorus exposes MCP tools across six capability groups: instance management, channel management, backend management, messaging, shared data, and commitments. Normative ledger queries are also exposed as MCP tools.

See docs/DESIGN.md for the full tool inventory.

### Store SPIs

Six store interfaces (blocking and reactive mirrors) cover the full domain: channels, messages, instances, shared data, watchdogs, and commitments.

See docs/DESIGN.md for SPI interfaces.

### External APIs

- `GET /.well-known/agent-card.json` — A2A ecosystem discovery
- `POST /a2a/message:send` — A2A-compatible message receive endpoint

---

## Depends On

- `casehub-ledger` — mandatory (for ledger entry subclassing and observability)

## Depended On By

| Repo | How |
|---|---|
| `claudony` | Embeds Qhorus directly; named `qhorus` datasource; provides CaseChannel SPI implementation |
| `casehub-engine` | Future — via CaseChannelProvider SPI (implemented by Claudony) |

---

## What This Repo Explicitly Does NOT Do

- Orchestrate agent workflows (that is casehub-engine)
- Manage human task inboxes (that is casehub-work)
- Own case state or process logic
- Interpret message content — purely infrastructure
- Provision or terminate AI agent processes (that is claudony)

---

## Named Datasource Requirement

Qhorus always runs on a named `qhorus` datasource. Never share it with domain tables.

See docs/DESIGN.md for datasource configuration.

---

## Normative Ledger — All Message Types Recorded

Every message of every type creates a ledger entry. The ledger is the complete, immutable, tamper-evident channel history. Telemetry event messages are indexed for aggregation. Regular message reads exclude event-type messages by design; the ledger query surface provides access to the full history.

See docs/DESIGN.md for ledger query capabilities.

---

## Normative Layer

Qhorus implements a 4-layer normative accountability framework:
1. **Descriptive** — what happened (messages, events)
2. **Prescriptive** — what was committed to (commitments)
3. **Evaluative** — whether commitments were kept (commitment state transitions)
4. **Corrective** — stalled obligation detection

See [docs/normative-layer.md](https://raw.githubusercontent.com/casehubio/qhorus/main/docs/normative-layer.md).

---

## Current State

- 1035+ tests passing (runtime + testing + examples modules)
- Channel backend abstraction complete (agent, human-participating, human-observer modes) — see ADR-0006
- A2A protocol bridge complete: backend registered, identity resolution chain implemented, resource layer refactored as thin adapter — closed #135
- Actor type is explicitly stored on every message and propagated to ledger without re-derivation
- Reactive store tests disabled — require PostgreSQL with native reactive driver (Docker not always available)

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/qhorus/main/docs/DESIGN.md) — full MCP tool surface, store SPIs, commitment lifecycle
- [docs/normative-layer.md](https://raw.githubusercontent.com/casehubio/qhorus/main/docs/normative-layer.md) — 4-layer normative accountability framework
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/qhorus/main/adr/INDEX.md) — architectural decision records (incl. ADR-0005 speech-act taxonomy)
