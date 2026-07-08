# Agent Communication Mesh

> **Scope:** Normative 3-channel layout (work/observe/oversight), mesh participation strategies
> **Audience:** All
> **Key repos:** casehub-qhorus (transport), casehub-engine (orchestration), casehub-engine-api (layout SPIs)
> **Protocols:** [normative-channel-layout-single-source](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/normative-channel-layout-single-source.md)

## Normative 3-Channel Layout

The platform uses a normative 3-channel layout for agent-to-agent and agent-to-human interactions:

| Channel | Purpose | Primary speech acts |
|---------|---------|---------------------|
| `work` | Task assignment and completion (prescriptive) | COMMAND, RESPONSE, DONE, DECLINE |
| `observe` | Passive monitoring and state sharing (descriptive) | EVENT |
| `oversight` | Human governance gates (commitment-based) | All obligation-carrying types (COMMAND, QUERY, RESPONSE, DONE, DECLINE, FAILURE, STATUS, HANDOFF); EVENT excluded — no telemetry on the governance channel (`deniedTypes = EVENT`) |

**Rationale:** Separation of concerns — work channel is for task execution, observe channel is for telemetry, oversight channel is for human accountability. This prevents telemetry noise from obscuring governance signals.

## Speech Acts (9 types)

All agent interactions are typed by speech act:

1. **COMMAND** — directive (requires DONE or DECLINE response)
2. **QUERY** — question (requires RESPONSE)
3. **RESPONSE** — answer to a QUERY
4. **DONE** — task completion confirmation
5. **DECLINE** — refusal to execute (with reason)
6. **FAILURE** — execution attempted but failed
7. **STATUS** — non-committal status update
8. **HANDOFF** — obligation transfer to named target
9. **EVENT** — telemetry (no response required)

**Write path:** All writes flow through `MessageService.dispatch(MessageDispatch)` — single gate for ACL, rate limit, LAST_WRITE semantics, ledger write, and fan-out.

`MessageDispatch` builder validates protocol invariants at `build()`:
- DONE/DECLINE/FAILURE/HANDOFF/RESPONSE require `inReplyTo` + `correlationId`
- HANDOFF requires `target`

## 4-Layer Normative Accountability Framework

These map to the 4-layer accountability framework implemented by `casehub-qhorus`:

1. **Illocutionary** — what was said (speech act type, channel)
2. **Commitment** — what was obligated (Commitment record, OPEN → FULFILLED/FAILED/EXPIRED)
3. **Temporal** — when obligations become stale (Watchdog, deadline enforcement)
4. **Enforcement** — casehub-engine orchestration reacts to commitment outcomes via CDI events

Full framework spec: [claudony agent mesh framework](https://github.com/casehubio/claudony/blob/main/docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md)

## Channel Layout SPI

`CaseChannelLayout` SPI in `casehub-engine-api` (`io.casehub.api.spi.mesh`) defines channel topology per case.

`ChannelSpec` record declares:
- `name` — channel identifier
- `semantics` — channel type (TASK, COORDINATION, TELEMETRY, OVERSIGHT, DEBATE)
- `deniedTypes` — speech acts excluded from this channel

**Standard implementations:**
- `NormativeChannelLayout` — 3-channel: work/observe/oversight
- `SimpleLayout` — 2-channel: work/observe (no governance gate)

Use `CaseChannelLayout.named("normative"|"simple")` for config-driven selection.

`CaseDefinition definition` param is intentionally null at all current call sites — forward-looking extensibility for per-definition topology.

See protocol: [normative-channel-layout-single-source](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/normative-channel-layout-single-source.md)

## Mesh Participation Strategy

`MeshParticipationStrategy` SPI in `casehub-engine-api` (`io.casehub.api.spi.mesh`) determines how an agent participates in the mesh.

`strategyFor(String workerId, UUID caseId)` returns `MeshParticipation`:
- `ACTIVE` — agent initiates and responds
- `REACTIVE` — agent responds only when addressed
- `SILENT` — agent observes only (no writes)

**Standard implementations:**
- `ActiveParticipationStrategy` — always returns ACTIVE
- `ReactiveParticipationStrategy` — always returns REACTIVE
- `SilentParticipationStrategy` — always returns SILENT

Use `MeshParticipationStrategy.named("active"|"reactive"|"silent")` for config-driven selection.

Null `caseId` is valid (strategy consulted before case exists).

## Commitment Tracking

`Commitment` in `casehub-qhorus` tracks agent obligations with 7-state lifecycle:

1. **OPEN** — obligation created, not yet fulfilled
2. **FULFILLED** — obligation completed successfully
3. **FAILED** — obligation failed (agent sent FAILURE)
4. **DECLINED** — obligation refused (agent sent DECLINE)
5. **EXPIRED** — deadline passed without resolution
6. **WITHDRAWN** — obligation cancelled by originator
7. **DELEGATED** — obligation transferred to named target (terminal for original obligor)

**Key distinction:** Qhorus `DELEGATED` is **terminal** for the original obligor (obligation transferred, child Commitment created). casehub-work `DELEGATED` is **non-terminal** (work reassigned, item stays active). These are different concepts with the same name.

## Message Ledger

`MessageLedgerEntry extends LedgerEntry` in `casehub-qhorus` records all 9 speech-act types in the tamper-evident ledger.

Every agent interaction is recorded with:
- `actorId` — sender
- `channelId` — conversation context
- `messageType` — speech act
- `correlationId` — conversation thread
- `inReplyTo` — message being responded to
- `traceId` — distributed trace linkage

Provides normative accountability: who said what, to whom, when, and in what context.

## Channel Backends (Fan-out)

`ChannelBackend` SPI in `casehub-qhorus-api` enables external systems to react to channel messages.

Implementations register for a specific channel and receive `post()` calls when messages are dispatched.

**Per-channel scope:** each backend knows its channel context.

**Use cases:**
- Claudony panel display (`ClaudonyChannelBackend`)
- Slack thread delivery (`SlackChannelBackend`)
- OpenClaw webhook dispatch (`ChannelBackend` in casehub-openclaw)

## Message Observers (Global Broadcast)

`MessageObserver` SPI in `casehub-qhorus-api` is a global broadcast across all channels.

**Cross-cutting concerns:**
- Clinical PI response monitoring (casehub-clinical)
- Inbound WorkItem bridge (casehub-engine-inbound)
- Channel context window (casehub-openclaw)

**Topology guidance:**
- `Scope.LOCAL` — CDI-only broadcast (single-node)
- `Scope.CLUSTER` — cross-node broadcast via `ChannelActivityBroadcaster`

For cluster-scoped delivery across fleet nodes, use `ChannelActivityBroadcaster` SPI with PostgreSQL LISTEN/NOTIFY implementation (`casehub-qhorus-postgres-broadcaster`).

See [qhorus messaging architecture](https://github.com/casehubio/qhorus/blob/main/docs/messaging-architecture.md) and [casehub-qhorus deep-dive](repos/casehub-qhorus.md).

## Service Facade Interfaces

Consumer-called APIs for channel management and message dispatch:

**Channel management:**
- `ChannelManager` + `ReactiveChannelManager` — channel lifecycle surface
- `ChannelService implements ChannelManager` — runtime implementation

**Message dispatch:**
- `MessageDispatcher` + `ReactiveMessageDispatcher` — message dispatch surface
- `MessageService implements MessageDispatcher` — runtime implementation

**Dashboard/UI composed views:**
- `QhorusDashboardService` — inject this for composed views (channel with message count, instance with capability tags, timeline mapping)

**Do NOT inject raw entity services for write operations** — all writes must flow through `MessageService.dispatch()` for ACL, rate limiting, LAST_WRITE semantics, and ledger capture.

See protocol: [qhorus-consumer-integration-pattern](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/qhorus-consumer-integration-pattern.md) *(link placeholder)*

## MCP Tool Surface

Six capability groups exposed as MCP tools for LLM agents:

1. **Channel management** — create, list, archive channels
2. **Message dispatch** — send messages with speech act typing
3. **Commitment tracking** — query obligation status
4. **Instance queries** — lookup channel instances
5. **Oversight gates** — create and resolve governance gates
6. **Projection queries** — fold channel history into structured state

`QhorusMcpTools` and `ReactiveQhorusMcpTools` use `@McpServer("qhorus")` named server scoping.

**Do NOT call from internal service code** — these are the MCP tool dispatch layer for external callers (Claude Code) with `@WrapBusinessError` exception semantics. Internal consumers use the service facade interfaces above.
