# claudony — Platform Deep Dive

**GitHub:** [casehubio/claudony](https://github.com/casehubio/claudony)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/casehub-parent/main/docs/PLATFORM.md)

---

## Purpose

Integration layer and operational dashboard. Runs Claude Code CLI sessions remotely via tmux, wires CaseHub + Qhorus together, and surfaces all three in a browser/PWA dashboard. The integration terminus — nothing depends on Claudony.

Two modes from one binary: **server** (owns sessions, WebSocket streaming, dashboard) and **agent** (MCP endpoint for a controller Claude instance).

---

## Module Structure

| Module | Purpose |
|---|---|
| `claudony-core` | `TmuxService`, `SessionRegistry`, `ExpiryPolicy` SPI + scheduler |
| `claudony-casehub` | Implements all 4 casehub-engine worker provisioner SPIs |
| `claudony-app` | Quarkus application: auth, fleet, MCP server, dashboard frontend |

---

## Key Abstractions

### Core (`claudony-core`)

| Class | Purpose |
|---|---|
| `TmuxService` | `ProcessBuilder` wrappers for all tmux commands |
| `SessionRegistry` | In-memory `ConcurrentHashMap<UUID, Session>` |
| `ExpiryPolicy` | SPI with 3 implementations: user-interaction, terminal-output, status-aware |
| `SessionIdleScheduler` | `@Scheduled` expiry enforcement |

**tmux is the source of truth.** Sessions live in tmux independent of the Quarkus process. On restart, `ServerStartup.bootstrapRegistry()` repopulates from `tmux list-sessions` (sessions with `claudony-` prefix).

### CaseHub SPI Implementations (`claudony-casehub`)

| Implementation | SPI | Behaviour |
|---|---|---|
| `ClaudonyWorkerProvisioner` | `WorkerProvisioner` | Creates tmux session running `claude` binary |
| `ClaudonyCaseChannelProvider` | `CaseChannelProvider` | Creates Qhorus channel named `case-{caseId}/{purpose}` |
| `ClaudonyWorkerContextProvider` | `WorkerContextProvider` | Builds Claude startup prompt from ledger lineage + channel name |
| `ClaudonyWorkerStatusListener` | `WorkerStatusListener` | Maps tmux lifecycle → CaseHub worker states; fires `WorkerStalledEvent` |
| `CaseLineageQuery` | Interface | Prior worker query — default: `EmptyCaseLineageQuery` (no-op); swap for JPA impl with casehub datasource |

### Application (`claudony-app`)

| Area | Classes | Purpose |
|---|---|---|
| Sessions | `SessionResource`, `TerminalWebSocket` | REST `/api/sessions`, WebSocket `/ws/{id}` (pipe-pane + FIFO streaming) |
| Auth | `ApiKeyAuthMechanism`, `AuthResource`, `CredentialStore` | WebAuthn passkeys (browser) + `X-Api-Key` (agent) |
| MCP | `McpServer` | 8 MCP tools for session management — exposes to controller Claude |
| Fleet | `PeerRegistry`, `PeerHealthScheduler`, `PeerResource` | Multi-node peer discovery and health |
| Dashboard | `index.html`, `dashboard.js` | Session cards, PR/CI status, service health |

---

## Depends On

| Repo | How |
|---|---|
| `quarkus-qhorus` | Embedded directly; named `qhorus` datasource |
| `casehub-engine` | Implements its 4 worker provisioner SPIs |
| `quarkus-ledger` | Transitively via Qhorus (`AgentMessageLedgerEntry`) and casehub-ledger |

## Depended On By

Nothing — Claudony is the integration terminus.

---

## What This Repo Explicitly Does NOT Do

- Define orchestration rules (that is casehub-engine)
- Define agent messaging protocols (that is quarkus-qhorus)
- Own audit ledger logic (that is quarkus-ledger)
- Manage human task inboxes (that is casehub-work)
- Reimplement channel, message, or commitment logic — Qhorus handles all of that

`TmuxService` and `SessionRegistry` are deliberately kept free of CaseHub/Qhorus concepts. The CaseHub wiring lives in `claudony-casehub` as a clean SPI implementation layer.

---

## Persistence Model

Three named persistence units:
- `claudony` datasource — auth, sessions (in-memory `SessionRegistry` + file `~/.claudony/credentials.json`)
- `qhorus` datasource — Qhorus H2 file database (`~/.claudony/qhorus`)
- Optional engine datasource — when CaseHub active

```properties
quarkus.hibernate-orm.qhorus.packages=io.quarkiverse.qhorus.runtime,io.quarkiverse.ledger.runtime.model,io.casehub.ledger.model
quarkus.flyway.qhorus.migrate-at-start=true
```

---

## Terminal Streaming (No PTY)

tmux does not expose a PTY to ProcessBuilder. Streaming uses:
- **Output:** `tmux pipe-pane` → FIFO → Java virtual thread → WebSocket
- **Input:** `tmux send-keys -t name -l "text"` (`-l` flag = literal mode, critical)
- **History on reconnect:** `tmux capture-pane -e -p -S -100` — sent synchronously before starting pipe-pane to avoid race conditions

---

## Authentication

- Browser: WebAuthn passkeys via `quarkus-security-webauthn` + `LenientNoneAttestation`
- Agent→Server: `X-Api-Key` header via `ApiKeyAuthMechanism`
- Rate limiting: sliding-window `AuthRateLimiter` on WebAuthn paths

---

## MCP Transport

`POST /mcp` (HTTP JSON-RPC) — not stdio. GraalVM-native compatible. Controller Claude connects as an MCP server consumer.

---

## Known Gaps

- Three-panel dashboard (CaseHub case graph + terminal + side panel) not yet built
- Worker↔Session↔Channel triple-link not stored on `Session` model (needed for the case graph panel)
- `ClaudonyWorkerProvisioner.provision()` does not store `caseWorkerId` on the session
- `casehub-work-casehub` adapter — planned bridge from WorkItemLifecycleEvent to CaseHub; blocked on CaseHub stability

---

## Current State

- 339+ tests passing (38 in `claudony-casehub` + 301 in `claudony-app`)
- Core complete: session management, WebSocket streaming, WebAuthn, fleet, CaseHub SPI wiring
- ADR-0005: CaseHub integration is optional — Claudony works as a standalone session manager without CaseHub

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/claudony/main/docs/DESIGN.md) — integration architecture, CaseHub SPI implementations, three-panel dashboard plan
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/claudony/main/adr/INDEX.md) — architectural decision records
