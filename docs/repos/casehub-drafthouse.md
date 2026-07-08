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
| `api/` | `casehub-drafthouse-api` | Pure Java domain model — `ReviewSession`, `ReviewResult`, `DocumentSide`, `ReviewSessionRegistry` |
| `runtime/` | `casehub-drafthouse` | Quarkus 3.34.3 app — MCP endpoints, Qhorus integration, LLM reviewer wiring |

---

## Key Abstractions

| Concept | Role |
|---|---|
| `ReviewSession` | A document review context: document sides (before/after), reviewer agents, grounded conversation |
| `DocumentSide` | One version of a document (before or after) within a review session |
| `ReviewResult` | Structured feedback from a reviewer agent |
| `ReviewSessionRegistry` | SPI for storing and retrieving active review sessions |

---

## Depends On

| Repo | Module | Nature |
|------|--------|--------|
| `casehub-qhorus-api` | `app` | `ChannelService`, `MessageService`, `ChannelGateway`, `DataService`, `InstanceService` — channel mesh SPIs |
| `casehub-qhorus` (runtime) | `runtime` | Channel mesh runtime — commitment lifecycle, typed messages |
| `quarkus-langchain4j-anthropic 1.9.1` | `runtime` | LLM calls via `@AiService` for reviewer agents (Phase 2) |

Future additions: `casehub-engine`, `casehub-eidos`.

## Depended On By

Nothing in the casehubio ecosystem — application tier only.

---

## Recent Features

**Quinoa integration (drafthouse#74)** — adopted casehub-pages workbench via Quinoa frontend build system. Replaces hand-coded HTML shell with `loadSite()` runtime. DebateEventBus migrated to `pages-event` CustomEvent. Hot-reload in dev mode, compiled with esbuild.

**WebSocket real-time updates (drafthouse#88)** — replaced SSE polling with WebSocket push for debate events (round transitions, point submissions, flags raised). Includes reconnection logic with exponential backoff (max 60s).

**Section highlighting (drafthouse#90)** — clicking a review point scrolls to and highlights the corresponding document section (before/after sides). Uses CSS `::part()` for styling.

**Replay adapter (drafthouse#95)** — replays design-review workspaces from CLAUDE.md snapshots into draft debate channels. Parser extracts review points + agent responses → channel messages. Marks points as VERIFIED (consensus) or DEFERRED (split). MCP tool: `casehubio-drafthouse:replay-design-review`.

**Document timeline (drafthouse#98)** — version navigation UI across review rounds. Allows comparing any two versions from the review history.

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

## Planned MCP Tool Surface (Phase 2)

`start_review`, `push_revision`, `get_cursor_context`, `get_diff`, `end_review`

---

## Current State

- Two-module Maven project (`api/` + `runtime/`) — restructured in drafthouse#21
- `casehub-qhorus 0.2-SNAPSHOT` dependency wired
- `quarkus-langchain4j-anthropic 1.9.1` added for Phase 2 LLM reviewer integration
- No deployed production instances

---

## Design Documents

- Research spec: `docs/superpowers/specs/2026-05-26-document-review-tool-research.md` (in drafthouse repo)
- [CLAUDE.md](https://raw.githubusercontent.com/casehubio/drafthouse/main/CLAUDE.md) — stack, module coordinates, key design decisions
