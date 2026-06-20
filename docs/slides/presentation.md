---
theme: default
title: CaseHub — AI Fusion Harness
info: |
  CaseHub: compliance-first infrastructure for multi-agent AI systems.
  Vision, architecture, and capabilities.
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
controls: false
hideNavigation: true
---

# CaseHub

## AI Fusion Harness for Multi-Agent Systems

Compliance-first infrastructure for regulated, accountable, AI-driven applications.

<br/>

*Written by LLMs, for LLMs.*  
*An accelerant for AI-Fusion driven digital transformations.*

---
layout: center
---

# The Accountability Gap

<br/>

> *"A log tells you what happened.*
> *A commitment tells you who was responsible, what they promised,*
> *and whether they followed through."*

<br/>

**LLMs reason well. They cannot commit.**

- No formal record of obligation
- No tamper-evident audit trail
- No SLA enforcement on AI actions
- Compliance cannot be delegated to LLM behaviour

---
layout: two-cols
---

# What CaseHub Is

**AI Fusion Harness** — blends two kinds of intelligence.

**Classical AI**
- Rules engines (Drools, CEP)
- Bayesian trust scoring
- Blackboard architecture
- Speech act theory — 9-type taxonomy, commitment lifecycle
- Deterministic, provable, auditable

**LLM-based AI**
- Autonomous agent reasoning
- Natural language understanding
- Generative content and routing
- Contextual, adaptive, conversational

::right::

<br/>

**The principle:** let each kind of intelligence do what it does best.

**The guarantee:** every agent interaction is a formal, accountable act.

**Built on Quarkus.** Production-grade. Native-image capable.

<br/>

**Compliance by design:**  
EU AI Act Art.12 — structurally enforced  
GDPR Art.17/22 — built into the audit layer  
GCP / FDA / FinCEN — proven across applications

---

# Architecture — Four Tiers

```
┌─────────────────────────────────────────────────────────────────┐
│  APPLICATION      devtown · aml · clinical · drafthouse · life  │
│                   quarkmind (living lab)                         │
├─────────────────────────────────────────────────────────────────┤
│  INTEGRATION      claudony · openclaw · connectors · iot         │
│                   casehub-ras · casehub-desiredstate             │
├─────────────────────────────────────────────────────────────────┤
│  ORCHESTRATION    engine · eidos · neural-text                   │
├─────────────────────────────────────────────────────────────────┤
│  FOUNDATION       platform · ledger · qhorus · work             │
└─────────────────────────────────────────────────────────────────┘
```

<br/>

**The rule:** bring your domain, use the platform, modify nothing below.

---
class: text-sm
---

# The Ecosystem

| Module | Layer | What it delivers |
|--------|-------|-------------|
| `casehub-platform` | Foundation | Zero-dep SPIs: identity, preferences, memory, agents, streams |
| `casehub-ledger` | Foundation | Tamper-evident audit ledger, trust scoring, GDPR erasure |
| `casehub-qhorus` | Foundation | Agent communication mesh, speech acts, commitments |
| `casehub-work` | Foundation | Human task lifecycle, SLA, delegation, escalation |
| `casehub-engine` | Orchestration | Blackboard+CMMN coordinator, routing, oversight gates |
| `casehub-eidos` | Orchestration | Agent identity, health probing, system prompt rendering |
| `casehub-neural-text` | Orchestration | Local ONNX inference, RAG, CRAG |
| `claudony` | Integration | Claude CLI sessions, agent mesh dashboard |
| `casehub-openclaw` | Integration | OpenClaw agent bridge, 5,400+ skills |
| `casehub-connectors` | Integration | Slack, Teams, email, SMS, webhooks |
| `casehub-iot` | Integration | Matter-aligned device abstraction (HA, OpenHAB) |
| `casehub-ras` | Integration | Reactive case creation from event streams |
| `casehub-desiredstate` | Integration | Desired-state runtime — intent to execution |
| `casehub-pages` | Foundation | YAML-driven visualization, TypeScript |
| `devtown · aml · clinical` | Application | Showcase + tutorial applications |
| `drafthouse · life · quarkmind` | Application | Specialist domains |

---
layout: section
---

# Foundation

*The shared layer every application builds on.*

---
class: text-sm
---

# casehub-platform — Identity, Preferences, Memory

**Identity & Access**
- `CurrentPrincipal` SPI — actorId, groups, tenancyId, crossTenantAdmin
- `GroupMembershipProvider` SPI — inverse membership query
- `casehub-platform-oidc` — OIDC-backed implementation
- `casehub-platform-scim` — SCIM 2.0 group sync

**Preferences**
- `PreferenceProvider` SPI — per-scope, runtime-changeable
- Backends: YAML file, JPA, MongoDB

**Memory (CaseMemoryStore)**
- 6 backends: in-memory · JPA · SQLite · Mem0 · Graphiti · NoOp
- Tenancy-isolated. GDPR erasure built in.
- Graphiti: temporal knowledge graph (Neo4j/FalkorDB/Kuzu)

---

# casehub-platform — Agents & Streams

**Agents**
- `AgentProvider` SPI — `run()` (one-shot) + `openSession()` (multi-turn)
- `agent-claude/` — Claude Code CLI subprocess
- `agent-claude-langchain4j/` — LangChain4j ChatModel bridge

**Streams**
- 5 classpath-activated modules: Kafka · AMQP · webhook · poll · Camel
- CloudEvents envelope throughout
- `StreamContext` — tenancy propagation in async processing

---

# casehub-ledger — Audit

**Tamper-evident audit. The compliance backbone.**

**Audit**
- Merkle Mountain Range (RFC 9162) — cryptographic inclusion proofs
- Ed25519 tlog-checkpoint publishing
- W3C PROV-DM lineage export
- GDPR Art.17 token-severing erasure
- EU AI Act Art.12 — `ComplianceSupplement` on every AI decision
- `ErasureReceiptLedgerEntry` — tamper-evident erasure record

---

# casehub-ledger — Trust Scoring

**Trust Scoring**
- Bayesian Beta algorithm — updated from attestation events
- EigenTrust peer verdict aggregation
- Capability-scoped + dimension-scoped scores

**Privacy**
- `ActorIdentity` — pseudonymisation mapping
- GDPR erasure without breaking audit chain

449 tests. Native image validated.

---
layout: two-cols
---

# casehub-qhorus

**The agent communication mesh.**

Every agent interaction is a formal speech act.

**9 Message Types**

| Type | Creates obligation? |
|------|-------------------|
| COMMAND | Yes → DONE/FAILURE/DECLINE |
| QUERY | Yes → RESPONSE/DECLINE |
| RESPONSE, DONE, DECLINE | Discharges obligation |
| STATUS | Progress update, no obligation |
| HANDOFF | Transfers obligation |
| FAILURE | Terminal failure |
| EVENT | Telemetry, no obligation |

::right::

**Commitment lifecycle**  
OPEN → FULFILLED / FAILED / EXPIRED / DECLINED / HANDOFF

**Key features**
- `MessageDispatch` — single enforcement gate; no bypass path
- `ChannelProjection<S>` — deterministic left-fold read models
- `CommitmentExpiredEvent` — deadline-based rerouting
- A2A SSE streaming · Slack-native backend

---

# casehub-qhorus — User Flow

**User flow — PI authorisation (Clinical)**

1. Case engine sends COMMAND to PI channel
2. PI receives as WorkItem (24h SLA)
3. PI responds via Slack or web
4. RESPONSE closes commitment
5. Ledger records causal chain

---
layout: two-cols
---

# casehub-work

**Human task lifecycle. Formal obligations for humans.**

<br/>

**10 WorkItem statuses**

```
CREATED → CLAIMED → IN_PROGRESS → COMPLETED
        → REJECTED / CANCELLED / EXPIRED
        → DELEGATED → DELEGATION_DECLINED
        → ESCALATED (non-terminal)
```

**Capabilities**
- SLA enforcement with `claimDeadline`
- Chained escalation policies
- M-of-N parallel group completion
- SpawnGroup — fan-out to multiple candidates
- WorkItem templates
- Semantic worker selection (`casehub-work-ai`)

::right::

<br/><br/>

**1,019+ tests**

<br/>

**User flow — SAR review (AML)**
1. Case creates WorkItem for compliance officer
2. 30-day FinCEN SLA starts
3. Officer claims and reviews investigation
4. Completes with SAR decision
5. Trust attestation written to ledger
6. Next SAR routes to higher-trust officers

<br/>

**Downstream users**  
engine · all applications

---
layout: section
---

# Orchestration

*Coordinates agents, humans, rules, and LLMs in a single case.*

---
class: text-sm
---

# casehub-engine

**Hybrid Blackboard + CMMN orchestration.**

**Two execution paths**
- **Choreography** — evaluates bindings on context change
- **Orchestration** — suspends case, awaits worker, resumes

**Routing intelligence**
- `LeastLoadedAgentStrategy` — default
- `TrustWeightedAgentStrategy` — Bayesian Beta outcomes
- `SemanticAgentRoutingStrategy` — embedding-based
- `CapabilitySpecializationStore` — DECLINE-pattern exclusion
- `ActionRiskClassifier` SPI — human gate for consequential actions

**Worker Outcomes:** `Success` · `Failure(reason)` · `Expired(reason)` · `Declined`  
**Bindings:** `capability` · `subCase` · `humanTask` · `inputSchemaOverride` · `contextWrite`

---

# casehub-engine — User Flow

**User flow — PR review (DevTown)**

1. PR arrives → case opens
2. Parallel bindings fire: security, architecture, test-coverage
3. Trust-weighted selection picks reviewers
4. Human gate if security flag raised
5. All bindings resolve → merge decision

---
---

# casehub-eidos — Agent Identity

**Structured agent identity. Routing intelligence.**

**4-layer AgentDescriptor**
- **Identity** — agentId, name, version, provider, modelFamily
- **Slot** — open string, domain-defined (e.g. `"senior-reviewer"`)
- **Capabilities** — qualityHint, epistemicDomains (per-domain confidence)
- **Disposition** — social orientation, rule-following, risk appetite, autonomy, conflict mode (5 axes)

**Capability Health Probing**
- `Ready` · `Degraded` · `Unavailable` · `EpistemicallyWeak`
- `EpistemicallyWeak` fires when domain confidence below threshold
- Prevents routing to out-of-domain agents before failure

---

# casehub-eidos — Routing Signals

**Routing signals**
- A2A_CARD format: qualityHint, latencyHintP50Ms, costHint, epistemicDomains
- `CapabilitySpecializationStore` — learns DECLINE patterns per domain

**System Prompt Rendering**
- MARKDOWN · PROSE · A2A_CARD formats
- Optional LLM semantic enrichment stage
- Multi-judge eval harness (Claude, Ollama, Jlama, GPU Llama3)

**Knowledge graph** — Wilson lower-bound reputation, task history, `TaskSemanticEnricher`


---

# casehub-neural-text

**Local AI inference. No cloud dependency.**

<br/>

**Inference modules** (zero casehub/Quarkus deps — shared with Hortora)

| Module | What it does |
|--------|-------------|
| `NliClassifier` | Hallucination detection — scores LLM output faithfulness |
| `TextClassifier` | Action risk classification |
| `ScalarRegressor` | Epistemic domain confidence estimation |
| `SparseEmbedder` | SPLADE sparse embeddings for precision retrieval |
| `CrossEncoderReranker` | Top-N precision reranking |

**RAG pipeline** (casehub-specific)
- Qdrant — tenancy-isolated corpus storage
- Hybrid search — dense + sparse, RRF fusion
- `CorpusStore` + `CaseRetriever` SPIs · corpus ingestion bridge · CRAG `RelevanceEvaluator`

Hallucination detection hook on engine output  
`ScalarRegressor` → epistemic confidence in eidos routing

---
layout: section
---

# Integration

*Bridges the platform to agents, devices, and people.*

---
class: text-sm
---

# Integration Layer

**claudony** — *Agent mesh reference implementation*
- Remote Claude Code CLI sessions via tmux
- WebAuthn passkeys, fleet management, WebSocket streaming
- MCP server for controller Claude instances
- Implements all 4 casehub-engine worker provisioner SPIs

**casehub-openclaw** — *OpenClaw agent bridge*
- `WorkerProvisioner` SPI for OpenClaw agents
- 9 MCP tools + 3 resources for OpenClaw → CaseHub
- TypeScript Plugin SDK (npm) + Python client (PyPI)
- Dual mode: heartbeat + direct call

**casehub-connectors** — *Messaging*
- Outbound: Slack, Teams, SMS, WhatsApp, email
- Inbound: email IMAP, Slack webhooks

**casehub-iot** — 10 Matter-aligned types · HA + OpenHAB · edge/cloud bridge

---
layout: section
---

# Reactive & Desired-State

*The platform watches. Cases happen automatically.*

---

# casehub-ras — Reticular Activating System

**Situational awareness. Reactive case creation.**

**Architecture**
```
SensoryEvent (IoT / Kafka / Qhorus / webhook)
  → RasEngine
    → Ganglion strategies (pick one or compose)
      → CompositeEventCorrelator → startCase()
```

**4 Ganglion strategies**
- `JavaSwitchGanglion` — deterministic, zero deps
- `DroolsCepGanglion` — sliding windows, temporal patterns
- `BayesianGanglion` — weighted multi-signal accumulation
- `LlmGanglion` — narrative / ambiguous signal detection

---

# casehub-ras — Composite Events & Use Cases

**Composite chains:** AND · OR · THRESHOLD · SEQUENCE · COUNT

**Use cases**
- Patient deterioration → clinical escalation case
- IoT anomaly cluster → investigation case
- Code commit pattern → PR review case
- Market signal → compliance review case

---
---

# casehub-desiredstate

**Declare intent. The platform reconciles.**

Immutable `DesiredStateGraph` — Alga-inspired.  
Plans transitions: prune before grow.  
Executes as Serverless Workflows inside cases.  
Continuously reconciles actual vs. desired.

**SPIs**
- `GoalCompiler` — intent → graph
- `ActualStateAdapter` — observe current state
- `NodeProvisioner` — add/remove nodes
- `FaultPolicy` — auto-retry → AI review → human WorkItem

**OTel tracing** — `desiredstate.*` span attributes

---

# casehub-ops

**CaseHub domain layer over desiredstate.**

**Modules**
- `deployment` — processes `casehub-deployment.yaml` → DesiredStateGraph
- `infra` — Terraform/Ansible augmentation
- `compliance` — SOC2 / GDPR / EU AI Act / DORA posture
- `iot` — IoT desired state

**The vision:** YAML → deploy · monitor · self-heal.

---
layout: section
---

# casehub-pages

*YAML-driven visualization. TypeScript. Zero Java at runtime.*

---

# casehub-pages

**Pure TypeScript dashboard rendering runtime.**  
*100% TypeScript. Near DashBuilder feature parity.*

**Stack** — TypeScript · React · Web Components · Apache ECharts · js-yaml · JSONata

**Core packages**
- `@casehub/pages-data` — DataSet model, filter/group/sort, external data
- `@casehub/pages-ui` — YAML parser, layout model, DashBuilder compatibility
- `@casehub/pages-viz` — chart wrappers (bar, line, pie, timeseries, table, metric, map)
- `@casehub/pages-component` — CSS grid layout, tabs, sidebar, accordion
- `@casehub/pages-runtime` — `loadSite(yaml, container)` API

28/31 DashBuilder dashboards render without modification.  
**Consumers:** claudony · drafthouse · devtown · aml · life

---
layout: section
---

# AI Infusion

*Every place classical and generative AI enters the system.*

---
class: text-xs
---

# Classical AI — Where It Lives

<br/>

| Location | What | How |
|----------|------|-----|
| casehub-ledger | Bayesian Beta trust scoring | Updated from attestation events per actor/capability/dimension |
| casehub-ledger | EigenTrust peer verdicts | Propagated from SOUND/FLAGGED attestations |
| casehub-engine | `TrustWeightedAgentStrategy` | Trust scores → agent selection |
| casehub-engine | `SemanticAgentRoutingStrategy` | Embedding similarity (40% semantic / 36% trust / 24% load) |
| casehub-engine | `ActionRiskClassifier` SPI | Action risk → gate or pass |
| casehub-eidos | `EpistemicallyWeak` health probe | Domain confidence below threshold → demote candidate |
| casehub-eidos | Vocab system | Belbin/DISC/Thomas-Kilmann axes → structured disposition matching |
| casehub-neural-text | `NliClassifier` | Hallucination: LLM output faithfulness against source facts |
| casehub-neural-text | `TextClassifier` | Action risk classification |
| casehub-neural-text | `ScalarRegressor` | Epistemic domain confidence estimation |
| casehub-neural-text | `SparseEmbedder` | SPLADE sparse embeddings for precision retrieval |
| casehub-neural-text | `CrossEncoderReranker` | Top-N precision reranking |
| casehub-neural-text | CRAG `RelevanceEvaluator` | Evaluates retrieved chunks, corrects low-relevance results |
| quarkmind | `StrategyTrustRouter` | Bayesian Beta routing among competing strategy plugins |
| casehub-ras | `DroolsCepGanglion` | CEP sliding windows for event stream pattern detection |
| casehub-ras | `BayesianGanglion` | Weighted multi-signal accumulation |

---
class: text-xs
---

# LLM — Where It Lives

<br/>

| Location | What | How |
|----------|------|-----|
| casehub-platform | `ClaudeAgentProvider` | Claude Code CLI — one-shot or multi-turn sessions |
| casehub-platform | `agent-claude-langchain4j` | LangChain4j ChatModel/StreamingChatModel bridge |
| casehub-platform | `memory-mem0` | Vector + BM25 semantic search |
| casehub-platform | `memory-graphiti` | Temporal knowledge graph — LLM entity extraction |
| casehub-eidos | System prompt rendering | Semantic enrichment: identity, role, capability, disposition, goal narratives |
| casehub-eidos | Knowledge graph | Wilson lower-bound reputation, task history |
| casehub-neural-text | `CorpusIngestionService` | LangChain4j dense embeddings for RAG |
| casehub-neural-text | `QdrantCaseRetriever` | Hybrid RRF retrieval — dense + sparse |
| casehub-drafthouse | Multi-LLM debate | Structured agent-to-agent critique, Qhorus-grounded |
| claudony | `ClaudeAgentProvider` | Claude Code CLI sessions as CaseHub workers |
| casehub-openclaw | OpenClaw agents | 5,400+ pre-built skills as workers |
| casehub-desiredstate | AI_REVIEW fault node | `AgentProvider` SPI for LLM fault diagnosis |
| casehub-ras | `LlmGanglion` | Narrative/ambiguous event signal detection |

---
class: text-sm
---

# AI Infusion — The Complete Picture

<br/>

**LLM Supervisor Mode** (clinical, aml)
- LLM supervises the case plan — adapts investigation path based on findings
- Routing decisions become dialogic, not rule-based

**LLM Triaging** (casehub-ras)
- `LlmGanglion` detects situations from unstructured streams
- Bridges sensor noise → structured accountability

**Hybrid Typed Fact Space** (engine + drools)
- Every fact: paradigm tag · confidence score · derivation chain
- Drools natively consumes LLM conclusions
- LLM sees hard constraints vs. uncertain inferences

**CBR** — Retain (ledger) → Retrieve (similarity) → Reuse (routing) → Revise (adaptive templates) · `CapabilitySpecializationStore` learns DECLINE patterns · A2A_CARD content routing

---
layout: section
---

# Applications

*Domain-specific showcases — every layer of the platform, made tangible.*

---

# Applications — Overview

<br/>

| Application | Domain | Market fit | Layers | AI infusion |
|-------------|--------|-----------|--------|-------------|
| casehub-aml | Anti-money laundering | 44/50 | 9 | Trust routing, risk gate, LLM supervisor |
| casehub-clinical | Clinical trials | 24/25 | 9 | Trust routing, risk gate, LLM protocol advisor |
| casehub-devtown | Software dev (PR review) | — | 7 | Trust-weighted reviewer routing |
| casehub-drafthouse | Document review | — | — | Multi-LLM debate, MCP-driven |
| casehub-life | Personal automation | — | 9 | OpenClaw skills, IoT, LLM concierge |
| quarkmind | StarCraft II game AI | — | 7 | Trust-weighted strategy routing |

<br/>

**Every application starts with a naive Java baseline.**  
Each layer closes a gap that naive implementation structurally cannot close.

---
class: text-sm
---

# casehub-aml

*Layers & AI infusion*

**Layers**
- L1–L4 Foundation stack — SLA, obligations, Merkle audit
- L5 casehub-engine — adaptive investigation paths
- L6 Trust routing — experienced agents on complex cases
- L7 IBM AMLSim comparison
- L8 casehub-platform memory — prior entity context
- L9 Human oversight gate — SAR filing, entity links

**AI infusion**
- Trust-weighted routing (Bayesian Beta from SAR outcomes)
- `AmlActionRiskClassifier` — PEP/high-risk → human gate
- Entity-resolution memory context before each investigation
- LLM supervisor mode — adaptive routing based on findings

---

# casehub-aml — User Flow

**SAR Investigation**

1. SAR trigger arrives
2. Adaptive case opens (entity type, risk score)
3. Entity-resolution, pattern-analysis, OSINT agents — parallel
4. PEP detection → oversight gate → compliance officer
5. SAR filing decision → trust attestation written
6. Future cases: higher-trust agents assigned

**Compliance gaps closed vs. IBM AMLSim**  
FinCEN audit chain · GDPR Art.17 · formal agent obligations · trust-weighted routing

---
class: text-sm
---

# casehub-clinical

*Layers & AI infusion · Highest market fit: 24/25*

**Layers**
- L1–L4 Baseline → ledger (GCP + GDPR)
- L5 Adaptive protocol paths (IRB gates, grade escalation)
- L6 Cross-site DSMB rollup
- L7 Trust routing — safety agents (threshold 0.75)
- L8 SUSAR oversight + GDPR Art.17 + EU AI Act Art.12
- L9 Eligibility screening + ClinicalAgent comparison

**AI infusion**
- `ClinicalTrustRoutingPolicyProvider` — SAFETY_MONITORING: 0.75 threshold
- `ClinicalActionRiskClassifier` + `SusarCriteriaEvaluator`
- SUSAR attestation writer → Bayesian Beta trust update
- `ProtocolAmendmentAdvisor` SPI — LLM implementation

---

# casehub-clinical — User Flow

**Adverse Event Escalation**

1. Grade 4+ AE reported → trust-weighted escalation case
2. CTCAE grading → senior monitor + DSMB in parallel
3. Unexpected AE → IND expedited safety reporting
4. Multi-site Grade 4+ pattern → DSMB rollup
5. Trust attestation updates for next routing

**10-row compliance gap vs. ClinicalAgent (arXiv 2404.14777)**  
SLA enforcement · PI authorization · GDPR erasure · multi-site · tamper-evident audit

---
class: text-sm
---

# casehub-devtown

*Layers & AI infusion*

**Layers**
- L1–L4 Foundation stack — SLA, obligations, audit, adaptive routing
- L5 casehub-engine — adaptive routing on code content
- L6 Trust routing — senior reviewers on sensitive PRs
- L7 Comparison vs. naive AI code review

**AI infusion**
- `DevtownActionRiskClassifier` — 8 action types, 4 categories
- Trust-weighted reviewer selection
- Memory: contributor history, reviewer context, code-area history
- LLM reviewer for security patterns

---

# casehub-devtown — User Flow

**PR Review**

1. PR webhook received
2. Code analysis → content-driven routing (security flag? architecture change?)
3. Parallel specialist reviewers (trust-weighted)
4. Human gate if security flag
5. M-of-N approvals → merge decision
6. Production incident → FLAGGED attestation → reviewer trust drops

---
layout: two-cols
---

# casehub-drafthouse

**MCP-driven document review with multi-LLM debate.**

<br/>

**MCP tools**
- `start_review` — opens review session
- `update_selection` — grounds discussion to document region
- `query_review` — query review state
- `end_review` — closes with summary
- Document comparison + version-tracked revision tools

Structured agent-to-agent debate loop. `ChannelProjection<ReviewState>`. Qhorus speech acts ground every critique.

::right::

<br/>

**AI infusion**
- Multiple LLM agents critique the same document
- Debate loop — each agent responds to other's critique
- Review grounded in document diffs, not memory
- `casehub-pages` embeds review dashboards

**User flow**
1. Document submitted for review
2. Multiple LLM reviewers assigned
3. Each reviewer critiques, responds to others
4. Human reviewer sees structured debate manifest
5. Revision cycle — new version re-enters loop
6. Review complete → decision recorded in ledger

---
layout: two-cols
---

# casehub-life

**Household, health, finance, elder care, legal coordination.**  
*Tutorial: OpenClaw as the execution layer.*

**Layers**
- L1 Naive Java baseline
- L2 SLA-enforced household tasks
- L3 casehub-qhorus — formal obligations
- L4 casehub-ledger — tamper-evident record
- L5 Adaptive coordination paths
- L6 Trust routing
- L7 OpenClaw integration — 5,400+ pre-built skills
- L8 casehub-platform memory
- L9 casehub-iot — Home Assistant + OpenHAB

::right::

<br/>

**The vision**  
The same platform that coordinates clinical trials manages your medical appointments. The same accountability primitives that close FinCEN SARs track your financial obligations.

**AI infusion**
- OpenClaw agents as household task workers
- IoT device state changes → RAS case creation
- LLM concierge via debate loop
- Trust-weighted skill routing for home automation

**Community marketplace**  
Automation recipes shared as `CasePlanModel` YAML.  
5,400+ OpenClaw skills, immediately available.

---
class: text-sm
---

# quarkmind — The Living Lab

*Same harness. Clinical trials over days. QuarkMind at millisecond tick granularity.*

**7 layers** — L1–L5 Blackboard, typed inter-plugin messaging, audit, adaptive selection · L6 Trust routing (Bayesian Beta) · L7 vs. L1 naive loop + ocraft/SC2 API · Validated across 30 IEM10 replays (PvT / PvZ / PvP)

**AI infusion**
- `StrategyTrustRouter` — BOOTSTRAP → QUALIFIED → BORDERLINE → EXCLUDED
- `GameOutcomeRecorder` — trust attestations on game end
- `EnemyBehavior` + `ReactiveStrategy` — counter-picks dominant player every 50 frames
- Three.js 3D visualiser — 65+ sprites, fog of war, replay scrub

**What it proves:** the harness isn't domain-specific. It's infrastructure.

---
layout: section
---

# The Platform Vision

---

# The Complete Platform

**Foundation**
- Platform — identity, memory, agents, streams
- Ledger — trust, audit, GDPR
- Qhorus — agent mesh, commitments
- Work — human tasks, SLA

**Orchestration**
- Engine — Blackboard+CMMN coordination
- Eidos — agent identity, routing intelligence
- Neural-text — local inference, RAG, CRAG

**Reactive**
- casehub-ras — situational awareness layer
- casehub-desiredstate — intent-driven infrastructure
- casehub-ops — compliance and deployment posture

---

# The Platform — Integration & AI Fusion

**Integration**
- claudony — agent mesh reference implementation
- openclaw — 5,400+ skills as workers
- connectors — Slack, Teams, email, SMS
- iot — 10 Matter-aligned device types
- casehub-pages — YAML-driven dashboards

**Applications**
- aml · clinical · devtown · drafthouse · life · quarkmind

**AI Fusion**
- Classical: trust, routing, inference, CEP
- LLM: agents, memory, triaging, supervision
- CBR: retain → retrieve → reuse → revise

---
layout: center
class: text-center
---

# The Flywheel

<br/>

```
Better outcomes
    ↓
Better trust scores
    ↓
Better routing
    ↓
Better outcomes
```

<br/>

**CBR closes the loop.**  
Past cases teach future cases.  
The platform gets smarter with every interaction.

---
layout: center
class: text-center
---

# Build on the Platform

<br/>

**Bring your domain. Use the platform. Modify nothing below.**

<br/>

*Written by LLMs, for LLMs.*  
*An accelerant for AI-Fusion driven digital transformations.*

<br/>

[casehubio.github.io](https://casehubio.github.io) · [github.com/casehubio](https://github.com/casehubio)

<style>
table { line-height: 1.3; }
td, th { padding: 0.2rem 0.5rem !important; }
.text-xs table { font-size: 0.72rem; }
.text-sm table { font-size: 0.8rem; }
/* Hide goto/nav panel that peeks in from top-right */
:global(.fixed.right-5) { display: none !important; }
</style>
