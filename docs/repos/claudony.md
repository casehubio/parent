# claudony — Platform Deep Dive

**GitHub:** [casehubio/claudony](https://github.com/casehubio/claudony)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Integration layer and operational dashboard. Runs Claude Code CLI sessions remotely via tmux, wires CaseHub + Qhorus together, and surfaces all three in a browser/PWA dashboard. The integration terminus — nothing depends on Claudony.

Two modes from one binary: **server** (owns sessions, WebSocket streaming, dashboard) and **agent** (MCP endpoint for a controller Claude instance).

---

## Module Structure

| Module | Purpose |
|---|---|
| `claudony-core` | Session lifecycle management — tmux session control, registry and expiry policy SPI, `TenantContext` SPI with tenant-filtered `SessionRegistry` |
| `claudony-casehub` | Implements the 4 casehub-engine worker provisioner SPIs |
| `claudony-app` | Quarkus application: authentication, session API, WebSocket streaming, MCP server, fleet management, browser dashboard |

---

## Key Abstractions

### Core (`claudony-core`)

Manages tmux session lifecycle: starting, stopping, and expiring sessions. A pluggable expiry policy SPI controls when sessions are considered idle. On restart, the registry is repopulated from live tmux sessions — tmux is the source of truth, independent of the Quarkus process. `TenantContext` SPI (`currentTenantId()`) with `DefaultTenantContext @ApplicationScoped` — delegates to `CurrentPrincipal.tenancyId()` when request scope is active, falls back to `TenancyConstants.DEFAULT_TENANT_ID` outside request context. `SessionRegistry` now filters `all()`/`find()`/`findByCaseId()` by tenant unconditionally; `allUnscoped()`/`findUnscoped()`/`existsByName()` for system operations (claudony#121).

See `docs/DESIGN.md` for class structure and expiry policy implementations.

### CaseHub SPI Implementations (`claudony-casehub`)

Implements all casehub-engine worker provisioner and execution SPIs:
- **`ClaudonyReactiveWorkerProvisioner`** (`WorkerProvisioner`) — creates a tmux session running the Claude CLI. `provision()` uses `Uni.combine()` to run `setupSession()` (blocking tmux IO, worker pool) and `QhorusCausalLinkResolver.resolve()` (reactive Qhorus DB, event loop) concurrently; resolver must be called from the event loop (before `runSubscriptionOn(workerPool)`) for `@WithSession("qhorus")` to hold the correct Vert.x safe sub-context (see protocol PP-20260616-d32bc3).
- **`QhorusCausalLinkResolver`** (`@ApplicationScoped`) — resolves `causedByEntryId` for each provisioned worker by looking up the Qhorus `MessageLedgerEntry` via `ReactiveMessageLedgerEntryRepository.findLatestByCorrelationId(channelId, correlationId, null)`, using `triggerChannelId` and `triggerCorrelationId` fields threaded through `ProvisionContext` by the engine (engine#231). Result stored in `causalContext: ConcurrentHashMap<CausalKey, UUID>` (where `CausalKey(tenancyId, caseId)`) in the provisioner; drained by `ClaudonyLedgerEventCapture` on `WorkerStarted` to set `CaseLedgerEntry.causedByEntryId`. The `causalContext` side-channel is permanent — `CaseLifecycleEvent` must not carry consumer-specific fields (engine#389). Establishes the W3C PROV-DM causal chain: COMMAND → WorkerStarted → CaseLedgerEntry (claudony#94).
- **`ClaudonyWorkerExecutionManager`** (`WorkerExecutionManager`) — virtual thread watcher; when a tmux session exits, stores `pendingExitSignals.put(caseId, roleName)` before publishing `WorkflowExecutionCompleted`; supports recovery after server restart via tmux session options (claudony#146)
- **`ClaudonyLedgerEventCapture`** — replaces casehub-ledger's excluded `CaseLedgerEventCapture`; on `WorkerExecutionCompleted`, drains `pendingExitSignals` and calls `CaseHubRuntime.signal('workers.<role>.exited', true)`, patching case context and triggering goal evaluation (`ConcurrentHashMap` drain pattern, same as `drainCausalContext`)
- **`CasehubStartupService`** — plain Java extraction from `ServerStartup.bootstrapCasehubWatchers()`; iterates registry on startup and restarts exit watchers for in-flight workers after server restart
- **`AgentCase`** — first production CaseHub case definition in claudony; extends `YamlCaseHub`; triggers on `.topic != null`; auto-completes when `workers.agent.exited == true` (claudony#148, renamed from `ResearcherCase` in claudony#150)
- **`CaseChannelProvider`** — creates a Qhorus channel per case/purpose; `postToChannel` receives `correlationId` and `deadline` as first-class params (engine#343) — no longer parsed from content JSON
- **`WorkerContextProvider`** — builds the Claude startup prompt from ledger lineage
- **`WorkerStatusListener`** — maps tmux lifecycle events to CaseHub worker states

See `docs/DESIGN.md` for the implementation details and the ledger lineage query interface.

### Application (`claudony-app`)

REST and WebSocket endpoints for session management and terminal streaming. WebAuthn passkey authentication for browser access; API key authentication for agent access. An MCP server exposes session management tools to a controller Claude instance. Fleet management handles multi-node peer discovery and health monitoring. A browser dashboard surfaces session cards, PR/CI status, and service health.

- `FleetMessageRelayObserver` — CLUSTER-scoped `MessageObserver` SPI implementation; on every Qhorus message dispatch, relays a channel-name tick to all healthy fleet peers via `POST /api/internal/channels/notify`. Enables real-time SSE delivery of `ChannelEventBus` ticks across fleet nodes when Qhorus shares a PostgreSQL instance (claudony#118).
- `ChannelSyncResource` has two endpoints: `POST /sync` (channel init, registers `ClaudonyChannelBackend`) and `POST /notify` (cross-node tick relay from `FleetMessageRelayObserver`).

`MeshResource` exposes the Qhorus mesh data to the dashboard via `QhorusDashboardService` — the correct consumer integration tier for dashboard/UI code (not `ReactiveQhorusMcpTools`, which is the MCP protocol dispatch layer for Claude Code). See `casehub/garden: docs/protocols/casehub/qhorus-consumer-integration-pattern.md`.

See `docs/DESIGN.md` for the endpoint inventory and authentication mechanism detail.

---

## Recent Features

**Pages/Quinoa adoption (claudony#161)** — migrated browser dashboard from hand-coded HTML to casehub-pages DSL. UI composition via `page()`, `tabs()`, `table()`, `metric()` primitives. Built with Quinoa (Quarkus frontend integration) — TypeScript compiled with esbuild, hot-reload in dev mode. Dashboard shows session cards, PR/CI status, service health.

**Multi-tenancy foundation (claudony#121)** — tenancyId enforcement throughout:
- `TenantContext` SPI with `DefaultTenantContext @ApplicationScoped` — delegates to `CurrentPrincipal.tenancyId()` when request scope is active, falls back to `TenancyConstants.DEFAULT_TENANT_ID` outside request context
- `SessionRegistry` filters `all()`/`find()`/`findByCaseId()` by tenant unconditionally
- `allUnscoped()`/`findUnscoped()`/`existsByName()` for system operations (cross-tenant admin, health checks)

**ProvisionerConfigRegistry SPI infrastructure (claudony#164, #163, #156)** — three-phase provisioner config model:
- `ProviderConfigSource` SPI — query interface for provisioner parameters (LLM provider, model, temperature, max tokens)
- `CompositeProviderConfigSource` — aggregates multiple sources, precedence-ordered (env vars → tenant prefs → system defaults)
- `WorkerContextProvider` — builds Claude startup prompt from ledger lineage + mesh system prompt (three-layer model: system + tenant + case)
- Removes `WorkerCommandResolver` — consolidated into `ProviderConfigSource` SPI

**casehub-qhorus-postgres-broadcaster migration** — Qhorus `casehub-qhorus-postgres-broadcaster` dependency added as compile-scope in `app/pom.xml` for LISTEN/NOTIFY cross-instance event fan-out.

**Separate Claudony and Qhorus MCP endpoints** — two distinct MCP server endpoints: Claudony MCP at `/mcp` (8 tools via `ClaudonyMcpTools`, `quarkus.mcp.server.server-info.name=claudony`), Qhorus MCP at `/qhorus` (40+ Qhorus tools, `serverInfo.name=qhorus`). Multi-server routing handled by `HttpMcpServerProcessor` build step iterating `config.servers()`. `McpServerIntegrationTest.qhorusToolsAvailableAtSeparateEndpoint()` verifies isolation.

**CasehubEnabledProfile** — test profile in `CaseEngineRoundTripTest` that implements `QuarkusTestProfile`; overrides config to enable CaseHub engine integration (`claudony.casehub.enabled=true`), configures agent command, fast poll intervals, agent mode, engine CDI indexing, and a custom `quarkus.arc.exclude-types` list that re-includes engine beans needed for round-trip tests.

**CaseHubRuntimeCompat** (`claudony-casehub`) — reflection-based compat shim for `CaseHubRuntime.signal()` that handles both void and `CompletionStage` return types across SNAPSHOT builds.

**Worker migration to `@WorkerBackend`** — `ClaudonyWorkerExecutionManager` annotated `@WorkerBackend @Priority(10) @ApplicationScoped` (qualifier from `io.casehub.engine.common.spi.scheduler.WorkerBackend`). Injected via `@Inject @WorkerBackend` in `ClaudonyLedgerEventCapture`, `ClaudonyReactiveWorkerProvisioner`, and `CaseEngineRoundTripTest`.

**System prompt delivery — three-layer prompt model:**
1. **`MeshSystemPromptTemplate`** — generates structured prompt based on `MeshParticipation` (ACTIVE: ROLE + MESH CHANNELS + STARTUP + PRIOR WORKERS + MESSAGE DISCIPLINE; REACTIVE: ROLE + MESH CHANNELS (respond when addressed) + PRIOR WORKERS; SILENT: no prompt)
2. **`ClaudonyProviderConfig`** — per-agent `systemPrompt` (`--system-prompt` CLI flag) and `appendSystemPrompt` (`--append-system-prompt` CLI flag)
3. **`WorkerCommandBuilder.mergeAppendPrompts()`** — merges static `appendSystemPrompt` config with dynamic mesh prompt into final CLI arguments

Assembly path: `ClaudonyReactiveWorkerContextProvider.buildContext()` → queries lineage + channels → `MeshSystemPromptTemplate.generate()` → stores in `WorkerContext.properties()` → provisioner passes as `dynamicAppendPrompt` to `WorkerCommandBuilder.build()`.

---

## Depends On

| Repo | How |
|---|---|
| `casehub-qhorus` | Embedded directly; named `qhorus` datasource |
| `casehub-qhorus-postgres-broadcaster` | LISTEN/NOTIFY cross-instance event fan-out |
| `casehub-engine` | Implements its 4 worker provisioner SPIs; `@WorkerBackend` qualifier |
| `casehub-ledger` | Transitively via Qhorus (agent message ledger entries) and casehub-ledger |

## Depended On By

Nothing — Claudony is the integration terminus.

---

## What This Repo Explicitly Does NOT Do

- Define orchestration rules (that is casehub-engine)
- Define agent messaging protocols (that is casehub-qhorus)
- Own audit ledger logic (that is casehub-ledger)
- Manage human task inboxes (that is casehub-work)
- Reimplement channel, message, or commitment logic — Qhorus handles all of that

The tmux session layer is deliberately kept free of CaseHub/Qhorus concepts. The CaseHub wiring lives in `claudony-casehub` as a clean SPI implementation layer.

---

## Persistence Model

Three named persistence units: `claudony` (auth, sessions), `qhorus` (Qhorus message store), and an optional engine datasource when CaseHub is active.

See `docs/DESIGN.md` for datasource configuration.

---

## Terminal Streaming (No PTY)

tmux does not expose a PTY to the Quarkus process. Streaming uses:
- **Output:** `tmux pipe-pane` → FIFO → Java virtual thread → WebSocket
- **Input:** `tmux send-keys` in literal mode
- **History on reconnect:** captured synchronously before starting pipe-pane to avoid race conditions

---

## Authentication

- Browser: WebAuthn passkeys via `quarkus-security-webauthn`
- Agent→Server: `X-Api-Key` header
- Rate limiting: sliding-window rate limiter on WebAuthn paths

---

## MCP Transport

`POST /mcp` (HTTP JSON-RPC) — not stdio. GraalVM-native compatible. Controller Claude connects as an MCP server consumer.

---

## Known Gaps

- Three-panel dashboard (CaseHub case graph + terminal + side panel) not yet built
- Worker↔Session↔Channel triple-link not stored on the session model (needed for the case graph panel)
- Worker provisioner does not store the CaseHub worker ID on the session
- `casehub-work-casehub` adapter — planned bridge from WorkItemLifecycleEvent to CaseHub; blocked on CaseHub stability

---

## Agent Mesh Framework

Claudony is the normative reference implementation of the CaseHub agent mesh framework — the pattern for how Claude instances communicate with each other and with the platform in a production multi-agent deployment.

**Platform SPIs (defined in `casehub-engine-api`, `io.casehub.api.spi.mesh`):**
- `CaseChannelLayout` — SPI declaring the channel topology for an agent case. Canonical implementations `NormativeChannelLayout` (work/observe/oversight) and `SimpleLayout` (work/observe) live in engine-api. Claudony uses `CaseChannelLayout.named("simple")` for lightweight cases; the `SimpleLayout` implementation is resolved from engine-api.
- `MeshParticipationStrategy` — SPI governing agent participation level (ACTIVE/REACTIVE/SILENT). Standard implementations in engine-api. Claudony's `ClaudonyReactiveWorkerContextProvider` selects via `MeshParticipationStrategy.named(config.meshParticipation())`.

**Normative channel layout (3-channel pattern):**

| Channel suffix | Semantics | Agent speech acts |
|----------------|-----------|-------------------|
| `/work` | Task assignment and completion | COMMAND, RESPONSE, DONE, DECLINE |
| `/observe` | Passive state broadcast | EVENT, INFORM |
| `/oversight` | Human governance gate | COMMAND (to human), RESPONSE (from human) |

`allowedTypes` on each `Channel` enforces this at the Qhorus layer — messages outside the declared types are rejected.

Full specification: [`docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md`](https://github.com/casehubio/claudony/blob/main/docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md)

Related epics: [claudony#86](https://github.com/casehubio/claudony/issues/86) (framework epic), [claudony#90](https://github.com/casehubio/claudony/issues/90) (`sessionMeta` caseId propagation requirement).

---

## Current State

- 703 tests passing (16 in `claudony-core` + 163 in `claudony-casehub` + 408 in `claudony-app` + integration, as of claudony#121 multi-tenancy foundation)
- Core complete: session management, WebSocket streaming, WebAuthn, fleet, CaseHub SPI wiring
- ADR-0005: CaseHub integration is optional — Claudony works as a standalone session manager without CaseHub

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/claudony/main/docs/DESIGN.md) — integration architecture, CaseHub SPI implementations, three-panel dashboard plan
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/claudony/main/adr/INDEX.md) — architectural decision records
