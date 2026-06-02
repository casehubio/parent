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

### Dispatch Gate

All channel writes flow through a single enforcement gate: `MessageService.dispatch(MessageDispatch)`. In order: paused check → `AllowedWritersPolicy` ACL → `RateLimiter` → LAST_WRITE overwrite semantics → `LedgerWriteService.record()` → `ChannelGateway.fanOut()`. There is no bypass path. `ReactiveMessageService` mirrors this with `dispatch(MessageDispatch) → Uni<DispatchResult>`.

`MessageDispatch` is the unified request object: `sender`, `type`, `content`, `correlationId`, `inReplyTo`, `artefactRefs`, `target`, `actorType`, `deadline` (all except sender/type/content optional). Builds via `MessageDispatch.builder(channelId, sender, type, content)`.

**Builder protocol invariants** — enforced at `build()`, not downstream:
- `DONE`, `DECLINE`, `FAILURE`, `HANDOFF`, `RESPONSE` require `inReplyTo`
- `DONE`, `DECLINE`, `FAILURE`, `HANDOFF`, `RESPONSE` require `correlationId`
- `HANDOFF` requires `target` (named recipient)

`DispatchResult` carries: `ledgerEntryId` (UUID of the `MessageLedgerEntry` written), `subjectId` (resolved domain aggregate), `causedByEntryId` (causal chain link), `parentReplyCount`.

**`subjectId` / `causedByEntryId` propagation priority:** explicit caller value → correlation root lookup (earliest in thread by `sequenceNumber ASC`) → `channelId` fallback. This lets domain consumers group all ledger entries for one investigation by `subjectId` without join logic.

See docs/DESIGN.md for dispatch builder and enforcement gate detail.

### Message Types (speech-act taxonomy — ADR-0005)

| Type | Intent | Creates obligation | Terminal? |
|------|--------|--------------------|-----------|
| QUERY | Information request | Yes → RESPONSE or DECLINE required | No |
| COMMAND | Action request | Yes → DONE, FAILURE, or DECLINE required | No |
| RESPONSE | Answers a QUERY | No (discharges QUERY obligation) | Yes (for that QUERY) |
| STATUS | Progress update on open COMMAND | No | No |
| DECLINE | Refuse a QUERY or COMMAND | No (discharges obligation) | Yes |
| HANDOFF | Delegate COMMAND to another agent | Transfers obligation | No |
| DONE | Successful COMMAND completion | No | Yes |
| FAILURE | Failed COMMAND | No | Yes |
| EVENT | Telemetry / observer signal | No | N/A — excluded from agent context |

Builder invariants (enforced at `build()`):
- RESPONSE, DONE, FAILURE, DECLINE, HANDOFF require `inReplyTo` + `correlationId`
- HANDOFF requires `target` (named recipient or capability tag)

See docs/DESIGN.md for internal channel semantics, commitment state machine, and MCP tool inventory.

---

### Channel Gateway

Outbound messages are routed through a channel backend SPI that supports multiple backend types: agent-to-agent (default), human-participating, and human-observer. An inbound normaliser SPI translates external human messages into the canonical message format before they enter the system. Fan-out to non-default backends is asynchronous and non-fatal. The default backend is always registered and handles all standard agent messaging. `MessageObserver` implementations may use any normal CDI scope.

**`ChannelInitialisedEvent`** — a record in `casehub-qhorus-api` (`io.casehub.qhorus.api.gateway`) fired by `ChannelGateway.initChannel()` on every call — both on channel creation and on startup recovery. External backends observe this via `@Observes ChannelInitialisedEvent` to re-register without implementing their own restart recovery logic.

**Startup recovery** — `ChannelGateway` rebuilds its in-memory registry from the channel store on `@Observes StartupEvent`. Previously the registry was empty after restart until channels were re-created or re-accessed. Each channel init is exception-isolated so a broken observer cannot abort the startup sequence.

**`findByNamePrefix`** — `ChannelService` and `ReactiveChannelService` expose `findByNamePrefix(prefix)`. The JPA path emits `LIKE 'prefix%' ESCAPE '!'` (metachar-safe, index-eligible). Use when listing channels by namespace prefix (e.g. all channels for a case) without a full table scan.

See docs/DESIGN.md for gateway class structure and SPI contracts.

### Ledger Integration

Every message sent — regardless of type — is recorded as a tamper-evident ledger entry extending `casehub-ledger`. The ledger is the complete, immutable channel history. Telemetry data from structured event messages is extracted and indexed for aggregation queries.

See docs/DESIGN.md for ledger entry structure and query capabilities.

### MCP Tool Surface

Qhorus exposes MCP tools across six capability groups: instance management, channel management, backend management, messaging, shared data, and commitments. Normative ledger queries are also exposed as MCP tools.

See docs/DESIGN.md for the full tool inventory.

### Channel Read-model Projection

Left-fold SPI over channel message history. Consumers implement `ChannelProjection<S>` to derive deterministic read-models (vote tallies, review manifests, digests) without scanning raw messages on every read.

| Type | Location | Purpose |
|---|---|---|
| `MessageView` | `api/message/` | Read-side DTO — canonical representation of a message for consumers; `type` field (not `messageType` — intentional rename matching `DispatchResult`) |
| `ChannelProjection<S>` | `api/spi/` | Pure left-fold SPI — `identity()` returns fresh empty state; `apply(S, MessageView)` folds one message |
| `ProjectionResult<S>` | `api/spi/` | Fold result: `state` (materialised S) + `lastMessageId` (null when channel was empty); pass as `previous` to incremental `project()` overload to resume without full rescan |
| `ProjectionService` | `runtime/message/` | `@ApplicationScoped` — four overloads: full, scoped-full, incremental, scoped-incremental; scope validation rejects conflicting `channelId` and `descending=true` |
| `ReactiveProjectionService` | `runtime/message/` | `@IfBuildProperty(casehub.qhorus.reactive.enabled=true)` — reactive mirror; uses `ReactiveMessageStore.stream()` + `collect().in()` |

Refs: qhorus#230 (projection SPI + `ProjectionService`), qhorus#231 (`ReactiveProjectionService`).

### Store SPIs

Six store interfaces (blocking and reactive mirrors) cover the full domain: channels, messages, instances, shared data, watchdogs, and commitments.

**New in qhorus#231:** `ReactiveMessageStore.stream(MessageQuery) → Multi<Message>` — streaming message query used by `ReactiveProjectionService` to collect message history reactively.

**New in engine#56:**
- `CommitmentStore.findOpenByObligor(String obligor)` — cross-channel query returning all OPEN commitments for a given obligor. Used by `casehub-engine-actor-state` to assemble the obligations slice of the actor state view.
- `ChannelStore.findByIds(Collection<UUID> ids)` — batch lookup emitting a single `IN(?)` query. Used when a set of channel IDs is already known and full `Channel` records are needed without N individual fetches.

See docs/DESIGN.md for SPI interfaces.

### External APIs

- `GET /.well-known/agent-card.json` — A2A ecosystem discovery
- `POST /a2a/message:send` — A2A-compatible message receive endpoint

### Module Structure

| Module | Contents |
|--------|----------|
| `api` | SPIs: `ChannelBackend`, `MessageObserver`, `HumanParticipatingChannelBackend`, `ChannelProjection<S>`; DTOs: `MessageView`; Records: `ProjectionResult<S>`; domain event types |
| `connectors` | Optional — `WatchdogAlertEvent → ConnectorService.send()` bridge; activates by classpath presence |
| `runtime` | `MessageService`, `ChannelGateway`, `QhorusDashboardService`, `ProjectionService`, `ReactiveProjectionService`, ledger integration, MCP tools, A2A endpoint |
| `connector-backend` | Optional — `ConnectorChannelBackend` implements `HumanParticipatingChannelBackend`; bridges `InboundMessage` CDI events (`@ObservesAsync`) from casehub-connectors into Qhorus channel dispatch; self-registers for channels with a `ChannelBackend` type of `CONNECTOR`. Activates by classpath presence. |
| `deployment` | Quarkus extension deployment descriptors |
| `testing` | In-memory store implementations for `@QuarkusTest` |

---

## Depends On

- `casehub-ledger` — mandatory (for ledger entry subclassing and observability)
- `casehub-platform-api` — direct compile dependency (`ActorType`, `ActorTypeResolver` from `io.casehub.platform.api.identity`)

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
1. **Illocutionary** — what was said (speech act type, channel)
2. **Commitment** — what was obligated (Commitment record, OPEN → FULFILLED/FAILED/EXPIRED)
3. **Temporal** — when obligations become stale (Watchdog, deadline enforcement)
4. **Enforcement** — casehub-engine orchestration reacts to commitment outcomes via CDI events

See [docs/normative-layer.md](https://raw.githubusercontent.com/casehibio/qhorus/main/docs/normative-layer.md).

### Normative Channel Layout

The agent mesh framework defines a 3-channel normative layout implemented via `NormativeChannelLayout` (Claudony SPI) and enforced at channel creation:

| Channel suffix | Semantics | `allowedTypes` |
|----------------|-----------|----------------|
| `/work` | Task assignment and completion (prescriptive) | `COMMAND, RESPONSE, DONE, DECLINE, EXPIRED` |
| `/observe` | Passive monitoring and state sharing (descriptive) | `EVENT, QUERY, STATUS` |
| `/oversight` | Human governance gates (commitment-based) | `COMMAND, RESPONSE` |

`allowedTypes` on `Channel` is enforced at message send time — messages outside the declared set are rejected with a protocol violation error. This is what makes the normative layer machine-checkable rather than advisory.

See the full agent mesh framework spec: [`casehubio/claudony docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md`](https://github.com/casehubio/claudony/blob/main/docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md).

---

## Current State

- 1035+ tests passing (runtime + testing + examples modules)
- Channel backend abstraction complete (agent, human-participating, human-observer modes) — see ADR-0006
- A2A protocol bridge complete: backend, identity resolution chain, and resource layer — closed #135
- Dispatch unification complete: `MessageService.send()` replaced by `dispatch(MessageDispatch)`; single enforcement gate covers all channel writes — closed #184
- `DispatchResult` carries `ledgerEntryId`, `subjectId`, `causedByEntryId`, `parentReplyCount`; `subjectId`/`causedByEntryId` propagated via correlation root lookup — closed #184
- Deadline enforcement: `MessageDispatch.deadline` propagated to `Message.deadline` for all types — closed #192
- `ReactiveMessageService.dispatch(MessageDispatch) → Uni<DispatchResult>` replaces `send()`; full enforcement parity deferred (#193) — service currently `@Disabled`
- Startup recovery via `@Observes StartupEvent` in `ChannelGateway`; `ChannelInitialisedEvent` fires on every `initChannel()` for backend re-registration — closed #181
- Actor type explicitly stored on every message and propagated to ledger without re-derivation
- Reactive store tests disabled — require PostgreSQL with native reactive driver (Docker not always available)

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/qhorus/main/docs/DESIGN.md) — full MCP tool surface, store SPIs, commitment lifecycle
- [docs/normative-layer.md](https://raw.githubusercontent.com/casehubio/qhorus/main/docs/normative-layer.md) — 4-layer normative accountability framework
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/qhorus/main/adr/INDEX.md) — architectural decision records (incl. ADR-0005 speech-act taxonomy)
