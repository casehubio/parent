# CaseHub Tutorial and Examples Strategy

> **Audience:** Java/Quarkus developers encountering CaseHub for the first time, through to architects evaluating it for regulated enterprise use.
> **Date:** 2026-05-03

---

## 1. What Exists Today

Each project already has good examples, but they are siloed. The pattern is consistent and strong within each project — it breaks down across projects.

| Project | Examples | Approach | What's missing |
|---|---|---|---|
| `casehub-ledger` | 9 scenarios (order-processing, EigenTrust, Merkle, GDPR Art.17/22, PROV-DM, OTel, trust-routing, pseudonymisation) | Single HTTP call → full JSON response | Cross-project wiring |
| `casehub-work` | 4 scenarios (expense approval, credit decision, content moderation, document review) | Narrative stdout + full ledger trail | How to add ledger, queues, AI modules |
| `casehub-qhorus` | 3 tiers: type-system tests (CI), normative-layout tests (CI), agent-communication examples (LLM) | Deterministic + live LLM | How qhorus connects to work and engine |
| `casehub-engine` | None yet — 16 patterns planned in issue #102 | — | Everything |

**Planned but unimplemented:**
- Engine issue #102 — 16 enterprise AI agent orchestration patterns
- Engine issue #209 — LangChain4j agentic integration (AgenticScopeBridge, CasehubPlanner, AgentListener)
- Work issue #152 — split work-examples into core and full variants

---

## 2. Design Principles for All Tutorials

These apply to every example, tutorial, and walkthrough written for CaseHub.

### 2.1 Standalone module value first

Every module must make sense on its own before it is wired to another. A developer who only uses `casehub-work` without `casehub-ledger` or `casehub-engine` should find complete, working examples for their use case. The value of adding the next module is demonstrated by showing what it *adds*, not by requiring it.

### 2.2 Progressive layering — each addition is a deliberate step

Layers are introduced one at a time. Each step answers: "Why would I add this? What problem does it solve that I currently have?" The developer should feel the need before they see the solution.

```
Layer 0: Business domain alone (no CaseHub)
Layer 1: Single CaseHub module (standalone value)
Layer 2: Two modules composed (first integration)
Layer 3: Three-module ecosystem (realistic production shape)
Layer 4: Full compliance stack (regulated deployment)
```

### 2.3 Real business domains, not artificial scaffolding

Examples use recognisable business scenarios that Java enterprise developers have encountered in their careers. The scenario should be comprehensible in 60 seconds without domain expertise. Abstract scenarios (Agent A sends message to Agent B) are not examples — they are tests.

**Preferred domains for Java developers:**
- Financial services (AML, fraud detection, credit decisions, expense approval)
- Insurance (claims processing, underwriting)
- Compliance and audit (regulatory reporting, GDPR workflows)
- Code review and software delivery
- Document processing and classification

### 2.4 Runnable from the outside in

Every example runs with a single command or HTTP call. The developer should see output before they read code. The output should be self-narrating (structured logs, readable JSON, narrative stdout).

### 2.5 Entry points that serve different goals

Not all developers start the same way. Three valid entry points exist simultaneously:

| Entry type | Who uses it | Starting point |
|---|---|---|
| **Bottom-up (module by module)** | Developer adopting one module at a time | Start with the standalone module example |
| **Top-down (from a real use case)** | Developer with a specific business problem | Start with the scenario, work backwards to modules |
| **Concept-first (execution control, trust, compliance)** | Developer evaluating a specific capability | Start with the capability showcase, see which modules enable it |

---

## 3. Module Layering Paths

### 3.1 The work module stack

The natural layering order for `casehub-work`, showing what each module adds:

```
Level 1: casehub-work runtime alone
  → WorkItem CRUD, claim/assign/complete lifecycle
  → Built-in SLA (expiresAt, claimDeadline)
  → Example: expense approval — single approver, basic lifecycle
  → Java developer analogy: a typed task queue with lifecycle states

Level 2: + casehub-work-queues
  → Label-based routing into named queues
  → Inbox views filtered by candidateGroups
  → Example: document review queue — route by team/skill
  → Java developer analogy: topic-based message routing

Level 3: + casehub-work-ledger (requires casehub-ledger)
  → Every WorkItem transition produces a ledger entry
  → Immutable hash chain, decision snapshots, peer attestations
  → Example: regulated credit decision — full audit trail
  → Java developer analogy: event sourcing where the event store is tamper-evident

Level 4: + casehub-work-ai
  → SemanticWorkerSelectionStrategy — route by skill embedding, not just group
  → LLM-assessed capability matching
  → Example: AI content moderation — route by detected content domain
  → Java developer analogy: semantic routing vs. string matching

Level 5: + casehub-work-notifications
  → Delegated to casehub-connectors (Slack, Teams, SMS, email)
  → Escalation → notification → human response
  → Example: SLA breach → Slack alert → human claim

Level 6: + casehub-work-adapter (connects to casehub-engine)
  → WorkItem completion signals plan item transition
  → Human task becomes a node in an orchestrated case
  → Example: case-embedded human approval gate
```

### 3.2 The ledger module stack

```
Level 1: casehub-ledger alone
  → Immutable entries, Merkle chain, trust scoring
  → Example: order-processing — hash chain per state transition
  → Java developer analogy: an append-only structured log you can prove

Level 2: + EigenTrust scoring
  → Trust scores computed from attestation history
  → Example: eigentrust-mesh — 3 agents rated over time, routing shifts
  → Java developer analogy: weighted round-robin that learns from outcomes

Level 3: + GDPR compliance
  → Right to erasure (Art.17), automated decision records (Art.22)
  → Example: art22-decision-snapshot — structured decision context per entry
  → Java developer analogy: structured logging that meets regulatory requirements by construction

Level 4: + Merkle verification + PROV-DM
  → Cryptographic inclusion proofs, external transparency log
  → Example: merkle-verification — verify any entry without server access
  → Java developer analogy: immutable log where you can prove a specific event occurred
```

### 3.3 The qhorus message layer

```
Level 1: 9 message types (type-system examples — CI, no LLM)
  → Deterministic tests showing what each type means and when to use it
  → Java developer analogy: typed method signatures for inter-agent calls

Level 2: Normative channel layout (3-channel pattern — CI, no LLM)
  → Work channel (COMMAND/DONE/FAILURE), Observe channel (STATUS/EVENT), Oversight (QUERY/RESPONSE)
  → Java developer analogy: separate topics for commands, telemetry, and queries

Level 3: Real LLM agents (agent-communication examples)
  → Code review pipeline: does the agent choose COMMAND for delegation?
  → Refund authorisation: does the agent ask (QUERY) before acting?
  → Out-of-scope decline: does the agent DECLINE correctly vs FAILURE?
  → Java developer analogy: typed API contracts, enforced at runtime

Level 4: Trust feedback loop
  → DONE → LedgerAttestation → TrustScoreJob → routing shifts
  → Java developer analogy: circuit breaker that adapts based on success history
```

### 3.4 Cross-module integration path

```
Stage 1: Single module
  → Pick: ledger, work, qhorus, or engine
  → Run the example, understand the SPI, write a custom implementation

Stage 2: Two modules
  → ledger + work: every WorkItem transition audited
  → ledger + qhorus: every message in the ledger
  → qhorus + work: WorkItem completion sends DONE to the originating agent

Stage 3: Three-module ecosystem
  → work + qhorus + ledger: human tasks + agent communication + audit
  → Scenario: AML investigation (see Section 6)

Stage 4: Full platform
  → + engine: orchestrated case, binding evaluation, ACM
  → + claudony: Claude sessions as workers
  → Scenario: clinical trial coordination (see Section 7)
```

---

## 4. The LangChain4j Agentic Patterns Connection

Engine issue #102 defines 16 enterprise patterns. Engine issue #209 defines the LangChain4j bridge (AgenticScopeBridge, CasehubPlanner, AgentListener). The LangChain4j agentic patterns (the 5 patterns from its model) map onto both the module layers and the enterprise scenarios.

### 4.1 The 5 LangChain4j patterns and their CaseHub mapping

| LangChain4j pattern | CaseHub expression | Engine issue | Tutorial level |
|---|---|---|---|
| **Sequential** | Linear binding chain — each binding fires when the previous worker completes | #101 (LLM Supervisor), #114 (ReAct) | Level 2 — two modules |
| **Loop** | LoopControl.select() cycles until exit condition met | #114 (ReAct Cycles) | Level 2 |
| **Parallel** | Multiple bindings fire simultaneously on one CaseContextChangedEvent | #107 (Elastic Research Teams) | Level 3 |
| **Parallel mapper** | Sub-case per item — parent waits for M-of-N | #112 (Sub-Case Orchestration) | Level 3 |
| **Conditional** | Binding condition (JQ/lambda) gates which path fires | #108 (Long-Running), #116 (Compliance) | Level 2 |

### 4.2 Where LangChain4j patterns appear in business scenarios

The AML tutorial (Section 6) exercises all five:
- **Sequential:** transaction flagged → entity resolution → OSINT → SAR narrative
- **Loop:** iterative evidence gathering until risk score exceeds threshold
- **Parallel:** three specialist agents (entity, pattern, sanctions) run concurrently
- **Parallel mapper:** batch of 10 suspicious transactions, each as a sub-case
- **Conditional:** different investigation path based on transaction type (structuring vs sanctions vs PEP)

This means the AML tutorial simultaneously teaches LangChain4j agentic patterns *and* CaseHub capabilities — a developer coming from langchain4j experience lands in familiar territory.

---

## 5. Concept-First Entry Points

Some developers want to understand a specific capability without going through all the modules. These standalone showcases focus on one concept.

| Concept | What it shows | Modules needed | Analogy for Java devs |
|---|---|---|---|
| **Execution control types** | Sequential, parallel, conditional, loop, parallel mapper | casehub-engine (alone) | Different thread/executor patterns, but declarative |
| **Human-in-the-loop** | WorkItem with SLA, escalation, delegation | casehub-work | A typed task with deadlines and handoff |
| **Speech acts** | 9 message types and when to use each | casehub-qhorus (type-system examples) | Strongly typed method signatures between services |
| **Trust scoring** | Bayesian Beta from outcomes; routing shifts over time | casehub-ledger (eigentrust-mesh, trust-routing) | Adaptive load balancer weighted by outcome history |
| **Tamper-evident audit** | Merkle chain, inclusion proofs, independent verification | casehub-ledger (merkle-verification) | Append-only event store with cryptographic proof |
| **GDPR compliance** | Art.17 erasure, Art.22 decision records | casehub-ledger (art22, privacy-pseudonymisation) | Structured logging that satisfies the regulation by construction |
| **Sub-case orchestration** | Parent case spawning and coordinating child cases | casehub-engine | Fork-join with independent lifecycle per branch |
| **LLM supervisor mode** | LLM reads state, selects next binding | casehub-engine (LlmPlanningStrategy) | Dynamic dispatch table driven by LLM reasoning |

---

## 6. Tutorial: AML Investigation (Java Developer Tutorial)

**Role:** Primary tutorial — demonstrates all CaseHub capabilities in a domain Java enterprise developers immediately recognise.

**Why Java developers relate:** Java dominates banking infrastructure. AML compliance systems — transaction monitoring, case management, SAR filing — are systems Java developers have built or integrated. They recognise the pain: audit trails that can't reconstruct the decision chain, human escalation that fires too late, SAR filings where nobody can say which agent made the call.

**Comparison baseline:** IBM AMLSim (open source, GitHub), industry whitepapers (AnChain, Sardine) — showing what current LLM-based AML coordination looks like without formal accountability.

### 6.1 Tutorial layers

**Layer 1 — The business scenario alone (no CaseHub)**

Show the problem: a transaction is flagged. Multiple specialists need to investigate. A human must file a SAR. Without coordination infrastructure:

```java
// The naive approach: direct service calls
EntityResolutionResult entity = entityService.resolve(transaction);
PatternResult pattern = patternService.analyzeStructuring(transaction);
OsintResult osint = osintService.checkSanctions(transaction);
String sarNarrative = narrativeService.draft(entity, pattern, osint);
// Who was responsible for which finding?
// What if one service failed? Was it retried?
// When did the compliance officer actually review this?
// Can we prove to FinCEN that the investigation was complete?
```

**Layer 2 — casehub-work: structured human task with SLA**

Add the compliance officer decision as a formal WorkItem with a 30-day FinCEN deadline:

```java
// WorkItem with regulatory SLA
WorkItemRequest sarReview = WorkItemRequest.builder()
    .title("SAR Review: Transaction TXN-2024-001")
    .category("aml-investigation")
    .candidateGroups("compliance-officers")
    .claimDeadline(Instant.now().plus(30, ChronoUnit.DAYS)) // FinCEN: 30 days
    .expiresAt(Instant.now().plus(45, ChronoUnit.DAYS))
    .payload(investigationFindings.toJson())
    .build();
```

**Layer 3 — casehub-qhorus: typed agent communication**

Replace direct service calls with formal speech acts:

```
[Transaction Monitor] COMMAND → Entity Resolution Agent: "Resolve beneficial ownership for TXN-001"
[Entity Resolution Agent] RESPONSE → "3-layer shell structure identified, ultimate beneficiary: ..."
[Transaction Monitor] COMMAND → Pattern Agent: "Assess structuring patterns for entity cluster"
[Pattern Agent] STATUS → "Analyzing 47 related transactions..."
[Pattern Agent] DONE → "High-confidence structuring: 23 transactions below $10k reporting threshold"
[Transaction Monitor] COMMAND → OSINT Agent: "Check sanctions and adverse media"
[OSINT Agent] DECLINE → "Insufficient clearance for PEP database access; route to senior analyst"
```

Every message is in the commitment lifecycle. The DECLINE is not an error — it is a formal record that the agent correctly identified a scope boundary.

**Layer 4 — casehub-ledger: FinCEN-compliant audit trail**

Every agent message writes a `MessageLedgerEntry`. Every WorkItem transition writes an entry. The Merkle chain means the regulator can verify the investigation record without accessing the server.

```bash
# Verify the investigation trail
GET /ledger/entries?subjectId={case-id}&format=prov-dm
# Returns W3C PROV-DM lineage: every agent, every decision, every human review, timestamped and chained
```

**Layer 5 — casehub-engine: adaptive case management**

The investigation path is not fixed. If the entity resolution reveals a PEP (Politically Exposed Person), the case bindings route differently. If three concurrent pattern checks contradict each other, the LLM supervisor selects the next binding dynamically.

```
CaseContext update: { "entityType": "PEP", "riskScore": 0.87 }
  → Binding condition (JQ): .entityType == "PEP" and .riskScore > 0.8
  → Fires: SeniorAnalystBinding (routes to compliance director, not officer)
  → WAITING state: durable suspension until director review complete
```

**Layer 6 — Trust routing**

After 50 investigations, which Pattern Agent has the highest SAR accuracy rate? Trust scores from `LedgerAttestation` records drive routing. The compliance officer who approved 40 SARs that were subsequently upheld gets routed the next complex case.

**Layer 7 — The comparison**

| Requirement | Naive LLM approach | IBM AMLSim | CaseHub |
|---|---|---|---|
| Auditable evidence chain (FinCEN 2024) | Not addressed | Simulation only | ✅ Merkle + commitment per agent |
| Human sign-off SLA | Ad-hoc | Not applicable | ✅ WorkItem claimDeadline |
| GDPR on transaction data | Not addressed | Not applicable | ✅ LedgerErasureService |
| Attribution per decision | Not possible | Not applicable | ✅ causedByEntryId chain |
| Trust-weighted routing | Not addressed | Not applicable | ✅ EigenTrust from attestation history |
| Adaptive investigation path | Fixed pipeline | Fixed simulation | ✅ ACM binding evaluation |

### 6.2 LangChain4j patterns exercised

| Pattern | AML expression |
|---|---|
| Sequential | Transaction flagged → entity → pattern → OSINT → SAR narrative |
| Loop | Iterative evidence gathering until risk confidence > threshold |
| Parallel | Entity, pattern, and sanctions checks run concurrently |
| Parallel mapper | Batch of flagged transactions, each as a sub-case investigation |
| Conditional | PEP detection routes to senior analyst; standard case routes to officer |

### 6.3 Engine issue #102 patterns covered

| Issue | Pattern | AML expression |
|---|---|---|
| #101 | LLM Supervisor Mode | Supervisor selects next investigation step based on accumulated evidence |
| #107 | Elastic Research Teams | Multiple specialist agents (entity, pattern, OSINT) coordinate via Qhorus |
| #112 | Sub-Case Orchestration | Batch investigation: parent case → per-transaction sub-cases |
| #113 | Regulatory Decision Automation | SAR filing with traceable reasoning + compliance officer sign-off gate |
| #115 | Human Escalation in Agent Pipelines | Compliance officer as first-class WorkItem, PEP routes to director |
| #116 | Compliance and Audit Workflows | FinCEN evidence chain, GDPR Art.17 erasure |

---

## 7. Showcase: Clinical Trial Coordination (Market Entry Demo)

**Role:** Market entry demonstration — shows CaseHub in a regulated domain where compliance features are legally mandatory, not optional.

**Audience:** Decision-makers and architects evaluating CaseHub for regulated industries. Not a getting-started tutorial — a demonstration of what becomes possible.

**Comparison baseline:** ClinicalAgent ([arXiv 2404.14777](https://arxiv.org/abs/2404.14777), GitHub open source) — peer-reviewed (ACM BCB '24), showing exactly what naive LLM trial coordination looks like.

### 7.1 What it demonstrates that ClinicalAgent cannot add

| GCP / ICH requirement | ClinicalAgent | CaseHub |
|---|---|---|
| Adverse event SLA (24h/7d) | No deadline tracking | WorkItem claimDeadline + auto-escalation |
| Protocol deviation authorisation | Agent decides autonomously | COMMAND from PI required; commitment lifecycle |
| Patient consent cascade (GDPR Art.17) | No GDPR capability | LedgerErasureService |
| Multi-site independence (50+ sites) | Single-case linear pipeline | Sub-case per site with trial-level rollup |
| Tamper-evident audit (FDA) | No audit trail | Merkle MMR + Ed25519-signed checkpoints |
| Trust-weighted safety agent routing | No trust model | Bayesian Beta from outcome attestations |

### 7.2 Engine issue #102 patterns covered

| Issue | Pattern | Clinical expression |
|---|---|---|
| #101 | LLM Supervisor Mode | Protocol amendment analysis — LLM reads accumulated case data to select next assessment |
| #108 | Long-Running Case Management | Trials run months to years — durable case state, WAITING across protocol review periods |
| #110 | Goal Decomposition | Trial objectives decompose into: recruitment, dosing, safety monitoring, endpoint analysis |
| #112 | Sub-Case Orchestration | Per-site sub-cases with independent investigator teams, rollup to trial-level status |
| #113 | Regulatory Decision Automation | FDA submission with traceable reasoning per protocol decision |
| #115 | Human Escalation | IRB/ethics committee approval gates with formal SLA |
| #116 | Compliance and Audit Workflows | GCP, FDA IND, EMA CTR, GDPR all enforced by platform construction |

### 7.3 Demonstration scenario

A 3-site oncology trial. Site A enrolls a patient, agents run eligibility screening across 12 criteria. A marginal criterion triggers an IRB consultation (WorkItem: 72-hour SLA). At Site B, a Grade 3 adverse event fires an automatic 24-hour safety escalation. At Site C, a protocol amendment is proposed — the LLM supervisor reads accumulated context from all three sites and recommends whether to proceed. The Merkle audit trail means FDA can independently verify the complete decision chain for every patient at every site.

ClinicalAgent runs as a linear pipeline for one site. It has no concept of SLA, no IRB gate, no adverse event escalation, and no audit trail.

---

## 8. Execution Control Showcase (Concept-First Entry)

**Role:** Standalone capability showcase — shows the five execution control patterns without requiring any domain knowledge. Entry point for developers coming from LangChain4j, Spring Batch, or workflow engine backgrounds.

**Why separate from the domain tutorials:** A developer evaluating whether CaseHub's execution model fits their needs should not need to understand AML to see how parallel binding evaluation works.

### 8.1 The five patterns, demonstrated independently

Each pattern runs as a standalone Quarkus application with a single HTTP endpoint:

**Pattern 1: Sequential** — linear chain, each step depends on the previous
```
POST /demo/sequential
→ Step A completes → Step B fires → Step C fires → case closes
→ Shows: binding conditions, event-driven handoff, zero polling
```

**Pattern 2: Conditional** — path chosen by case state
```
POST /demo/conditional?riskLevel=high
→ highRisk=true → RegulatoryReviewBinding fires
→ highRisk=false → AutoApprovalBinding fires
→ Shows: JQ predicate binding conditions, same case definition, different paths
```

**Pattern 3: Parallel** — simultaneous execution from one state change
```
POST /demo/parallel
→ CaseContext update → 3 bindings fire simultaneously
→ All 3 workers run in parallel, no coordination required
→ Shows: automatic parallelism without declaration
```

**Pattern 4: Loop** — iterative until condition met
```
POST /demo/loop
→ ResearchAgent runs → publishes findings → confidence score increases
→ Loops until confidence > 0.85 → exits → report generated
→ Shows: LoopControl, exit condition on accumulated state
```

**Pattern 5: Parallel mapper** — fan-out, one sub-case per item
```
POST /demo/parallel-mapper
→ 5 items in input list → 5 sub-cases created
→ Each sub-case runs independently → all complete → parent aggregates
→ Shows: sub-case orchestration, M-of-N completion, result rollup
```

### 8.2 Comparison to LangChain4j patterns

| LangChain4j | CaseHub equivalent | Key difference |
|---|---|---|
| Sequential chain | Linear binding chain | LangChain4j is code; CaseHub is declarative + audit-traced |
| Agent loop | LoopControl.select() | CaseHub loop has durable state — survives restart |
| Parallel | Multi-binding evaluation | CaseHub parallel exploits state changes automatically |
| Parallel mapper | Sub-case orchestration | CaseHub sub-cases have independent lifecycle, SLA, compliance |
| Conditional | JQ/lambda binding condition | CaseHub conditions operate on the full accumulated case context |

---

## 9. Documentation Structure

### 9.1 Where tutorials and examples live

```
<repo>/
├── examples/                    ← Runnable examples (Maven modules)
│   ├── <scenario-name>/
│   │   ├── pom.xml
│   │   ├── README.md            ← What this shows; how to run it; what the output means
│   │   └── src/
├── docs/
│   ├── DESIGN.md                ← Architecture reference (current)
│   ├── LAYERING.md              ← Module selection guide (to create)
│   └── tutorials/               ← Step-by-step tutorials (to create)
│       ├── getting-started.md
│       └── <concept>.md

casehub-parent/docs/
├── use-case-analysis.md         ← This document's sibling (done ✅)
├── tutorial-strategy.md         ← This document (done ✅)
├── gastown-casehub-analysis-v2.md
└── tutorials/                   ← Cross-project tutorials (to create)
    ├── aml-investigation/       ← Layer-by-layer AML tutorial
    └── execution-control/       ← Concept-first pattern showcase
```

### 9.2 Per-module LAYERING.md structure

Each repo should have `docs/LAYERING.md` with this shape:

```markdown
# When to use this module

## Standalone (no other casehub modules required)
What you get: ...
Example: link to examples/<name>

## Combined with casehub-ledger
What is added: ...
When to add it: ...
Example: link to examples/<name>

## Combined with casehub-qhorus
...

## Do not add yet if:
- You don't need compliance audit (save for later)
- You don't have multiple candidate agents (start with least-loaded)
```

---

## 10. Phased Delivery

### Phase 1 — Foundation (can start now)

- [ ] `docs/LAYERING.md` in casehub-work (module selection guide)
- [ ] Execution control showcase (5 patterns, standalone Quarkus app, no LLM)
- [ ] Split work-examples into core and full variants (issue #152)
- [ ] Cross-project integration example: work + ledger (expense approval with audit trail)

### Phase 2 — AML Tutorial (Java developer primary tutorial)

- [ ] Layer 1: naive Java approach (comparison baseline, no CaseHub)
- [ ] Layer 2: + casehub-work (compliance officer WorkItem with SLA)
- [ ] Layer 3: + casehub-qhorus (typed agent communication)
- [ ] Layer 4: + casehub-ledger (FinCEN audit trail)
- [ ] Layer 5: + casehub-engine (adaptive investigation path)
- [ ] Comparison table vs IBM AMLSim and industry whitepapers
- [ ] Blocked on: engine issue #209 (LangChain4j bridge) for Layer 5

### Phase 3 — LangChain4j Pattern Examples (after issue #209)

- [ ] Sequential, loop, parallel, parallel mapper, conditional — each as a standalone example in casehub-engine
- [ ] Mapping table: LangChain4j pattern → CaseHub expression → AML scenario
- [ ] Covers engine issue #102 children: #101, #107, #112, #113, #114, #115, #116

### Phase 4 — Clinical Trial Showcase (market entry demo)

- [ ] Multi-site trial scenario
- [ ] Comparison against ClinicalAgent (open source baseline)
- [ ] GCP compliance requirements map
- [ ] FDA audit trail demonstration

---

## 11. Decisions and Rationale

| Decision | Rationale |
|---|---|
| AML as primary tutorial, not security incident response | Java developers work in banking; AML compliance systems are what they build. Security incident response (MyAntFarm comparison) is strong on community fit but weak on market entry gap (SOAR is a crowded incumbent market). |
| Clinical trials as showcase, not tutorial | GCP compliance requires domain knowledge to follow. It makes the market entry argument compellingly but is a poor teaching vehicle for a Java developer without pharma background. |
| Execution control showcase separate from domain tutorials | A developer evaluating CaseHub's binding model should not need to understand AML. Separate entry points for separate purposes. |
| Examples in each project repo, not a separate tutorials repo | Examples run in CI. They are tested code. Separating them from the project creates drift. |
| Layer-by-layer structure over "start with the full stack" | The standalone value of each module is the argument for adoption. A developer who adds ledger to an existing work deployment should see ledger demonstrated standalone first. |
| LangChain4j patterns as the bridge for developers coming from langchain4j | The AML tutorial exercises all 5 LangChain4j agentic patterns. A developer who knows langchain4j lands in familiar territory and sees what CaseHub adds on top. |

---

## 12. References

- Engine issue #102: [Epic: casehub Ecosystem Use Cases](https://github.com/casehubio/engine/issues/102)
- Engine issue #209: [Epic: langchain4j-agentic integration](https://github.com/casehubio/engine/issues/209)
- Work issue #152: [Split casehub-work-examples into core and full variants](https://github.com/casehubio/work/issues/152)
- Work issue #122: [Epic: Documentation and examples coverage](https://github.com/casehubio/work/issues/122)
- Use case analysis: `docs/use-case-analysis.md`
- ClinicalAgent baseline: [arXiv 2404.14777](https://arxiv.org/abs/2404.14777)
- IBM AMLSim baseline: [GitHub IBM/AMLSim](https://github.com/IBM/AMLSim/)
- LangChain4j agentic patterns: [langchain4j agents tutorial](https://github.com/langchain4j/langchain4j/blob/main/docs/docs/tutorials/agents.md)
