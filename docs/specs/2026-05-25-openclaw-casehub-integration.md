# Research Spec: CaseHub × OpenClaw — Life and Enterprise Automation

**Status:** Research / Pre-design — no implementation decisions made  
**Date:** 2026-05-25  
**Origin:** Exploratory conversation — casehubio/parent session 2026-05-25

---

## 1. Purpose

This document captures a structured research conversation exploring how CaseHub could
integrate with OpenClaw and related platforms (Sai, Coworker.ai) to serve both household
personal life automation and enterprise co-worker automation use cases. It is a pre-design
artefact: it records findings, identifies opportunities, names gaps, and defers implementation
decisions to follow-on specs and issues.

Nothing in this document is ruled in for implementation. Nothing is yet ruled out unless
explicitly stated.

---

## 2. Platform Landscape

### 2.1 OpenClaw

**What it is:** Open-source, self-hosted personal AI agent. Reached 250,000+ GitHub stars
within 60 days of launch — the fastest-growing project on GitHub at that rate.

**Architecture:**
- Heartbeat-based execution: a persistent background process checks a task list at regular
  intervals and acts autonomously without user input
- 20+ messaging platforms as the primary UI: WhatsApp, Telegram, Slack, Discord, iMessage,
  Teams, Signal, and others — the agent lives where the user already is, eliminating
  context-switching
- 100+ built-in skills; 5,400+ community-built skills in the Awesome OpenClaw registry
- Multi-LLM backend support: Claude, DeepSeek, GPT models, local models
- Browser automation via CDP-based snapshot system (structured, not vision-based)
- Companion tool Peekaboo: screenshot and visual QA for agents on macOS
- Docker and self-hosted deployment; can be air-gapped
- Surfaces human decision points: agent runs autonomously, interrupts only when a decision
  is required

**Target users:** individual users automating personal workflows; developers building
autonomous agents; teams adopting agentic workflows.

**What it does NOT do:**
- No formal commitment or obligation lifecycle — skill execution is fire-and-forget
- No tamper-evident audit
- No formal multi-agent coordination protocol
- No SLA enforcement or escalation
- No trust scoring

### 2.2 Sai by Simular AI

**What it is:** Always-on desktop AI co-worker using computer-use (vision-based) interaction
with arbitrary GUI applications. Powered by Simular's Agent S framework.

**Architecture:**
- Perception: vision-only (raw screenshots, not DOM). Mixture of Grounding (MoG) routes
  different UI elements to specialised perception experts rather than a monolithic LLM
- Neuro-symbolic approach: generalist model handles high-level planning; specialist models
  handle low-level execution (button localisation, text highlighting)
- Benchmark progression (OSWorld): Agent S 20.6% → S2 48.8% → S3 69.9% (human level: 72%)
- Agent S3 adds native code generation/execution (Python/Bash) as an alternative to pure
  GUI interaction
- Critical action approval gates: before executing actions classified as monetary,
  irreversible, or involving sensitive data, Sai pauses and requests explicit human approval
- Primarily single-agent: no documented multi-agent coordination
- No A2A or MCP protocol usage
- No open API or plugin SDK: integration is via browser/desktop UI automation only
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

**What it is:** Enterprise AI agent orchestration platform. Importantly: NOT computer-use.
Agents execute via API calls to connected systems (100+ integrations). The key differentiator
is OM1 — Organisational Memory.

**OM1 (Organisational Memory):**
- Decomposes every document, message, and tool output into atomic facts
- Discovers entities (people, companies, projects, tasks) across 120+ relationship dimensions
- Maps entity relationships continuously as connected tools are indexed
- Pre-generates summaries and computes centrality scores for fast recall
- Permission-aware: recall respects the principal's access rights across connected systems
- Sub-second graph traversal: context available to agents in milliseconds rather than the
  seconds required by sequential tool calls
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
  automation. Computer-use is a fallback for when no structured API exists, not a replacement
  for API integrations.

---

## 3. Strategic Positioning

### 3.1 CaseHub and OpenClaw Are Complementary Layers

CaseHub and OpenClaw do not compete. They address different layers of the same problem:

| Dimension | OpenClaw | CaseHub |
|---|---|---|
| What it does | Executes tasks (browser, messaging, cron, 5,400 skills) | Governs agent interactions (commitment, SLA, audit, trust, escalation) |
| Execution model | Heartbeat / fire-and-forget skills | Case orchestration with formal lifecycle |
| Human interaction | Natural language task input | Formal speech acts (COMMAND → RESPONSE, WorkItem gates) |
| Multi-agent | Skills chain; no formal coordination | Full commitment lifecycle, DELEGATED, HANDOFF |
| Accountability | None — best-effort | Merkle ledger, tamper-evident, Bayesian trust scoring |
| Failure handling | Silent failure or error log | SLA breach → escalation → human gate |
| Memory | None across sessions | Ledger (immutable history) — semantic index: gap (see §9) |

OpenClaw is excellent execution plumbing. CaseHub is the accountability mesh that sits around
it for anything that matters. They compose naturally: OpenClaw workers inside CaseHub cases,
with CaseHub providing the governance layer OpenClaw explicitly does not have.

### 3.2 The Bidirectional Integration Model

The integration is not one-directional. Two independent directions of value:

**Direction 1 — CaseHub uses OpenClaw (execution layer):**
- CaseHub cases provision OpenClaw workers via the `WorkerProvisioner` SPI
- CaseHub's `CaseChannelProvider` creates Qhorus channels per case/purpose
- OpenClaw executes skills (browse, scrape, email, message) and reports back via
  `WorkerStatusListener`
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

The earlier framing that "low-compliance use cases don't need CaseHub" was incorrect and
revised during the conversation. Even without the ledger, casehub-work provides formal task
lifecycle and SLA enforcement that is missing from OpenClaw's fire-and-forget model. A
grocery order with a Wednesday deadline and escalation if not placed is a casehub-work
WorkItem. That is valuable without tamper-evidence.

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
- Tamper-evident audit trail for enterprise compliance (regulated industries: finance,
  healthcare, legal)
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

**Do not borrow:**

*Sai's vision-based computer-use stack* — OpenClaw already handles browser automation via
CDP snapshots, which is faster and more reliable than screenshot-based perception. Anthropic's
own guidance: APIs before computer-use. Vision-based computer-use is a last resort.

### 4.3 Fit-Gap from Coworker.ai — What to Borrow

**Keep:**

*CaseMemoryStore — semantic fact index alongside the ledger:*

The most significant gap. CaseHub's ledger records what happened tamper-evidently. It is
not a queryable semantic knowledge graph. Every case starts cold — no prior context is
automatically available. Coworker's OM1 solves context fragmentation: "what do I already
know about this client / this property / this investigation?"

Proposed: `CaseMemoryStore` SPI — a semantic fact index that lives alongside the ledger,
not replacing it:
- Ledger: tamper-evident "what happened" — immutable, Merkle-chained
- Memory store: queryable "what do we know" — atomic facts, entity relationships, recall
- Each completed case emits structured facts to the store
- Future cases query the store for relevant context before acting
- Permission-aware recall: uses existing `CurrentPrincipal` + `GroupMembershipProvider`
  from casehub-platform-api to enforce access boundaries
- Module: `casehub-memory` (SPI in platform-api, with pluggable backend adapters — see
  §4.3a and §8.1 for backend evaluation and adapter strategy)

#### §4.3a — Open Source Memory Backend Evaluation

Rather than building the memory layer from scratch, a field of open source projects exists
that could back the `CaseMemoryStore` SPI via REST adapter. Seven projects were evaluated:

| Project | Approach | REST API | Self-hosted | Temporal reasoning | Key limitation |
|---|---|---|---|---|---|
| **Mem0** | Vector + BM25 + optional graph | ✅ Full REST | ✅ Docker | ❌ 49% LongMemEval | Graph memory $249/month paywall |
| **Graphiti** (Zep) | Temporal knowledge graph — bitemporal edges, fact validity windows | ✅ REST + MCP | ✅ (needs Neo4j/FalkorDB/Kuzu) | ✅ 63–91% LongMemEval | Community Edition deprecated; 3+ extra systems |
| **Memori** | SQL-native, atomic facts in Postgres | ✅ REST + MCP | ✅ Postgres | ✅ 81.95% LoCoMo | Smaller ecosystem; newer |
| **Hindsight** | 4-way hybrid retrieval (semantic + BM25 + entity graph + temporal) | ✅ REST | ✅ Docker | ✅ State-of-art LongMemEval | Small ecosystem; less battle-tested |
| **Cognee** | Graph-vector hybrid | ✅ REST | ✅ | Unknown | Python-centric; smaller community |
| **Letta** | Episodic / context-window management | ✅ REST | ✅ | Unknown | Episodic focus — not a knowledge graph |
| **LangChain memory** | Framework component (Python) | ❌ | N/A | N/A | Not a service; Python-only; ruled out |
| **GraphRAG** (Microsoft) | Knowledge graph extraction | Azure only | ❌ Too buggy | Unknown | Research quality; not self-hostable |

**Ruled out immediately:** LangChain memory (framework component, not a service),
GraphRAG (too buggy for self-hosting, Azure-dependent, research quality).

**The critical integration constraint:** every one of these services scopes memory by
`userId` and `sessionId`. None of them know about CaseHub's `CurrentPrincipal`, life
domains (health/finance/household), or `GroupMembershipProvider` boundaries. CaseHub must
wrap any backend's API with its own permission model — privacy domain partitioning is
enforced at the `CaseMemoryStore` SPI layer, not assumed from the external service.
This is a design requirement regardless of which backend is chosen.

**Recommended approach:** `CaseMemoryStore` SPI with pluggable backend adapters, following
the existing CDI priority ladder pattern (`@DefaultBean` → `@ApplicationScoped` →
`@Alternative @Priority(1)`). Three adapter tiers:

*Default adapter — Memori:*
SQL-native, stores facts in Postgres — the same database CaseHub already operates. Zero
additional infrastructure. Sub-10ms local latency. Human-readable memory (facts are plain
SQL rows — interpretable and auditable, aligning with CaseHub's transparency values). 81.95%
accuracy on LoCoMo long-conversation benchmark. The zero-cost entry point for `casehub-memory`.

*Standard adapter — Mem0:*
48,000+ GitHub stars, production-proven, Apache 2.0, full REST API, 20+ storage backends
including pgvector on Postgres. Docker self-hosted. Adds vector + BM25 retrieval on top of
SQL. Trade-off: graph memory requires $249/month cloud tier; vector-only on open-source.
Temporal reasoning weak (49% LongMemEval). Best for deployments that want a large ecosystem
and broad storage backend flexibility.

*Temporal adapter — Graphiti (Zep):*
Temporal knowledge graph with bitemporal edges — facts have explicit start/end validity
windows, not just embeddings. Best temporal reasoning (63–91% LongMemEval). Hybrid retrieval:
semantic + BM25 + graph traversal with no LLM inference during retrieval, P95 300ms latency.
Apache 2.0. Trade-off: requires Graphiti + Neo4j/FalkorDB/Kuzu — three additional systems.
Community Edition deprecated February 2026. Best for regulated domains where "what did the
agent know on 15 March?" is a compliance question (clinical, financial, legal).

This adapter strategy means: no lock-in to a fast-moving ecosystem (Mem0 paywall changes,
Graphiti deprecation wave — this space is actively unstable); permission enforcement at
CaseHub's layer regardless of backend; start simple (Memori, Postgres only) and graduate
as needs grow.

*modelHint on worker capability descriptor:*

Coworker routes tasks to the optimal model automatically (cost/accuracy/complexity
tradeoff). CaseHub's trust scoring routes to the best *agent*; it has no mechanism to
select the appropriate model tier at provisioning time.

Proposed: add `modelHint` field to worker capability description:
- Values: REASONING (Opus-class), MECHANICAL (Haiku-class), BALANCED (Sonnet-class)
- `WorkerProvisioner` SPI respects the hint when provisioning a worker session
- OpenClaw already supports multiple LLM backends — the execution side is already there
- Combined with trust scoring: "route to the most trusted worker for this capability,
  provisioned with the appropriate model tier for the task complexity"

**Do not borrow:**

*Coworker's model routing infrastructure* — they build a multi-cloud model selector with
cost and accuracy optimisation as a managed service. The `modelHint` field on the worker
descriptor is sufficient at CaseHub's level of abstraction.

### 4.4 Enterprise Memory and Context

The OM1 insight applies to enterprise CaseHub deployments, not just personal life:

- Enterprise agents suffer the same context fragmentation problem: what happened in the last
  investigation, client engagement, or code review is not automatically available to the next
  case
- `CaseMemoryStore` addresses this with permission-aware recall — facts from prior cases are
  available to future cases within the same permission scope
- For regulated enterprise (financial crime, clinical): the memory layer must respect the
  same access control boundaries as the primary case data

---

## 5. Household and Personal Life Automation

### 5.1 Motivation

Personal life has several domains where the accountability properties CaseHub was designed
for matter more than in many enterprise workflows, yet tooling treats everything as
best-effort reminders. The specific domains where formal commitment tracking, SLA
enforcement, and human governance gates add genuine value:

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
  before agent acts
- Level 4 (ledger) appropriate for this domain: tamper-evident record of health decisions,
  GDPR Art.17 for medical data

**Financial governance:**
- Not budget tracking — formal commitment lifecycle for major financial decisions
- Agent commits to finding the best remortgage rate by a deadline: DONE or escalated to human
- Every significant spend decision requires human approval above a threshold (oversight
  channel pattern)
- Trust scoring: which financial agent gives the most accurate rate comparisons, cost
  estimates, deal valuations
- Level 4 (ledger) appropriate: tamper-evident record of major financial decisions

**Elder and family care coordination:**
- Multiple agents, multiple principals (family members), multiple care providers
- Human governance gates for significant care decisions
- SLA equivalent: medication administered by 8am or alert carer
- GDPR Art.17 and sensitive data handling: highest sensitivity personal data
- Multi-site structure equivalent to clinical multi-site: one trial-level case + per-site
  sub-cases maps to one family-level case + per-location sub-cases (home, care home, hospital)
- Level 4 mandatory: regulated data, documented obligation to care, potential legal relevance

**Legal and compliance cycles:**
- Contract renewals, tax deadlines, visa renewals, insurance renewals
- Hard deadlines with real consequences
- Agent-discoverable, human-approvable
- Audit trail matters: proof of filing, proof of notice, proof of action
- Level 3 or 4 depending on stakes

**Household task management:**
- Grocery ordering: SLA-based reorder (run out of milk Thursday = WorkItem with Wednesday
  deadline and escalation if not placed)
- Home maintenance: annual boiler service, quarterly gutter clean — SLA-driven WorkItems
  that open automatically, route to agent or human, escalate if nothing happens
- Energy/utility management: monitoring agent on observe channel surfaces observations;
  decisions about switching providers route to oversight channel for human approval
- Level 1 (casehub-work) sufficient: formal task lifecycle and SLA without ledger

**Appointment booking:**
- Multi-step workflow: check availability → propose slot → human confirms → book →
  24h reminder → cancellation watch
- OpenClaw does the browsing and API calls; casehub-engine orchestrates the workflow and
  holds the human gate
- Booking deadline: "prices change after Friday" = SLA on the confirmation gate
- Level 2-3 sufficient

**Family task delegation:**
- "Pick up kids at 3:30" as COMMAND → family member or agent RESPONSE confirmation →
  DONE on pickup
- No RESPONSE by 2pm → escalation → alternative arrangement triggered
- This is Qhorus commitment lifecycle on an everyday task
- Level 2 sufficient (casehub-qhorus for commitment tracking)

**Travel planning:**
- Multi-step with budget gate (human approval) and booking deadline
- casehub-engine CasePlanModel: destination research → budget check → flight search →
  hotel search → human approval → booking → document collection → reminders
- OpenClaw does all web browsing and API calls
- Level 3 sufficient

**Contractor coordination:**
- Quote request → quote comparison → human approval → booking → work confirmation →
  payment authorisation → work sign-off
- External human actor (contractor) as obligor — see §5.4
- Level 3, with Level 4 if warranty or insurance claim documentation needed

### 5.3 Actor Taxonomy — Three Types

Personal life automation introduces a third actor category not present in devtown or clinical:

**Type 1 — AI agents** (present in all existing repos):
- Named personas: home-agent, health-agent, finance-agent, travel-agent
- OpenClaw instances acting as CaseHub workers
- Agent identity: `{model-family}:{persona}@{major}` — existing convention applies
- Trust scoring applies: which agent is most reliable for which capability

**Type 2 — Household principals** (present in existing repos as authenticated users):
- Authenticated family members with assigned roles
- Role hierarchy: household-admin > household-member > household-junior
- Examples: both adults as household-admin; older teenager as household-member;
  younger children as household-junior
- Each authenticates via Claudony (WebAuthn passkey) or via OpenClaw bridge
- RBAC roles map to Qhorus channel allowed_writers and casehub-engine WorkItem assignees
- MultiInstanceCoordinator handles M-of-N quorum decisions across multiple adults

**Type 3 — External human actors** (NOT present in any existing CaseHub repo — gap):
- Unregistered third parties to whom the system tracks commitments: contractors, doctors,
  service providers, landlords, utility companies
- Example: "plumber committed to come Thursday" — obligor has no CaseHub account
- Example: "GP said she would call back this afternoon" — obligor is external and
  unauthenticated
- These actors make commitments (verbal, via text, via email) that the system should track
  and follow up on
- Follow-up mechanism: OpenClaw's multi-channel reach (WhatsApp, SMS, email) acts as the
  agent that chases the external actor when the Watchdog fires
- This is a material gap in CaseHub's actor model — see §9.4

### 5.4 External Human Actor Commitment Pattern

The concrete workflow for external actor commitments (not yet implemented):

1. User tells home-agent: "the plumber said he'll be here Thursday between 10am and 12pm"
2. System creates a Commitment with the plumber as the obligor (external actor, no account)
3. A Watchdog is set for Thursday 12pm
4. At Thursday 12pm: if no DONE signal received (agent was home, confirmed arrival), the
   Watchdog fires
5. The escalation action: home-agent sends a WhatsApp or SMS message to the plumber's number
   asking for an ETA update
6. If no response within N hours: escalation to household-admin as oversight WorkItem
7. The entire follow-up chain is tracked as a case with a tamper-evident record (if Level 4
   is active)

This pattern applies broadly: any third-party commitment that matters (contractor, doctor,
school, insurance company) becomes a tracked obligation with automated follow-up rather than
a mental note.

### 5.5 Privacy Partitioning Across Life Domains

Personal life has hard data boundaries that enterprise data governance does not typically
address:

- Health data must not be visible to finance agents or work agents
- Financial data must not bleed into household agents accessible to children
- Work/professional data must not be visible to household agents
- Children's data has separate access rules from adult household data

This is stronger than ACL on individual channels — it is domain-level isolation.

**Current state:** CaseHub's permission model (Qhorus allowed_writers + RBAC + CurrentPrincipal)
is role and channel based. It does not have structural domain isolation that prevents
cross-domain data bleed at the system level.

**What is needed:** either a configuration of the existing permission model (strict role
partitioning with no cross-domain roles) or a structural property of the casehub-life
domain model that enforces isolation by design.

The `CaseMemoryStore` must respect the same domain boundaries: facts emitted from health
cases must not be recallable by agents operating in the finance or household domain. This is
a design constraint on the memory layer, not just a runtime permission check.

**GDPR relevance:** Art.17 erasure in the ledger applies to personal data. In a personal
life deployment, virtually all case data is personal data. The erasure mechanism needs to be
first-class in casehub-life, not opt-in.

**Open question:** is privacy partitioning a configuration of the existing permission model
or a structural property of casehub-life's domain model? Not resolved.

### 5.6 Household Permission Topology and M-of-N

Multi-adult households require quorum-based approval for shared decisions:

**Decision categories (proposed, not finalised):**
- Single-party decisions: either adult can approve (grocery order, school pickup, minor
  household tasks)
- Dual-party decisions: both adults must approve (holiday booking, major purchase above
  threshold, significant financial commitment)
- Individual decisions: single named principal only (personal health decisions, professional
  decisions)
- Junior-accessible: household-junior can request (QUERY) but cannot COMMAND

**Existing machinery that composes:**
- `MultiInstanceCoordinator` — already handles M-of-N WorkItem completion
- RBAC — household-admin, household-member, household-junior roles
- Qhorus `allowed_writers` — which roles can write COMMANDs to which channels
- casehub-engine conditional branching — different workflow paths based on decision type

**Open question:** how is quorum configuration expressed in casehub-life? Is it a
CasePlanModel property, a Qhorus channel property, or a casehub-life-specific configuration
entity? Not resolved.

### 5.7 Memory Layer vs. Authoritative External Data

Two distinct problems that must not be conflated:

**Problem A — What agents have done (CaseMemoryStore):**
Facts derived from completed CaseHub cases. "Last time we reviewed energy providers was
March 2026." "Home-agent booked the boiler service with CompanyX on 2026-04-15."
This is addressed by the CaseMemoryStore SPI described in §4.3.

**Problem B — Ground truth about the user's life (external authoritative data):**
Data that exists independently of CaseHub: Google Calendar, bank feeds, medical records,
smart home sensor readings, email history, contacts, property records. An agent booking
a dentist appointment needs the user's calendar, insurance details, and location — none
of which came from a CaseHub case output.

**The boundary:** CaseMemoryStore captures what agents have done. External authoritative
data is what IS true about the user's life, independent of agent actions.

**Open question:** how does the system make external authoritative data available to agents
before and during cases? Options include: an external data SPI that agents can query, a
caching/indexing layer that CaseMemoryStore includes, or a separate data connector layer.
Not resolved. This is the direct analogue of Coworker's OM1 applied to personal life —
OM1 solved this for enterprise tool outputs; the personal equivalent must solve it for
personal data sources.

### 5.8 Strategic Positioning — Open Question

Two fundamentally different product directions, not yet chosen:

**Option A — Developer showcase (consistent with devtown and clinical):**
- Target: Java developer evaluating CaseHub for personal life automation
- Tutorial layers structured by foundation module adoption (Level 0 → Level 4)
- Code is production-grade at every layer
- Comparison baseline: OpenClaw alone, or a Zapier/Make automation
- casehub-life looks like devtown and clinical: a tutorial-structured application repo with
  explicit layers and a LAYER-LOG.md

**Option B — Consumer product:**
- Target: non-technical household wanting AI-powered life management
- Tutorial layers structured by personal complexity: single person → couple → household
  with children → multi-generational (includes elderly parent)
- Different design decisions throughout: simpler configuration, opinionated defaults,
  minimal required expertise
- Comparison baseline: Siri Shortcuts, Apple Reminders, a personal assistant app

**Implication:** the choice fundamentally changes the domain model design, the tutorial
structure, the comparison narrative, and the entry point for the repo. This must be decided
before a design doc is written. Not resolved.

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

This applies to all tasks, not just compliance-sensitive ones. Grocery ordering, appointment
booking, contractor follow-up — any task where "did it actually happen?" matters.

### 6.2 DECLINE as Semantic Signal — Defeasible Routing

Default logic: "by default, route this task to agent A." This default is defeasible —
it holds unless a reason defeats it.

In OpenClaw, skill failure returns an error. The failure has no semantic content. The
system learns nothing from it.

In Qhorus, DECLINE is a speech act. It carries a machine-readable reason. "DECLINE:
insufficient local knowledge" and "DECLINE: calendar conflict" are different defeaters:

- Three DECLINEs citing "insufficient local knowledge" for contractor research → update the
  routing default: route contractor research to web-research agent, not home-agent
- DECLINE citing "calendar conflict" → retry same agent next available slot

Over time, DECLINE and HANDOFF patterns accumulate into a learned model of which agent
handles which tasks well. This is the precursor to trust scoring — before the ledger is
active, the routing defaults are already adapting to agent behaviour.

### 6.3 HANDOFF for Obligation Transfer

When home-agent passes a task to finance-agent without Qhorus, the obligation evaporates.
There is no record of who is responsible after the hand-off, no Watchdog, no deadline.

With HANDOFF:
- Original Commitment on home-agent closes (DELEGATED terminal state)
- Child Commitment opens on finance-agent
- Watchdog transfers with the obligation
- The obligation is never lost as it moves between agents
- The user can always query: who currently holds this obligation?

Critical constraint: **HANDOFF cannot launder a permission escalation.** When an obligation
is transferred, the receiving agent must independently satisfy the ACL of the target channel.
Finance-agent must be a permitted writer on the finance work channel regardless of who
initiated the HANDOFF. This should be documented explicitly — it is not currently stated in
the Qhorus deep-dive or protocols.

### 6.4 Channel Separation — Work / Observe / Oversight

OpenClaw's heartbeat monitoring loop and task execution currently share the same conceptual
channel. There is no distinction between:

- "Fridge temperature is 4°C" — a STATUS, descriptive, no obligation created
- "Order groceries now" — a COMMAND, prescriptive, obligation created
- "Should I switch energy providers?" — an oversight QUERY requiring human decision before
  any action

When these mix, agents either over-trigger (treating every observation as requiring action)
or under-trigger (treating every instruction as advisory).

The normative channel separation enforces this structurally:

| Channel | Message types | Effect |
|---|---|---|
| `/observe` | STATUS, EVENT | Factual, descriptive; no Commitments created |
| `/work` | COMMAND, RESPONSE, DONE, DECLINE, HANDOFF, FAILURE | Prescriptive; Commitments created and tracked |
| `/oversight` | COMMAND, RESPONSE | Human governance gate; workflow pauses until RESPONSE |

An always-on monitoring agent (boiler pressure, energy prices, calendar watch) emits to
the observe channel. A task execution agent emits to the work channel. A spending decision
above a threshold routes to the oversight channel for human confirmation before any action.

This separation is architectural, not per-skill logic. Skills do not decide what to do with
their output — the channel semantics determine the consequence.

### 6.5 Oversight Channel as Uniform Human Governance Gate

Currently, every OpenClaw skill that needs human approval implements its own approval
mechanism: a Telegram message, a WhatsApp prompt, a custom callback. These are:
- Inconsistent — different UX per skill
- Untracked — no formal record that an approval was sought and granted
- Without deadline — no escalation if the human doesn't respond
- Without audit — no proof of what was approved and when

The oversight channel makes this uniform:
- Any action requiring human governance routes a COMMAND to the oversight channel
- OpenClaw delivers the oversight channel message via the user's preferred messaging app
  (WhatsApp, Telegram, iMessage)
- The Commitment has a deadline: no RESPONSE by 2pm triggers escalation
- The approval is recorded (with Level 4: tamper-evidently)

This is the same mechanism for: booking a holiday, authorising a £200 spend, approving a
medical appointment, deciding whether to switch broadband provider, confirming a contractor
quote. One mechanism, consistently applied, formally tracked.

**The complete loop with ActionRiskClassifier:**
`ActionRiskClassifier` classifies action as risky → routes to oversight channel → OpenClaw
delivers to WhatsApp/Telegram → user responds → Commitment fulfilled → workflow continues.
The CaseHub layer handles this uniformly; the skill author writes no approval logic.

### 6.6 Deontic Permission Model

The normative layer enforces who is permitted to issue COMMANDs, not just who is
authenticated.

For a household: Qhorus `allowed_writers` on channels defines which principals can create
obligations:
- Children: can read observe channels; cannot write COMMANDs to work channels
- Household members: can COMMAND on shared household work channels; not on financial channels
- Household admin only: can COMMAND on health and financial channels

**Deontic consequence:** a COMMAND from an unauthorised principal never creates a Commitment.
The obligation never opens. Permission violations do not produce phantom obligations that
then expire and trigger false escalations. The normative and permission layers are consistent.

Combined with the planned RBAC (§7): three-layer enforcement:
1. Authentication (Claudony — WebAuthn, API key): who is this principal?
2. RBAC (`@RolesAllowed`, `CurrentPrincipal.roles()`): what is this principal permitted to do?
3. Channel ACL (Qhorus `allowed_writers`): can this principal write to this specific channel?

Each gate is independent. A principal can pass authentication and still fail the channel ACL.

### 6.7 STATUS and EVENT — Preventing Monitoring From Creating Spurious Obligations

For always-on personal agents, the distinction between observation and obligation is
critical. Without speech act types, the agent must decide in skill logic whether an
observation warrants action. With STATUS and EVENT as first-class types:

- STATUS: boiler pressure is 0.8 bar → below threshold → engine creates a WorkItem "check
  boiler pressure" — but the STATUS itself creates no Commitment
- EVENT: energy price spike detected → routes to finance-agent for decision — the EVENT is
  not a COMMAND; finance-agent decides whether to act
- COMMAND: "book car service" → Commitment opens, Watchdog is set

Monitoring agents can emit observations freely without accidentally creating obligations.
The channel semantics determine the consequence, not the skill logic.

### 6.8 Default Logic in Routing

Default logic provides the formal underpinning for the routing behaviour:

- Default: route household maintenance tasks to home-agent
- This default is defeated by: DECLINE (with reason), HANDOFF (to named alternative),
  trust score falling below threshold, overload signal
- The defeated default updates: future similar tasks route differently without manual
  reconfiguration
- Over time, as DECLINE reasons and HANDOFF patterns accumulate, routing defaults become a
  learned model of agent capability and reliability

This is defeasible reasoning at the routing layer. The DECLINE and HANDOFF speech acts are
the formal defeat conditions. This is a natural precursor to full trust scoring (Level 4)
— the routing system improves from Level 2 onward, before the ledger is active.

---

## 7. RBAC / ACL — Complementary Layers

The planned RBAC implementation for CaseHub complements the Qhorus normative permission
model without overlapping it. Three distinct enforcement points at different levels:

| Layer | Mechanism | What it controls |
|---|---|---|
| Authentication | Claudony: WebAuthn passkeys, X-Api-Key | Identity: who is this principal? |
| RBAC (planned) | `@RolesAllowed`, `CurrentPrincipal.roles()` | Authorisation: what is this principal permitted to do? |
| Channel ACL | Qhorus `allowed_writers` | Location: can this principal write to this specific channel? |

For OpenClaw integration: an OpenClaw agent acting on behalf of a principal inherits that
principal's roles. A teenager's device authenticating with role `household-junior` cannot
trigger a financial COMMAND — not because the skill checks for it, but because:
- RBAC rejects the REST call at the Claudony layer, or
- The dispatch gate rejects the write because `household-junior` is not in `allowed_writers`
  on the finance work channel

The skill author writes no permission logic. The enforcement is structural.

**Key deontic consequence:** a COMMAND from an unauthorised principal never creates a
Commitment. The obligation never opens. No phantom obligations, no false escalations.

**HANDOFF permission constraint (to be documented):** when an obligation is transferred via
HANDOFF, the receiving agent must independently satisfy the target channel's ACL. HANDOFF
cannot be used to escalate permissions — the receiving agent needs its own authorisation.
This constraint is not yet documented in the Qhorus deep-dive or in any protocol. It should
be added before RBAC is implemented.

---

## 8. What Lives Where

### 8.1 New Foundation Modules

**`casehub-memory`** (new repo or new module in casehub-platform):
- `CaseMemoryStore` SPI: semantic fact index, queryable, permission-aware
- Permission-aware recall enforced at the SPI layer via `CurrentPrincipal` +
  `GroupMembershipProvider` — not delegated to the backend service
- Domain isolation at the SPI layer: facts from health cases must not be recallable by
  agents in finance or household domains, regardless of backend
- Fact emission: completed cases emit structured facts; mechanism TBD (CDI observer pattern
  consistent with existing ledger capture)
- In-memory `@Alternative @Priority(1)` implementation for test isolation
  (following casehub-ledger-memory pattern)

**Pluggable backend adapters** (see §4.3a for full evaluation):

| Adapter | Backend | Infrastructure | Best for |
|---|---|---|---|
| Default | **Memori** | Postgres only (existing) | Zero-cost entry; all deployments |
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
- Guides model selection without prescribing it — the provisioner decides how to apply the
  hint for its specific worker type

### 8.2 New Integration Module

**`casehub-openclaw`** (new repo, integration tier — analogous to claudony):
- Implements `WorkerProvisioner` SPI: provisions OpenClaw instances as CaseHub workers
- Implements `CaseChannelProvider` SPI: creates Qhorus channels per case/purpose
- Implements `WorkerStatusListener` SPI: maps OpenClaw session lifecycle to CaseHub worker
  states
- Bridges OpenClaw's multi-channel messaging (WhatsApp, Telegram, iMessage) to Qhorus
  oversight channel delivery
- Depends on: casehub-qhorus, casehub-engine; does not depend on casehub-ledger (optional)

### 8.3 New Application Repo

**`casehub-life`** (new repo, application tier — analogous to devtown and casehub-clinical):
- Domain model: to be designed (see §9 — gap)
- Capability tags: household-management, health-coordination, financial-planning,
  family-scheduling, travel-planning, legal-deadline, contractor-coordination
- Trust dimensions: deadline-reliability, cost-accuracy, factual-accuracy,
  proactive-alerting
- CasePlanModels: appointment-cycle, home-maintenance-cycle, financial-review,
  travel-plan, contractor-coordination, care-coordination
- Actor taxonomy: AI agents (OpenClaw personas) + household principals (RBAC roles) +
  external human actors (contractors, doctors — gap: §9.4)
- Tutorial layers: structure depends on strategic positioning decision (§5.8 — unresolved)
- Uses casehub-openclaw as the worker provisioner

### 8.4 OpenClaw Skill Pack (outside CaseHub repos)

A set of OpenClaw skills that enable Direction 2 (OpenClaw → CaseHub) integration.
Published to the Awesome OpenClaw community skill registry:

- `casehub-workitem` — create a WorkItem from natural language with deadline and assignee
- `casehub-case` — start a CasePlanModel for a complex workflow
- `casehub-queue` — route a task to a named queue
- `casehub-status` — query status of a running case
- `casehub-commit` — acknowledge a COMMAND as a Commitment from within a skill
- `casehub-done` — close a Commitment from within a skill

These are opt-in. A bare OpenClaw install is unchanged. Installing the casehub skill pack
layers CaseHub coordination on top of the existing 5,400-skill ecosystem.

### 8.5 Enterprise Deployment Considerations

For enterprise co-worker deployments (Sai/Coworker pattern on CaseHub):
- `casehub-openclaw` is the worker provisioner for OpenClaw-based enterprise agents
- Claudony remains the worker provisioner for Claude CLI-based enterprise agents
- `CaseMemoryStore` provides the OM1 equivalent for enterprise case context
- `ActionRiskClassifier` provides the Sai approval gate equivalent, uniformly
- `casehub-ledger` provides the compliance audit trail that Sai and Coworker explicitly lack
- RBAC provides the enterprise access control that neither competitor has formalised

---

## 9. Gaps and Limitations

### 9.1 No Semantic Memory Layer (CaseMemoryStore)

**Gap:** CaseHub has no queryable semantic fact index. The ledger is immutable history, not
a knowledge graph. Every case starts cold — no prior context is automatically available.

**Impact:** agents cannot build on prior interactions; the same research is redone each case;
context fragmentation is identical to the problem Coworker's OM1 solves.

**Proposed resolution:** `casehub-memory` module — `CaseMemoryStore` SPI with pluggable
backend adapters (Memori default, Mem0 standard, Graphiti temporal). See §4.3a and §8.1.

**Critical design constraint:** all evaluated open source backends scope memory by their
own `userId`/`sessionId` model. None is aware of CaseHub's `CurrentPrincipal`, life domains,
or `GroupMembershipProvider`. Permission-aware recall and privacy domain partitioning must
be enforced at the `CaseMemoryStore` SPI layer — wrapping the backend's API with CaseHub's
permission model. This is non-negotiable and applies to all three adapter options.

**Open questions:** how are facts emitted from cases (CDI observer consistent with ledger
pattern? explicit API call from case definition?); how does the store relate to authoritative
external data (§5.7); module placement (standalone repo vs. casehub-platform module).

### 9.2 No ActionRiskClassifier SPI

**Gap:** workers have no mechanism to declare action risk and trigger a CaseHub gate
automatically. Workers must either know CaseHub's internal gate mechanism or implement
per-agent approval logic.

**Impact:** Sai's bounded autonomy model is replicated ad-hoc per skill rather than
enforced structurally. The uniform oversight channel pattern (§6.5) cannot be triggered
automatically without this SPI.

**Proposed resolution:** `ActionRiskClassifier` SPI in `casehub-engine-api`. See §8.1.

### 9.3 No modelHint on Worker Descriptor

**Gap:** `WorkerProvisioner` SPI provisions workers but has no mechanism to guide model
tier selection. All workers of the same type are provisioned identically regardless of
task complexity.

**Impact:** suboptimal cost/capability tradeoff — REASONING tasks get MECHANICAL models
(poor quality) or MECHANICAL tasks get REASONING models (unnecessary cost).

**Proposed resolution:** `modelHint` field on worker capability descriptor. See §8.1.

### 9.4 No External Human Actor Representation

**Gap:** CaseHub's actor model covers authenticated AI agents and authenticated human
principals. It has no representation for external human actors who are obligors (contractors,
doctors, service providers) but have no CaseHub account.

**Impact:** the external actor commitment pattern (§5.4) cannot be implemented. Commitments
made by third parties cannot be formally tracked or followed up on by the system.

**Proposed resolution:** requires design. Options include:
- An `ExternalActor` entity in casehub-qhorus-api (name, contact info, communication
  channel preference)
- Commitments with `ExternalActor` as obligor, Watchdog fires, follow-up via OpenClaw
  multi-channel messaging
- No authentication required for external actors — they are tracked, not authenticated

**Not resolved.** Needs design before casehub-life can handle contractor coordination.

### 9.5 Memory Layer / External Authoritative Data Boundary

**Gap:** no mechanism for agents to read authoritative external data sources (Google
Calendar, bank feeds, medical records, smart home sensors, email) as context before or
during cases. CaseMemoryStore (§9.1) captures what agents have done; it does not capture
ground truth from external systems.

**Impact:** agents starting a new case have no access to the user's calendar, financial
state, health records, or home sensor data unless the skill explicitly fetches it.
OpenClaw skills can fetch this data, but it is not systematically available as case context.

**Proposed resolution:** requires design. The boundary between CaseMemoryStore and an
external data connector layer must be defined. Not resolved.

### 9.6 Privacy Domain Partitioning Not Implemented

**Gap:** no structural isolation between personal life data domains (health / finance /
work / household). Current permission model is role and channel based; it does not prevent
cross-domain data bleed at the system level.

**Impact:** health facts in the memory layer could be recalled by finance agents unless
role configuration explicitly prevents it. Configuration-based isolation is fragile;
structural isolation is needed for a personal life deployment.

**Proposed resolution:** requires design. Either a structural property of the casehub-life
domain model or an extension to CaseMemoryStore's permission model. Not resolved.

### 9.7 OpenClaw as WorkerProvisioner Not Implemented

**Gap:** `WorkerProvisioner` SPI is defined in casehub-engine-api and implemented in
Claudony. No implementation exists for OpenClaw as a worker type.

**Impact:** Direction 1 (CaseHub → OpenClaw) is architecturally clear but not buildable
without `casehub-openclaw`.

**Proposed resolution:** `casehub-openclaw` integration module. See §8.2.

### 9.8 OpenClaw → CaseHub Skill Surface Not Implemented

**Gap:** no OpenClaw skills exist for creating WorkItems, starting cases, or querying
case status.

**Impact:** Direction 2 (OpenClaw → CaseHub) is not accessible to OpenClaw users.

**Proposed resolution:** casehub skill pack for OpenClaw. See §8.4.

### 9.9 HANDOFF Permission Constraint Not Documented

**Gap:** the constraint that a HANDOFF cannot escalate permissions — the receiving agent
must independently satisfy the target channel ACL — is not documented in the Qhorus
deep-dive, the normative layer documentation, or any protocol file.

**Impact:** a developer implementing HANDOFF could inadvertently design a system where
HANDOFF is used to work around channel ACL restrictions. This is a correctness and security
concern once RBAC is active.

**Proposed resolution:** document in casehub-qhorus.md (Depends On / Key Abstractions
section) and in a protocol file when RBAC lands.

### 9.10 Household M-of-N Quorum Configuration Not Designed

**Gap:** `MultiInstanceCoordinator` handles M-of-N task completion. But no mechanism exists
for configuring which household decisions require which quorum — this is a casehub-life
domain concern, not a foundation concern.

**Impact:** dual-party approval for major purchases, holiday bookings, etc. is not
implementable without a quorum configuration mechanism in casehub-life.

**Proposed resolution:** requires design within casehub-life domain model. Not resolved.

### 9.11 casehub-life Domain Model Not Designed

**Gap:** the casehub-life application repo does not exist. No domain model, no entities,
no capability tags, no trust dimensions, no CasePlanModels, no tutorial layer structure,
no comparison baseline.

**Impact:** all casehub-life discussion is currently conceptual. No implementation is
possible without this design.

**Prerequisite:** strategic positioning decision (§5.8 — developer showcase vs. consumer
product). This must be resolved first as it drives the entire domain model design.

---

## 10. Open Questions

These questions were explicitly identified as unresolved during the research conversation
and must be addressed before design work can proceed:

1. **Strategic positioning of casehub-life:** developer showcase (like devtown/clinical) or
   consumer product? Drives tutorial structure, domain model complexity, comparison baseline,
   and entry point design. (§5.8)

2. **External authoritative data boundary:** how does the system make external data (calendar,
   bank, medical records, smart home) available as agent context? Is this inside
   CaseMemoryStore or a separate layer? (§5.7, §9.5)

3. **External human actor model:** how are external obligors (contractors, doctors) represented?
   What entity holds their commitment? How does follow-up trigger? (§5.4, §9.4)

4. **Privacy domain partitioning:** configuration of existing permission model or structural
   property of casehub-life domain model? (§5.5, §9.6)

5. **Household M-of-N quorum configuration:** how is quorum expressed — CasePlanModel
   property, Qhorus channel property, or casehub-life domain entity? (§5.6, §9.10)

6. **CaseMemoryStore fact emission:** how do completed cases emit facts to the memory store?
   CDI observer (consistent with existing ledger pattern)? Explicit API call from case
   definition? Automatic extraction from ledger entries? (§9.1)

7. **casehub-memory module placement:** standalone repo or module within casehub-platform
   or casehub-ledger? (§8.1)

---

## 11. What Was Explicitly Ruled Out

Items explicitly excluded during the research conversation — not deferred, not reconsidered:

- **Sai's vision-based computer-use stack:** OpenClaw already handles browser automation
  via CDP snapshots, which is faster and more reliable. Computer-use (vision-based) is a
  fallback for when no structured API exists — Anthropic's own guidance.
- **Coworker's model routing infrastructure:** too complex and managed-service in nature.
  The `modelHint` field on the worker descriptor is the appropriate abstraction.
- **Treating low-compliance personal use cases as outside CaseHub's scope:** revised.
  casehub-work provides valuable task lifecycle and SLA enforcement at Level 1 without
  the ledger. The ledger is opt-in for domains that require tamper-evidence.
- **CaseHub as a general life OS or personal productivity app:** the value is in structured
  accountability for things that matter — health, finance, legal, care. Not grocery lists
  per se, though Level 1 casehub-work is still useful there.
- **LangChain memory modules:** a Python framework component, not a standalone service.
  Tightly coupled to the LangChain framework; no language-agnostic REST API; not applicable
  as a `CaseMemoryStore` backend.
- **Microsoft GraphRAG:** research quality. Known to be too buggy for self-hosting; Azure
  deployment only; hours to launch due to Python dependency issues. Not production-ready.
- **Building CaseMemoryStore from scratch without a backend:** unnecessary given the
  quality of open source options. The SPI adapter pattern provides the right abstraction
  without re-implementing retrieval, embedding, or graph traversal.
