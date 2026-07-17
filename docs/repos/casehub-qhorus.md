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
| Space | Recursive channel hierarchy grouping related channels with parent/child nesting (max depth 10). `Space` record in `api/channel/`: `id`, `name`, `description`, `parentSpaceId`, `tenancyId`, `createdAt`. `SpaceStore` and `ReactiveSpaceStore` SPIs in `api/store/`; `SpaceService` in runtime (cycle detection, depth validation, subtree depth computation). |
| Message | Speech-act message with a typed intent (query, command, response, etc.) — see ADR-0005. |
| Topic | Named sub-conversation within a channel. `Topic` record in `api/message/`: `id`, `channelId`, `name`, `resolved`, `resolvedAt`, `resolvedBy`, `createdAt`, `tenancyId`. `TopicSummary` record for aggregated views. `TopicStore` SPI. `TopicService` in runtime: resolve/unresolve, rename (cascade to messages), merge (move messages + delete source), move across channels (commitment gate — blocks on open commitments). Default topic is `"general"`. |
| Commitment | Obligation with a defined lifecycle from open through resolution states. |
| CommitmentDeclinedEvent | CDI event record in `api/message/` alongside `CommitmentState`; fired by `CommitmentService.decline()` when a commitment transitions to DECLINED; carries `commitmentId`, `correlationId`, `channelId`, `obligor`, `requester`; consumers observe for scope-calibration signals (trust dimension tracking). Refs qhorus#251. |
| CommitmentExpiredEvent | CDI event record in `api/message/`; fired by `CommitmentService.expireOverdue()` once per expired commitment; carries `commitmentId`, `correlationId`, `channelId`, `obligor` (nullable), `requester`, `expiresAt`; signals deadline-based rerouting and stall detection. Blocks engine#504 and devtown#14. Refs qhorus#281. |
| Instance | Agent registry entry with capability tags and multiple addressing modes. |
| Presence | Caffeine cache-backed agent presence tracking with heartbeat degradation. `Presence` record in `api/channel/`: `memberId`, `status`, `reportedStatus`, `lastSeenAt`, `statusMessage`. `PresenceStatus` enum: ONLINE, AVAILABLE, BUSY, AWAY, OFFLINE. `PresenceService` in runtime: heartbeat (only reportable statuses accepted), effective status computed from elapsed time (awayTimeout -> AWAY, offlineTimeout -> OFFLINE via cache expiry). |
| ChannelMembership | Channel membership with role-based access. `ChannelMembership` record in `api/channel/`: `channelId`, `memberId`, `role`, `tenancyId`, `joinedAt`, `lastReadMessageId`. `MemberRole` enum: PARTICIPANT, OBSERVER, MODERATOR. `ChannelMembershipStore` SPI: put, find, findByChannel, findByMember, updateRole, updateLastReadMessageId, delete, deleteAll. |
| ArtefactRef | Typed artefact reference attached to messages. `ArtefactRef` record in `api/message/`: `uri` (required), `type` (required `ArtefactType`), `label`, `scope` (`SelectionScope`). `ArtefactType` enum: DOCUMENT, CODE, CASE, WORK_ITEM, CHANNEL, MESSAGE, EXTERNAL, DEBATE. `SelectionScope` record: `startLine`, `endLine`, `startOffset`, `endOffset`, `selectedText`. |
| SharedData + ArtefactClaim | Shared artefact store with claim/release lifecycle. |
| Watchdog | Condition-based alert registration. |

See docs/DESIGN.md for channel semantics, message types, commitment state machine, and addressing modes.

### Dispatch Gate

All channel writes flow through a single enforcement gate: `MessageService.dispatch(MessageDispatch)`. In order: paused check → `AllowedWritersPolicy` ACL → `RateLimiter` → LAST_WRITE overwrite semantics → `LedgerWriteService.record()` → `ChannelGateway.fanOut()`. There is no bypass path. `ReactiveMessageService` mirrors this with `dispatch(MessageDispatch) → Uni<DispatchResult>`.

**LAST_WRITE version-aware delivery** (qhorus#313) — `Message.version` counter enables AT_LEAST_ONCE delivery for LAST_WRITE channels. V26 migration.

**Delivery metrics** (qhorus#312) — 4 Micrometer metrics in `DeliveryService`: `qhorus.delivery.messages.delivered` (counter, backendId tag), `qhorus.delivery.failures` (counter, backendId tag), `qhorus.delivery.backends.unhealthy` (gauge), `qhorus.delivery.cursor.lag` (gauge per backend).

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

**`MessageObserver` scope** — `MessageObserver.Scope` enum: `LOCAL` (in-JVM only, zero serialisation) and `CLUSTER` (crosses process/machine boundaries via network transport). The dispatcher discovers all implementations via `@Any Instance<MessageObserver>`. Channel name filtering via `channels()` method (empty = all channels). Three delivery backends implement this SPI: Kafka (`LOCAL` scope — produces to a topic, not cross-node), WebSocket (`CLUSTER` scope), Webhook (`CLUSTER` scope). The dispatcher has a `dispatchClusterOnly()` path for cross-node delivery via `ChannelActivityBroadcaster` SPI.

**`ChannelInitialisedEvent`** — a record in `casehub-qhorus-api` (`io.casehub.qhorus.api.gateway`) fired by `ChannelGateway.initChannel()` on every call — both on channel creation and on startup recovery. External backends observe this via `@Observes ChannelInitialisedEvent` to re-register without implementing their own restart recovery logic.

**Startup recovery** — `ChannelGateway` rebuilds its in-memory registry from the channel store on `@Observes StartupEvent`. Previously the registry was empty after restart until channels were re-created or re-accessed. Each channel init is exception-isolated so a broken observer cannot abort the startup sequence.

**`ChannelService.create()`** — calls `channelGateway.initChannel()` after persist. `ChannelBackend` implementations self-register for runtime-created channels without the caller needing to invoke `initChannel()` explicitly. Refs qhorus#254.

**`findByNamePrefix`** — `ChannelService` and `ReactiveChannelService` expose `findByNamePrefix(prefix)`. The JPA path emits `LIKE 'prefix%' ESCAPE '!'` (metachar-safe, index-eligible). Use when listing channels by namespace prefix (e.g. all channels for a case) without a full table scan.

See docs/DESIGN.md for gateway class structure and SPI contracts.

### Ledger Integration

Every message sent — regardless of type — is recorded as a tamper-evident ledger entry extending `casehub-ledger`. The ledger is the complete, immutable channel history. Telemetry data from structured event messages is extracted and indexed for aggregation queries.

See docs/DESIGN.md for ledger entry structure and query capabilities.

### MCP Tool Surface

Qhorus exposes MCP tools scoped to named server `"qhorus"` via `@McpServer("qhorus")`, across ten capability groups: instance management, channel management, backend management, messaging, shared data, commitments, normative ledger queries, spaces (9 tools: create/list/delete/get/rename/update_description/move_space/move_channel_to_space/list_space_channels), topics (6 tools: list/resolve/unresolve/rename/merge/move), presence (3 tools: set_presence/get_presence/get_channel_presence), and membership (5 tools: join_channel/leave_channel/list_members/mark_channel_read/get_unread_counts). Build-property switching: `QhorusMcpTools` activates when `casehub.qhorus.reactive.enabled` is false/absent; `ReactiveQhorusMcpTools` activates when true.

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

**Topic-aware projections** — `project_channel` MCP tool accepts optional `topic` parameter and `max_messages` limit. Both constraints go on the same `MessageQuery` when both are set. `get_channel_digest` includes `topicBreakdown` (list of `TopicDigest`) in its response. `TopicDigest` carries `name`, `messageCount`, `lastActivityAt`, `resolved`, `resolvedAt`.

Refs: qhorus#230 (projection SPI + `ProjectionService`), qhorus#231 (`ReactiveProjectionService`).

### Store SPIs

Nine store interfaces (blocking and reactive mirrors) in `api/store/` cover the full domain: channels, messages, instances, shared data, watchdogs, commitments, spaces, topics, and channel memberships. Cross-tenant variants (`CrossTenantChannelStore`, `CrossTenantCommitmentStore`, `CrossTenantMessageStore`, `CrossTenantWatchdogStore`) and query types (`api/store/query/`) are co-located. JPA implementations in `runtime/` use `*Entity` suffixed classes (e.g. `ChannelEntity`, `MessageEntity`) to distinguish persistence from domain records. Refs qhorus#314.

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
| `api` | SPIs: `ChannelBackend`, `MessageObserver` (with `Scope.LOCAL`/`CLUSTER` enum and `channels()` filter), `HumanParticipatingChannelBackend`, `ChannelProjection<S>`, `CommitmentAttestationPolicy` (abstract 3-arg: `attestationFor(MessageType, String, CommitmentContext)`; 2-arg default delegates with null; DONE→SOUND, FAILURE/DECLINE/RESPONSE→FLAGGED); Store SPIs in `api/store/` (blocking + reactive mirrors, cross-tenant variants, query types) — including `SpaceStore`/`ReactiveSpaceStore`, `TopicStore`, `ChannelMembershipStore`; Domain records in `api/{channel,message,instance,data,watchdog}/` — `Channel`, `Message`, `Commitment`, `Instance`, `SharedData`, `Watchdog`, `ChannelCreateRequest`, `FindOrCreateResult`, `Space`, `SpaceCreateRequest`, `Presence`, `PresenceStatus`, `ChannelMembership`, `MemberRole`, `Topic`, `TopicSummary`, `ArtefactRef`, `ArtefactType`, `SelectionScope`; Service facades in `api/channel/` and `api/message/` — `ChannelManager`, `ReactiveChannelManager`, `MessageDispatcher`, `ReactiveMessageDispatcher`; DTOs: `MessageView`; Records: `ProjectionResult<S>`, `CommitmentContext` (`api/spi/` — carries `correlationId`, `channelId`, `channelName`, `commitmentId`; passed to `CommitmentAttestationPolicy.attestationFor()` so evidential policy implementations can query the ledger before deciding verdict; refs qhorus#304); domain event types |
| `connectors` | Optional — `WatchdogAlertEvent → ConnectorService.send()` bridge; activates by classpath presence |
| `runtime` | `MessageService`, `ChannelGateway`, `QhorusDashboardService`, `ProjectionService`, `ReactiveProjectionService`, `SpaceService`, `TopicService`, `PresenceService`, `ChannelMembershipService`, ledger integration, MCP tools (scoped to `@McpServer("qhorus")`), A2A endpoint. `QhorusCloudEventAdapter` — `@ApplicationScoped` CDI adapter observing `@ObservesAsync MessageReceivedEvent`, fires `Event<CloudEvent>.fireAsync()` with type `io.casehub.qhorus.message.<messageType>` and source `/casehub-qhorus/channel/<channelId>`; tenancyId extension. `CloudEventMapper` handles the mapping (shared with kafka-observer). **OpenTelemetry** — `QhorusTracingConfig` (`casehub.qhorus.tracing.*`) with per-operation span flags: `enabled` (master switch), `dispatch`, `commitments`, `fanOut`, `ledgerWrite`, `delivery`. All default true. OTel API is an optional dependency. `runtime.audit` package: `EvidentialChecker` (`@DefaultBean @ApplicationScoped`) — two entry points: `check(String messageType, String content, BenchmarkContext)` (benchmark path, Zone 1–3 variants) and `checkObligation(String terminalType, CommitmentContext)` (attestation path vocabulary check). Injectable by consumers (e.g. casehub-devtown pre-attestation checks). Refs qhorus#303. |
| `connector-backend` | Optional — `ConnectorChannelBackend` implements `HumanParticipatingChannelBackend`; bridges `InboundMessage` CDI events (`@ObservesAsync`) from casehub-connectors into Qhorus channel dispatch; self-registers for channels with a `ChannelBackend` type of `CONNECTOR`. `ConnectorQhorusMeshBridge` implements `ConnectorMeshBridge`; posts a STATUS message to the configured delivery channel (`casehub.qhorus.connector-backend.delivery-channel`) after each successful MCP connector delivery; activates by classpath presence alongside `ConnectorChannelBackend`. Activates by classpath presence. |
| `slack-channel` | Optional — `SlackChannelBackend` implements `HumanParticipatingChannelBackend`; delivers outbound messages to Slack threads via `SlackBotClient` with thread continuity through a composite in-memory + DB-backed cache keyed by `(channelId, correlationId)`. `SlackInboundNormaliser` routes thread replies as RESPONSE, new messages as QUERY. REST: `PUT/GET/DELETE /slack-channel/bindings/{channelId}`. Credentials: Tier 1.5 (workspaceId as config key). Activates by classpath presence. Refs qhorus#261. |
| `deployment` | Quarkus extension deployment descriptors |
| `persistence-memory` | Standalone in-memory store implementations (qhorus#169) — `InMemoryMessageStore`, `InMemoryInstanceStore`, `InMemoryChannelStore`, `InMemoryCommitmentStore`, `InMemoryWatchdogStore`, `InMemoryCrossTenantMessageStore`, `InMemoryCrossTenantCommitmentStore`, `InMemoryDeliveryCursorStore`. Moved from `testing/` to a standalone module; `testing/` depends on it transitively. ArtifactId: `casehub-qhorus-persistence-memory`. Changed from test→compile scope in `testing` module (qhorus#322); consumers that relied on transitive export must add direct dependency. |
| `testing` | Test utilities for `@QuarkusTest`. `MessageLedgerEntryTestFactory` is in `casehub-qhorus-testing` (package `io.casehub.qhorus.testing`) — promoted from `runtime/src/test/` to make it available to consumer test suites (qhorus#280). Depends on `persistence-memory` as test scope only (qhorus#322). |
| `kafka-observer` | Optional — `KafkaMessageObserver` implements `MessageObserver` (scope: `LOCAL`). Serialises `MessageReceivedEvent` to CloudEvent via `CloudEventMapper`, produces to `qhorus-messages` channel via SmallRye Reactive Messaging Kafka emitter. Channel name filter via `KafkaObserverConfig.channels()`. Activates by classpath presence. |
| `websocket-observer` | Optional — `WebSocketMessageObserver` implements `MessageObserver` (scope: `CLUSTER`). Pushes events as JSON to subscribed WebSocket connections via `WebSocketConnectionRegistry`. `ChannelWebSocketEndpoint` at `/qhorus/ws/channels/{channelId}` — supports lastEventId catch-up replay: query param `lastEventId` triggers server-side buffering during catch-up, `catchup_begin`/`catchup_end`/`catchup_truncated` control frames, configurable `maxMessages` (default 500) via `WebSocketCatchUpConfig`. Activates by classpath presence. |
| `webhook-observer` | Optional — `WebhookMessageObserver` implements `MessageObserver` (scope: `CLUSTER`). JPA-persisted webhook registrations (`WebhookRegistrationEntity`). `WebhookRegistry` manages registrations with startup DB reload. `WebhookRegistryResource` REST at `/qhorus/webhooks`. HMAC-SHA256 signing via `CredentialResolver` from casehub-platform-api. Delivery on virtual threads with configurable timeout. Activates by classpath presence. |
| `postgres-broadcaster` | Optional — `PostgresChannelActivityBroadcaster` implements `ChannelActivityBroadcaster` SPI for cross-node backend delivery via PostgreSQL LISTEN/NOTIFY (qhorus#162). Exponential backoff reconnection with `closeHandler` stale guard (qhorus#325). Activates by classpath presence. Config prefix: `casehub.qhorus.broadcaster.postgres.*`. |
| `examples` | `@QuarkusTest` integration examples demonstrating channel usage patterns |

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

## Principal Integration

**`QhorusInboundCurrentPrincipal`** — `@DefaultBean @ApplicationScoped` reads `X-Tenancy-ID` header via `TenancyContextFilter @PreMatching` and populates `CurrentPrincipal.tenancyId()` for all HTTP requests. Displaced by any `@Alternative` (test fixtures, `OidcCurrentPrincipal`). Refs qhorus#269.

**Test note:** modules that include both `qhorus` runtime and `casehub-platform` must add `quarkus.arc.exclude-types=io.casehub.platform.mock.MockCurrentPrincipal` in test `application.properties` to prevent CDI ambiguity between `MockCurrentPrincipal @DefaultBean` and `QhorusInboundCurrentPrincipal @DefaultBean`.

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

See [docs/normative-layer.md](https://raw.githubusercontent.com/casehubio/qhorus/main/docs/normative-layer.md).

### Normative Channel Layout

The agent mesh framework defines a 3-channel normative layout implemented via `NormativeChannelLayout` in `casehub-engine-api` (`io.casehub.api.spi.mesh`) and enforced at channel creation:

| Channel suffix | Semantics | `allowedTypes` | `deniedTypes` |
|----------------|-----------|----------------|---------------|
| `/work` | Task assignment and completion (prescriptive) | null (all types permitted) | null |
| `/observe` | Passive monitoring and state sharing (descriptive) | `EVENT` | null |
| `/oversight` | Human governance gates (commitment-based) | null (all deliberative types permitted) | `EVENT` |

Type constraints on `Channel` are enforced at message dispatch time. `deniedTypes` wins when a type appears in both sets. The oversight channel uses `deniedTypes=EVENT` (denylist) rather than `allowedTypes` (allowlist) because an allowlist would block DONE, DECLINE, FAILURE, STATUS, and HANDOFF — all valid deliberative speech acts that governance participants must be able to send. Only EVENT (telemetry, no commitment effect, excluded from `pollAfter` by default) is structurally excluded from the governance channel. See PP-20260604-a7ad99 and GE-20260519-28967d.

See the full agent mesh framework spec: [`casehubio/claudony docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md`](https://github.com/casehubio/claudony/blob/main/docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md).

---

## A2A SSE Streaming (qhorus#147, qhorus#278)

- `GET /a2a/tasks/{id}/stream` — SSE endpoint returning `text/event-stream`
- `streamTask()` is `@RunOnVirtualThread` (not `@Transactional`) — active model: `LinkedBlockingQueue<OutboundMessage>` with `queue::offer`; all SSE writes from one virtual thread
- Named keepalive events (`event: keepalive`) sent every `casehub.qhorus.a2a.sse.heartbeat-interval-seconds` (default 15s) — prevents proxy idle-timeout teardown. SSE comment lines not used (RESTEasy SseEventSource fires handlers for comment-only frames; named events are used instead).
- Orphan detection: `sink.isClosed()` checked each iteration
- Max-duration: `casehub.qhorus.a2a.sse.max-duration-seconds` (default 1800s)
- `A2ATaskState.TERMINAL_TYPES` (Set<MessageType>) and `TERMINAL_STATES` (Set<String>) constants; `fromMessageType(MessageType)` — used by SSE event serialisation
- DECLINE maps to `"cancelled"` (not `"failed"`) across all three A2ATaskState paths
- Known constraint: SSE subscriptions don't survive server restart
- ADRs: 0013 (lazy registration), 0014 (Consumer registry pattern)

## Type-Safe Channel API (qhorus#246, qhorus#247)

- `ChannelCreateRequest.allowedTypes` / `deniedTypes` changed from `String` to `Set<MessageType>`
- `ChannelCreateRequest.barrierContributors`, `allowedWriters`, `adminInstances` changed from `String` to `List<String>`
- `ChannelService.findOrCreateWithBinding()` renamed to `findOrCreate()` with dual-mode lookup; returns `FindOrCreateResult` (in `api/channel/`)
- `MessageType.serializeTypes(Set<MessageType>)` — sorted canonical CSV
- `ChannelService.setTypeConstraints(UUID, Set<MessageType>, Set<MessageType>)` — typed params
- MCP tools parse at boundary; service layer is typed throughout
- `AutoChannelSpec` (connector-backend) also changed to `Set<MessageType>`

## Reactive ObligorTrustPolicy (qhorus#235)

`ReactiveMessageService` trust gate now calls `obligorTrustPolicy.permits()` via `Infrastructure.getDefaultWorkerPool()` — custom policy beans honoured in both blocking and reactive paths. ADR: 0015 (worker-pool delegation).

## CDI Fix (qhorus#276)

`QhorusInboundCurrentPrincipal` changed from `@DefaultBean` to plain `@ApplicationScoped` — prevents CDI ambiguity in consumer apps that also include `casehub-platform` on the classpath.

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
