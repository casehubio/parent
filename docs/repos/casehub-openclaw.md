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
| `core` | `ContextMessage`, `WindowContent`, `ChannelRingBuffer`, `ChannelContextWindowService`, `OpenClawHookClient`, REST context endpoint. `OpenClawHookClient.invoke()` has a 5-arg overload accepting explicit `deliveryUrl` — used by `OversightGateService` for oversight delivery. `OpenClawCasehubConfig.Oversight` group: `Optional<String> agentId()` (dedicated messaging agent for oversight; falls back to work agent if absent). |
| `casehub` | `ChannelContextWindowObserver` (`MessageObserver` SPI), `OpenClawChannelBackend` (`ChannelBackend` SPI), `OpenClawWorkerProvisioner`, `OpenClawCaseChannelProvider`, `OpenClawWorkerStatusListener`, `OpenClawAgentRegistry` (tracks agentId → session registration). **Epic 6:** `OversightGateService` — `evaluate()` archives deliver:webhook text as non-resolving STATUS (no commitment state change); `fulfill()` processes human oversight gate responses (Phase 2 gate entry wiring deferred to openclaw#30). `CaseChannelNames` (package-private channel name utility). |
| `app` | Runnable Quarkus application — wires core + casehub modules. REST endpoints: `POST /openclaw/delivery/channel/{channelId}` (deliver:webhook → `OversightGateService.evaluate()`), `POST /openclaw/delivery/oversight/{gateId}` (oversight response → `OversightGateService.fulfill()`), `GET /channel-context/{agentId}?since={seq}` |
| `plugin/` | TypeScript OpenClaw plugin — `before_prompt_build` hook via Plugin SDK; published to npm. TypeScript-only due to OpenClaw Plugin SDK design — see ADR 0001. |
| `python/` | Python channel client library (thin HTTP wrapper); published to PyPI. No hook registration (hooks are TypeScript-only). |

### Hook API

| Endpoint | Direction | Purpose |
|----------|-----------|---------|
| `POST /hooks/agent` | CaseHub → OpenClaw | Deliver a case step prompt to a running OpenClaw agent |
| `POST /hooks/wake` | CaseHub → OpenClaw | Wake a dormant agent with context |
| `deliver:webhook` | OpenClaw → CaseHub | Heartbeat or result delivery from an autonomous agent |

### ChannelContextWindow

`MessageObserver` implementation (`ChannelContextWindowObserver`) that maintains an in-memory ring buffer of recent cross-channel messages. In-memory only, best-effort — no JPA, no Flyway, no named datasource. Correctness layer is Qhorus (ledger); `ChannelContextWindow` is the intelligence layer only. Exposed as `GET /channel-context/{agentId}?since={seq}` — the Python SDK calls this before prompt construction to inject relevant channel history into the system context.

**Association design:** two-phase binding managed across the `casehub` module SPIs: `bindAgent(agentId, caseId)` is called by `OpenClawWorkerProvisioner` at provision time; `bindChannel(caseId, channelId)` is called by `OpenClawCaseChannelProvider` when the channel is assigned. `ChannelContextWindowService` joins at query time — no cross-SPI coordination at write time. `unbindAgent()` is called by `OpenClawWorkerStatusListener.onWorkerCompleted()` for cleanup.

### OpenClawHookClient (Epic 2)

`@ApplicationScoped` CDI bean. `ConcurrentHashMap<String, OpenClawSession>` keyed by `agentId`. `registerSession(agentId, sessionKey, webhookUrl)` called by `WorkerProvisioner` at provision time. `invoke()` catches `WebApplicationException` (Quarkus REST Client behaviour on 5xx — does not return a `Response`). `Response.close()` called in `finally` block (`jakarta.ws.rs.core.Response` does not implement `AutoCloseable`). `forWebhook()` factory on `AgentInvocationRequest` enforces `deliver=webhook`.

**Known limitation:** Session registry is last-write-wins per `agentId` — concurrent same-`agentId` workers not supported until `workerId` is available in `WorkResult` (upstream engine enhancement).

**Deferred (verify against live API):** `sessionName` JSON field name; `wakeMode` values for direct-call pattern; `/hooks/wake` body schema.

### ChannelBackend SPI

Implements the Qhorus `ChannelBackend` SPI to wire bidirectional message flow between a Qhorus channel and an OpenClaw agent. Inbound (CaseHub → OpenClaw) routes via `/hooks/agent`. Outbound (OpenClaw → CaseHub) routes via the `deliver:webhook` normaliser.

### Oversight Gate (Epic 6)

`OversightGateService` owns the gate lifecycle:

- `evaluate(workChannelId, agentId, output)` — called by the delivery webhook for every OpenClaw result: archives the agent text output as a non-resolving STATUS message on the work channel. Completion signaling is via MCP tool calls (`casehub_done`, `casehub_reject`, etc.) — no speech-act classification occurs. `commitmentId` is injected into the COMMAND message by `OpenClawChannelBackend.post()`.
- `fulfill(gateId, rawOutput)` — called by the oversight delivery webhook when human responds:
  1. Parse approval (first word must be `"approved"`; null/blank → rejected)
  2. Look up `Commitment` by `correlationId=gateId` (durable — survives restart)
  3. Dispatch RESPONSE/DECLINE to oversight (closes Commitment) + STATUS to work channel

**Known limitation:** STATUS dispatched to work channel instead of DONE because `inReplyTo` (original COMMAND message ID) is not available at delivery time (openclaw#16).

### Layer 0 — Quarkus MCP Endpoint (Epic 7)

Exposes CaseHub accountability primitives as MCP tools and resources. Implements Direction 2 of the CaseHub ↔ OpenClaw integration: OpenClaw agents calling CaseHub.

**Transport:** `POST /mcp` — streamable-HTTP via `quarkus-mcp-server`.

**Tools:**

| Tool | Purpose |
|------|---------|
| `casehub_commit` | Declare a commitment for a channel |
| `casehub_done` | Mark a commitment fulfilled |
| `casehub_reject` | Decline/reject a commitment |
| `casehub_checkpoint` | Record a progress checkpoint |
| `casehub_escalate` | Escalate to oversight channel |
| `casehub_create_workitem` | Create a human WorkItem |
| `casehub_open_case` | Open a new case instance |
| `casehub_status` | Query agent commitment status |
| `casehub_queue` | Queue a task for deferred execution |

**Resources:**

| URI | What it exposes |
|-----|----------------|
| `casehub://agent/{id}/commitments` | Active commitments for a given agent |
| `casehub://agent/{id}/cases` | Open cases for a given agent |
| `casehub://channel/{id}/recent` | Recent messages in a channel |

**Plugin hooks (TypeScript):**

| Hook | Role |
|------|------|
| `before_tool_call` | Pre-flight commitment check before tool execution |
| `agent_end` | Flush pending commitments on session close |
| `session_start` | Bootstrap session context and active commitments |
| `heartbeat_prompt_contribution` | Inject commitment state into recurring heartbeat prompts |

Global SKILL.md files (stateless) drive the agent's accountability behaviour via the MCP layer. See `docs/specs/openclaw-skill-pack.md`.

### Plugin SDK (Epic 5)

TypeScript `before_prompt_build` hook implemented via OpenClaw Plugin SDK in `plugin/`. Calls `GET /channel-context/{agentId}` and invokes `appendSystemContext` to prepend CaseHub channel history into the agent's system prompt before each LLM call. Published to npm. ADR 0001 documents the TypeScript-only decision.

The `python/` library is a thin HTTP client (no hook registration); published to PyPI independently.

---

## Two Invocation Modes

**Heartbeat (OpenClaw autonomous → CaseHub):** An OpenClaw agent running autonomously produces output and delivers it via `deliver:webhook`. The integration layer normalises the payload and creates a CaseHub case to track the work.

**Direct call (CaseHub case step → OpenClaw):** A running CaseHub case reaches a step that routes to an OpenClaw agent. The integration layer calls `POST /hooks/agent` with the step context as the agent prompt.

These two modes are mutually exclusive per invocation. A given agent interaction is either initiated by OpenClaw or by CaseHub — never both simultaneously. This is the golden rule for reasoning about invocation flow.

---

## Depends On

- `casehub-qhorus` — mandatory (`ChannelBackend` SPI, `MessageObserver` SPI)
- `casehub-engine-api` — SPI interfaces only (`WorkerProvisioner`, `CaseChannelProvider`, `WorkerStatusListener`). Uses `casehub-engine-api` rather than `casehub-engine` to avoid pulling engine CDI beans with unsatisfied persistence SPIs into the `casehub/` module.
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

## Current State

- Epic 1 (scaffold): complete — Maven structure, CLAUDE.md, CI
- Epic 2 (OpenClaw hook API client): complete — `OpenClawHookClient`, session registry, `deliver:webhook` normaliser (branch `issue-002-openclaw-hook-client`)
- Epic 3 (ChannelContextWindow service): complete — in-memory ring buffer, `ChannelContextWindowObserver`, REST endpoint (branch `issue-003-channel-context-window`)
- Epic 4 (CaseHub SPIs: `WorkerProvisioner`, `ChannelBackend`, `CaseChannelProvider`, `WorkerStatusListener`): complete — branch `issue-4-casehub-spi-implementations`
- Epic 5 (TypeScript Plugin SDK + Python client library): complete — `plugin/` (npm), `python/` (PyPI), ADR 0001
- Epic 6 (OversightGateService, oversight delivery endpoint): complete; subsequently simplified in openclaw#28 — `evaluate()` archives webhook text as non-resolving STATUS, gate entry wired to MCP tool calls (`casehub_done`/`casehub_reject`) rather than speech-act classification
- Epic 7 (Layer 0 — Quarkus MCP endpoint, 9 tools, 3 resources, 4 plugin hooks, global SKILL.md files): complete (openclaw#19)

---

## Design Documents

- `docs/specs/openclaw-integration.md` — integration architecture and hook API
- `docs/specs/openclaw-skill-pack.md` — skill pack structure and routing
- Research spec in `casehubio/parent` — original scoping analysis
