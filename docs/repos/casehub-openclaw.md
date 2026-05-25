# casehub-openclaw — Platform Deep Dive

**GitHub:** [casehubio/openclaw](https://github.com/casehubio/openclaw)
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Integration tier module (like Claudony). Bridges CaseHub ↔ OpenClaw. Provisions OpenClaw instances as CaseHub workers via `/hooks/agent`; provides `ChannelContextWindow` for cross-channel LLM context injection; implements the `ChannelBackend` SPI for bidirectional Qhorus ↔ OpenClaw wiring; Python SDK component for `before_prompt_build` hook.

---

## Key Abstractions

### Module Structure

| Module | Contents |
|--------|----------|
| `core` | `ChannelContextWindow`, ring buffer persistence, REST context endpoint |
| `casehub` | `ChannelBackend` SPI implementation, `WorkerProvisioner` SPI implementation |
| `app` | Runnable Quarkus application — wires core + casehub modules |
| `python/` | Python SDK — `before_prompt_build` hook, `appendSystemContext` |

### Hook API

| Endpoint | Direction | Purpose |
|----------|-----------|---------|
| `POST /hooks/agent` | CaseHub → OpenClaw | Deliver a case step prompt to a running OpenClaw agent |
| `POST /hooks/wake` | CaseHub → OpenClaw | Wake a dormant agent with context |
| `deliver:webhook` | OpenClaw → CaseHub | Heartbeat or result delivery from an autonomous agent |

### ChannelContextWindow

`MessageObserver` implementation that maintains a ring buffer of recent cross-channel messages. Persisted for durability. Exposed as `GET /channel-context/{agentId}?since={seq}` — the Python SDK calls this before prompt construction to inject relevant channel history into the system context.

### ChannelBackend SPI

Implements the Qhorus `ChannelBackend` SPI to wire bidirectional message flow between a Qhorus channel and an OpenClaw agent. Inbound (CaseHub → OpenClaw) routes via `/hooks/agent`. Outbound (OpenClaw → CaseHub) routes via the `deliver:webhook` normaliser.

### Python SDK

Hooks into OpenClaw's `before_prompt_build` lifecycle. Calls `GET /channel-context/{agentId}` and invokes `appendSystemContext` to prepend the CaseHub channel window to the agent's system prompt before each LLM call.

---

## Two Invocation Modes

**Heartbeat (OpenClaw autonomous → CaseHub):** An OpenClaw agent running autonomously produces output and delivers it via `deliver:webhook`. The integration layer normalises the payload and creates a CaseHub case to track the work.

**Direct call (CaseHub case step → OpenClaw):** A running CaseHub case reaches a step that routes to an OpenClaw agent. The integration layer calls `POST /hooks/agent` with the step context as the agent prompt.

These two modes are mutually exclusive per invocation. A given agent interaction is either initiated by OpenClaw or by CaseHub — never both simultaneously. This is the golden rule for reasoning about invocation flow.

---

## Depends On

- `casehub-qhorus` — mandatory (`ChannelBackend` SPI, `MessageObserver` SPI)
- `casehub-engine` — `WorkerProvisioner` SPI, `CaseChannelProvider` SPI, `WorkerStatusListener` SPI
- `casehub-platform-api` — `CurrentPrincipal`, `GroupMembershipProvider` for permission-aware context injection

## Depended On By

| Repo | How |
|------|-----|
| `casehub-life` | As `WorkerProvisioner` — OpenClaw agents as household and care task workers |
| Any application repo | Any application using OpenClaw as its execution layer |

---

## What This Repo Explicitly Does NOT Do

- Replace Claudony — different worker types (Claude CLI vs OpenClaw agents); both are valid `WorkerProvisioner` implementations
- Implement OpenClaw's skill engine — executes skills via `/hooks/agent` prompt routing; skill authoring and packaging is OpenClaw's concern
- Own Qhorus channel semantics or the commitment lifecycle — those belong to casehub-qhorus
- Own case orchestration or `CasePlanModel` — that is casehub-engine

---

## Named Datasource

`openclaw` — used by `ChannelContextWindow` for ring buffer persistence. Never share with domain tables.

---

## Current State

Scaffold only — Epic 1 complete (Maven structure, CLAUDE.md, CI). No implementation yet.

---

## Design Documents

- `docs/specs/openclaw-integration.md` — integration architecture and hook API
- `docs/specs/openclaw-skill-pack.md` — skill pack structure and routing
- Research spec in `casehubio/parent` — original scoping analysis
