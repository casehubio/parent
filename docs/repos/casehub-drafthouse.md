# casehub-drafthouse — Platform Deep Dive

**GitHub:** [casehubio/drafthouse](https://github.com/casehubio/drafthouse) (local: `~/claude/casehub/drafthouse`)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

MCP-driven document review tool. Any LLM (Claude Code, Claudony, or any MCP client) can open a document, show before/after versions, create reviewer LLM agents, and have grounded conversations about specific document regions. Evolved from md-compare; promoted to the CaseHub application tier to leverage Qhorus channels and LangChain4j for provider-agnostic LLM calls.

---

## Module Structure

| Module | Artifact ID | Purpose |
|--------|-------------|---------|
| `server/api/` | `casehub-drafthouse-api` | Pure Java domain model — `ReviewSession`, `ReviewResult`, `DocumentSide`, `BrainstormSession`, `DebateSessionStore` SPI, `DebateSessionSnapshot`, `ResolvedReviewer` |
| `server/runtime/` | `casehub-drafthouse` | Quarkus app — MCP endpoints, Qhorus integration, LLM reviewer wiring, brainstorming tools, debate persistence, context tracking, terminal endpoint |

---

## Key Abstractions

| Concept | Role |
|---|---|
| `ReviewSession` | A document review context: document sides (before/after), reviewer agents, grounded conversation |
| `DocumentSide` | One version of a document (before or after) within a review session |
| `ReviewResult` | Structured feedback from a reviewer agent |
| `ReviewSessionRegistry` | SPI for storing and retrieving active review sessions |
| `BrainstormSession` | A brainstorming session context: options with states (EXPLORED, RECOMMENDED, ELIMINATED, SELECTED), lifecycle (ACTIVE → CONVERGED / ABANDONED) |
| `DebateSessionStore` | Pluggable SPI for debate session persistence — `save(DebateSessionSnapshot)`, `load(UUID)`, `remove(UUID)`, `loadAll()` |
| `DebateSessionSnapshot` | Serializable debate state: channel, documents, comparison, participants, agent ID |
| `ResolvedReviewer` | Resolved reviewer identity: `agentId`, `name`, `instructions` — produced by `ReviewerResolver` via Eidos `AgentRegistry` |

---

## Depends On

| Repo | Module | Nature |
|------|--------|--------|
| `casehub-qhorus-api` | `app` | `ChannelService`, `MessageService`, `ChannelGateway`, `DataService`, `InstanceService` — channel mesh SPIs |
| `casehub-qhorus` (runtime) | `runtime` | Channel mesh runtime — commitment lifecycle, typed messages |
| `casehub-eidos-api` | `runtime` | `AgentRegistry`, `AgentDescriptor`, `AgentQuery` — Eidos identity model for multi-LLM reviewer registry |
| `quarkus-langchain4j-anthropic 1.9.1` | `runtime` | LLM calls via `@AiService` for reviewer agents (Phase 2) |

Future additions: `casehub-engine`.

## Depended On By

Nothing in the casehubio ecosystem — application tier only.

---

## Recent Features

**Quinoa integration (drafthouse#74)** — adopted casehub-pages workbench via Quinoa frontend build system. Replaces hand-coded HTML shell with `loadSite()` runtime. DebateEventBus migrated to `pages-event` CustomEvent. Hot-reload in dev mode, compiled with esbuild.

**WebSocket real-time updates (drafthouse#88)** — replaced SSE polling with WebSocket push for debate events (round transitions, point submissions, flags raised). Includes reconnection logic with exponential backoff (max 60s).

**Section highlighting (drafthouse#90)** — clicking a review point scrolls to and highlights the corresponding document section (before/after sides). Uses CSS `::part()` for styling.

**Replay adapter (drafthouse#95)** — replays design-review workspaces from CLAUDE.md snapshots into draft debate channels. Parser extracts review points + agent responses → channel messages. Marks points as VERIFIED (consensus) or DEFERRED (split). MCP tool: `casehubio-drafthouse:replay-design-review`.

**Document timeline (drafthouse#98)** — version navigation UI across review rounds. Allows comparing any two versions from the review history.

**Brainstorming MCP tools** — session model (`BrainstormSession` with ACTIVE/CONVERGED/ABANDONED states, `BrainstormOption` with EXPLORED/RECOMMENDED/ELIMINATED/SELECTED statuses) and 7 MCP tools: `start_brainstorm`, `present_options`, `update_option`, `set_recommendation`, `mark_eliminated`, `mark_selected`, `end_brainstorm`. `BrainstormSessionRegistry` manages active sessions. `TerminalEndpoint` WebSocket at `/api/terminal` provides PTY-based shell sessions via pty4j.

**Multi-LLM reviewer registry** — `DraftHouseReviewerRegistry` implements `io.casehub.eidos.api.AgentRegistry`, backed by `ConcurrentHashMap<String, AgentDescriptor>`. `ReviewerDescriptorSeeder` (`@Startup`) seeds 4 reviewer personas: `drafthouse-structural-reviewer` (structural integrity), `drafthouse-content-reviewer` (accuracy, evidence), `drafthouse-readability-reviewer` (clarity, prose), `drafthouse-completeness-reviewer` (coverage, edge cases) — all share slot `document-reviewer`. `ReviewerResolver` resolves `agentId` → `ResolvedReviewer` via `AgentRegistry.findById()`, renders system prompt via `SystemPromptRenderer`.

**Debate session persistence** — pluggable `DebateSessionStore` SPI with `save`/`load`/`remove`/`loadAll`. `JpaDebateSessionStore` (activated by `casehub.drafthouse.persistence.enabled=true` via `@IfBuildProperty`) persists `DebateSessionEntity` with `fromSnapshot()`/`toSnapshot()` conversion. `NoOpDebateSessionStore` (`@DefaultBean`) provides in-memory fallback. `DebateSession.fromSnapshot()` restores documents, comparison, and participants.

**Context meter UI + report_context MCP tool** — `report_context` MCP tool in `DebateMcpTools` accepts `debateSessionId` and `usagePercent` (0-100), updates `ContextTracker`, pushes `ContextSnapshot` via WebSocket. `DebateEventResource.pushContextSnapshot()` sends `context-usage` events. `<context-gauge>` Lit web component displays percentage bar with three color states: normal (accent), warn (>=60%), error (>=80%), pulse animation on threshold breach. Tooltip shows server contribution chars, window size, message count.

**Export debate summary MCP tool** — `export_debate_summary` MCP tool in `DebateMcpTools` accepts `debateSessionId` and `outputPath`, projects debate summary via `DebateChannelProjection`, appends active selection and working set, prepends reviewer info, writes to markdown file on disk.

---

## What This Repo Explicitly Does NOT Do

- Provide general-purpose document storage (no document database — review state is in-memory or JPA when added)
- Implement consensus or voting across reviewers (each reviewer is independent)
- Know anything about git, PRs, or source control (`casehub-devtown` owns that domain)
- Implement audit trail, case orchestration, or agent identity — those are foundation concerns

---

## Channel Usage Pattern

DraftHouse uses a single APPEND channel per review session with QUERY/RESPONSE. This is idiomatic for a non-normative consumer — it does not apply the 3-channel NormativeChannelLayout (work/observe/oversight), which is Claudony's concern. QUERY/COMMAND from `casehub-qhorus`'s 9-type speech-act taxonomy are used for grounded review conversations.

---

## MCP Tool Surface

**Brainstorming:** `start_brainstorm`, `present_options`, `update_option`, `set_recommendation`, `mark_eliminated`, `mark_selected`, `end_brainstorm`

**Debate:** `report_context`, `export_debate_summary`

**Replay:** `casehubio-drafthouse:replay-design-review`

**Planned (Phase 2):** `start_review`, `push_revision`, `get_cursor_context`, `get_diff`, `end_review`

---

## Current State

- Two-module Maven project (`server/api/` + `server/runtime/`) — restructured in drafthouse#21
- `casehub-qhorus 0.2-SNAPSHOT` dependency wired
- `casehub-eidos-api` wired for multi-LLM reviewer registry
- `quarkus-langchain4j-anthropic 1.9.1` added for Phase 2 LLM reviewer integration
- Brainstorming MCP tools, debate persistence, context tracking, and export tools operational
- No deployed production instances

---

## Design Documents

- Research spec: `docs/superpowers/specs/2026-05-26-document-review-tool-research.md` (in drafthouse repo)
- [CLAUDE.md](https://raw.githubusercontent.com/casehubio/drafthouse/main/CLAUDE.md) — stack, module coordinates, key design decisions
