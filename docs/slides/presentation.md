---
theme: default
title: CaseHub — AI Fusion Harness
info: |
  CaseHub: compliance-first infrastructure for multi-agent AI systems.
  Vision, architecture, and roadmap.
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
---

# CaseHub

## AI Fusion Harness for Multi-Agent Systems

Compliance-first infrastructure for regulated, accountable, AI-driven applications.

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

<br/>

**Classical AI**
- Rules engines (Drools, CEP)
- Bayesian trust scoring
- Blackboard architecture
- Deterministic, provable, auditable

**LLM-based AI**
- Autonomous agent reasoning
- Natural language understanding
- Generative content and routing
- Contextual, adaptive, conversational

::right::

<br/><br/><br/>

**The principle:** let each kind of intelligence do what it does best.

<br/>

**The guarantee:** every agent interaction is a formal, accountable act.

<br/>

**Built on Quarkus.** Production-grade. Native-image capable.

<br/>

✅ EU AI Act Art.12 — structurally enforced  
✅ GDPR Art.17/22 — built into the audit layer  
✅ GCP / FDA / FinCEN — proven across applications  

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

# The Ecosystem

| Module | Layer | What it does |
|--------|-------|-------------|
| `casehub-platform` | Foundation | Zero-dep SPIs: identity, preferences, memory, agents, streams |
| `casehub-ledger` | Foundation | Tamper-evident audit ledger, trust scoring, GDPR erasure |
| `casehub-qhorus` | Foundation | Agent communication mesh, speech acts, commitments |
| `casehub-work` | Foundation | Human task lifecycle, SLA, delegation, escalation |
| `casehub-engine` | Orchestration | Blackboard+CMMN coordinator, routing, oversight gates |
| `casehub-eidos` | Orchestration | Agent identity, health probing, system prompt rendering |
| `casehub-neural-text` | Orchestration | Local ONNX inference, RAG, CRAG |
| `claudony` | Integration | Claude CLI sessions, agent mesh dashboard |
| `casehub-openclaw` | Integration | OpenClaw agent bridge |
| `casehub-connectors` | Integration | Slack, Teams, email, SMS, webhooks |
| `casehub-iot` | Integration | Matter-aligned device abstraction (HA, OpenHAB) |
| `casehub-ras` | Integration 🔜 | Reactive case creation from event streams |
| `casehub-desiredstate` | Integration 🔜 | Desired-state runtime |
| `casehub-pages` | Foundation 🔜 | YAML-driven visualization, TypeScript |
| `devtown · aml · clinical` | Application | Showcase + tutorial applications |
| `drafthouse · life · quarkmind` | Application | Specialist domains |

---
layout: section
---

# Foundation

*The shared layer every application builds on.*

---

# casehub-platform

**Zero-dependency SPIs shared by every module.**

<br/>

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
- Graphiti backend: temporal knowledge graph (Neo4j/FalkorDB/Kuzu)

**Agents**
- `AgentProvider` SPI — `run()` (one-shot) + `openSession()` (multi-turn)
- `agent-claude/` — Claude Code CLI subprocess
- `agent-claude-langchain4j/` — LangChain4j bridge

**Streams** (platform#98)
- 5 classpath-activated stream modules: Kafka, AMQP, webhook, poll, Camel
- CloudEvents envelope throughout
- `StreamContext` propagation — P1.8 design

---

# casehub-ledger

**Tamper-evident audit + actor trust. The compliance backbone.**

<br/>

**Audit**
- Merkle Mountain Range (RFC 9162) — cryptographic inclusion proofs
- Ed25519 tlog-checkpoint publishing
- W3C PROV-DM lineage export
- GDPR Art.17 token-severing erasure
- EU AI Act Art.12 — `ComplianceSupplement` on every AI decision

**Trust Scoring**
- Bayesian Beta algorithm — updated from attestation events
- EigenTrust peer verdict aggregation
- Capability-scoped + dimension-scoped scores
- Three retrieval strategies: materialized · TTL-cached · on-demand

**Privacy**
- `ActorIdentity` — pseudonymisation mapping
- `LedgerPrivacyProducer` — erasure without breaking audit chain
- `ErasureReceiptLedgerEntry` — tamper-evident erasure record (opt-in)

**Downstream users:** qhorus · engine · work · all applications  
**Test coverage:** 449 tests. Native image validated.

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

**7-State Commitment lifecycle**  
OPEN → FULFILLED / FAILED / EXPIRED / DECLINED / HANDOFF / CANCELLED

::right::

<br/><br/>

**Key features**
- `MessageDispatch` — single enforcement gate; no bypass path
- `ChannelProjection<S>` — deterministic left-fold read models
- `CommitmentExpiredEvent` — triggers deadline-based rerouting
- A2A SSE streaming — `/a2a/tasks/{id}/stream`
- Slack-native backend — thread-aware delivery (qhorus#261)
- 1,000+ tests

<br/>

**User flow example — PI authorisation (Clinical)**
1. Case engine sends COMMAND to PI channel
2. PI receives as `casehub-work` WorkItem (24h SLA)
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

**User flow example — SAR review (AML)**
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
layout: two-cols
---

# casehub-engine

**Hybrid Blackboard + CMMN orchestration.**

<br/>

**Two execution paths**
- **Choreography** — evaluates bindings on context change
- **Orchestration** — suspends case, awaits worker, resumes

**Routing intelligence**
- `LeastLoadedAgentStrategy` — default
- `TrustWeightedAgentStrategy` — Bayesian Beta outcomes
- `SemanticAgentRoutingStrategy` — embedding-based (40% semantic / 36% trust / 24% load)
- `CapabilitySpecializationStore` — DECLINE-pattern exclusion learning

**Oversight gate**
- `ActionRiskClassifier` SPI — before every consequential action
- Human gate via Qhorus oversight channel
- ChainedReactive: most-restrictive-wins, fail-safe=GateRequired

::right::

<br/>

**Worker Outcomes (sealed)**
- `Success` · `Failure(reason)` · `Expired(reason)` · `Declined`
- `OutcomePolicy` per outcome type
- DECLINE/FAILURE → failure cascade (not silent completion)

**Bindings** (YAML DSL)
- Target types: `capability` · `subCase` · `humanTask`
- Fields: `inputSchemaOverride` · `contextWrite` · `outcomes`
- Triggers: `contextChange` · `schedule`/`timer`

**User flow — PR review (DevTown)**
1. PR arrives → case opens
2. Parallel: security, architecture, test-coverage bindings fire
3. Trust-weighted selection picks reviewers
4. Human gate if security flag
5. All bindings resolve → merge decision

---

# casehub-eidos

**Structured agent identity. Routing intelligence.**

<br/>

**4-layer AgentDescriptor**
- **Identity** — agentId, name, version, provider, modelFamily
- **Slot** — open string, domain-defined (e.g. `"senior-reviewer"`)
- **Capabilities** — qualityHint, epistemicDomains (per-domain confidence)
- **Disposition** — Bayesian Beta social orientation, rule-following, risk appetite, autonomy, conflict mode (5 axes)

**Capability Health Probing**
- `Ready` · `Degraded` · `Unavailable` · `EpistemicallyWeak`
- `EpistemicallyWeak` fires when domain confidence below threshold
- Prevents routing to out-of-domain agents before failure

**Routing signals**
- A2A_CARD format: qualityHint, latencyHintP50Ms, costHint, epistemicDomains
- `CapabilitySpecializationStore` — learns DECLINE patterns per domain

**System Prompt Rendering**
- MARKDOWN · PROSE · A2A_CARD formats
- Optional LLM semantic enrichment stage
- Eval harness: multi-judge (Claude, Ollama, Jlama NEON, GPU Llama3)

**Vocabulary system**
- Belbin · DISC · Thomas-Kilmann · SVO · CasehubSlot

🔜 **Knowledge graph** — Wilson lower-bound reputation, task history, `TaskSemanticEnricher`

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
- `CorpusStore` + `CaseRetriever` SPIs
- Corpus ingestion bridge — `@Scheduled` polling from external sources

**CRAG** (Corrective RAG — neural-text#33)
- `@Decorator` on `CaseRetriever`
- `RelevanceEvaluator` SPI — evaluates chunks, corrects low-relevance results
- Classpath-activated

🔜 Hallucination detection hook on engine output  
🔜 `ScalarRegressor` → epistemic confidence in eidos routing  

---
layout: section
---

# Integration

*Bridges the platform to agents, devices, and people.*

---

# Integration Layer

<br/>

**claudony** — *Agent mesh reference implementation*
- Remote Claude Code CLI sessions via tmux
- WebAuthn passkeys, fleet management, WebSocket streaming
- MCP server for controller Claude instances
- Implements all 4 casehub-engine worker provisioner SPIs
- `ResearcherCase` — first production CaseHub case in Claudony

**casehub-openclaw** — *OpenClaw agent bridge*
- `WorkerProvisioner` SPI for OpenClaw agents
- Oversight gate (OversightGateService)
- Layer 0: 9 MCP tools + 3 resources for OpenClaw → CaseHub
- TypeScript Plugin SDK (npm) + Python client (PyPI)
- Dual mode: heartbeat (OpenClaw → CaseHub) + direct call (CaseHub → OpenClaw)

**casehub-connectors** — *Messaging*
- Outbound: Slack, Teams, SMS, WhatsApp, email
- Inbound: email IMAP, Slack webhooks
- Pure `java.net.http` — no Camel SDKs

**casehub-iot** — *Typed device abstraction*
- 10 Matter-aligned device types
- Real-time providers: Home Assistant (WebSocket) + OpenHAB (SSE)
- Bridge: `iot-bridge` (edge) + `iot-bridge-server` (cloud DeviceProvider SPI)
- 5,400+ OpenClaw skills accessible via openclaw integration

---
layout: section
---

# Coming — Platform Expansion

---

# casehub-ras

## Reticular Activating System 🔜

**"The platform watches. Cases happen automatically."**

<br/>

**Architecture**
```
SensoryEvent (IoT / Kafka / Qhorus / webhook)
  → RasEngine
    → Ganglion strategies (pick one or compose)
      → CompositeEventCorrelator
        → startCase()
```

**4 Ganglion strategies**
- `JavaSwitchGanglion` — deterministic, zero deps
- `DroolsCepGanglion` — sliding windows, temporal patterns
- `BayesianGanglion` — weighted multi-signal accumulation
- `LlmGanglion` — narrative / ambiguous signal detection (slow path)

**Composite event chains**
- AND · OR · THRESHOLD · SEQUENCE · COUNT
- Configurable time windows
- Declared in YAML `SituationDefinition`

**Use cases**
- Patient deterioration → escalation case
- IoT anomaly cluster → investigation case
- Code commit pattern → PR review case
- Market signal → compliance review case

---
layout: two-cols
---

# casehub-desiredstate 🔜

**Declare intent. The platform reconciles.**

<br/>

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

**Examples**
- Nefarious Dungeons — dungeon entity management
- Data Pipeline — medallion architecture (Bronze→Silver→Gold)
- Agent topology management (casehub-ops)

::right::

<br/>

## casehub-ops 🔜

**CaseHub domain layer over desiredstate.**

<br/>

**Modules**
- `deployment` — processes `casehub-deployment.yaml` → DesiredStateGraph; sub-compilers for agents, streams, channels, detection, trust
- `infra` — Terraform/Ansible augmentation
- `compliance` — SOC2 / GDPR / EU AI Act / DORA posture
- `iot` — IoT desired state

<br/>

**The vision:** declare your agent topology in YAML. The platform deploys it, monitors it, and self-heals it.

---
layout: section
---

# AI Infusion

*Every place classical and generative AI enters the system.*

---

# Classical AI — Where It Lives Today

<br/>

| Location | What | How |
|----------|------|-----|
| casehub-ledger | Bayesian Beta trust scoring | Updated from attestation events per actor/capability/dimension |
| casehub-ledger | EigenTrust peer verdicts | Propagated from SOUND/FLAGGED attestations |
| casehub-engine | `TrustWeightedAgentStrategy` @Priority(1) | Trust scores → agent selection |
| casehub-engine | `SemanticAgentRoutingStrategy` @Priority(2) | Embedding similarity (40% semantic / 36% trust / 24% load) |
| casehub-engine | `ActionRiskClassifier` SPI | Action risk → gate or pass |
| casehub-eidos | `EpistemicallyWeak` health probe | Domain confidence below threshold → demote candidate |
| casehub-eidos | Vocab system | Belbin/DISC/Thomas-Kilmann axes → structured disposition matching |
| casehub-neural-text | `NliClassifier` | Hallucination: LLM output faithfulness against source facts |
| casehub-neural-text | `TextClassifier` | Action risk classification (action type → gate decision) |
| casehub-neural-text | `ScalarRegressor` | Epistemic domain confidence estimation |
| casehub-neural-text | `SparseEmbedder` | SPLADE sparse embeddings for precision retrieval |
| casehub-neural-text | `CrossEncoderReranker` | Top-N precision reranking of retrieval candidates |
| casehub-neural-text | CRAG `RelevanceEvaluator` | Evaluates retrieved chunks, corrects low-relevance results |
| quarkmind | `StrategyTrustRouter` | Bayesian Beta routing among competing strategy plugins |
| casehub-ras 🔜 | `DroolsCepGanglion` | CEP sliding windows for event stream pattern detection |
| casehub-ras 🔜 | `BayesianGanglion` | Weighted multi-signal accumulation |

---

# LLM — Where It Lives Today

<br/>

| Location | What | How |
|----------|------|-----|
| casehub-platform | `ClaudeAgentProvider` | Claude Code CLI subprocess — one-shot or multi-turn sessions |
| casehub-platform | `agent-claude-langchain4j` | LangChain4j ChatModel/StreamingChatModel bridge over AgentSession |
| casehub-platform (memory) | `memory-mem0` | Vector + BM25 semantic search (Mem0 OSS) |
| casehub-platform (memory) | `memory-graphiti` | Temporal knowledge graph — LLM entity extraction (Neo4j/FalkorDB) |
| casehub-eidos | System prompt rendering | Optional semantic enrichment: identity, role, capability, disposition, goal narratives |
| casehub-eidos | Eval harness | Multi-judge evaluation (Claude, Ollama, Jlama NEON, TornadoVM GPU) |
| casehub-neural-text | `CorpusIngestionService` | LangChain4j `OnnxEmbeddingModel` — dense embeddings for RAG |
| casehub-neural-text | `QdrantCaseRetriever` | Hybrid RRF retrieval — dense + sparse, LLM reranking optional |
| casehub-drafthouse | Multi-LLM debate | Structured agent-to-agent critique, Qhorus-grounded review loop |
| claudony | `ClaudeAgentProvider` | Claude Code CLI sessions as CaseHub workers |
| casehub-openclaw | OpenClaw agents | 5,400+ pre-built skills as workers |
| casehub-desiredstate 🔜 | AI_REVIEW fault node | `AgentProvider` SPI for LLM diagnosis of faults |
| casehub-ras 🔜 | `LlmGanglion` | Narrative/ambiguous event signal detection |

---

# AI Infusion — What's Coming

<br/>

**LLM Supervisor Mode** (clinical, aml)
- LLM supervises the case plan itself — not just individual steps
- Adapts investigation path based on emerging findings
- Routing decisions become dialogic, not just rule-based

**LLM Triaging** (casehub-ras)
- `LlmGanglion` detects situations from unstructured streams
- Classifies ambiguous events into case types
- Bridges sensor noise → structured accountability

**Hybrid Typed Fact Space** (engine + drools)
- Every fact: paradigm tag · confidence score · derivation chain
- Drools natively consumes LLM conclusions
- LLM sees hard constraints vs. uncertain inferences
- `casehub-drools` module — Drools-as-Worker integration

**CBR: The Complete Vision** (ledger + neural-text + engine)
- **Retain** ✅ ledger records outcome as retrievable case
- **Retrieve** 🔜 `CaseRetriever` SPI — similarity across analogous problems
- **Reuse** ✅ implementation routing selects based on retrieved context
- **Revise** 🔜 adaptive plan templates from top-k retrieved cases

**CapabilitySpecializationStore** ✅ (eidos#55)
- Agents learn what they can't do
- DECLINE patterns → proactive routing exclusion
- Foundation for full adaptive routing epic (#258)

**Content Routing** (eidos + engine)
- A2A_CARD routing signals: `qualityHint`, `latencyHintP50Ms`, `costHint`
- Machine-to-machine capability negotiation
- Route not by name, but by fitness and cost

---
layout: section
---

# Applications

*Domain-specific showcases — every layer of the platform, made tangible.*

---

# Applications — Overview

<br/>

| Application | Domain | Market fit | Tutorial layers | AI infusion |
|-------------|--------|-----------|-----------------|-------------|
| casehub-aml | Anti-money laundering | 44/50 | 9 (Layer 7 pending) | Trust routing, SUSAR-style risk gate |
| casehub-clinical | Clinical trials | 24/25 market | 9 (complete) | Trust routing, risk gate, LLM protocol advisor |
| casehub-devtown | Software dev (PR review) | — | 6 complete | Trust-weighted reviewer routing |
| casehub-drafthouse | Document review | — | Active | Multi-LLM debate, MCP-driven |
| casehub-life | Personal automation | — | 2 complete | OpenClaw skill execution layer |
| quarkmind | StarCraft II game AI | — | 7 (complete) | Trust-weighted strategy routing |

<br/>

**Baseline comparison in every app:** each begins with naive Java.  
Every layer closes a gap that a naive implementation structurally cannot close.

---
layout: two-cols
---

# casehub-aml

**FinCEN-compliant AML investigation.**  
*Tutorial + showcase. Java developers in financial services.*

**Layers complete**
- ✅ L1 Naive Java baseline
- ✅ L2 casehub-work — 30-day FinCEN SLA
- ✅ L3 casehub-qhorus — formal obligation per specialist agent
- ✅ L4 casehub-ledger — tamper-evident audit, GDPR Art.17
- ✅ L5 casehub-engine — adaptive investigation paths
- ✅ L6 Trust routing — experienced agents on complex cases
- 🔜 L7 IBM AMLSim comparison
- ✅ L8 casehub-platform memory — prior entity context
- ✅ L9 Human oversight gate — SAR filing, entity links

::right::

<br/>

**AI infusion**
- Trust-weighted routing (Bayesian Beta from SAR outcomes)
- `AmlActionRiskClassifier` — PEP/high-risk-score actions → human gate
- Entity-resolution memory context before each investigation
- 🔜 LLM supervisor mode — adaptive routing based on findings

**User flow**
1. SAR trigger arrives
2. Adaptive case opens (entity type, risk score)
3. Entity-resolution, pattern-analysis, OSINT agents route in parallel
4. PEP detection → oversight gate → compliance officer
5. SAR filing decision → trust attestation written
6. Future cases: higher-trust agents assigned

**Compliance gaps closed vs. IBM AMLSim**
- FinCEN audit chain · GDPR Art.17 · formal agent obligations
- Trust-weighted routing · adaptive paths

---
layout: two-cols
---

# casehub-clinical

**GCP/FDA-compliant clinical trial coordination.**  
*Tutorial + showcase. Highest market fit: 24/25.*

**Layers complete** (all 9)
- ✅ L1–L4 Baseline → ledger (GCP + GDPR)
- ✅ L5 Adaptive protocol paths (IRB gates, grade escalation)
- ✅ L6 Cross-site DSMB rollup
- ✅ L7 Trust routing — safety agents (threshold 0.75)
- ✅ L8 SUSAR oversight + GDPR Art.17 + EU AI Act Art.12
- ✅ L9 Eligibility screening + ClinicalAgent comparison

::right::

<br/>

**AI infusion**
- `ClinicalTrustRoutingPolicyProvider` — SAFETY_MONITORING: 0.75 threshold
- `ClinicalActionRiskClassifier` + `SusarCriteriaEvaluator`
- SUSAR attestation writer → Bayesian Beta trust update
- `ProtocolAmendmentAdvisor` SPI 🔜 LLM implementation pending

**User flow**
1. Grade 4+ AE reported → escalation case
2. Safety monitor assigned (trust-weighted)
3. CTCAE grading → senior monitor + DSMB in parallel
4. Unexpected AE → IND expedited safety reporting (7-day or 15-day)
5. Multi-site Grade 4+ pattern → DSMB rollup
6. Trust attestation updates for next routing

**10-row compliance gap table vs. ClinicalAgent (arXiv 2404.14777)**  
SLA enforcement · PI authorization · GDPR erasure · multi-site · tamper-evident audit · trust routing · adaptive protocol paths

---
layout: two-cols
---

# casehub-devtown

**AI-assisted software development.**  
*PR review, merge queues, trust-weighted reviewer routing.*

**Layers complete (1–6)**
- ✅ L1 Naive Java baseline
- ✅ L2 casehub-work — reviewer SLA
- ✅ L3 casehub-qhorus — reviewer obligations (DECLINE when outside expertise)
- ✅ L4 casehub-ledger — tamper-evident review record
- ✅ L5 casehub-engine — adaptive routing on security flags
- ✅ L6 Trust routing — senior reviewers on sensitive PRs
- 🔜 L7 Comparison vs. naive AI code review

::right::

<br/>

**AI infusion**
- `DevtownActionRiskClassifier` — 8 action types, 4 categories
- Trust-weighted reviewer selection (review-thoroughness, false-positive-rate, scope-calibration dimensions)
- `HumanOversight.GENERAL` — catch-all oversight group
- Memory: contributor history, reviewer context, code-area history
- 🔜 LLM reviewer for security patterns

**User flow**
1. PR webhook received
2. Code analysis → content-driven routing (security flag? architecture change?)
3. Parallel specialist reviewers (trust-weighted)
4. Human gate if security flag
5. M-of-N approvals → merge decision
6. Production incident? → FLAGGED attestation → reviewer trust drops

**Compliance:** GDPR Art.17 actor erasure · tamper-evident review chain

---
layout: two-cols
---

# casehub-drafthouse

**MCP-driven document review with multi-LLM debate.**

<br/>

**Live MCP tools**
- `start_review` — opens review session
- `update_selection` — grounds discussion to document region
- `query_review` — query review state
- `end_review` — closes with summary

**Architecture**
- Structured agent-to-agent debate loop
- `ChannelProjection<ReviewState>` — deterministic review manifest
- Qhorus speech acts ground every critique
- LangChain4j + Claude Agent SDK provider pattern

::right::

<br/>

**AI infusion**
- Multiple LLM agents critique the same document
- Debate loop — each agent responds to other's critique
- Review grounded in document diffs, not memory
- `casehub-pages` embeds review dashboards (planned)

**User flow**
1. Document submitted for review
2. Multiple LLM reviewers assigned
3. Each reviewer critiques, responds to others
4. Human reviewer sees structured debate manifest
5. Revision cycle — new version re-enters loop
6. Review complete → decision recorded in ledger

🔜 Document comparison MCP tools  
🔜 Version-tracked revision history  
🔜 `casehub-pages` review dashboard embedding

---
layout: two-cols
---

# casehub-life

**Household, health, finance, elder care, legal coordination.**  
*Tutorial: OpenClaw as the execution layer.*

**Current status — Layer 2 (casehub-work)**
- ✅ L1 Naive Java baseline
- ✅ L2 SLA-enforced household tasks
- 🔜 L3 casehub-qhorus — formal obligations
- 🔜 L4 casehub-ledger — tamper-evident record
- 🔜 L5 Adaptive coordination paths
- 🔜 L6 Trust routing
- 🔜 L7 OpenClaw integration — 5,400+ pre-built skills
- 🔜 Layer 9 casehub-iot — Home Assistant + OpenHAB

::right::

<br/>

**Vision**
- Same platform that coordinates clinical trials manages your medical appointments
- Same accountability primitives that close FinCEN SAR tracks your financial obligations
- IoT integration: device-driven case types (thermostat anomaly → comfort case)

**AI infusion (planned)**
- OpenClaw agents as household task workers
- IoT device state changes → RAS case creation
- LLM concierge via casehub-drafthouse debate loop
- Trust-weighted skill routing for home automation

**Community marketplace** — automation recipes shared as `CasePlanModel` YAML

---

# quarkmind — The Living Lab

**StarCraft II game AI. Proof that the harness holds everywhere.**

<br/>

**Why it matters**  
Clinical trials operate over days. QuarkMind operates at millisecond tick granularity.  
The same harness. The same SPIs. Completely different timing.

**7 layers complete**
- ✅ L1–L5 Blackboard coordination, typed inter-plugin messaging, audit, adaptive selection
- ✅ L6 Trust routing — Bayesian Beta strategy routing among competing implementations
- ✅ L7 Comparison vs. L1 naive loop + ocraft/SC2 API

**Validation**  
30 IEM10 replays — `ReplayValidationHarness`. Statistical coverage across PvT / PvZ / PvP.

**AI infusion**
- `StrategyTrustRouter` — four-phase Bayesian Beta maturity model
  - BOOTSTRAP → QUALIFIED → BORDERLINE → EXCLUDED
- `GameOutcomeRecorder` — writes trust attestations on game end
- `EnemyBehavior` + `ReactiveStrategy` — counter-picks dominant player every 50 frames
- Three.js 3D visualiser — 65+ unit sprites, fog of war, replay scrub

**What it proves:** harness generality. The pattern isn't domain-specific. It's infrastructure.

---
layout: section
---

# casehub-pages

*YAML-driven visualization. TypeScript. Zero Java at runtime.*

---

# casehub-pages

**Pure TypeScript dashboard rendering runtime.**  
*Renamed from melviz. Moving to `casehubio/casehub-pages`.*

<br/>

**Stack**  
TypeScript · React · Web Components · Apache ECharts · js-yaml · JSONata · Webpack

**Core packages**
- `@casehub/pages-data` — DataSet model, filter/group/sort, external data (REST, CSV, Prometheus, JSONata)
- `@casehub/pages-ui` — YAML parser, layout model, DashBuilder compatibility
- `@casehub/pages-viz` — Web Component chart wrappers (bar, line, pie, timeseries, table, metric, map)
- `@casehub/pages-component` — CSS grid layout, tabs, pills, sidebar, carousel, accordion
- `@casehub/pages-runtime` — `loadSite(yaml, container)` API

**One API call, YAML config:**
```typescript
loadSite(yaml, document.getElementById('dashboard'))
```

**DashBuilder compatibility** — 28/31 sample dashboards render without modification.

**Status:** 602 data tests · 148 component tests · 100 runtime tests

**Consumers:** claudony · drafthouse · devtown · aml · life

🔜 Forms support (`pages-llm-prompter` component already exists)  
🔜 View state persistence  
🔜 Case status dashboards — trust scores, actor state, commitment views

---
layout: section
---

# The Road Ahead

---
layout: two-cols
---

# Platform Roadmap

**Near term**

🔜 `StreamContext` propagation — P1.8  
🔜 Auth retrofit — OIDC across all harnesses  
🔜 casehub-ras — reactive case creation  
🔜 casehub-desiredstate — full test suite  
🔜 casehub-pages → `casehubio/casehub-pages`  
🔜 CBR Retrieve — `CaseRetriever` similarity layer  
🔜 CBR Revise — adaptive plan templates  
🔜 Hybrid Typed Fact Space (`casehub-drools`)  
🔜 Hallucination detection hook on engine output  
🔜 LLM Supervisor Mode (aml, clinical)  
🔜 LLM triaging via `LlmGanglion` (casehub-ras)  

::right::

<br/>

**Architecture vision**

```
Sensory layer (ras)
  → Situational awareness
    → Case creation (automatic)
      → Coordination (engine)
        → Classical AI (rules, Bayesian)
        → LLM reasoning (agents)
        → Human gates (qhorus + work)
          → Audit (ledger)
            → Trust update
              → Better routing next time
```

<br/>

**The flywheel:**  
Better outcomes → better trust scores  
→ better routing → better outcomes.

CBR closes the loop:  
Past cases teach future cases.

---
layout: center
class: text-center
---

# Build on the Platform

<br/>

**Foundation** — platform · ledger · qhorus · work  
**Orchestration** — engine · eidos · neural-text  
**Integration** — claudony · openclaw · connectors · iot  
**Visualization** — casehub-pages  
**Reactive** — casehub-ras · casehub-desiredstate  

<br/>

**Bring your domain. Use the platform. Modify nothing below.**

<br/>

[casehubio.github.io](https://casehubio.github.io) · [github.com/casehubio](https://github.com/casehubio)
