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

## 1.5 Tutorial Taxonomy

CaseHub tutorials are not a single artifact type. There are three distinct forms, each
serving a different audience need. They are independent — not a hierarchy.

### Architectural style guides

**What:** How large-scale applications compose. Decisions, tradeoffs, platform coherence,
boundary rules, module relationships. Written for architects and senior developers
evaluating the platform or planning an integration.

**Form:** Reference documents — PLATFORM.md, AGENTIC-HARNESS-GUIDE.md,
gastown-casehub-analysis-v2.md, LAYER-LOG.md. Not runnable code. Dense with rationale.

**Examples today:** PLATFORM.md capability ownership table, casehub-devtown
`docs/gastown-casehub-analysis-v2.md`, AML vs ClinicalAgent comparison table.

### Reference architecture applications

**What:** Production-grade domain applications built on the CaseHub foundation — demonstrating the full harness integration in a real-world domain. Each is a reference architecture: correct, deployable, and potentially production-ready if the community evolves it in that direction.

**Form:** A production application repo (devtown, AML, clinical) with ARC42STORIES.MD as the architectural record, LAYER-LOG.md capturing the integration progression, blog entries capturing decisions, and git history capturing chronology. Runnable end-to-end with a single HTTP call at every layer. Domain knowledge is a prerequisite — practitioners in each field will have it.

**Build pattern:** Vertical slice first, then deepen (see §2.2). Layers are ordered for reading — the sequence in which a developer understands the architecture — not for building.

**Tutorial role:** Tutorial content is a byproduct of this record, not its purpose. Spot tutorials and architectural highlights are extracted from the reference architecture; they do not drive it.

**Examples today:** casehub-aml (Layers 1–3 complete), casehub-devtown (Layers 1, 2, 5).

### Spot and technique tutorials

**What:** Isolated demonstration of one specific concept, API, or architectural pattern.
Self-contained — no domain setup, no prior layers required. Not end-to-end.

**Form:** A module example, a standalone `@QuarkusTest` scenario, or a focused doc with
runnable code. Should run in under 30 seconds and produce self-narrating output.

**Types:**
- **Technique:** how to use a specific API correctly — e.g., `MessageDispatch.builder()`
  protocol, CommitmentStore lifecycle queries, Flyway named-datasource scoping
- **Approach:** how to apply an architectural pattern — e.g., `@DefaultBean` displacement,
  normative 3-channel layout, `@Alternative @Priority` for SPI overrides
- **Showcase:** isolated demonstration of a platform capability — e.g., Merkle inclusion
  proof, trust score cold-start, GDPR Art.17 erasure flow

**Examples today:** qhorus `SecureCodeReviewScenario`, qhorus normative-layout tests,
casehub-ledger 9-scenario examples, the execution control showcase (§8 below).

**Relationship to reference architectures:** reference architectures generate spot tutorial material as
a by-product. A pattern discovered while building AML Layer 3 becomes a technique entry
in the spot tutorial catalogue. A gotcha becomes a garden entry. The reference architecture is
the source; the spot tutorial is the extracted, reusable form.

---

## 2. Design Principles for All Tutorials

These apply to every example, tutorial, and walkthrough written for CaseHub.

### 2.0 CaseHub is an agentic harness — domain applications build on it

The **CaseHub foundation** is an agentic harness — infrastructure that coordinates multiple agents (human and AI), enforces formal accountability per interaction, adapts paths based on accumulated context, and produces an independently verifiable audit trail. The domain applications (aml, clinical, devtown, QuarkMind) are built on this harness; they are not the harness itself.

This is what distinguishes CaseHub from adjacent tools:
- **LangChain4j** makes a single agent smart (reasoning, tool use) — runs inside the harness
- **Quarkus Flow** makes a single step durable (retry, backoff, state) — runs inside the harness
- **CaseHub** makes the full multi-agent coordination accountable — the harness itself

The foundation modules that constitute the harness:

| Module | Harness function |
|--------|-----------------|
| casehub-qhorus | Agent communication — COMMAND creates formal obligation; DONE/DECLINE are typed outcomes |
| casehub-work | Human-in-the-loop — SLA-bounded task gates, escalation |
| casehub-engine | Orchestration — adaptive paths, CasePlanModel, task routing |
| casehub-ledger | State persistence and audit — tamper-evident evidence chain, resumability |
| casehub-connectors | External tool dispatch — Slack/Teams and other integrations |

Four domain applications currently demonstrate the harness across domains:

| App | Domain | Audience |
|-----|--------|----------|
| casehub-aml | Financial crime investigation | Java developers in financial services |
| casehub-clinical | Clinical trial coordination | Java developers in regulated healthcare |
| casehub-devtown | PR review orchestration | Java developers in software engineering |
| QuarkMind | StarCraft II game AI | R&D / living lab |

Each demonstrates that the same harness holds across domains — from regulated enterprise compliance to game AI. An LLM with all four as reference material can build a fifth domain application in any domain without asking questions.

### 2.0b Domain applications are reference architectures

Every CaseHub domain application is a **reference architecture** — a production-grade system demonstrating the full CaseHub harness in a real domain, with potential for production adoption if the community evolves it in that direction. They are not tutorial applications; they are real applications whose documentation is thorough enough to teach.

The architectural record serves two purposes beyond the running system. First, **understanding** — how the layers integrate and how the parts come together, which is necessary for humans and LLMs to refactor, extend, improve, and fix the system confidently. Second, **cross-domain reuse** — not cloning this domain, but using the architectural patterns as a structural template for new domain implementations. An AML system uses the layer integration sequence, CDI displacement pattern, and content-driven binding conditions from devtown as a starting point; it does not copy the PR review domain logic.

Where teaching is needed, it happens through two mechanisms extracted from the reference architecture, not embedded in it:

- **Spot tutorials** — isolated, self-contained demonstrations of one concept or pattern (see §1.5). Extracted from the reference architecture as needed.
- **Architectural highlights** — focused explanations of how specific techniques come together: why `@DefaultBean` displacement keeps each layer a coherent deployable state, how content-driven binding conditions replace author-declared routing, how parallel WAITING enables max-not-sum cycle time. These emerge from the reference architecture record; they do not drive it.

The "field" qualifier on each domain matters: each reference architecture targets practitioners who already have domain knowledge — because that knowledge is a prerequisite, not a barrier. GCP compliance is standard for a Java developer in pharma. AML workflow is standard for a Java developer at a bank. Code review orchestration is standard for any Java developer. CaseHub domain applications assume that knowledge and show what the platform adds.

There is no hierarchy between reference architectures. AML, clinical, and devtown each serve their own domain. AML is not "the" primary reference — it is the reference architecture for financial services, and currently the furthest along.

### 2.1b Production-first — the layer documentation emerges from the integration sequence

Every domain application is designed and built for production deployment. The layer documentation structure is not a separate design concern — it emerges from documenting the natural sequence in which you would integrate CaseHub foundation modules when building a real application.

**Do not make architectural decisions to serve the documentation.** Every line of code must justify its existence in a deployed production system. The architectural record documents what you built; it does not drive what you build.

The only layer with a deliberate comparison baseline is Layer 1: the domain without CaseHub. This shows what a team would actually write without the platform, making the accountability gap visible before the foundation modules close it. From Layer 2 onward, every implementation decision is a production decision. **The code must be production quality throughout — no gap markers or annotations in source files.** Accountability gaps are documented in LAYER-LOG.md (or ARC42STORIES.MD §9.4) in a structured table per layer entry, mapping each gap to the foundation module that closes it.

The foundation modules map to architectural layers in LAYER-LOG.md. This table is a
**reading guide** — the order in which a developer should encounter the layers to
understand the architecture. It is not a build sequence. Build order is driven by
vertical slices (see §2.2).

| Layer | What it adds | What gap it closes |
|-------|-------------|-------------------|
| 1 | Domain baseline — domain logic alone | Baseline: this is what you'd write without CaseHub |
| 2 | casehub-work | No formal deadline or human task lifecycle |
| 3 | casehub-qhorus | No formal obligation per agent interaction |
| 4 | casehub-ledger | No tamper-evident audit trail |
| 5 | casehub-engine | Fixed pipeline; no adaptive paths |
| 6 | Trust routing | No trust model; random or round-robin agent selection |
| 7 | Comparison | Explicit contrast with existing tools in the field |

Each layer adds one foundation concern and makes its value tangible relative to the
previous layer. Some layers may be built out of this reading order when a vertical slice
demands it — document what was built and why in LAYER-LOG.md regardless of sequence.

### 2.1 Standalone module value first

Every module must make sense on its own before it is wired to another. A developer who only uses `casehub-work` without `casehub-ledger` or `casehub-engine` should find complete, working examples for their use case. The value of adding the next module is demonstrated by showing what it *adds*, not by requiring it.

### 2.2 Vertical slice planning — build end-to-end first, then deepen

**A vertical slice is the thinnest working path through all relevant layers that
produces a testable result.** One case opens, one agent receives a COMMAND, one
human review WorkItem is created, one ledger entry is written, one commitment is
tracked. The full stack is exercised — even if each layer handles only one scenario.

Build vertical slices before completing any single layer to full production depth.
Integration failures and architectural mismatches surface on the first slice, before
significant layer logic has been built out.

**Planning vertical slices:**

Before starting implementation, pre-identify as many vertical slices as the domain
warrants. Then sequence them using two criteria:

1. **Sequential dependencies first.** Some layers can only be built after another is
   in place — the earlier layer enables the later one. Ledger must precede trust
   routing. Engine must precede content-driven routing. These dependencies determine
   the hard ordering.

2. **Minimal layer delta next.** Among slices that have no hard dependency ordering,
   prefer the slice that reuses the most of what is already built. A slice that adds
   one new foundation module is preferable to one that adds three, even if both are
   technically independent. This keeps each slice small, reviewable, and well-bounded.

**Caveats:**

- Some layers that appear orthogonal have soft ordering: qhorus before ledger is not
  a hard dependency, but qhorus messaging generates the entries that make ledger
  meaningful. Document these soft orderings in LAYER-LOG.md.
- A layer may intentionally be split across slices — deliver the minimal version
  needed for the current slice, deepen it in a later slice that needs the extra depth.
- Not every vertical slice needs to cover all layers. A slice that adds engine
  routing without touching ledger is valid if ledger coverage comes in the next slice.

**Example slice sequence for devtown:**
1. PR submitted → case opened → outcome returned *(Layer 1 + Layer 5 foundation)* ✅
2. Case opened → human review WorkItem with SLA *(adds Layer 2)* ✅
3. Case opened → specialist COMMAND dispatched → commitment fulfilled *(adds Layer 3)*
4. Case opened → tamper-evident ledger entry written *(adds Layer 4)*
5. Case opened → trust-weighted agent selected from attestation history *(adds Layer 6)*

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

### 2.5 Match the tutorial type to the audience need

The three tutorial types (§1.5) serve different developer needs. Matching the type to
the need is as important as the content.

| Developer need | Artifact | Starting point |
|---|---|---|
| Evaluating CaseHub architecture for an enterprise decision | Architectural style guide | PLATFORM.md, gastown analysis, ARC42STORIES.MD |
| Understanding how a full domain integration is structured | Reference architecture | Domain app (devtown/AML/clinical) — ARC42STORIES.MD Chapter Index |
| Integrating one module into an existing system | Spot tutorial (technique) | Standalone module examples (casehub-work, qhorus) |
| Understanding one concept deeply before committing | Spot tutorial or architectural highlight | Technique/approach/showcase for that specific capability |
| Evaluating a specific CaseHub capability | Spot tutorial (showcase) | Isolated example: Merkle proof, trust routing, 3-channel layout |

**Spot and technique tutorials are not entries into a field tutorial.** A developer who
reads `SecureCodeReviewScenario` to understand commitment lifecycle has everything they
need — they do not need to complete a field tutorial first. Design spot tutorials to be
fully self-contained.

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

## 4. LangChain4j, Quarkus Flow, and CaseHub — Three Layers, Not Three Alternatives

This is the most important architectural distinction to get right in the tutorials. Developers coming from LangChain4j experience will ask: "Do I need CaseHub if I already have LangChain4j?" The answer requires understanding that these operate at completely different levels of granularity. They are not alternatives — they are a stack.

### 4.1 The three layers

```
┌──────────────────────────────────────────────────────────────────────┐
│  CaseHub case                                                         │
│  Duration: days, weeks, months                                        │
│  Scope: multiple humans + multiple agents + audit + compliance        │
│  Concerns: obligations, SLA, trust routing, regulatory evidence chain │
├──────────────────────────────────────────────────────────────────────┤
│  Quarkus Flow workflow (one case step)                                │
│  Duration: minutes to hours                                           │
│  Scope: bounded, durable execution of one unit of work               │
│  Concerns: task sequencing, error handling, durable state             │
├──────────────────────────────────────────────────────────────────────┤
│  LangChain4j agent (one agent's reasoning)                           │
│  Duration: seconds to minutes                                         │
│  Scope: one AI agent deciding how to use its tools                   │
│  Concerns: tool selection, reasoning loop, result synthesis           │
└──────────────────────────────────────────────────────────────────────┘
```

**The Java developer analogy:**

- **LangChain4j** is the AI reasoning library your service uses — the equivalent of a domain library. It gives one agent the ability to think, call tools, and loop until it has an answer.
- **Quarkus Flow** is the durable workflow that service executes — the equivalent of a Spring Batch step or a BPMN service task. It defines what "run entity resolution" means: which APIs to call, how to handle retries, how to structure the result.
- **CaseHub** is the enterprise process orchestrating everything above it — the equivalent of an enterprise BPM engine (jBPM, Camunda), but adaptive rather than fixed-path. It coordinates which agents work on what, enforces SLAs, tracks formal obligations, and produces the audit trail the regulator sees.

Each layer is independent. You can use LangChain4j without Quarkus Flow. You can use Quarkus Flow without CaseHub. But when you need all three concerns simultaneously — regulated, multi-agent, long-running, auditable — the stack is the answer.

### 4.2 Why the LangChain4j patterns are NOT CaseHub patterns

The 5 LangChain4j agentic patterns (sequential, loop, parallel, parallel mapper, conditional) describe how **one agent** reasons internally. At the CaseHub level, these are not patterns — they are simply how the binding system works by default:

| LangChain4j "pattern" | At CaseHub level | Why it's not a pattern |
|---|---|---|
| **Sequential** | Binding chain | Default behaviour: A's output satisfies B's condition. No declaration needed. |
| **Parallel** | Multi-binding evaluation | CaseHub evaluates ALL matching bindings simultaneously on every state change — automatic, not declared. This is one of CaseHub's fundamental advantages over workflow engines. |
| **Conditional** | JQ predicate binding condition | Every binding has a condition. This is the most basic CaseHub concept, not a special pattern. |
| **Loop** | LoopControl.select() | CaseHub's LoopControl handles this with full CaseContext awareness — more powerful than a simple while loop. |
| **Parallel mapper** | Sub-case orchestration | CaseHub sub-cases each have full lifecycle, SLA, compliance, and commitment tracking — far richer than LangChain4j's parallel map. |

**The key insight:** At the CaseHub level, parallel execution is the default, conditions are everywhere, and loops are handled by LoopControl. A developer who frames these as "CaseHub patterns" is operating at the wrong layer.

### 4.3 Where LangChain4j patterns DO apply — inside a single agent

The LangChain4j patterns apply within the innermost layer: how a single agent reasons during its execution as a CaseHub worker. The entity resolution agent in an AML investigation might use:

- **Sequential** (internally): query company registry → check PEP database → cross-reference news → synthesise result
- **Loop** (internally): search, evaluate confidence, search different sources if confidence < threshold
- **Conditional** (internally): if jurisdiction is offshore, call additional screening tool

None of this is visible to CaseHub. CaseHub sees the agent as a black box that eventually sends a formal RESPONSE message with its findings. The agent's internal reasoning is LangChain4j's concern; the formal accountability for that RESPONSE — who committed to it, whether it arrived within SLA, whether trust score should update — is CaseHub's concern.

### 4.4 What engine issue #209 (AgenticScopeBridge) actually does

Issue #209 is not about expressing LangChain4j patterns in CaseHub. It is about making LangChain4j agents work smoothly as CaseHub workers — specifically:

- **AgenticScopeBridge**: maps CaseContext (the case's shared blackboard state) into the `AgenticScope` format that LangChain4j agents expect, and writes agent outputs back to the EventLog
- **CasehubPlanner**: implements LangChain4j's `Planner` interface, delegating to `LoopControl.select()` — so an LLM-driven planner can be used as a CaseHub worker
- **CasehubAgentListener**: records every LangChain4j agent invocation as an EventLog entry with `causedByEntryId` — so the agent's tool calls appear in the case's audit trail

The bridge makes LangChain4j agents first-class CaseHub workers. It does not import LangChain4j patterns into CaseHub.

### 4.5 The teaching story for the AML tutorial

The correct framing — relatable for a Java developer:

> "The entity resolution agent uses LangChain4j internally to decide which company registries to query and how to reason about the results. That's its job. CaseHub's job is different: it records that this agent was formally assigned the task, tracks whether it delivered its RESPONSE within the investigation SLA, updates its trust score based on whether the SAR it contributed to was upheld, and ensures the entire sequence is in an independently verifiable audit trail. LangChain4j makes the agent smart. CaseHub makes the agent accountable."

The AML tutorial is not "here are the 5 LangChain4j patterns expressed in CaseHub." It is "here is how a LangChain4j-powered agent operates as one accountable participant in a regulated multi-agent case managed by CaseHub." That is a stronger and more accurate story.

---

## 5. Spot and Technique Tutorials

Spot and technique tutorials are first-class artifacts — not entry points into a field
tutorial. A developer who reads one has everything they need for that concept. They do
not need to work through a field tutorial first or after.

**Design rules for spot tutorials:**
- Self-contained: one module, one concept, one runnable scenario
- Produces output in under 30 seconds
- No domain setup required — uses a synthetic or abstract scenario if needed
- Documents exactly what it teaches and what it does not cover

### Technique tutorials — how to use a specific API correctly

These answer: "what is the right way to call this?" Typically a short test or example
class demonstrating the API contract, common mistakes, and the correct form.

| Technique | What it teaches | Location |
|---|---|---|
| `MessageDispatch.builder()` protocol | Required fields per message type; builder validates at build() | qhorus normative-layout examples |
| `CommitmentStore` lifecycle queries | requester vs. obligor semantics; terminal state handling | qhorus testing module |
| `@DefaultBean` displacement | How CDI priority resolution works across module boundaries | AGENTIC-HARNESS-GUIDE.md §Anti-patterns |
| Flyway named-datasource scoping | Path scoping rule; qhorus vs. domain migration separation | parent protocols |
| `WorkItemRequest` with SLA | claimDeadline, candidateGroups, escalation chain | casehub-work examples |

### Approach tutorials — how to apply an architectural pattern

These answer: "when and why would I do it this way?" Typically a short walkthrough of
an architectural decision with the code that implements it.

| Approach | What it teaches | Location |
|---|---|---|
| Normative 3-channel layout | work/observe/oversight semantics; allowedTypes enforcement | qhorus normative-layout examples |
| Vertical slice planning | Identify slices, order by minimal delta, respect sequential deps | This doc §2.2 |
| Inner-SPI displacement pattern | How AML QhorusAmlInvestigator displaces DefaultAmlInvestigationService | AML LAYER-LOG Layer 3 |
| `@Alternative @Priority` for SPI overrides | Pattern B from alternative-extension-patterns.md | parent protocols |
| Content-driven binding conditions | JQ predicates on CaseContext; security flag triggers reviewer | devtown LAYER-LOG Layer 5 |

### Showcase tutorials — isolated demonstration of a platform capability

These answer: "what does this capability actually do?" Typically a runnable scenario
with self-narrating output that can be completed in one HTTP call or test run.

| Concept | What it shows | Modules needed | Analogy for Java devs |
|---|---|---|---|
| **Execution control types** | Sequential, parallel, conditional, loop, parallel mapper | casehub-engine | Different thread/executor patterns, but declarative |
| **Human-in-the-loop** | WorkItem with SLA, escalation, delegation | casehub-work | Typed task queue with lifecycle states and handoff |
| **Speech acts** | 9 message types and when to use each | casehub-qhorus (type-system examples) | Strongly typed method signatures between services |
| **Commitment lifecycle** | COMMAND creates obligation; DONE/DECLINE discharge it | casehub-qhorus (`SecureCodeReviewScenario`) | Futures with typed resolution and obligation tracking |
| **Trust scoring** | Bayesian Beta from outcomes; routing shifts over time | casehub-ledger (eigentrust-mesh, trust-routing) | Adaptive load balancer weighted by outcome history |
| **Tamper-evident audit** | Merkle chain, inclusion proofs, independent verification | casehub-ledger (merkle-verification) | Append-only event store with cryptographic proof |
| **GDPR compliance** | Art.17 erasure, Art.22 decision records | casehub-ledger (art22, privacy-pseudonymisation) | Structured logging that satisfies the regulation by construction |
| **Sub-case orchestration** | Parent case spawning and coordinating child cases | casehub-engine | Fork-join with independent lifecycle per branch |
| **LLM supervisor mode** | LLM reads state, selects next binding | casehub-engine (LlmPlanningStrategy) | Dynamic dispatch table driven by LLM reasoning |

---

## 6. AML Investigation — Reference Architecture for Financial Services

**Role:** Reference architecture demonstrating CaseHub for Java developers in financial services — banking, AML compliance, transaction monitoring, SAR filing. Production-grade, with potential for community adoption. Currently the furthest-along reference implementation (Layers 1–3 complete, Layers 4–7 in progress).

**Why this audience relates:** Java dominates banking infrastructure. AML compliance systems — transaction monitoring, case management, SAR filing — are systems Java developers in this field have built and integrated. They recognise the failure modes first-hand: audit trails that can't reconstruct the decision chain, human escalation that fires too late, SAR filings where nobody can say which agent made the call.

**Comparison baseline:** IBM AMLSim (open source, GitHub), industry whitepapers (AnChain, Sardine) — showing what current LLM-based AML coordination looks like without formal accountability.

### 6.0 Vertical slices

| Slice | Layers touched | Deliverable |
|---|---|---|
| 1 | 1 + 2 + 3 | Transaction flagged → specialist agents dispatched → compliance WorkItem created with 30-day SLA ✅ |
| 2 | + 4 | Slice 1 + tamper-evident ledger entry per investigation → FinCEN-verifiable audit trail |
| 3 | + 5 | Slice 2 + PEP detection triggers senior analyst binding (engine adaptive routing) |
| 4 | + 6 | Slice 3 + trust-weighted agent selection from SAR outcome attestations |

Slices 2–4 are ordered by sequential dependency: ledger before trust (trust reads attestation data written by ledger). Engine adaptive routing (Slice 3) is orthogonal to trust routing (Slice 4) but delivers more foundation value sooner.

### 6.1 Layer integration sequence

**Layer 1 — The business scenario alone (no CaseHub)**

Show the problem: a transaction is flagged. Multiple specialists need to investigate. A human must file a SAR. Without coordination infrastructure:

```java
// Domain baseline (no CaseHub): direct service calls
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

### 6.2 What each layer contributes — the AML split

The AML tutorial demonstrates why all three layers matter by showing what each one contributes:

**LangChain4j (inside the entity resolution agent):**
The entity resolution agent uses LangChain4j's tool-calling internally — it queries company registries, evaluates confidence, loops to search additional sources if confidence is below threshold, conditionally calls the PEP screening tool for offshore jurisdictions. This is LangChain4j's domain. CaseHub does not see or control this reasoning.

**Quarkus Flow (the entity resolution workflow step):**
The entity resolution step is a durable Quarkus Flow task — if the external registry API times out, the workflow retries with backoff. The result is structured into the format the case expects. This is the bounded, durable execution layer.

**CaseHub (the investigation case):**
CaseHub sees the entity resolution agent as a worker that was issued a COMMAND, committed to delivering a RESPONSE, did so within SLA (or didn't — triggering escalation), and whose result contributed to a SAR narrative that was either upheld or overturned. That outcome feeds the agent's trust score. The full investigation — multiple specialist agents, compliance officer WorkItem with 30-day FinCEN SLA, adaptive path on PEP detection — is CaseHub's domain.

The summary for the tutorial audience:

> "LangChain4j makes each agent smart. Quarkus Flow makes each step durable. CaseHub makes the investigation accountable."

That is three sentences covering three layers. A Java developer who has used Spring Batch (workflow), a domain library (reasoning), and an enterprise BPM tool (process orchestration) has already experienced all three concerns separately — CaseHub is what happens when all three are integrated with formal obligations, trust scoring, and regulatory audit."

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

## 7. Clinical Trial Coordination — Reference Architecture for Regulated Healthcare

**Role:** Reference architecture demonstrating CaseHub for Java developers in pharma, biotech, and clinical research organisations. GCP domain knowledge is a prerequisite for this audience — and it is standard knowledge for Java developers in that field. Production-grade; potential for adoption by organisations building compliant trial coordination systems.

**Comparison baseline:** ClinicalAgent ([arXiv 2404.14777](https://arxiv.org/abs/2404.14777), GitHub open source) — peer-reviewed (ACM BCB '24), showing exactly what naive LLM trial coordination looks like.

### 7.1 The compliance gap it closes

| GCP / ICH requirement | ClinicalAgent | CaseHub |
|---|---|---|
| Adverse event SLA (24h/7d) | No deadline tracking | WorkItem claimDeadline + auto-escalation |
| Protocol deviation authorisation | Agent decides autonomously | COMMAND from PI required; commitment lifecycle |
| Patient consent cascade (GDPR Art.17) | No GDPR capability | LedgerErasureService |
| Multi-site independence (50+ sites) | Single-case linear pipeline | Sub-case per site with trial-level rollup |
| Tamper-evident audit (FDA) | No audit trail | Merkle MMR + Ed25519-signed checkpoints |
| Trust-weighted safety agent routing | No trust model | Bayesian Beta from outcome attestations |

### 7.2 Layer integration sequence

**Layer 1 — Domain baseline (no CaseHub foundation)**

```java
// Domain baseline (no CaseHub): direct service calls
PatientEligibility eligibility = eligibilityService.screen(patient, protocol);
AdverseEventAssessment ae = safetyService.assess(adverseEvent);
// Who signed off on this eligibility decision?
// What if the safety assessor was unavailable?
// When did the PI actually review the protocol deviation?
// Can we prove to the FDA that the trial followed GCP?
```

**Layer 2 — casehub-work: formal human task with GCP SLA**

```java
// Adverse event: 24h SLA for serious events (GCP requirement)
WorkItemRequest adverseEventReview = WorkItemRequest.builder()
    .title("Grade 3 AE: Patient P-2024-007, Study ABC-001")
    .category("adverse-event-assessment")
    .candidateGroups("safety-monitors")
    .claimDeadline(Instant.now().plus(24, ChronoUnit.HOURS)) // GCP: serious AE within 24h
    .payload(adverseEvent.toJson())
    .build();
```

**Layer 3 — casehub-qhorus: typed agent communication**

```
[Trial Coordinator] COMMAND → Eligibility Agent: "Screen patient P-007 against Protocol v2.1"
[Eligibility Agent] RESPONSE → "12/14 criteria met; criteria 7 and 11 require PI waiver"
[Trial Coordinator] COMMAND → Protocol Deviation Agent: "Assess dosing schedule deviation"
[Protocol Deviation Agent] DECLINE → "Grade 3 AE flagged; PI authorisation required before assessment"
[Trial Coordinator] COMMAND → Safety Monitor: "Assess CTCAE Grade 3 event for patient P-007"
[Safety Monitor] STATUS → "Reviewing concurrent medications..."
[Safety Monitor] DONE → "Causally unrelated to protocol; continue dosing"
```

The DECLINE is not an error — it is a formal record that the agent correctly identified a protocol gate before acting.

**Layer 4 — casehub-ledger: FDA audit trail**

Every agent decision, every WorkItem transition, and every PI authorisation creates a `MessageLedgerEntry`. The Merkle chain means the FDA can verify the complete investigation record without accessing the server. GDPR Art.17: patient consent withdrawal erases PII from ledger entries while preserving anonymised trial data.

**Layer 5 — casehub-engine: adaptive protocol paths**

CTCAE Grade 3+ AE routes to senior safety monitor; Grade 4+ fires immediate DSMB escalation. IRB consultation gate suspends the case until approval (WAITING state, durable across restarts). LLM supervisor reads accumulated multi-site context to recommend protocol amendments.

**Layer 6 — Trust routing**

After 50 trial events, which safety monitor has the highest `safety-accuracy` score? Trust scores from `LedgerAttestation` records drive routing. Experienced safety monitors are automatically prioritised on CTCAE Grade 4+ events.

**Layer 7 — Comparison vs ClinicalAgent**

| Requirement | ClinicalAgent | CaseHub |
|---|---|---|
| Adverse event SLA enforcement | Not addressed | WorkItem claimDeadline |
| PI authorisation for deviations | Agent decides autonomously | COMMAND commitment lifecycle |
| GDPR consent withdrawal | Not applicable | LedgerErasureService |
| Multi-site independence | Single pipeline | Sub-case per site |
| FDA tamper-evident audit | Not addressed | Merkle MMR |
| Trust-weighted safety routing | Not addressed | EigenTrust from attestation history |

### 7.3 Engine issue #102 patterns covered

| Issue | Pattern | Clinical expression |
|---|---|---|
| #101 | LLM Supervisor Mode | Protocol amendment analysis — LLM reads accumulated case data to select next assessment |
| #108 | Long-Running Case Management | Trials run months to years — durable case state, WAITING across protocol review periods |
| #110 | Goal Decomposition | Trial objectives decompose into: recruitment, dosing, safety monitoring, endpoint analysis |
| #112 | Sub-Case Orchestration | Per-site sub-cases with independent investigator teams, rollup to trial-level status |
| #113 | Regulatory Decision Automation | FDA submission with traceable reasoning per protocol decision |
| #115 | Human Escalation | IRB/ethics committee approval gates with formal SLA |
| #116 | Compliance and Audit Workflows | GCP, FDA IND, EMA CTR, GDPR all enforced by platform construction |

### 7.4 Showcase scenario

A 3-site oncology trial. Site A: agents run eligibility screening across 12 criteria; a marginal criterion triggers an IRB consultation (WorkItem: 72-hour SLA). Site B: a CTCAE Grade 3 adverse event fires automatic 24-hour safety escalation. Site C: a protocol amendment is proposed — the LLM supervisor reads accumulated context from all three sites and recommends whether to proceed. The Merkle audit trail means FDA can independently verify the complete decision chain for every patient at every site.

ClinicalAgent runs as a linear pipeline for one site. It has no concept of SLA, no IRB gate, no adverse event escalation, and no audit trail.

---

## 7.5 PR Review Orchestration — Reference Architecture for Software Engineering Coordination

**Role:** Reference architecture demonstrating CaseHub for Java developers in software engineering and DevOps — a domain every Java developer knows from their own daily practice. Shows the gap between naive AI code review and a system where every specialist reviewer is formally accountable, every missed finding is traceable, and routing improves from outcome history. Production-grade; potential for adoption by engineering teams.

**Comparison baseline:** GitHub Copilot code review, CodeRabbit — showing what LLM-based review looks like without formal accountability or adaptive routing.

### 7.5.0 Vertical slices

| Slice | Layers touched | Deliverable |
|---|---|---|
| 1 | 1 + 5 | PR submitted → CasePlanModel opens → content-driven routing fires → outcome returned ✅ |
| 2 | + 2 | Slice 1 + human review WorkItem with SLA; breach escalation ✅ |
| 3 | + 3 | Slice 2 + typed COMMAND per specialist agent; DECLINE is formal scope boundary |
| 4 | + 4 | Slice 3 + tamper-evident ledger entry per case; causedByEntryId links findings to actions |
| 5 | + 6 | Slice 4 + trust-weighted specialist selection from post-merge outcome attestations |

Slices 1 and 2 are complete. Slices were built out of reading-order (Layer 5 before
Layers 2–4) because engine adaptive routing was the architectural priority — this is
correct vertical slice practice and is captured in LAYER-LOG.md.

Slices 3–5 are ordered by sequential dependency: ledger (Slice 4) before trust (Slice 5),
since trust scoring reads attestation data written by ledger. Slice 3 (qhorus) has no
hard dependency but delivers the obligation lifecycle teaching that makes Slice 4's
audit trail meaningful.

### 7.5.1 Layer integration sequence

**Layer 1 — Domain baseline (no CaseHub foundation)**

```java
// Domain baseline (no CaseHub): direct service calls
SecurityAnalysis security = securityAnalyzer.analyze(pr);
ArchitectureReview arch = architectureReviewer.review(pr);
String comment = commentService.post(pr, security, arch);
// Who was responsible for the missed SQL injection?
// What if the security reviewer was unavailable?
// When did the reviewer actually look at this code?
// Can we trace the production incident back to this review?
```

**Layer 2 — casehub-work: PR review WorkItem with SLA**

```java
// Security review with response SLA
WorkItemRequest reviewRequest = WorkItemRequest.builder()
    .title("PR #456: Add payment processing endpoint")
    .category("security-review")
    .candidateGroups("security-reviewers")
    .claimDeadline(Instant.now().plus(4, ChronoUnit.HOURS)) // 4h SLA for security reviews
    .payload(pr.toJson())
    .build();
```

**Layer 3 — casehub-qhorus: typed COMMAND to specialist reviewers**

```
[PR Orchestrator] COMMAND → Security Agent: "Review authentication handling in PaymentController"
[Security Agent] RESPONSE → "No SQL injection; rate limiting absent on /payment endpoint"
[PR Orchestrator] COMMAND → Architecture Agent: "Review transaction boundary in PaymentService"
[Architecture Agent] DECLINE → "Distributed transaction pattern outside my scope; route to senior architect"
[PR Orchestrator] COMMAND → Test Coverage Agent: "Assess coverage for payment flow"
[Test Coverage Agent] DONE → "Coverage at 67%; payment failure path untested"
```

The DECLINE is not an error — it is a formal record that the agent correctly identified a scope boundary. The review continues; a senior architect is routed the binding concern.

**Implementation note for Claude:** Follow the AML reference implementation (`casehub-aml` Layer 3,
`QhorusAmlInvestigator`). The pattern is: a non-`@DefaultBean @ApplicationScoped` inner-SPI
implementation that dispatches typed COMMAND messages and handles DONE/DECLINE/FAILURE replies
— injected by an outer coordinator that is already wired in from Layer 2. Do NOT build a
separate `PrReviewApplicationService` implementation at Layer 3. The port interface
displacement for this layer happens at the inner specialist-dispatch level (follow AML),
not at the outer use-case port. Adding `@Alternative @Priority(N)` to any existing class, or
`@Unremovable` to a new class, is a signal that you are building tutorial scaffolding
rather than production code — stop and redesign.

**Layer 4 — casehub-ledger: tamper-evident review record**

Every review decision is in the ledger with `causedByEntryId` linking findings to actions. When a production security incident is traced to a merged PR, the ledger answers: who reviewed it, what did they find, what did they miss, and what was their trust score at the time.

**Layer 5 — casehub-engine: adaptive review routing**

Security flag in code analysis triggers security reviewer binding. Large architectural refactor triggers senior architect binding. LLM supervisor reads accumulated PR context (file types, change size, historical incident patterns) and selects the next binding dynamically.

**Layer 6 — Trust routing**

Security reviewers with improving `false-positive-rate` scores get routed more sensitive PRs. Post-merge production incidents trigger a FLAGGED attestation, updating trust scores automatically. Routing shifts over time without manual configuration.

**Layer 7 — Comparison vs direct AI code review**

| Requirement | GitHub Copilot / CodeRabbit | CaseHub devtown |
|---|---|---|
| Formal accountability per reviewer | Not addressed | COMMAND commitment lifecycle |
| Reviewer response SLA | Not addressed | WorkItem claimDeadline |
| DECLINE when outside expertise | Not addressed | Formal scope boundary, re-routed |
| Trace production incident to missed finding | Not addressed | causedByEntryId chain |
| Trust-weighted routing | Not addressed | EigenTrust from outcome attestations |
| Adaptive routing on code content | Static rules | Engine binding conditions on case context |

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

### 8.2 Relationship to LangChain4j patterns

Developers coming from LangChain4j will recognise the names but the execution model is fundamentally different. These are not "CaseHub's version of LangChain4j patterns" — they are how CaseHub's binding system works naturally. The comparison is useful for orientation, not for equivalence:

| LangChain4j "pattern" | CaseHub reality | Why different |
|---|---|---|
| Sequential chain | Binding chain — A's output satisfies B's condition | Not a pattern: it's the default. No explicit sequencing declaration. |
| Agent loop | LoopControl.select() with full CaseContext | CaseHub's loop is durable — survives restarts, spans transactions |
| Parallel | All matching bindings fire on one state change | Not a pattern: automatic. CaseHub evaluates all bindings simultaneously by default. |
| Parallel mapper | Sub-case orchestration — each item gets full lifecycle | CaseHub sub-cases have SLA, compliance, and commitment tracking. LangChain4j parallel map has none of this. |
| Conditional | JQ predicate on accumulated case state | Not a pattern: every binding has a condition. It's the most basic CaseHub concept. |

The showcase's goal is not to teach "CaseHub's version of LangChain4j." It is to show that the execution control capabilities developers associate with LangChain4j emerge naturally from CaseHub's binding model — with significantly more power (durability, audit, SLA) and without explicit declaration. A developer who reaches for LangChain4j for coordination is solving the problem at the wrong layer.

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

### Phase 2 — AML Reference Architecture (financial services)

- [x] Layer 1: domain baseline (no CaseHub)
- [x] Layer 2: + casehub-work (compliance officer WorkItem with 30-day FinCEN SLA)
- [ ] Layer 3: + casehub-qhorus (typed agent communication)
- [ ] Layer 4: + casehub-ledger (FinCEN audit trail)
- [ ] Layer 5: + casehub-engine (adaptive investigation path)
- [ ] Layer 6: trust routing from SAR outcome attestations
- [ ] Layer 7: comparison table vs IBM AMLSim and industry whitepapers
- [ ] Blocked on: engine P1.3 for Layers 5–6

### Phase 3 — LangChain4j Pattern Examples (after issue #209)

- [ ] Sequential, loop, parallel, parallel mapper, conditional — each as a standalone example in casehub-engine
- [ ] Mapping table: LangChain4j pattern → CaseHub expression → AML scenario
- [ ] Covers engine issue #102 children: #101, #107, #112, #113, #114, #115, #116

### Phase 3b — Devtown Reference Architecture (software engineering coordination)

- [ ] Layer 1: domain baseline (no CaseHub)
- [ ] Layer 2: + casehub-work (PR review WorkItem with SLA)
- [ ] Layer 3: + casehub-qhorus (typed COMMAND to specialist reviewers)
- [ ] Layer 4: + casehub-ledger (tamper-evident review record)
- [ ] Layer 5: + casehub-engine (adaptive routing on code content)
- [ ] Layer 6: trust routing from post-merge outcome attestations
- [ ] Layer 7: comparison table vs GitHub Copilot code review, CodeRabbit

### Phase 4 — Clinical Reference Architecture (regulated healthcare)

- [ ] Layer 1: domain baseline (no CaseHub)
- [ ] Layer 2: + casehub-work (adverse event WorkItem with 24h GCP SLA)
- [ ] Layer 3: + casehub-qhorus (typed COMMAND to PI, DECLINE on scope boundary)
- [ ] Layer 4: + casehub-ledger (FDA Merkle audit, GDPR Art.17 consent withdrawal)
- [ ] Layer 5: + casehub-engine (adaptive paths: CTCAE grade routing, IRB gate)
- [ ] Layer 6: trust routing from safety agent outcome attestations
- [ ] Layer 7: comparison table vs ClinicalAgent (arXiv 2404.14777)
- [ ] 3-site oncology showcase scenario

---

## 11. Decisions and Rationale

| Decision | Rationale |
|---|---|
| AML as field tutorial for Java developers in financial services, not security incident response | Java developers in banking know AML from their careers — no domain onboarding needed. Security incident response (MyAntFarm comparison) is strong on community fit but weak on market entry gap (SOAR is a crowded incumbent market). |
| AML, clinical, and devtown are reference architectures | GCP domain knowledge is a prerequisite for clinical — but standard for Java developers in pharma/biotech. Code review orchestration is standard for any Java developer. Each reference architecture targets practitioners who already have domain knowledge. Tutorial value is a byproduct of the architectural record, not a design goal. |
| Production-first: tutorial structure emerges from the integration sequence | Designing for the tutorial produces tutorial code. Designing for production and documenting the progressive integration sequence produces production code that teaches. The only tutorial-specific element is the Layer 1 domain baseline. |
| Execution control showcase separate from domain tutorials | A developer evaluating CaseHub's binding model should not need to understand AML. Separate entry points for separate purposes. |
| Examples in each project repo, not a separate tutorials repo | Examples run in CI. They are tested code. Separating them from the project creates drift. |
| Layer-by-layer structure over "start with the full stack" | The standalone value of each module is the argument for integration. A developer who adds ledger to an existing work deployment should see ledger demonstrated standalone first. |
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
