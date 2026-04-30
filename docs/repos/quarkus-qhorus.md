# quarkus-qhorus — Platform Deep Dive

**GitHub:** [casehubio/quarkus-qhorus](https://github.com/casehubio/quarkus-qhorus)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/PLATFORM.md)

---

## Purpose

Agent communication mesh and governance methodology for multi-agent AI systems. Gives every agent interaction the formal status of an accountable act — grounded in speech act theory, deontic logic, defeasible reasoning, and social commitment semantics. The LLM reasons; Qhorus enforces, records, and derives. Independently embeddable in any Quarkus app. Designed for Quarkiverse submission.

Designed after research into A2A, AutoGen, LangGraph, OpenAI Swarm, Letta, and CrewAI. See [docs/normative-layer.md](https://raw.githubusercontent.com/casehubio/quarkus-qhorus/main/docs/normative-layer.md) for the theoretical framing.

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
| `MessageLedgerEntry` | `LedgerEntry` subclass (JOINED inheritance). Records **all 9 message types** as tamper-evident entries. |
| `LedgerWriteService` | Writes `MessageLedgerEntry` on every message send (all types, non-fatal, `REQUIRES_NEW`) |
| `MessageLedgerEntryRepository` | Queries: `listEntries` (7 filters), `findLatestByCorrelationId`, causal chain traversal, stalled detection, telemetry aggregation |

All 9 message types are recorded. For EVENT messages with structured JSON, `tool_name` and `duration_ms` are extracted as telemetry fields.

### MCP Tool Surface

`@Tool` methods in `QhorusMcpTools` (blocking) / `ReactiveQhorusMcpTools` (reactive):
- Instance management: `register_instance`, `deregister_instance`, `list_instances`, `get_instance`
- Channel management: `create_channel`, `list_channels`, `get_channel`, `delete_channel`, `get_channel_digest`, `add_writer`, `remove_writer`
- Messaging: `send_message`, `check_messages`, `read_messages`, `get_message`, `wait_for_reply`
- Observers: `register_observer`, `read_observer_events`, `clear_observer`, `list_observers`
- Shared data: `store_data`, `get_data`, `list_data`, `claim_artefact`, `release_artefact`
- Commitments: `open_commitment`, `acknowledge_commitment`, `fulfill_commitment`, `decline_commitment`, `fail_commitment`, `delegate_commitment`, `list_commitments`, `get_commitment`, `list_stalled_obligations`
- Ledger queries (normative): `list_ledger_entries` (with `type_filter`, `sender`, `correlation_id`, `sort`), `get_obligation_chain`, `get_causal_chain`, `get_obligation_stats`, `get_telemetry_summary`, `get_channel_timeline`

Key parameter name: messages use `sender` (not `agent_id`).

### Store SPIs

7 store interfaces (blocking + reactive mirrors):
`ChannelStore`, `MessageStore`, `InstanceStore`, `DataStore`, `WatchdogStore`, `PendingReplyStore`, `CommitmentStore`

### External APIs

- `GET /.well-known/agent-card.json` — A2A ecosystem discovery
- `POST /a2a/message:send` — A2A-compatible message receive endpoint

---

## Depends On

- `quarkus-ledger` — mandatory (for `MessageLedgerEntry` subclass and ledger observability)

## Depended On By

| Repo | How |
|---|---|
| `claudony` | Embeds Qhorus directly; named `qhorus` datasource; provides `ClaudonyCaseChannelProvider` SPI impl |
| `casehub-engine` | Future — via `CaseChannelProvider` SPI (implemented by Claudony) |

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

In Claudony's `application.properties`:
```properties
quarkus.datasource.qhorus.db-kind=h2
quarkus.hibernate-orm.qhorus.datasource=qhorus
quarkus.hibernate-orm.qhorus.packages=io.quarkiverse.qhorus.runtime,io.quarkiverse.ledger.runtime.model
```

---

## Normative Ledger — All 9 Types Recorded

Every message of all 9 types (`QUERY`, `COMMAND`, `RESPONSE`, `STATUS`, `DECLINE`, `HANDOFF`, `DONE`, `FAILURE`, `EVENT`) creates a `MessageLedgerEntry`. The ledger is the complete, immutable, tamper-evident channel history.

For EVENT messages with structured telemetry JSON, `tool_name` and `duration_ms` are extracted as indexed fields for `get_telemetry_summary`.

`check_messages` excludes EVENT messages by design. Use `read_observer_events` for EVENT delivery assertions in tests. Use `list_ledger_entries` to query the full history.

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
