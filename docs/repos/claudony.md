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
- **CaseChannelProvider** — creates a Qhorus channel per case/purpose; `postToChannel` receives `correlationId` and `deadline` as first-class params (engine#343) — no longer parsed from content JSON
- **WorkerContextProvider** — builds the Claude startup prompt from ledger lineage
- **WorkerStatusListener** — maps tmux lifecycle events to CaseHub worker states

See `docs/DESIGN.md` for the implementation details and the ledger lineage query interface.

### Application (`claudony-app`)

REST and WebSocket endpoints for session management and terminal streaming. WebAuthn passkey authentication for browser access; API key authentication for agent access. An MCP server exposes session management tools to a controller Claude instance. Fleet management handles multi-node peer discovery and health monitoring. A browser dashboard surfaces session cards, PR/CI status, and service health.

`MeshResource` exposes the Qhorus mesh data to the dashboard via `QhorusDashboardService` — the correct consumer integration tier for dashboard/UI code (not `ReactiveQhorusMcpTools`, which is the MCP protocol dispatch layer for Claude Code). See `docs/protocols/casehub/qhorus-consumer-integration-pattern.md`.

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

## Agent Mesh Framework

Claudony is the normative reference implementation of the CaseHub agent mesh framework — the pattern for how Claude instances communicate with each other and with the platform in a production multi-agent deployment.

**Key SPIs (defined in `claudony-casehub`):**
- `CaseChannelLayout` — declares the channel topology for a case type: which channels to create, their semantics (work / observe / oversight), and allowed speech-act types per channel
- `MeshParticipationStrategy` — governs how a Claude instance joins and leaves the mesh: channel subscription, capability announcement, session lifecycle hooks

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

- 475+ tests passing (4 in `claudony-core` + 130 in `claudony-casehub` + 341 in `claudony-app`)
- Core complete: session management, WebSocket streaming, WebAuthn, fleet, CaseHub SPI wiring
- ADR-0005: CaseHub integration is optional — Claudony works as a standalone session manager without CaseHub

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/claudony/main/docs/DESIGN.md) — integration architecture, CaseHub SPI implementations, three-panel dashboard plan
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/claudony/main/adr/INDEX.md) — architectural decision records
