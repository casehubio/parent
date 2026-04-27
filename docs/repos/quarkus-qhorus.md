# quarkus-qhorus — Platform Deep Dive

**GitHub:** [casehubio/quarkus-qhorus](https://github.com/casehubio/quarkus-qhorus)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/PLATFORM.md)

---

## Purpose

Peer-to-peer agent communication mesh. The coordination layer for multi-agent AI systems — typed channels, typed messages (speech-act taxonomy), commitment/obligation tracking, shared artefact store, and structured observability. Independently embeddable in any Quarkus app. Designed for Quarkiverse submission.

Grounded in speech act theory and deontic logic (see `docs/normative-layer.md`). Designed after research into A2A, AutoGen, LangGraph, OpenAI Swarm, Letta, and CrewAI.

---

## Key Abstractions

### Domain Model

| Entity | Purpose |
|---|---|
| `Channel` | Typed communication channel. 5 semantics: APPEND, COLLECT, BARRIER, EPHEMERAL, LAST_WRITE. Has `allowed_writers` and `admin_instances` ACLs. |
| `Message` | Speech-act message. 9 types: QUERY, COMMAND, RESPONSE, STATUS, DECLINE, HANDOFF, DONE, FAILURE, EVENT (see ADR-0005) |
| `Commitment` | Obligation lifecycle. 7 states: OPEN → FULFILLED / DECLINED / FAILED / DELEGATED / EXPIRED. `CommitmentService` drives transitions. |
| `Instance` | Agent registry entry with `Capability` tags. 3 addressing modes: by id, by capability, by role. |
| `SharedData` + `ArtefactClaim` | Shared artefact store with claim/release lifecycle. |
| `PendingReply` | `wait_for_reply` long-poll correlation with SSE keepalives. |
| `Watchdog` | Condition-based alert registration. |

### Ledger Integration

| Class | Purpose |
|---|---|
| `AgentMessageLedgerEntry` | `LedgerEntry` subclass (JOINED inheritance) for structured EVENT telemetry |
| `LedgerWriteService` | Writes ledger entry on every structured EVENT message (non-fatal, `REQUIRES_NEW`) |

Ledger entries only created for EVENT type messages with valid JSON containing `tool_name` (String) and `duration_ms` (Long).

### MCP Tool Surface

39 `@Tool` methods in `QhorusMcpTools` (blocking) / `ReactiveQhorusMcpTools` (reactive):
- Instance management: `register_instance`, `deregister_instance`, `list_instances`, `get_instance`
- Channel management: `create_channel`, `list_channels`, `get_channel`, `delete_channel`, `add_writer`, `remove_writer`
- Messaging: `send_message`, `check_messages`, `read_messages`, `get_message`, `wait_for_reply`
- Observers: `register_observer`, `read_observer_events`, `clear_observer`, `list_observers`
- Shared data: `store_data`, `get_data`, `list_data`, `claim_artefact`, `release_artefact`
- Commitments: `open_commitment`, `acknowledge_commitment`, `fulfill_commitment`, `decline_commitment`, `fail_commitment`, `delegate_commitment`, `list_commitments`, `get_commitment`, `list_stalled_obligations`
- Observability: `list_events`, `get_channel_timeline`

### Store SPIs

7 store interfaces (blocking + reactive mirrors):
`ChannelStore`, `MessageStore`, `InstanceStore`, `DataStore`, `WatchdogStore`, `PendingReplyStore`, `CommitmentStore`

### External APIs

- `GET /.well-known/agent-card.json` — A2A ecosystem discovery
- `POST /a2a/message:send` — A2A-compatible message receive endpoint

---

## Depends On

- `quarkus-ledger` — mandatory (for `AgentMessageLedgerEntry` and ledger observability)

## Depended On By

| Repo | How |
|---|---|
| `claudony` | Embeds Qhorus directly; named `qhorus` datasource; provides `ClaudonyCaseChannelProvider` SPI impl |
| `casehub-engine` | Future — via `CaseChannelProvider` SPI (implemented by Claudony) |

---

## What This Repo Explicitly Does NOT Do

- Orchestrate agent workflows (that is casehub-engine)
- Manage human task inboxes (that is quarkus-work)
- Own case state or process logic
- Interpret message content — purely infrastructure
- Provision or terminate AI agent processes (that is claudony)

---

## Named Datasource Requirement

Qhorus always runs on a named `qhorus` datasource. Never share it with domain tables.

In Claudony's `application.properties`:
```properties
quarkus.datasource.qhorus.db-kind=h2
quarkus.hibernate-orm.qhorus.datasource=qhorus
quarkus.hibernate-orm.qhorus.packages=io.quarkiverse.qhorus.runtime,io.quarkiverse.ledger.runtime.model
```

---

## EVENT Message Telemetry Pattern

Agent tool calls record telemetry as EVENT messages with structured JSON:
```json
{ "tool_name": "create_channel", "duration_ms": 42, "result": "ok" }
```
`LedgerWriteService` writes a `AgentMessageLedgerEntry` for each such EVENT. Events without valid JSON or missing mandatory fields are silently skipped with a WARN log.

`check_messages` excludes EVENT messages by design. Use `read_observer_events` to assert EVENT delivery in tests.

---

## Normative Layer

Qhorus implements a 4-layer normative accountability framework:
1. **Descriptive** — what happened (messages, events)
2. **Prescriptive** — what was committed to (commitments)
3. **Evaluative** — whether commitments were kept (commitment state transitions)
4. **Corrective** — stalled obligation detection (`list_stalled_obligations`)

See [docs/normative-layer.md](https://raw.githubusercontent.com/casehubio/quarkus-qhorus/main/docs/normative-layer.md).

---

## Current State

- ~800+ tests passing (runtime + testing module)
- All 15 implementation phases complete through reactive dual-stack
- Reactive store tests are `@Disabled` — require PostgreSQL with native reactive driver (Docker not always available)
- Phase 8 (embed in Claudony unified MCP endpoint) still pending

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/quarkus-qhorus/main/docs/DESIGN.md) — full MCP tool surface, store SPIs, commitment lifecycle
- [docs/normative-layer.md](https://raw.githubusercontent.com/casehubio/quarkus-qhorus/main/docs/normative-layer.md) — 4-layer normative accountability framework
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/quarkus-qhorus/main/adr/INDEX.md) — architectural decision records (incl. ADR-0005 speech-act taxonomy)
