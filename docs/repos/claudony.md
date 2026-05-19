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
| `claudony-core` | Session lifecycle management — tmux session control, registry, and expiry policy SPI |
| `claudony-casehub` | Implements the 4 casehub-engine worker provisioner SPIs |
| `claudony-app` | Quarkus application: authentication, session API, WebSocket streaming, MCP server, fleet management, browser dashboard |

---

## Key Abstractions

### Core (`claudony-core`)

Manages tmux session lifecycle: starting, stopping, and expiring sessions. A pluggable expiry policy SPI controls when sessions are considered idle. On restart, the registry is repopulated from live tmux sessions — tmux is the source of truth, independent of the Quarkus process.

See `docs/DESIGN.md` for class structure and expiry policy implementations.

### CaseHub SPI Implementations (`claudony-casehub`)

Implements all 4 casehub-engine worker provisioner SPIs:
- **WorkerProvisioner** — creates a tmux session running the Claude CLI
- **CaseChannelProvider** — creates a Qhorus channel per case/purpose
- **WorkerContextProvider** — builds the Claude startup prompt from ledger lineage
- **WorkerStatusListener** — maps tmux lifecycle events to CaseHub worker states

See `docs/DESIGN.md` for the implementation details and the ledger lineage query interface.

### Application (`claudony-app`)

REST and WebSocket endpoints for session management and terminal streaming. WebAuthn passkey authentication for browser access; API key authentication for agent access. An MCP server exposes session management tools to a controller Claude instance. Fleet management handles multi-node peer discovery and health monitoring. A browser dashboard surfaces session cards, PR/CI status, and service health.

See `docs/DESIGN.md` for the endpoint inventory and authentication mechanism detail.

---

## Depends On

| Repo | How |
|---|---|
| `casehub-qhorus` | Embedded directly; named `qhorus` datasource |
| `casehub-engine` | Implements its 4 worker provisioner SPIs |
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

## Current State

- 339+ tests passing (38 in `claudony-casehub` + 301 in `claudony-app`)
- Core complete: session management, WebSocket streaming, WebAuthn, fleet, CaseHub SPI wiring
- ADR-0005: CaseHub integration is optional — Claudony works as a standalone session manager without CaseHub

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/claudony/main/docs/DESIGN.md) — integration architecture, CaseHub SPI implementations, three-panel dashboard plan
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/claudony/main/adr/INDEX.md) — architectural decision records
