# Research Spec: CaseHub × OpenClaw — Life and Enterprise Automation

**Status:** Research complete — repos bootstrapped, content promoted to individual repos
**Date:** 2026-05-25
**Origin:** Exploratory conversation — casehubio/parent session 2026-05-25
**Promoted to:**
- casehub-openclaw: `docs/specs/openclaw-integration.md`, `docs/specs/openclaw-skill-pack.md`
- casehub-life: `docs/specs/life-automation.md`, `docs/specs/life-actor-model.md`
- casehub-platform: `docs/specs/case-memory-store.md`
- platform deep-dives: `docs/repos/casehub-openclaw.md`, `docs/repos/casehub-life.md`

---

## 1. Purpose

This document captures a structured research conversation exploring how CaseHub could
integrate with OpenClaw and related platforms (Sai, Coworker.ai) to serve both household
personal life automation and enterprise co-worker automation use cases. It is a pre-design
artefact: it records findings, identifies opportunities, names gaps, and defers implementation
decisions to follow-on specs and issues.

Nothing in this document is ruled in for implementation. Nothing is yet ruled out unless
explicitly stated in §13.

---

## 2. Platform Landscape

### 2.1 OpenClaw

**What it is:** Open-source, self-hosted personal AI agent. Reached 250,000+ GitHub stars
within 60 days of launch — the fastest-growing project on GitHub at that rate. Renamed from
Clawdbot (November 2025) to OpenClaw (January 2026) when mapped webhooks were introduced.

**Core architecture:**
- Heartbeat-based execution: a persistent background process checks a task list at regular
  intervals and acts autonomously without user input
- 20+ messaging platforms as the primary UI: WhatsApp, Telegram, Slack, Discord, iMessage,
  Teams, Signal, and others — the agent lives where the user already is
- 100+ built-in skills; 5,400+ community-built skills in the ClawHub registry
- Multi-LLM backend support: Claude, DeepSeek, GPT models, local models
- Browser automation via CDP-based snapshot system (structured, not vision-based)
- Companion tool Peekaboo: screenshot and visual QA for agents on macOS
- Docker and self-hosted deployment; can be air-gapped

**Skill architecture (technical):**
Skills are not HTTP endpoints. A skill is a directory containing a `SKILL.md` file with
three layers:
- Layer 1 — YAML frontmatter: name, description, version, trigger phrases, required tools,
  permissions. The runtime reads this to decide whether a skill should handle a request.
- Layer 2 — Instruction block: markdown content containing step-by-step AI directives —
  a scoped system prompt defining persona, procedures, output format, validation rules.
- Layer 3 — Supporting resources: optional scripts (Python, Bash, TypeScript/Deno),
  configuration files, API integration code.

Skills are invoked by the Agent Core's intent router based on semantic matching against
trigger phrases. The caller cannot specify "run skill X by name" via a direct API call —
they send a prompt and the AI routes to the appropriate skill internally.

**External invocation — the Hook API:**
OpenClaw exposes HTTP endpoints on the Gateway for external trigger:

| Endpoint | Purpose |
|---|---|
| `POST /hooks/wake` | Lightweight nudge — wakes agent with a text event |
| `POST /hooks/agent` | Full agent run — executes a prompt, can deliver reply anywhere |
| `POST /hooks/<name>` | Custom-named endpoint mapped to wake or agent action via config |
| `POST /v1/chat/completions` | OpenAI-compatible completions endpoint |

`POST /hooks/agent` key fields: `message` (required), `agentId`, `wakeMode`, `deliver`,
`channel`, `to`, `model`, `fallbacks`, `thinking`, `timeoutSeconds`.

Delivery modes after an agent run:
- `deliver: "webhook"` — POST finished result payload to an arbitrary HTTP URL
- `deliver: "announce"` — fallback-deliver final text to a chat channel
- `deliver: "none"` — no runner fallback delivery

Authentication: Bearer token in `Authorization` header (required). Query-string tokens
rejected (400). Always use HTTPS in production.

**Python SDK:**
`from openclaw import OpenClawClient` — programmatic access to agent management, task
execution, context injection, and response handling. Supports scoped agent sessions:
`client.get_agent("home-agent", session_name="household-main")`.

Context injection via `before_prompt_build` plugin hook:
```python
@agent.on("before_prompt_build")
def inject_context(ctx):
    return { "appendSystemContext": "...dynamic context..." }
```
`appendSystemContext` lands in the system prompt — rebuilt fresh every turn, never compacted.
This is the compaction-safe injection point for channel context (see §8).

**Pluggable context engine:** if a plugin provides `kind: "context-engine"`, OpenClaw
delegates all context assembly to that engine. This is the deepest integration point for
casehub-openclaw (see §9.2).

**Session management:**
OpenClaw rebuilds its system prompt from scratch on every agent run. Sessions reset daily
(4:00 AM local) and on idle timeout. `session:start` lifecycle hook is planned but not
yet implemented. Channel history backfill on session start is an open feature request (#27231),
not yet shipped. Agents have no automatic memory of what happened in prior sessions unless
context is explicitly injected.

**The real value of the OpenClaw skill ecosystem:**
The 5,400+ community skills are pre-built integrations with specific platforms and APIs —
not generic tools. Examples of what exists:
- Banking and Open Banking API skills
- Google Calendar, iCal integration skills
- Home Assistant / smart home IoT skills
- Health tracker skills (Fitbit, Apple Health data)
- Messaging skills (WhatsApp, Telegram, SMS, email — as sender/receiver, not just UI)
- Social media skills (Twitter/X, LinkedIn, Reddit)
- News and RSS aggregation skills
- Flight tracking and travel booking skills
- CRM and enterprise platform skills

**Distinction from browser MCP:** a browser skill can do anything a human can do in a
browser, but it is slow, vision-based, and fragile to UI changes. The pre-built platform
skills use native APIs, are stable, fast, and already handle auth. The browser is a
fallback for when no native integration exists. Maximising OpenClaw value means building
use cases around the pre-built skill ecosystem, not the browser. See §5.3a and §5.3b.

**What OpenClaw does NOT do:**
- No formal commitment or obligation lifecycle — skill execution is fire-and-forget
- No tamper-evident audit
- No formal multi-agent coordination protocol
- No SLA enforcement or escalation
- No trust scoring
- No persistent channel awareness between heartbeat ticks
- No cross-session memory without explicit injection

### 2.2 Sai by Simular AI

**What it is:** Always-on desktop AI co-worker using computer-use (vision-based) interaction
with arbitrary GUI applications. Powered by Simular's Agent S framework.

**Architecture:**
- Perception: vision-only (raw screenshots, not DOM). Mixture of Grounding (MoG) routes
  different UI elements to specialised perception experts rather than a monolithic LLM
- Neuro-symbolic approach: generalist model handles high-level planning; specialist models
  handle low-level execution (button localisation, text highlighting)
- Benchmark progression (OSWorld): Agent S 20.6% → S2 48.8% → S3 69.9% (human level: 72%)
- Agent S3 adds native code generation/execution (Python/Bash) as alternative to pure GUI
- Critical action approval gates: before executing actions classified as monetary,
  irreversible, or involving sensitive data, Sai pauses and requires explicit human approval
- Primarily single-agent: no documented multi-agent coordination
- No A2A or MCP protocol usage
- No open API or plugin SDK — integration is via browser/desktop UI automation only
- No tamper-evident audit trail: transparency is live screen visibility, not cryptographic
  proof

**Target users:** enterprise knowledge workers automating desktop workflows.

**What it does NOT do:**
- No multi-agent orchestration
- No formal obligation tracking
- No SLA or deadline enforcement
- No trust scoring
- No open ecosystem (no SDK, no plugin model)

### 2.3 Coworker.ai

**What it is:** Enterprise AI agent orchestration platform. NOT computer-use — agents
execute via API calls to connected systems (100+ integrations). The key differentiator
is OM1 — Organisational Memory.

**OM1 (Organisational Memory):**
- Decomposes every document, message, and tool output into atomic facts
- Discovers entities (people, companies, projects, tasks) across 120+ relationship dimensions
- Maps entity relationships continuously as connected tools are indexed
- Pre-generates summaries and computes centrality scores for fast recall
- Permission-aware: recall respects the principal's access rights across connected systems
- Sub-second graph traversal: context available to agents in milliseconds
- Continuously indexes 40+ enterprise tools

**Multi-agent coordination:** structured data/context passing between agents. Not A2A
protocol-based. Central OM1 provides shared context.

**Model routing:** automatically routes tasks to the optimal model (OpenAI, Anthropic,
Google, Llama, Mistral) based on task complexity, cost, and accuracy requirements.

**Compliance:** SOC 2 Type II, GDPR, CASA Tier 2.

**What it does NOT do:**
- No computer-use or GUI automation
- No tamper-evident audit trail (OM1 is a knowledge graph, not an immutable ledger)
- No formal obligation lifecycle
- No SLA enforcement
- No trust scoring

### 2.4 Computer-Use Agents — 2026 Industry State

Relevant findings from broader research:

- **DOM-aware agents outperform vision-only by 12–17 percentage points** on common tasks.
  Vision-only takes ~60 seconds on form filling; DOM-based takes ~1 second.
- **Production failure rate:** 80%+ of AI agent pilots fail within 6 months. The leading
  cause is not intelligence — it is reliability and access to production systems.
- **Cascading failure math:** 85% per-step reliability × 10-step workflow = ~20% end-to-end
  success rate.
- **Fewer than 1 in 4 organisations** successfully scale agents past pilots.
- **Stuck-state failure modes:** Repeater (same action repeatedly), Looper (A→B→A
  oscillation), Reflection loops. Not yet universally solved.
- **Schema drift:** silent failures when API schemas change; agents fail without error.
- **Winning strategy is bounded autonomy**, not full autonomy. Low-risk, well-instrumented
  workflows deliver ROI. Full end-to-end independence is not the production winner.
- **Emerging protocols:** MCP (Anthropic — agent-to-tool) and A2A (Google — agent-to-agent)
  are both now under the Linux Foundation Agentic AI Foundation. Complementary: MCP = hands,
  A2A = social skills. Neither Sai nor Coworker use them.
- **Anthropic's guidance on computer-use:** APIs and connectors preferred BEFORE screen
  automation. Computer-use is a fallback for when no structured API exists.

---

## 3. Strategic Positioning

### 3.1 CaseHub and OpenClaw Are Complementary Layers

CaseHub and OpenClaw do not compete. They address different layers of the same problem:

| Dimension | OpenClaw | CaseHub |
|---|---|---|
| Primary role | Executes tasks (pre-built platform skills, heartbeat, messaging delivery) | Governs agent interactions (commitment, SLA, audit, trust, escalation) |
| Execution model | Heartbeat / fire-and-forget skills | Case orchestration with formal lifecycle |
| Human interaction | Natural language task input | Formal speech acts (COMMAND → RESPONSE, WorkItem gates) |
| Multi-agent | Skills chain; no formal coordination | Full commitment lifecycle, DELEGATED, HANDOFF |
| Accountability | None — best-effort | Merkle ledger, tamper-evident, Bayesian trust scoring |
| Failure handling | Silent failure or error log | SLA breach → escalation → human gate |
| Channel awareness | No cross-session or cross-agent memory | Qhorus channels + ChannelContextWindow (see §8) |
| Memory | None across sessions | Ledger (immutable history) + CaseMemoryStore (semantic, see §4.3) |

OpenClaw is excellent execution plumbing with a rich pre-built integration ecosystem.
CaseHub is the accountability mesh and orchestration layer. They compose naturally: OpenClaw
workers inside CaseHub cases, CaseHub providing the governance OpenClaw explicitly does not
have.

### 3.2 The Bidirectional Integration Model

The integration is not one-directional. Two independent directions of value:

**Direction 1 — CaseHub uses OpenClaw (orchestrated execution):**
- CaseHub cases provision OpenClaw workers via the `WorkerProvisioner` SPI
- CaseHub's `CaseChannelProvider` creates Qhorus channels per case/purpose
- CaseHub invokes OpenClaw skill execution via `POST /hooks/agent` on demand (no heartbeat
  required for in-case steps — see §3.4)
- OpenClaw executes skills (bank aggregation, calendar integration, Home Assistant, messaging)
  and reports back via `WorkerStatusListener`
- CaseHub orchestrates the workflow lifecycle; OpenClaw executes the individual steps
- OpenClaw's multi-channel delivery (WhatsApp, Telegram, iMessage) surfaces CaseHub's
  human governance gates in the messaging platforms users already monitor

**Direction 2 — OpenClaw uses CaseHub capabilities (optional add-on skills):**
- OpenClaw users who install casehub skills get CaseHub coordination on top of their
  existing skill ecosystem without changing anything else
- Proposed skill surface (not yet built):
  - `casehub-workitem` — create a WorkItem from a natural language instruction with deadline
    and assignee
  - `casehub-case` — start a CasePlanModel for a complex multi-step workflow
  - `casehub-queue` — route a task to a named queue (home / health / finance)
  - `casehub-status` — query the status of a running case
  - `casehub-commit` — acknowledge a COMMAND as a Commitment from within a skill
  - `casehub-done` — close a Commitment from within a skill
  - `casehub-context` — retrieve recent channel context from ChannelContextWindow for
    explicit context injection when the automatic hook is not active
- These are opt-in: a bare OpenClaw user gets none of this; installing casehub skills
  layers CaseHub coordination on top of the existing 5,400-skill ecosystem

### 3.3 The Ledger Is Opt-In

CaseHub's foundation modules are independently embeddable. The progressive adoption model
applies equally to enterprise and household contexts:

| Level | Modules added | What it provides |
|---|---|---|
| 0 | OpenClaw only | Skill execution, heartbeat, messaging UI |
| 1 | + casehub-work | Every task has lifecycle (claimed → in-progress → done), SLA, deadline enforcement, escalation, delegation |
| 2 | + casehub-qhorus | Multiple agents coordinate via formal channels; commitment lifecycle (COMMAND → RESPONSE → DONE/DECLINE/HANDOFF); obligation tracking |
| 3 | + casehub-engine | Complex multi-step workflow orchestration; conditional branching; parallel tasks; human governance gates |
| 4 | + casehub-ledger | Tamper-evident Merkle audit; trust scoring; GDPR Art.17 erasure; cryptographic proof |

CaseMemoryStore (casehub-platform optional modules) is orthogonal to this ladder — it
can be added at any level, from Level 1 upward. It provides cross-case semantic context
to all CaseHub consumers regardless of which other modules are active. Adding a Memori
adapter requires only Postgres, which any CaseHub deployment already runs.

Even at Level 1, casehub-work provides formal task lifecycle and SLA enforcement missing
from OpenClaw's fire-and-forget model. A grocery order with a Wednesday deadline and
escalation if not placed is a WorkItem. That is valuable without tamper-evidence.

### 3.4 OpenClaw Integration — Technical Invocation Model

**Skills are not individual HTTP endpoints.** External systems cannot call "run skill X"
directly. The caller sends a prompt to `/hooks/agent`; OpenClaw's intent router determines
which skill to invoke based on semantic matching. For practical purposes this works cleanly
— "pull this month's transactions from all three bank accounts" reliably routes to the
banking skill. For maximum determinism, use a dedicated `agentId` pre-configured with only
the relevant skills installed.

**Two distinct integration modes — when to use each:**

**Heartbeat mode — OpenClaw owns the timing decision:**

Use when:
- No CaseHub case exists yet — OpenClaw is watching for a condition that should *create* one
- The trigger is ambient and conditional: energy prices drop below threshold, social mention
  detected, health tracker shows anomaly, flight price changes, email arrives matching pattern
- OpenClaw must reason autonomously: "is this condition met? is this worth acting on?"
- Monitoring is continuous and indefinite, not bounded by a case lifecycle
- The outcome is: create a CaseHub WorkItem or case, alert a human via messaging platform

**Direct call (`POST /hooks/agent`) — CaseHub owns the timing decision:**

Use when:
- A case is already running and needs a specific skill executed *now*
- CaseHub determines timing: SLA expiry, WorkItem completion, stage transition, CDI event
- The task is deterministic — "pull this month's transactions" not "watch for transactions"
- SLA precision matters: skill must run within seconds of the trigger, not on next tick
- The result feeds back into the running case workflow

**The golden rule:**
> If the question is *"when should this happen?"* → heartbeat owns the decision.
> If the question is *"do this now, as part of this case"* → CaseHub fires a direct call.

**The natural hybrid:**
Heartbeat detects condition → calls `casehub-case` or `casehub-workitem` skill → CaseHub
case opens → CaseHub orchestrates subsequent steps via direct calls. OpenClaw shifts from
autonomous agent to orchestrated executor the moment a case opens.

| Pattern | Who decides timing | Bounded by case? | Result goes to |
|---|---|---|---|
| Heartbeat | OpenClaw | No | Creates WorkItem / case |
| Direct call | CaseHub | Yes | Case step result |
| Hybrid | OpenClaw starts, CaseHub continues | OpenClaw: no → CaseHub: yes | Both |

**Direct call example:**
```bash
POST /hooks/agent
Authorization: Bearer SECRET

{
  "message": "Pull this month's transactions from all three linked accounts and categorise by spend type",
  "agentId": "finance-agent",
  "deliver": "webhook",
  "to": "https://casehub.internal/openclaw/delivery/channel/{channelId}",
  "timeoutSeconds": 30
}
```

OpenClaw executes the banking skill, generates output, POSTs the result to the CaseHub
channel endpoint. The Qhorus channel receives it as a typed speech act. No heartbeat
involved.

---

## 4. Enterprise Use Cases

### 4.1 The Co-worker AI Pattern

The enterprise AI co-worker model (Sai, Coworker.ai) addresses the same coordination
problem CaseHub solves, but without CaseHub's formal accountability layer.

**What enterprise co-workers do well:**
- Autonomous execution of multi-step desktop and API workflows
- Context-aware task routing across connected enterprise tools
- Bounded autonomy with human approval for critical actions

**What they lack that CaseHub provides:**
- Tamper-evident audit trail for regulated industries (finance, healthcare, legal)
- Formal obligation lifecycle: COMMAND creates a tracked Commitment with SLA and escalation,
  not just a task log entry
- Trust scoring: over time, which agents handle which tasks reliably — Bayesian Beta scoring
  from outcomes
- Multi-agent obligation transfer: HANDOFF formally moves the obligation, Watchdog moves
  with it, the original obligor is released
- DECLINE with semantic content: a refusal carries a machine-readable reason that updates
  routing defaults

### 4.2 Fit-Gap from Sai — What to Borrow

**Keep:**

*ActionRiskClassifier SPI* — Sai's critical action approval gate is the most transferable
idea. Sai classifies actions before executing: monetary, irreversible, sensitive-data =
human approval required; reversible = autonomous. CaseHub already has the gate mechanism
(WorkItem + COMMAND/RESPONSE commitment). What it lacks is a way for workers to *trigger*
that gate based on what they are about to do, without knowing CaseHub internals.

Proposed: `ActionRiskClassifier` SPI in `casehub-engine-api`:
```
classify(PlannedAction action) → RiskDecision
  RiskDecision: AUTONOMOUS | GATE_REQUIRED(reason, reversible)
```
- Workers declare what they are about to do and whether it is risky
- Engine classifies and either proceeds or creates a WorkItem gate automatically
- Worker has no knowledge of the gate mechanism — decoupling is complete
- Composes with existing WorkItem SLA and escalation machinery
- Sai's version is ad-hoc per-agent; CaseHub's would be uniform across all workers

**The complete ActionRiskClassifier + oversight loop:**
`ActionRiskClassifier` classifies action as risky → routes to oversight Qhorus channel →
OpenClaw delivers to WhatsApp/Telegram via `deliver: webhook` → user responds → Commitment
fulfilled → workflow continues. Skill authors write no approval logic whatsoever.

**Do not borrow:**

*Sai's vision-based computer-use stack* — OpenClaw already handles browser automation via
CDP snapshots, which is faster and more reliable than screenshot-based perception. Anthropic's
own guidance: APIs before computer-use. Vision-based computer-use is a last resort.

### 4.3 Fit-Gap from Coworker.ai — What to Borrow

**Keep:**

*CaseMemoryStore — semantic fact index alongside the ledger:*

Coworker's OM1 identified the gap; the capability itself is general to all of CaseHub —
not an OpenClaw feature. Every CaseHub case currently starts cold. Facts established in
prior cases — about an entity, an agent's behaviour, a recurring pattern — are invisible
to the next case unless explicitly passed as parameters. This affects all three existing
application repos and any future consumer, with or without OpenClaw involved.

**The problem across all CaseHub consumers:**
- **devtown:** new PR review for contributor X — prior pattern of test coverage gaps, prior
  DECLINE by security-agent on auth code — invisible unless manually surfaced
- **clinical:** new adverse event for a patient with prior Grade 3 hepatotoxicity withdrawal
  from a previous trial — invisible at case open; requires manual record review
- **AML:** new transaction alert involving an entity that appeared in 3 prior SAR filings
  and is part of a known network — hours of manual research to establish what CaseMemoryStore
  would surface in milliseconds

Proposed: `CaseMemoryStore` SPI in `casehub-platform-api` — a semantic fact index that
lives alongside the ledger, not replacing it:

| Store | Purpose | Properties |
|---|---|---|
| Ledger | Tamper-evident "what happened" | Immutable, Merkle-chained, permanent |
| CaseMemoryStore | Queryable "what we know" | Atomic facts, entity relationships, semantic recall |

- Each completed case emits structured facts to the store (mechanism TBD — CDI observer
  consistent with existing ledger capture)
- Future cases query the store for relevant context before acting
- Permission-aware recall: enforces `CurrentPrincipal` + `GroupMembershipProvider`
  boundaries at the SPI layer — not delegated to the backend service
- Domain isolation enforced at the SPI layer — facts from one domain must not be recallable
  by agents operating in a different domain
- Module placement: `casehub-platform` — SPI in `platform-api`, @DefaultBean no-op in
  `platform`, adapters as optional modules — consistent with PreferenceProvider and
  CurrentPrincipal patterns (casehubio/platform#27)

**Distinct from ChannelContextWindow (§8):**
CaseMemoryStore is long-term indefinite semantic memory consumed by all CaseHub case steps
and worker types. ChannelContextWindow (§8) is a short-term TTL buffer specific to
casehub-openclaw for injecting recent Qhorus channel activity into OpenClaw agent turns.
They are related but serve entirely different consumers and timescales.

#### §4.3a — Open Source Memory Backend Evaluation

Rather than building the memory layer from scratch, a field of open source projects exists
that could back the `CaseMemoryStore` SPI via REST adapter:

| Project | Approach | REST API | Self-hosted | Temporal reasoning | Key limitation |
|---|---|---|---|---|---|
| **Mem0** | Vector + BM25 + optional graph | ✅ Full REST | ✅ Docker | ❌ 49% LongMemEval | Graph memory $249/month paywall |
| **Graphiti** (Zep) | Temporal knowledge graph — bitemporal edges, fact validity windows | ✅ REST + MCP | ✅ (needs Neo4j/FalkorDB/Kuzu) | ✅ 63–91% LongMemEval | Community Edition deprecated Feb 2026; 3+ extra systems |
| **Memori** | SQL-native, atomic facts in Postgres | ✅ REST + MCP | ✅ Postgres only | ✅ 81.95% LoCoMo | Smaller ecosystem; newer |
| **Hindsight** | 4-way hybrid (semantic + BM25 + entity graph + temporal) | ✅ REST | ✅ Docker | ✅ State-of-art LongMemEval | Small ecosystem; less battle-tested |
| **Cognee** | Graph-vector hybrid | ✅ REST | ✅ | Unknown | Python-centric; smaller community — ruled out |
| **Letta** | Episodic / context-window management | ✅ REST | ✅ | Unknown | Episodic focus, not a knowledge graph — ruled out |
| **LangChain memory** | Framework component (Python) | ❌ | N/A | N/A | Not a service; Python-only — ruled out |
| **GraphRAG** (Microsoft) | Knowledge graph extraction | Azure only | ❌ Too buggy | Unknown | Research quality; not self-hostable — ruled out |

**The critical integration constraint:** every evaluated service scopes memory by its own
`userId`/`sessionId` model. None knows about CaseHub's `CurrentPrincipal`, life domains,
or `GroupMembershipProvider` boundaries. CaseHub must wrap any backend's API with its own
permission model — privacy domain partitioning is enforced at the `CaseMemoryStore` SPI
layer, not assumed from the external service. This is non-negotiable regardless of backend.

**Recommended approach:** `CaseMemoryStore` SPI with pluggable backend adapters, following
the existing CDI priority ladder pattern:

| Adapter | Backend | Infrastructure | Best for |
|---|---|---|---|
| Default | **Memori** | Postgres only (existing) | Zero-cost entry; all deployments; human-readable SQL facts align with CaseHub transparency values |
| Standard | **Mem0** | Docker + pgvector | Larger ecosystem; vector + BM25 retrieval; 48k GitHub stars |
| Temporal | **Graphiti** | Graphiti + Neo4j/FalkorDB/Kuzu | Regulated domains where "what did the agent know on 15 March?" is a compliance question |

This adapter strategy means no lock-in to a fast-moving ecosystem; permission enforcement
at CaseHub's layer regardless of backend; start simple (Memori, Postgres only) and graduate
as needs grow.

*modelHint on worker capability descriptor:*

Coworker routes tasks to the optimal model automatically. CaseHub routes to the best
*agent* via trust scoring; it has no mechanism to select the appropriate model tier at
provisioning time.

Proposed: add `modelHint` field to worker capability description:
- Values: REASONING (Opus-class), MECHANICAL (Haiku-class), BALANCED (Sonnet-class)
- `WorkerProvisioner` SPI respects the hint when provisioning a worker session
- OpenClaw already supports multiple LLM backends — the execution side is already there
- Combined with trust scoring: "route to the most trusted worker for this capability,
  provisioned with the appropriate model tier for the task complexity"

**Do not borrow:**

*Coworker's model routing infrastructure* — they build a multi-cloud model selector as a
managed service. The `modelHint` field on the worker descriptor is the appropriate
abstraction at CaseHub's level.

### 4.4 Enterprise Memory and Context

The OM1 insight applies to enterprise CaseHub deployments, not just personal life:

- Enterprise agents suffer the same context fragmentation: what happened in the last
  investigation, client engagement, or code review is not available to the next case
- `CaseMemoryStore` addresses this with permission-aware recall — facts from prior cases
  are available to future cases within the same permission scope
- For regulated enterprise (financial crime, clinical): the memory layer must respect the
  same access control boundaries as the primary case data — the SPI layer enforces this

### 4.5 Maximising OpenClaw Skill Value — Enterprise

The most compelling enterprise use cases for CaseHub + OpenClaw are ones where the
pre-built skill ecosystem does genuine work — not generic browser automation.

**Social/news monitoring → governed response:**
OpenClaw heartbeats across Twitter/X, LinkedIn, Reddit (social skills), plus RSS/news APIs.
CaseHub severity-routes based on what's found: neutral → observe channel (no action);
negative → WorkItem for draft response with SLA; crisis → oversight channel with human
RESPONSE required before anything posts. OpenClaw drafts and posts once approved (social
skill). This is the enterprise co-worker pattern: OpenClaw provides the platform integrations;
CaseHub provides the governance.

**Multi-source investigation aggregation:**
OpenClaw pulls data from CRM, email, Slack, document stores (platform skills) at the start
of an investigation case step. CaseMemoryStore provides context from prior related cases.
CaseHub orchestrates: gather → analyse → human review gate → file → audit. Every source
consulted and every decision is ledgered tamper-evidently — neither Sai nor Coworker provide
this.

---

## 5. Household and Personal Life Automation

### 5.1 Motivation

Personal life has several domains where the accountability properties CaseHub was designed
for matter more than in many enterprise workflows, yet tooling treats everything as
best-effort reminders:

- Health coordination: missed follow-up appointments have real health consequences
- Elder/family care: care obligations need formal tracking and escalation
- Legal/financial deadlines: hard consequences for missing them
- Home maintenance: contractor commitments routinely go unfulfilled
- Family coordination: multi-principal obligations across household members

OpenClaw handles execution well. CaseHub handles the accountability around execution.
The combination addresses what neither can do alone.

### 5.2 Use Case Domains

**Health coordination:**
- Medication adherence tracking, appointment follow-up cycles, lab result monitoring,
  referral chain management
- SLA: "schedule cardiology follow-up within 14 days of GP referral" — WorkItem with deadline
  and escalation
- Named obligor: GP is the principal who must authorise, equivalent to clinical PI
- Oversight channel: any significant health decision requires explicit human confirmation
- Level 4 (ledger) appropriate: tamper-evident record of health decisions, GDPR Art.17

**Financial governance:**
- Formal commitment lifecycle for major financial decisions — not budget tracking
- Multi-account aggregation: OpenClaw banking skills pull transactions from three accounts
  + investment portfolio; CaseHub creates monthly review WorkItems with budget sign-off gate;
  approved actions (cancel subscription, move funds) execute via OpenClaw skills
- Major spend decisions above a threshold require oversight channel RESPONSE before agent acts
- Trust scoring: which financial agent gives the most accurate rate comparisons over time
- Level 4 (ledger) appropriate: tamper-evident record of major financial decisions

**Elder and family care coordination:**
- Multiple agents, multiple principals (family members), multiple care providers
- Human governance gates for significant care decisions
- SLA: medication administered by 8am or alert carer
- GDPR Art.17 and sensitive data: highest sensitivity personal data
- Multi-site structure: one family-level case + per-location sub-cases (home, care home,
  hospital) — equivalent to clinical multi-site
- Level 4 mandatory: regulated data, documented obligation to care, potential legal relevance

**Legal and compliance cycles:**
- Contract renewals, tax deadlines, visa renewals, insurance renewals
- Hard deadlines with real consequences — agent-discoverable, human-approvable
- Audit trail matters: proof of filing, proof of notice, proof of action
- Level 3 or 4 depending on stakes

**Household task management:**
- Grocery ordering: SLA-based reorder — WorkItem with Wednesday deadline and escalation if
  not placed before Thursday milk runs out
- Home maintenance: annual boiler service, quarterly gutter clean — SLA-driven WorkItems
  that open automatically, route to agent or human, escalate if nothing happens
- Energy/utility management: monitoring agent emits STATUS to observe channel; decisions
  about switching providers route to oversight channel for human approval
- Level 1 (casehub-work) sufficient: formal task lifecycle and SLA without ledger

**Appointment booking:**
- Multi-step workflow: check availability → propose slot → human confirms → book →
  24h reminder → cancellation watch
- OpenClaw does the browsing and calendar API calls; casehub-engine holds the human gate
- Booking deadline: "prices change after Friday" = SLA on the confirmation gate
- Level 2–3 sufficient

**Family task delegation:**
- "Pick up kids at 3:30" as COMMAND → family member or agent RESPONSE confirmation →
  DONE on pickup
- No RESPONSE by 2pm → escalation → alternative arrangement triggered
- Qhorus commitment lifecycle on an everyday task
- Level 2 sufficient

**Travel planning:**
- Multi-step with budget gate and booking deadline
- CasePlanModel: destination research → budget check → flight search → hotel search →
  human approval → booking → document collection → reminders
- OpenClaw does all web browsing and API calls; CaseHub orchestrates and holds the gates
- Level 3 sufficient

**Contractor coordination:**
- Quote request → quote comparison → human approval → booking → work confirmation →
  payment authorisation → work sign-off
- External human actor (contractor) as obligor — see §5.4
- Level 3, with Level 4 if warranty or insurance claim documentation needed

### 5.3 Actor Taxonomy — Three Types

Personal life automation introduces a third actor category not present in devtown or clinical:

**Type 1 — AI agents:**
- Named personas: home-agent, health-agent, finance-agent, travel-agent
- OpenClaw instances acting as CaseHub workers
- Agent identity: `{model-family}:{persona}@{major}` — existing convention applies
- Trust scoring applies: which agent is most reliable for which capability

**Type 2 — Household principals:**
- Authenticated family members with assigned roles
- Role hierarchy: household-admin > household-member > household-junior
- Examples: both adults as household-admin; older teenager as household-member;
  younger children as household-junior
- Each authenticates via Claudony (WebAuthn passkey) or via OpenClaw bridge
- RBAC roles map to Qhorus channel allowed_writers and casehub-engine WorkItem assignees
- MultiInstanceCoordinator handles M-of-N quorum decisions across multiple adults

**Type 3 — External human actors (gap — not yet in CaseHub):**
- Unregistered third parties to whom the system tracks commitments: contractors, doctors,
  service providers, landlords, utility companies
- Example: "plumber committed to come Thursday" — obligor has no CaseHub account
- Example: "GP said she would call back this afternoon" — external, unauthenticated
- These actors make commitments (verbal, via text, via email) that the system should track
  and follow up on
- Follow-up mechanism: OpenClaw's multi-channel reach (WhatsApp, SMS, email) acts as the
  agent that chases the external actor when the Watchdog fires
- Material gap in CaseHub's actor model — see §11.4

### 5.3a Maximising OpenClaw Skill Value — Household

The most valuable household use cases are those where the pre-built OpenClaw skill ecosystem
is doing the integration work — not just a browser. The examples below use native platform
skills; none requires browser automation.

**Multi-account financial aggregation + governance:**
OpenClaw pulls transactions from three bank accounts (Open Banking skills), plus investment
portfolio summary (investment skill). CaseHub takes over: WorkItems for approve/reject
flagged transactions, oversight gate for any consequent action (cancel subscription, move
funds), tamper-evident record of what was reviewed and when. The skill work is genuine
multi-source assembly. CaseHub governs the decision cycle on top.

**Smart home + health coordination:**
OpenClaw reads from a health tracker (Fitbit/Apple Health skill) and pill dispenser
(Home Assistant IoT skill). CaseHub creates a WorkItem "confirm medication taken — 30 min
SLA." OpenClaw monitors the dispenser for confirmation signal. No confirmation → CaseHub
escalates → OpenClaw contacts carer via WhatsApp (messaging skill). Every step a genuine
skill — calendar, health tracker, IoT, two messaging channels — none of it browser.

**Calendar + contractor commitment cycle:**
OpenClaw reads your Google Calendar (calendar skill) — contractor is due Thursday. CaseHub
opens the external actor Commitment. 24h before: OpenClaw sends WhatsApp confirmation
request (messaging skill). No response within 2h → CaseHub escalates → OpenClaw tries SMS
(second messaging skill). Day-of: heartbeat monitors arrival confirmation signal. Multiple
skills, one workflow — calendar, two messaging channels, heartbeat monitoring.

**Energy monitoring → governed decision:**
OpenClaw heartbeats on energy tariff APIs (utility skill) and monitors usage via smart
meter integration (Home Assistant skill). When a better tariff is found: posts EVENT to
household observe channel. The EVENT reaches home-agent's context via ChannelContextWindow
(see §8). CaseHub routes to oversight channel for human RESPONSE before any switching
action is taken.

**On browser-based use cases:** A compelling browser-based use case is not ruled out — if
it strongly showcases CaseHub's accountability layer and would generate significant public
traction with OpenClaw's community, it is worth pursuing. But this is a separate objective
from maximising the value of OpenClaw's pre-built skill ecosystem. Both objectives are
valid; they should not be conflated.

### 5.4 External Human Actor Commitment Pattern

The concrete workflow for external actor commitments (not yet implemented):

1. User tells home-agent: "the plumber said he'll be here Thursday between 10am and 12pm"
2. System creates a Commitment with the plumber as the obligor (external actor, no account)
3. A Watchdog is set for Thursday 12pm
4. At Thursday 12pm: if no DONE signal received (agent was home, confirmed arrival), the
   Watchdog fires
5. Escalation: home-agent sends WhatsApp or SMS to the plumber's number asking for ETA
   (OpenClaw messaging skill)
6. If no response within N hours: escalation to household-admin as oversight WorkItem
7. The entire follow-up chain is tracked as a case with tamper-evident record (Level 4)

This pattern applies broadly: any third-party commitment (contractor, doctor, school,
insurance company) becomes a tracked obligation with automated follow-up.

### 5.5 Privacy Partitioning Across Life Domains

Personal life has hard data boundaries that enterprise governance does not typically address:

- Health data must not be visible to finance agents or work agents
- Financial data must not bleed into household agents accessible to children
- Work/professional data must not be visible to household agents
- Children's data has separate access rules from adult household data

This is stronger than ACL on individual channels — it is domain-level isolation.

**Current state:** CaseHub's permission model (Qhorus allowed_writers + RBAC +
CurrentPrincipal) is role and channel based. It does not have structural domain isolation
that prevents cross-domain data bleed at the system level.

The `CaseMemoryStore` and `ChannelContextWindow` must both respect domain boundaries:
facts from health cases must not be recallable by finance agents; health channel messages
must not appear in household agent context windows.

**GDPR relevance:** Art.17 erasure in the ledger applies to personal data. In a personal
life deployment, virtually all case data is personal data. The erasure mechanism must be
first-class, not opt-in.

**Open question:** is privacy partitioning a configuration of the existing permission model
or a structural property of the casehub-life domain model? Not resolved. (§12.4)

### 5.6 Household Permission Topology and M-of-N

Multi-adult households require quorum-based approval for shared decisions:

**Decision categories (proposed, not finalised):**
- Single-party decisions: either adult can approve (grocery order, school pickup, minor tasks)
- Dual-party decisions: both adults must approve (holiday booking, major purchase above
  threshold, significant financial commitment)
- Individual decisions: single named principal only (personal health, professional decisions)
- Junior-accessible: household-junior can request (QUERY) but cannot COMMAND

**Existing machinery that composes:**
- `MultiInstanceCoordinator` — already handles M-of-N WorkItem completion
- RBAC — household-admin, household-member, household-junior roles
- Qhorus `allowed_writers` — which roles can write COMMANDs to which channels
- casehub-engine conditional branching — different paths based on decision type

**Open question:** how is quorum configuration expressed in casehub-life? CasePlanModel
property, Qhorus channel property, or casehub-life-specific configuration entity? (§12.5)

### 5.7 Memory Layer vs. Authoritative External Data

Two distinct problems that must not be conflated:

**Problem A — What agents have done (CaseMemoryStore):**
Facts derived from completed CaseHub cases. "Last time we reviewed energy providers was
March 2026." "Home-agent booked the boiler service with CompanyX on 2026-04-15."
Addressed by the CaseMemoryStore SPI (§4.3).

**Problem B — Ground truth about the user's life (external authoritative data):**
Data that exists independently of CaseHub: Google Calendar, bank feeds, medical records,
smart home sensor readings, email history, contacts, property records. An agent booking
a dentist appointment needs the user's calendar, insurance details, and location — none
of which came from a CaseHub case output.

**The boundary:** CaseMemoryStore captures what agents have done. External authoritative
data is what IS true about the user's life, independent of agent actions.

**Open question:** how does the system make external authoritative data available to agents
before and during cases? (§12.2)

### 5.8 Strategic Positioning — Open Question

Two fundamentally different product directions, not yet chosen:

**Option A — Developer showcase (consistent with devtown and clinical):**
- Target: Java developer evaluating CaseHub for personal life automation
- Tutorial layers structured by foundation module adoption (Level 0 → Level 4)
- Code is production-grade at every layer
- Comparison baseline: OpenClaw alone, or a Zapier/Make automation
- casehub-life looks like devtown and clinical: tutorial-structured with LAYER-LOG.md

**Option B — Consumer product:**
- Target: non-technical household wanting AI-powered life management
- Tutorial layers structured by personal complexity: single person → couple → household
  with children → multi-generational (includes elderly parent)
- Simpler configuration, opinionated defaults, minimal required expertise
- Comparison baseline: Siri Shortcuts, Apple Reminders, a personal assistant app

**Implication:** the choice fundamentally changes the domain model design, tutorial
structure, comparison narrative, and repo entry point. Must be decided before a design
doc is written. Not resolved. (§12.1)

---

## 6. Qhorus Normative Layer — Opportunities for OpenClaw

### 6.1 Commitment Tracking — The "Did It Actually Happen?" Problem

OpenClaw's skill execution is alethic — it describes what happened or didn't happen. The
Qhorus normative layer is deontic — it describes what was promised, what is owed, and what
happens when obligations are not met.

The biggest failure mode in personal AI agents: the agent confirms it will do something,
and the user has no machine-readable record that an obligation exists, no deadline, no
Watchdog. The agent can go quiet with no consequence.

**How Qhorus solves this:**
- User instruction to OpenClaw agent = COMMAND speech act
- Agent acknowledgement = RESPONSE — opens a Commitment
- The Commitment exists independently of the agent's subsequent behaviour
- Watchdog fires at the deadline if DONE never arrives
- The agent cannot silently fail a commitment — expiry is a named state that triggers
  consequents (escalation, notification, alternative action)

This applies to all tasks, not just compliance-sensitive ones.

### 6.2 DECLINE as Semantic Signal — Defeasible Routing

Default logic: "by default, route this task to agent A." This default is defeasible —
it holds unless a reason defeats it.

In OpenClaw, skill failure returns an error. The failure has no semantic content. The
system learns nothing from it.

In Qhorus, DECLINE is a speech act. It carries a machine-readable reason:
- Three DECLINEs citing "insufficient local knowledge" for contractor research → update
  routing default: route to web-research agent, not home-agent
- DECLINE citing "calendar conflict" → retry same agent next available slot

Over time, DECLINE and HANDOFF patterns accumulate into a learned model of agent capability.
This is the precursor to trust scoring — routing defaults adapt before the ledger is active.

### 6.3 HANDOFF for Obligation Transfer

When home-agent passes a task to finance-agent without Qhorus, the obligation evaporates.
With HANDOFF:
- Original Commitment on home-agent closes (DELEGATED terminal state)
- Child Commitment opens on finance-agent
- Watchdog transfers with the obligation — never lost as it moves between agents
- The user can always query: who currently holds this obligation?

**Critical constraint:** HANDOFF cannot launder a permission escalation. The receiving
agent must independently satisfy the ACL of the target channel. Finance-agent must be a
permitted writer on the finance work channel regardless of who initiated the HANDOFF.
This constraint is not yet documented in Qhorus deep-dive or protocols. (§11.9)

### 6.4 Channel Separation — Work / Observe / Oversight

OpenClaw's heartbeat monitoring and task execution share the same conceptual channel.
There is no distinction between a boiler pressure reading (observation) and a purchase
order (obligation). When these mix, agents over-trigger or under-trigger.

The normative channel separation enforces this structurally:

| Channel | Message types | Effect |
|---|---|---|
| `/observe` | STATUS, EVENT | Factual, descriptive; no Commitments created |
| `/work` | COMMAND, RESPONSE, DONE, DECLINE, HANDOFF, FAILURE | Prescriptive; Commitments created and tracked |
| `/oversight` | COMMAND, RESPONSE | Human governance gate; workflow pauses until RESPONSE |

Monitoring agents emit to observe. Task agents emit to work. Spending decisions above
threshold route to oversight for human confirmation. This is architectural, not per-skill
logic.

### 6.5 Oversight Channel as Uniform Human Governance Gate

Currently, every OpenClaw skill that needs human approval implements its own mechanism:
a Telegram message, a WhatsApp prompt, a custom callback. These are inconsistent,
untracked, without deadline, and without audit.

The oversight channel makes this uniform:
- Any risky action routes a COMMAND to the oversight channel
- OpenClaw delivers via the user's preferred messaging app (WhatsApp, Telegram, iMessage)
- Commitment has a deadline: no RESPONSE by 2pm triggers escalation
- Approval is recorded (tamper-evidently at Level 4)

This is the same mechanism for: booking a holiday, authorising a £200 spend, approving
a medical appointment, confirming a contractor quote. One mechanism, consistently applied.

### 6.6 Deontic Permission Model

The normative layer enforces who is permitted to issue COMMANDs, not just who is
authenticated:
- Children: can read observe channels; cannot write COMMANDs to work channels
- Household members: can COMMAND on shared household channels; not financial channels
- Household admin only: can COMMAND on health and financial channels

**Deontic consequence:** a COMMAND from an unauthorised principal never creates a Commitment.
The obligation never opens. No phantom obligations, no false escalations.

Combined with the planned RBAC (§7): three-layer enforcement:
1. Authentication (Claudony — WebAuthn, API key): who is this principal?
2. RBAC (`@RolesAllowed`, `CurrentPrincipal.roles()`): what is this principal permitted to do?
3. Channel ACL (Qhorus `allowed_writers`): can this principal write to this specific channel?

Each gate is independent. A principal can pass authentication and still fail the channel ACL.

### 6.7 STATUS and EVENT — Preventing Monitoring From Creating Spurious Obligations

Without speech act types, the agent must decide in skill logic whether an observation
warrants action. With typed speech acts:
- STATUS: boiler pressure 0.8 bar → below threshold → WorkItem created — but the STATUS
  itself creates no Commitment
- EVENT: energy price spike → routes to finance-agent for decision — the EVENT is not a
  COMMAND; finance-agent decides whether to act
- COMMAND: "book car service" → Commitment opens, Watchdog set

Monitoring agents emit observations freely without accidentally creating obligations.

### 6.8 Default Logic in Routing

Default logic provides the formal underpinning for routing behaviour:
- Default: route household maintenance tasks to home-agent
- Defeated by: DECLINE (with reason), HANDOFF (to named alternative), trust score below
  threshold, overload signal
- Defeated defaults update: future similar tasks route differently without reconfiguration

Over time, DECLINE reasons and HANDOFF patterns become a learned model of agent capability.
This is a natural precursor to full trust scoring — the routing system improves from Level 2
onward, before the ledger is active.

### 6.9 Qhorus ↔ OpenClaw Channel Wiring

**Terminology collision:** OpenClaw "channels" = messaging platform connections (Telegram,
WhatsApp, Slack, Discord). Qhorus "channels" = typed normative communication channels in
the accountability layer. Same word, completely different concepts. In the wired architecture
these are complementary: a Qhorus oversight channel routes a human decision *via* OpenClaw's
WhatsApp delivery. One is the normative structure; the other is the delivery mechanism.

**Write path (OpenClaw → Qhorus):** OpenClaw executes skill, generates output, POSTs to
Qhorus channel endpoint via `deliver: "webhook"`. casehub-openclaw adapter receives it,
wraps in a `MessageDispatch` with appropriate speech act type, calls `MessageService.dispatch()`.
OpenClaw's output becomes a first-class Qhorus message — tracked, committed, Watchdog-
eligible, ledgered. Clean and achievable now without changes to OpenClaw.

**Read path — active (Qhorus → OpenClaw LLM):** when a COMMAND arrives on a Qhorus
channel, `ChannelBackend.post()` (implemented by casehub-openclaw) calls `POST /hooks/agent`
with the COMMAND content. OpenClaw's LLM receives it as a prompt and responds. This is
event-driven, clean, and fits both systems' architectures.

**Read path — passive (observe channel, cross-agent awareness):** this does NOT work
naturally. OpenClaw has no automatic awareness of other agents' channel activity between
heartbeat ticks. Addressed by the `ChannelContextWindow` service (§8).

**Speech act classification — the key design question:**
OpenClaw's LLM outputs natural language. Qhorus expects typed speech acts. Three approaches:

| Approach | How | Reliability | Complexity |
|---|---|---|---|
| Infer from context | Adapter infers type from what triggered the run: heartbeat → STATUS, task completion → DONE | Coarse but zero-friction | Low |
| Skill instruction prefix | SKILL.md instructs LLM to prefix: `[STATUS] Boiler pressure 1.2 bar` | Good — explicit in output | Medium |
| Structured skill output | Skill outputs JSON: `{"type": "STATUS", "content": "..."}` | Highest — no ambiguity | High per-skill |

Approach 1 is the starting point; Approach 3 is the target for important skills.

**ChannelBackend SPI as bidirectional bridge:**
`casehub-openclaw` implements `ChannelBackend` SPI (same as Claudony):
- Qhorus → OpenClaw: `ChannelBackend.post()` → `/hooks/agent` with message content
- OpenClaw → Qhorus: `deliver: webhook` → Qhorus channel endpoint

The full normative loop applies to all OpenClaw agent communications: Commitment tracking,
Watchdog, speech act types, ledger. OpenClaw becomes a participant in the normative mesh,
not just an external execution runtime.

### 6.10 End-to-End Mesh Fit Assessment

The fundamental mismatch: Qhorus's normative mesh assumes persistent channel participants
continuously aware of what others post. OpenClaw is episodic — discrete turns with no
inherent inter-turn memory.

| Pattern | Fit | Notes |
|---|---|---|
| COMMAND received → agent responds → DONE/DECLINE | ✅ Clean | ChannelBackend.post() → /hooks/agent → deliver:webhook |
| Human oversight gate (COMMAND on oversight channel) | ✅ Clean | Same push model; OpenClaw delivers to WhatsApp |
| Commitment tracking on all interactions | ✅ Clean | Qhorus owns this; no OpenClaw changes needed |
| Ledger records all agent communications | ✅ Clean | Qhorus owns this; no OpenClaw changes needed |
| Channel history context at turn start | ⚠️ Requires engineering | ChannelContextWindow + before_prompt_build injection (§8) |
| Observe channel passive watch | ⚠️ Approximation | Heartbeat + ChannelContextWindow injection; not real-time |
| Multi-agent channel awareness | ⚠️ Requires engineering | Cross-channel context injection via ChannelContextWindow |
| Continuous observation (true streaming) | ❌ Not natural | OpenClaw is episodic; approximated by heartbeat |

The active patterns (COMMAND/RESPONSE, oversight gates) are a strong fit. The passive
patterns (observe channel, cross-agent awareness) require the ChannelContextWindow service
and are approximations rather than true persistent subscription. This is a bounded,
known limitation — not blocking, but must be designed around.

---

## 7. RBAC / ACL — Complementary Layers

The planned RBAC implementation complements the Qhorus normative permission model without
overlapping it. Three distinct enforcement points:

| Layer | Mechanism | What it controls |
|---|---|---|
| Authentication | Claudony: WebAuthn passkeys, X-Api-Key | Identity: who is this principal? |
| RBAC (planned) | `@RolesAllowed`, `CurrentPrincipal.roles()` | Authorisation: what is this principal permitted to do? |
| Channel ACL | Qhorus `allowed_writers` | Location: can this principal write to this specific channel? |

For OpenClaw integration: an OpenClaw agent acting on behalf of a principal inherits that
principal's roles. A teenager's device with `household-junior` role cannot trigger a
financial COMMAND — not because the skill checks for it, but because RBAC rejects the REST
call at Claudony, or the dispatch gate rejects the write because `household-junior` is not
in `allowed_writers` on the finance work channel. The skill author writes no permission logic.

**Key deontic consequence:** a COMMAND from an unauthorised principal never creates a
Commitment. The obligation never opens. No phantom obligations, no false escalations.

**HANDOFF permission constraint (to be documented):** HANDOFF cannot escalate permissions —
the receiving agent must independently satisfy the target channel ACL. Not yet documented
in the Qhorus deep-dive or any protocol. Must be added before RBAC is implemented. (§11.9)

---

## 8. ChannelContextWindow — Bridging Episodic and Continuous

### 8.1 What It Is

A short-term, agent-scoped, TTL-evicting buffer of Qhorus channel activity — purpose-built
to bridge OpenClaw's episodic model with Qhorus's continuous channel mesh.

| Store | Lifespan | Content | Purpose |
|---|---|---|---|
| Ledger | Permanent | Tamper-evident event chain | Compliance audit |
| CaseMemoryStore | Indefinite | Semantic facts, entity relationships | Cross-case knowledge recall |
| **ChannelContextWindow** | **Minutes/hours (TTL)** | **Raw channel messages, sliding window** | **LLM context injection at turn start** |

These three stores serve different consumers and must not be conflated. The
ChannelContextWindow is NOT in the critical path for correctness — commitments, Watchdog,
and ledger are completely unaffected by whether the cache works. A cache miss means the
agent had less context for one turn. It does not break the system.

### 8.2 Why It's Necessary — Concrete Examples

Without cross-channel context injection, each OpenClaw agent operates in an information
silo. It knows only: (a) the single message that woke it, (b) what it itself did in prior
turns via its own memory files. It does NOT know what other agents are observing, what the
current state of the household or case is, or what another agent just reported.

**Example 1 — Grocery agent ignores a budget warning**

*Without ChannelContextWindow:*
finance-agent posted to the household observe channel 20 minutes ago: *"Monthly discretionary
budget exhausted — essentials only until month end."*
grocery-agent's heartbeat fires. COMMAND: run this week's shopping order. It executes the
full regular shop — wine, premium coffee, non-essentials. £180 charged. The budget warning
was there. The grocery agent was connected to the same mesh. But it had no idea.

*With ChannelContextWindow:*
grocery-agent wakes. `before_prompt_build` injects: *"finance-agent posted 20 min ago on
household/observe: discretionary budget exhausted, essentials only."* LLM sees this, switches
to essentials-only basket, posts STATUS explaining the adjustment, creates an oversight
WorkItem for any additions. User gets a WhatsApp: *"Grocery order trimmed to essentials
given the budget position — tap to review additions."*

This is not an edge case. It happens every month. Without the cache, the agents are not a
mesh — they are independent processes that happen to share a commitment framework.

**Example 2 — Medical agent asks an irrelevant question**

*Without ChannelContextWindow:*
Smart home sensors have been posting to health/observe all morning: 9am patient not yet up,
10am still in bedroom, 11:02am movement detected in kitchen. health-agent heartbeat fires
at 11:05am for the morning medication check. It knows none of this. It sends a generic
WhatsApp: *"Have you taken your morning medication?"*

*With ChannelContextWindow:*
health-agent wakes. Hook injects the morning movement log. LLM sees patient was in the
kitchen — where the medication is kept — 3 minutes ago. Response: *"I noticed you were in
the kitchen just now — did you take your morning tablets while you were there?"*

In a care coordination context — elderly parent, multiple carers — this is the difference
between technology that builds trust and technology that gets turned off.

**Example 3 — Security finding missed by code review agent (enterprise)**

*Without ChannelContextWindow:*
security-agent runs parallel to general code review. It posts two EVENTs to the case observe
channel: *"Possible credential pattern in auth.java line 47"*, *"Hardcoded endpoint in
config.py."* code-review-agent's SLA timer fires. It completes its structural review, posts
DONE with a quality assessment. No mention of the security findings. PR approved.

*With ChannelContextWindow:*
code-review-agent wakes. Hook injects security-agent's findings. LLM sees the credential
flag, escalates case severity, creates a security-review WorkItem with specific file
references, holds its own DONE until the security WorkItem resolves. Additionally: the case
ledger shows code-review-agent had the security findings in context at decision time. Without
the cache, you cannot prove this. With it, you can.

**Example 4 — Travel agent books a trip that conflicts with a deadline**

*Without ChannelContextWindow:*
calendar-agent posted to household/observe at 9am: *"Work deadline Friday 5pm — Project X
deliverable."* travel-agent's booking case starts at 11am. COMMAND: book weekend flights
departing Friday evening. Books a 6pm departure. User misses the deadline.

*With ChannelContextWindow:*
travel-agent wakes. Hook injects calendar-agent's deadline notice. LLM sees the 5pm
deadline, flags the conflict: *"Friday 6pm departure is tight against your 5pm project
deadline — want Saturday morning instead?"* Routes to oversight channel for human decision.

The agent did not need to know about project deadlines in advance. It needed to know what
the calendar-agent had observed and posted. One line of injected context prevents a real
problem.

### 8.3 Why Not Just Query the Ledger?

The ledger has all of this. But it is designed for tamper-evident audit, not LLM context
assembly:

- It stores a flat sequence of all lifecycle events across the entire platform — not
  pre-filtered by agent relevance
- Querying for "recent channel messages relevant to this agent, formatted for a system
  prompt" requires significant transformation that is not the ledger's job
- It has no concept of "what's relevant for agent X right now" — that is a routing concern,
  not a compliance concern
- The ledger's Merkle chain is optimised for verification, not millisecond context retrieval

The ChannelContextWindow is not storing new data. It is presenting existing Qhorus channel
activity in the right format, for the right consumer, at the right time. The analogy: a bank
has both a transaction ledger and a current balance display — they serve different consumers.
The ledger is the permanent tamper-evident record. The window is the live operational view.

### 8.4 The Complexity Justification

The concern about unnecessary complexity is valid and worth addressing directly.

**What the cache actually is:**
- A `MessageObserver` implementation: ~3–4 lines to register, passively receives all
  Qhorus messages at near-zero cost to the dispatch path
- A per-channel ring buffer: a standard data structure, configurable size and TTL
- A single REST endpoint: `GET /channel-context/{agentId}?since={sequenceNumber}`
- A Python SDK `before_prompt_build` hook: ~20 lines, fires before each agent turn

**The alternative complexity:** without this, every skill that needs cross-agent awareness
must explicitly call other agents' endpoints, maintain its own state, and handle its own
staleness. That produces N bespoke per-skill solutions instead of one shared infrastructure
piece. The cache is simpler than the workarounds it replaces.

**The visibility test:** a user who installs casehub-openclaw and sees grocery-agent ignore
a finance-agent budget warning will conclude the integration doesn't work. The cache is what
makes the multi-agent mesh visible and tangible to users. Without it, the normative layer is
invisible — commitments track correctly, ledger records faithfully, but agents behave as if
isolated. Correct infrastructure, broken user experience.

### 8.5 Technical Architecture

**MessageObserver SPI — the collection layer:**
casehub-openclaw implements `MessageObserver` SPI in casehub-qhorus. Receives every
dispatched message across all channels passively. Writes to per-channel ring buffers.
The observer must never throw — Qhorus fanOut to non-default backends is non-fatal by
design. Catch, log, increment metric, continue.

**Ring buffer — the storage layer:**
Per-channel ring buffer of recent messages. Configurable:
- Max messages per channel (e.g. 100)
- TTL (e.g. 30 minutes)
- Drop policy on overflow: always keep newest, drop oldest

**REST endpoint — the query layer:**
`GET /channel-context/{agentId}?since={sequenceNumber}`
Returns: messages on channels associated with the agent, since the specified sequence
number, formatted for LLM system prompt injection. Single call, pre-filtered, pre-formatted.

**`since` cursor — use sequenceNumber, not timestamp:**
Qhorus messages have a monotonic `sequenceNumber`. The casehub-openclaw component tracks
the last sequenceNumber seen per agent session. Using wall-clock timestamps introduces
clock skew risk; sequenceNumber is unambiguous.

**Python SDK hook — the injection layer:**
```python
@agent.on("before_prompt_build")
def inject_channel_context(ctx):
    recent = cache_client.get(
        agent_id=ctx.agent_id,
        since=ctx.last_sequence_number
    )
    if recent.overflow:
        note = f"Note: {recent.dropped} messages not retained (volume). Full history in ledger."
    elif recent.empty:
        note = f"No channel activity in the last {recent.ttl_minutes} minutes."
    else:
        note = format_channel_messages(recent.messages)
    return { "appendSystemContext": note }
```

`appendSystemContext` lands in the system prompt — rebuilt every turn, never compacted.
This is the compaction-safe injection point. The `before_prompt_build` hook in v2 is
preferred over `prependContext` / `before_agent_start` (v1) which could silently disappear
if `allowPromptInjection` is disabled by an operator.

**Alternative — casehub-openclaw as pluggable context engine:**
If casehub-openclaw provides `kind: "context-engine"`, OpenClaw delegates all context
assembly to it. The context engine can then inject Qhorus channel history, CaseMemoryStore
facts, and WorkerContextProvider lineage (same as Claudony does with ledger lineage) as a
unified context package. More powerful than the hook approach; more complex to implement.

**Cross-channel awareness:**
The endpoint supports optional cross-channel context: messages from observe channels that
the agent is registered to watch (not just channels it owns). This enables home-agent to see
finance-agent's recent observe channel posts without subscribing to every channel individually.

### 8.6 Reliability and Failure Modes

**Two-layer reliability contract:**

| Layer | Mechanism | Reliability guarantee |
|---|---|---|
| Correctness | Qhorus (commitments, Watchdog, ledger) | Reliable — not affected by cache |
| Intelligence | ChannelContextWindow | Best-effort — graceful degradation |

A cache miss means the agent had less context for one turn. It does not break the system,
lose a commitment, or corrupt the audit record.

**Failure mode: ring buffer overflow**
If message volume is high or heartbeat interval is long, the buffer fills and older messages
are evicted before the agent wakes. Fix: configurable size; metric on overflow frequency.
When overflow occurs, inject an explicit signal: *"Note: N messages not retained (high
volume). Full history available in ledger."* The LLM knows it has a partial view.

**Failure mode: TTL expiry before agent wakes**
If an agent is dormant beyond the TTL, messages expire before the window is queried. The
agent wakes to an empty window. Fix: configurable TTL. An empty window must never return
silently — inject: *"No channel activity retained in the last {TTL} — agent was dormant."*
Absence of activity is itself informative.

**Failure mode: cache service unavailable**
The REST endpoint is down when the Python SDK hook fires. Fix: fail open — agent proceeds
without context injection. Turn still completes; the COMMAND that triggered it is still
processed. Log and alert on repeated failures; do not break the agent turn.

**Failure mode: MessageObserver write failure**
Observer fires but cache write throws. Fix: catch, log, increment metric — never propagate
back to Qhorus. The message is already in the ledger; the only loss is the cache copy.

**Failure mode: multiple OpenClaw instances**
Per-agent last-turn sequenceNumber needs consistency across instances. Options: sticky
routing (each agentId always hits the same cache instance), shared cache (Redis or similar),
or accept per-instance state with slight risk of re-delivering messages the agent has
already seen (consequence: redundant context, not missing context).

**Design rules:**
1. Never fail a Qhorus fanOut because of cache write failure
2. Always signal partial views — overflow and TTL expiry inject explicit notices, not silent
   empty windows
3. Use sequenceNumber as the since cursor — not wall-clock timestamp
4. Fail open on cache unavailability — agent turn continues with less context
5. Buffer size and TTL are deployment configuration — tuned to heartbeat interval and
   expected message volume
6. Alert on repeated failures — in health monitoring, not the critical alert path

---

## 9. What Lives Where

### 9.1 New Foundation Modules

**`CaseMemoryStore` — optional modules in `casehub-platform` (casehubio/platform#27):**

A general platform capability benefiting all CaseHub consumers — not OpenClaw-specific.
Module structure mirrors the existing PreferenceProvider and CurrentPrincipal pattern:

| Module | Artifact | Purpose |
|---|---|---|
| `platform-api` (existing) | `casehub-platform-api` | `CaseMemoryStore` SPI added here alongside `CurrentPrincipal` and `PreferenceProvider` |
| `platform` (existing) | `casehub-platform` | `@DefaultBean` no-op — zero overhead when no adapter installed |
| `memory-memori/` (new) | `casehub-memory-memori` | SQL-native Postgres adapter (default — zero extra infra) |
| `memory-mem0/` (new) | `casehub-memory-mem0` | Vector + BM25 adapter (Docker + pgvector) |
| `memory-graphiti/` (new) | `casehub-memory-graphiti` | Temporal knowledge graph adapter (regulated domains) |

SPI design constraints:
- Permission-aware recall enforced at the SPI layer via `CurrentPrincipal` +
  `GroupMembershipProvider` — not delegated to the backend service
- Domain isolation at the SPI layer: facts from one domain must not be recallable by
  agents in a different domain, regardless of backend
- Fact emission: completed cases emit structured facts; mechanism TBD (CDI observer
  pattern consistent with existing ledger capture)
- In-memory `@Alternative @Priority(1)` for test isolation

Consumer issues tracking adoption: casehubio/devtown#43, casehubio/clinical#33,
casehubio/aml#32.

Pluggable backend adapters (see §4.3a for full evaluation):

| Adapter | Backend | Infrastructure | Best for |
|---|---|---|---|
| Default | **Memori** | Postgres only (existing) | Zero-cost entry; all deployments; human-readable SQL |
| Standard | **Mem0** | Docker + pgvector | Larger ecosystem; vector retrieval |
| Temporal | **Graphiti** | Graphiti + Neo4j/FalkorDB/Kuzu | Regulated domains; temporal queries |

All adapters are REST-based (Quarkus RestClient). Backends are swappable via CDI priority.
The SPI layer enforces CaseHub's permission model regardless of which adapter is active.

**`ActionRiskClassifier` SPI in `casehub-engine-api`**:
- `classify(PlannedAction) → RiskDecision`
- `RiskDecision`: AUTONOMOUS | GATE_REQUIRED(reason, reversible)
- Engine creates a WorkItem gate automatically on GATE_REQUIRED
- Worker has no knowledge of gate mechanism
- Default: AUTONOMOUS (existing behaviour unchanged unless classifier is present)

**`modelHint` field on worker capability descriptor (in `casehub-engine-api`)**:
- Values: REASONING, MECHANICAL, BALANCED
- `WorkerProvisioner` implementations (Claudony, casehub-openclaw) respect the hint
- Guides model selection without prescribing it — the provisioner decides how to apply it

### 9.2 New Integration Module — `casehub-openclaw`

New repo, integration tier — analogous to Claudony. Contains both Java (Quarkus) and
Python components.

**Java components:**
- Implements `WorkerProvisioner` SPI: provisions OpenClaw instances as CaseHub workers
  via `POST /hooks/agent` on demand (direct call mode) — no heartbeat required for
  in-case steps
- Implements `CaseChannelProvider` SPI: creates Qhorus channels per case/purpose
- Implements `WorkerStatusListener` SPI: maps OpenClaw session lifecycle to CaseHub
  worker states
- Implements `ChannelBackend` SPI: bidirectional bridge
  - Qhorus → OpenClaw: `ChannelBackend.post()` → `POST /hooks/agent`
  - OpenClaw → Qhorus: webhook delivery endpoint that receives OpenClaw output and calls
    `MessageService.dispatch()` with appropriate speech act classification
- Implements `MessageObserver` SPI: populates the ChannelContextWindow ring buffers
- Hosts `ChannelContextWindow` REST service: `GET /channel-context/{agentId}?since={seq}`
- Optionally provides pluggable context engine (`kind: "context-engine"`) for deeper
  context assembly integration
- Depends on: casehub-qhorus, casehub-engine; does not depend on casehub-ledger (optional)

**Python component:**
- OpenClaw plugin implementing `before_prompt_build` hook
- Calls ChannelContextWindow REST endpoint before each agent turn
- Injects result as `appendSystemContext` (compaction-safe, system-prompt space)
- Handles overflow and TTL signalling explicitly — never silently returns empty
- Tracks last-turn sequenceNumber per agent session

**Two invocation patterns supported by casehub-openclaw:**

| Pattern | Trigger | OpenClaw role | CaseHub role |
|---|---|---|---|
| Monitor | OpenClaw heartbeat detects condition | Autonomous — decides when to trigger | Receives created case/WorkItem |
| Execute | CaseHub case step | Orchestrated — executes on demand via /hooks/agent | Determines timing, consumes result |

### 9.3 New Application Repo — `casehub-life`

New repo, application tier — analogous to devtown and casehub-clinical.

- Domain model: to be designed (§11.11 — gap)
- Capability tags: household-management, health-coordination, financial-planning,
  family-scheduling, travel-planning, legal-deadline, contractor-coordination
- Trust dimensions: deadline-reliability, cost-accuracy, factual-accuracy, proactive-alerting
- CasePlanModels: appointment-cycle, home-maintenance-cycle, financial-review,
  travel-plan, contractor-coordination, care-coordination
- Actor taxonomy: AI agents (OpenClaw personas) + household principals (RBAC roles) +
  external human actors (contractors, doctors — gap: §11.4)
- Tutorial layers: structure depends on strategic positioning decision (§5.8 — unresolved)
- Uses casehub-openclaw as the worker provisioner

### 9.4 OpenClaw Skill Pack (outside CaseHub repos)

A set of OpenClaw skills enabling Direction 2 (OpenClaw → CaseHub). Published to ClawHub:

- `casehub-workitem` — create a WorkItem from natural language with deadline and assignee
- `casehub-case` — start a CasePlanModel for a complex workflow
- `casehub-queue` — route a task to a named queue
- `casehub-status` — query status of a running case
- `casehub-commit` — acknowledge a COMMAND as a Commitment from within a skill
- `casehub-done` — close a Commitment from within a skill
- `casehub-context` — retrieve recent channel context from ChannelContextWindow explicitly
  (for use cases where automatic hook injection is not active)

These are opt-in. A bare OpenClaw install is unchanged.

### 9.5 Enterprise Deployment Considerations

For enterprise co-worker deployments (Sai/Coworker pattern on CaseHub):
- `casehub-openclaw` is the worker provisioner for OpenClaw-based enterprise agents
- Claudony remains the worker provisioner for Claude CLI-based enterprise agents
- `CaseMemoryStore` provides the OM1 equivalent for enterprise case context
- `ActionRiskClassifier` provides the Sai approval gate equivalent, uniformly
- `casehub-ledger` provides the compliance audit trail that Sai and Coworker explicitly lack
- RBAC provides the enterprise access control that neither competitor has formalised

---

## 10. Open Source Memory Backend Evaluation

See §4.3a for the full table. Summary of disposition:

| Project | Disposition | Reason |
|---|---|---|
| Memori | ✅ Default adapter | SQL-native, Postgres only, zero extra infra, human-readable |
| Mem0 | ✅ Standard adapter | 48k stars, full REST, Apache 2.0, vector + BM25 |
| Graphiti | ✅ Temporal adapter | Bitemporal edges, 63–91% LongMemEval, Apache 2.0 |
| Hindsight | 🔲 Reserved | State-of-art temporal, MIT license; smaller ecosystem — revisit |
| Cognee | ❌ Ruled out | Python-centric, smaller community |
| Letta | ❌ Ruled out | Episodic focus only, not a knowledge graph |
| LangChain memory | ❌ Ruled out | Framework component, not a service, Python-only |
| GraphRAG | ❌ Ruled out | Research quality, Azure-dependent, too buggy to self-host |

---

## 11. Gaps and Limitations

### 11.1 No Semantic Memory Layer (CaseMemoryStore)

**Gap:** CaseHub has no queryable semantic fact index. The ledger is immutable history, not
a knowledge graph. Every case starts cold — no prior context is automatically available.

**Impact across all application repos:**
- devtown: contributor history, module risk signals, and agent capability facts are
  invisible at case open — manually surfaced or ignored
- clinical: patient history, site compliance patterns, and drug AE patterns require manual
  record review — slow and inconsistent
- AML: entity history, prior SAR filings, and counterparty networks require hours of manual
  research per investigation

**This is a general platform gap, not an OpenClaw-specific concern.** The gap affects all
three existing application repos and any future consumer, regardless of worker type.

**Proposed resolution:** optional modules in `casehub-platform` — `CaseMemoryStore` SPI
in `platform-api`, @DefaultBean no-op in `platform`, optional adapter modules for Memori
(default), Mem0, and Graphiti. See §4.3a and §9.1. Tracking: casehubio/platform#27.

Consumer adoption tracked in: casehubio/devtown#43, casehubio/clinical#33,
casehubio/aml#32.

**Critical design constraint:** all evaluated backends scope memory by their own
`userId`/`sessionId` model. Permission-aware recall and domain isolation must be enforced
at the SPI layer. Non-negotiable for all three adapter options.

**Open questions:** how are facts emitted from cases? (§12.6); how does the store relate
to authoritative external data? (§12.2)

### 11.2 No ActionRiskClassifier SPI

**Gap:** workers have no mechanism to declare action risk and trigger a CaseHub gate
automatically. Workers must either know CaseHub's internal gate mechanism or implement
per-agent approval logic.

**Impact:** bounded autonomy is replicated ad-hoc per skill rather than enforced
structurally. The uniform oversight channel pattern (§6.5) cannot be triggered automatically.

**Proposed resolution:** `ActionRiskClassifier` SPI in `casehub-engine-api`. See §9.1.

### 11.3 No modelHint on Worker Descriptor

**Gap:** `WorkerProvisioner` SPI provisions workers but has no mechanism to guide model
tier selection.

**Impact:** suboptimal cost/capability tradeoff — REASONING tasks provisioned with
MECHANICAL models or vice versa.

**Proposed resolution:** `modelHint` field on worker capability descriptor. See §9.1.

### 11.4 No External Human Actor Representation

**Gap:** CaseHub's actor model covers authenticated AI agents and authenticated human
principals. No representation for external human actors (contractors, doctors, service
providers) who are obligors but have no CaseHub account.

**Impact:** the external actor commitment pattern (§5.4) cannot be implemented.

**Proposed resolution:** requires design:
- An `ExternalActor` entity in casehub-qhorus-api (name, contact info, preferred channel)
- Commitments with `ExternalActor` as obligor, Watchdog fires, follow-up via OpenClaw
  multi-channel messaging
- No authentication required — external actors are tracked, not authenticated

Not resolved. Needs design before casehub-life can handle contractor coordination.

### 11.5 Memory Layer / External Authoritative Data Boundary

**Gap:** no mechanism for agents to read authoritative external data sources (Google
Calendar, bank feeds, medical records, smart home sensors, email) as context before or
during cases. CaseMemoryStore captures what agents have done; it does not capture ground
truth from external systems.

**Impact:** agents starting a new case have no access to the user's calendar, financial
state, or home sensor data unless the skill explicitly fetches it per-turn.

**Proposed resolution:** requires design. The boundary between CaseMemoryStore and an
external data connector layer must be defined. Not resolved. (§12.2)

### 11.6 Privacy Domain Partitioning Not Implemented

**Gap:** no structural isolation between personal life data domains (health / finance /
work / household). Current permission model is role and channel based.

**Impact:** health facts in the memory layer could be recalled by finance agents unless
role configuration explicitly prevents it. Configuration-based isolation is fragile.

**Proposed resolution:** requires design. Not resolved. (§12.4)

### 11.7 OpenClaw as WorkerProvisioner Not Implemented

**Gap:** `WorkerProvisioner` SPI is defined in casehub-engine-api and implemented in
Claudony. No implementation exists for OpenClaw.

**Impact:** Direction 1 (CaseHub → OpenClaw) is architecturally clear but not buildable.

**Proposed resolution:** `casehub-openclaw` integration module. See §9.2.

### 11.8 OpenClaw → CaseHub Skill Surface Not Implemented

**Gap:** no OpenClaw skills exist for creating WorkItems, starting cases, or querying
case status.

**Impact:** Direction 2 (OpenClaw → CaseHub) is not accessible to OpenClaw users.

**Proposed resolution:** casehub skill pack for OpenClaw. See §9.4.

### 11.9 HANDOFF Permission Constraint Not Documented

**Gap:** the constraint that HANDOFF cannot escalate permissions — receiving agent must
independently satisfy the target channel ACL — is not documented in the Qhorus deep-dive,
normative layer documentation, or any protocol file.

**Impact:** a developer could inadvertently design a HANDOFF-based permission escalation.
Correctness and security concern once RBAC is active.

**Proposed resolution:** document in casehub-qhorus.md and in a protocol file when RBAC
lands.

### 11.10 Household M-of-N Quorum Configuration Not Designed

**Gap:** `MultiInstanceCoordinator` handles M-of-N task completion, but no mechanism
exists for configuring which household decisions require which quorum.

**Impact:** dual-party approval for major purchases is not implementable without this.

**Proposed resolution:** requires design within casehub-life domain model. Not resolved.
(§12.5)

### 11.11 casehub-life Domain Model Not Designed

**Gap:** the casehub-life application repo does not exist. No domain model, entities,
capability tags, trust dimensions, CasePlanModels, tutorial layer structure, or comparison
baseline.

**Impact:** all casehub-life discussion is currently conceptual.

**Prerequisite:** strategic positioning decision (§5.8 — developer showcase vs. consumer
product). This must be resolved first. (§12.1)

### 11.12 ChannelContextWindow Not Implemented

**Gap:** no service exists to buffer Qhorus channel activity for OpenClaw agent context
injection. The `MessageObserver` SPI, ring buffer, REST endpoint, and Python SDK hook
described in §8 are not built.

**Impact:** the passive observation patterns and multi-agent channel awareness problems
(§6.10) have no solution. Agents operate in information silos despite sharing a mesh.

**Proposed resolution:** implement as part of `casehub-openclaw` module. See §9.2.

### 11.13 OpenClaw Mesh Participation Is Partially Approximated (Known Limitation)

**Not a gap — a known, bounded limitation of the architecture:**
The active patterns (COMMAND/RESPONSE, oversight gates) are a strong, clean fit.
The passive patterns (observe channel continuous subscription, true real-time cross-agent
awareness) are approximations: heartbeat + ChannelContextWindow injection at turn start
rather than true persistent channel subscription.

**Impact:** agents have a sliding-window view of channel activity, not a real-time stream.
A message posted 1 second before an agent's turn starts is seen; a message posted 1 second
after the agent turns starts may not be seen until the next turn. For heartbeat-interval
monitoring use cases this is acceptable. For sub-second coordination it is not.

**Mitigation:** the direct call mode (`POST /hooks/agent`) can be used for time-sensitive
coordination — CaseHub fires the agent immediately when coordination is needed rather than
waiting for the next heartbeat tick.

### 11.14 OpenClaw session:start Hook Not Yet Implemented (OpenClaw Gap)

**Gap (in OpenClaw, not CaseHub):** the `session:start` lifecycle hook is listed under
"Future Events / Planned event types" in OpenClaw documentation (issue #48383). Channel
history backfill on session start is an open feature request (issue #27231), not shipped.

**Impact on casehub-openclaw:** the Python SDK `before_prompt_build` hook (§8.5) works
today and is the correct approach. The `session:start` hook, when available, would provide
an additional integration point for one-time context restoration at session creation.

**No action required from CaseHub:** monitor OpenClaw for implementation; update
casehub-openclaw Python component when available.

---

## 12. Open Questions

These questions were explicitly identified as unresolved and must be addressed before
design work can proceed:

1. **Strategic positioning of casehub-life:** developer showcase (like devtown/clinical) or
   consumer product? Drives tutorial structure, domain model complexity, comparison baseline,
   and entry point design. (§5.8)

2. **External authoritative data boundary:** how does the system make external data (calendar,
   bank, medical records, smart home) available as agent context? Is this inside
   CaseMemoryStore, a separate connector layer, or handled entirely by OpenClaw skills? (§5.7)

3. **External human actor model:** how are external obligors (contractors, doctors) represented?
   What entity holds their commitment? How does follow-up trigger via OpenClaw? (§5.4, §11.4)

4. **Privacy domain partitioning:** configuration of existing permission model or structural
   property of casehub-life domain model? How does it extend to ChannelContextWindow? (§5.5)

5. **Household M-of-N quorum configuration:** how is quorum expressed — CasePlanModel
   property, Qhorus channel property, or casehub-life domain entity? (§5.6)

6. **CaseMemoryStore fact emission:** how do completed cases emit facts to the memory store?
   CDI observer (consistent with existing ledger pattern)? Explicit API call from case
   definition? Automatic extraction from ledger entries? (§11.1)

7. **casehub-memory module placement:** standalone repo or module within casehub-platform
   or casehub-ledger? (§9.1)

8. **Speech act classification approach:** which approach for classifying OpenClaw LLM
   output as Qhorus speech acts — infer from context, skill instruction prefix, or
   structured JSON output? Likely graduated: infer first, move to structured per-skill. (§6.9)

9. **`/tools/invoke` endpoint — direct skill invocation:** the OpenClaw main repo README
   mentions a `/tools/invoke` endpoint requiring `sessions_spawn` permission. Not fully
   documented. Investigate whether this enables direct skill invocation by name, which would
   strengthen the casehub-openclaw execute pattern. (§3.4)

10. **ChannelContextWindow — pluggable context engine vs. hook:** should casehub-openclaw
    implement a full `kind: "context-engine"` plugin for OpenClaw, or is the
    `before_prompt_build` hook sufficient? The context engine is more powerful but more
    complex. (§8.5)

---

## 13. What Was Explicitly Ruled Out

Items explicitly excluded — not deferred, not reconsidered. Notes on why, to avoid
retreading ground:

- **Sai's vision-based computer-use stack:** OpenClaw already handles browser automation via
  CDP snapshots, which is faster and more reliable. Anthropic's own guidance: APIs before
  computer-use. Vision-based is a last resort.

- **Coworker's model routing infrastructure:** too complex and managed-service in nature.
  `modelHint` on the worker descriptor is the appropriate abstraction level.

- **Treating low-compliance personal use cases as outside CaseHub's scope:** revised during
  conversation. casehub-work provides valuable task lifecycle and SLA enforcement at Level 1
  without the ledger. A grocery order with a deadline is a WorkItem. Valuable without
  tamper-evidence.

- **Browser MCP as the primary OpenClaw integration value:** valid as a fallback, but not
  what distinguishes OpenClaw. The real value is the 5,400+ pre-built platform integration
  skills (banking, calendar, Home Assistant, health trackers, social media). Use cases should
  be designed around those, not generic browser automation, unless the browser use case is
  compelling enough to showcase CaseHub specifically — in which case it is a separate,
  orthogonal objective.

- **CaseHub as a general life OS:** the value is in structured accountability for things
  that matter — health, finance, legal, care. Casual reminders and grocery lists benefit from
  Level 1 (casehub-work SLA) but that is not the showcase.

- **LangChain memory modules:** a Python framework component, not a standalone service.
  No language-agnostic REST API. Not applicable as a CaseMemoryStore backend.

- **Microsoft GraphRAG:** research quality. Too buggy for self-hosting; Azure deployment
  only; hours to launch due to Python dependency issues. Not production-ready.

- **Building CaseMemoryStore from scratch without a backend:** unnecessary given the
  quality of open source options. The SPI adapter pattern provides the right abstraction
  without re-implementing retrieval, embedding, or graph traversal.

- **Cognee as CaseMemoryStore backend:** Python-centric, smaller community, cloud less
  mature. Hindsight is a more interesting smaller-ecosystem option if Mem0 and Graphiti
  are insufficient — Cognee is not the better choice.

- **Letta as CaseMemoryStore backend:** episodic and context-window management focus —
  not designed as a semantic knowledge graph. Not the right tool for the CaseMemoryStore
  use case.

- **Making ChannelContextWindow reliable as a message bus:** it is a best-effort context
  cache, not a delivery guarantee layer. That is the correct design. Adding full delivery
  guarantees would make it a second message bus — exactly what it should not be. The Qhorus
  commitment lifecycle and ledger provide correctness guarantees; the cache improves agent
  intelligence only.
