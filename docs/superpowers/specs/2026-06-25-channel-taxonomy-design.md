# Channel Taxonomy Formalisation — Design Spec

**Issue:** parent#293
**Date:** 2026-06-25
**Status:** Draft

---

## 1. Goal

Rewrite `docs/CHANNELS.md` as a complete design reference for the CaseHub channel
taxonomy. The document serves two audiences: platform developers extending the
channel system, and third-party application builders choosing which channel
patterns to use.

### Deliverables

1. Updated `docs/CHANNELS.md` — the authoritative channel taxonomy
2. `docs/PLATFORM.md` fixes — three inconsistencies surfaced during review:
   - `/observe` speech acts listed as "EVENT, QUERY, STATUS" (line 571) — code is EVENT only
     (confirmed by `NormativeChannelLayout` and agent-mesh-primitives spec PP-20260604-a7ad99)
   - `/work` speech acts include "EXPIRED" (line 570) — EXPIRED is a `CommitmentState` /
     `WorkItem` status, not a `MessageType`
   - Known Placement Violations (line 617) still lists `CaseChannelLayout` in `claudony-casehub`
     — extraction to `casehub-engine-api` shipped in parent#93; Capability Ownership table
     (line 394) already reflects the correct location
   - `docs/repos/casehub-qhorus.md` Normative Channel Layout table: same /observe and /work
     corrections (EVENT only for /observe, remove EXPIRED from /work)
3. No code changes — this is a design/documentation issue

### Current doc issues (CHANNELS.md)

The existing `docs/CHANNELS.md` contains several errors that the rewrite corrects:

- `/work` allowedTypes listed as "COMMAND, RESPONSE, DONE, DECLINE" — code is null (unrestricted)
- INFORM listed as a message type — not a qhorus `MessageType` value
- CaseChannelLayout described as "Current home: claudony-casehub" — already extracted to
  `casehub-engine-api` (parent#93)
- Discriminator table lists "governance" as a separate purpose value — folded into coordination
  (see §4 rationale)

### Out of Scope

- Extracting a `DeliberationChannelBackend` interface (premature — only two examples)
- Adding a `ChannelPurpose` enum to qhorus-api (no programmatic discovery need yet)
- Implementing the open patterns (separate issues per pattern)

---

## 2. Document Structure

The rewritten CHANNELS.md has seven sections:

1. **Preamble** — what channels are, the layered protocol stack
2. **Speech Act Foundation** — FIPA lineage and the 22→9 reduction
3. **Channel Taxonomy** — five purpose categories with all patterns classified
4. **Discriminator Dimensions** — eight dimensions including ChannelSemantic and FIPA protocol
5. **Purpose × Semantic Matrix** — recommended combinations
6. **FIPA Interaction Protocol Cross-Reference** — each pattern mapped to nearest FIPA protocol
7. **Open Design Space** — landing zone for future channel patterns not yet classified;
     currently empty after promotion of negotiation/consensus/planning and dismissal of
     audit trail and broadcast as cross-cutting concerns

---

## 3. Speech Act Foundation

Qhorus `MessageType` is a deliberate reduction of FIPA ACL's 22 communicative acts
to 9 speech acts. The design rationale: concerns that FIPA handled as speech acts
belong in different layers of CaseHub's stack — infrastructure (propagate), engine
orchestration (cancel, request-when, subscribe), or error handling (not-understood).

### 22→9 Mapping

**Merged into qhorus (14 FIPA acts → 9 MessageTypes):**

| MessageType | FIPA acts absorbed | How |
|---|---|---|
| COMMAND | request, cfp | A call-for-proposal is a type of command |
| QUERY | query-if, query-ref | Merged — both ask for information |
| RESPONSE | inform, confirm, propose, inform-if, inform-ref | All deliver information/judgment |
| DECLINE | refuse, reject-proposal | Both reject an obligation or offer |
| DONE | accept-proposal | Both signal positive resolution of an exchange (see note below) |
| FAILURE | failure | Direct 1:1 |
| HANDOFF | proxy | Transfer obligation to another agent |
| STATUS | *(carved from inform)* | New — progress reports distinguished from terminal responses |
| EVENT | *(no FIPA equivalent)* | New — observer-only telemetry, not a speech act |

**DONE ← accept-proposal note:** In FIPA, accept-proposal occurs *before* work begins
(accepting an offer kicks off execution). DONE occurs *after* work completes. These are
at opposite lifecycle points. Both signal positive resolution, but CaseHub's negotiation
flow, when implemented (§4.2c), handles accept-proposal semantics at the channel pattern
level rather than the speech-act level.

**disconfirm note:** FIPA disconfirm is an informational act ("I know that proposition P
is false") — about truth, not refusal. CaseHub doesn't need a separate "that's false"
speech act; RESPONSE with disagreeing content covers the ground. disconfirm is not mapped
to DECLINE (which handles refusal); it is simply not needed as a distinct speech act.

**Dropped entirely (8 FIPA acts):**

| FIPA act | Why dropped | CaseHub layer that handles it |
|---|---|---|
| agree | Implicit — starting work signals acceptance | Engine (worker dispatch) |
| cancel | Case lifecycle, not agent discourse | Engine (case state machine) |
| disconfirm | Informational — "P is false"; RESPONSE covers disagreement | Not needed as distinct act |
| not-understood | Error handling, not communication | Qhorus (exceptions) |
| propagate | Infrastructure fan-out | Claudony (fleet relay) |
| request-when | Reactive triggers | Engine (CDI events, signal bridge) |
| request-whenever | Reactive triggers | Engine (CDI events, signal bridge) |
| subscribe | Structural membership, not negotiated | Engine (CaseChannelLayout) |

---

## 4. Channel Taxonomy

Five purpose categories. Each pattern carries discriminator values, recommended
ChannelSemantic, MessageType constraints, and FIPA cross-reference.

**Design decision: governance folded into coordination.** The existing CHANNELS.md
lists governance as a sixth purpose value. This spec removes it. At the speech-act
level, governance IS coordination — the oversight channel uses the same obligation
exchange pattern (COMMAND → RESPONSE) as the work channel. The distinction is in
participants (human↔engine vs agent↔engine) and type constraints (deniedTypes=EVENT),
not in the fundamental communication pattern. Consensus (§4.1c) generalises
oversight to M-of-N, further confirming that governance is a coordination sub-pattern.

### 4.1 Coordination Channels — obligation exchange

Channels where one party commands and another responds with completion or refusal.
The fundamental pattern is obligation creation and fulfilment.

#### 4.1a Agent Mesh (work/observe/oversight)

The normative 3-channel layout for any agent participating in the CaseHub mesh.
Declared by `CaseChannelLayout` SPI, `allowedTypes` enforced at the Qhorus layer.

- **Implementations:** `NormativeChannelLayout` (3-channel), `SimpleLayout` (2-channel, no oversight)
- **Home:** `casehub-engine-api` (`io.casehub.api.spi.mesh`)
- **Semantic:** APPEND
- **FIPA:** Request (work, oversight), Subscribe (observe)

`MeshParticipationStrategy` is the companion SPI — ACTIVE, REACTIVE, or SILENT
engagement determines which channels surface in the agent's context.

| Channel | Purpose | allowedTypes | deniedTypes |
|---------|---------|-------------|-------------|
| /work | Obligation-carrying coordination | null (open) | null |
| /observe | Telemetry broadcast | EVENT only | null |
| /oversight | Human governance gate | null (open) | EVENT |

#### 4.1b Ad-hoc Engine Channels

Channels opened on-demand at specific engine lifecycle points, outside the
mesh layout topology.

- **"coordination"** — opened at case start for initial coordination
- **"worker:{name}"** — per-worker command dispatch channel
- **Home:** `casehub-engine` runtime (CaseStartedEventHandler, WorkerScheduleEventHandler)
- **Semantic:** APPEND
- **FIPA:** Request

#### 4.1c Consensus Gate (open — not yet implemented)

M-of-N independent votes collected until a threshold is met. No discourse —
each participant makes an independent judgment. Generalises oversight from
single-human to multi-party.

- **Semantic:** APPEND (votes accumulate; threshold evaluation in the backend/projection).
  Alternative: BARRIER for the N-of-N special case (unanimous — all must write).
  BARRIER is wrong for general M-of-N: it requires ALL contributors, not M-of-N.
  COLLECT clears after delivery, losing vote history. Threshold logic belongs in the
  `ConsensusChannelBackend`, not the transport semantic — `ChannelSemantic` describes
  data flow, not application-level decision logic.
- **Turn structure:** one-way per participant (vote), threshold-gated release
- **Lifecycle:** gated — opens, collects, releases on threshold, closes
- **Participants:** M-of-N (human, agent, or mixed)
- **FIPA:** Multi-party Propose (no direct FIPA equivalent for threshold semantics)
- **First likely consumer:** clinical DSMB approval, multi-agent oversight gates

**Probable ChannelBackend shape:**

```
ConsensusChannelBackend implements ChannelBackend
  - threshold: int (M required out of N contributors)
  - contributors: Set<String> (declared participants)
  - post(): validates contributor identity, records vote
  - Projects via ConsensusProjection → ConsensusState
    - votes: Map<String, Vote> (contributor → accept/reject + rationale)
    - threshold: int
    - met: boolean
    - outcome: PENDING | APPROVED | REJECTED

On threshold met → fires CDI event (ConsensusReachedEvent)
  - caseId, channelId, outcome, votes
  - Engine signal bridge routes to case context
```

### 4.2 Deliberation Channels — structured discourse

Channels for multi-participant reasoning toward a shared conclusion.
Not about task coordination — about reaching a conclusion through discourse.

**Shared structural pattern** (documented, not extracted as code): all deliberation
channels implement Qhorus `ChannelBackend` directly, use `ChannelProjection<S>` to
fold message history into a typed state, and are activated by `ChannelInitialisedEvent`
observation. Future deliberation channels follow this pattern with their own state types.

**Projection variant:** `RenderableProjection<S>` (extends `ChannelProjection<S>`)
adds `projectionName()` and `render()` — making the projection available as an MCP tool
via `ProjectionRegistry` and `project_channel`. `DebateChannelProjection` implements
`RenderableProjection<ReviewState>` (MCP-visible). `ReviewChannelProjection` implements
plain `ChannelProjection<ReviewState>` (renders via `ReviewConversationRenderer` directly,
not through the MCP tool path). Deliberation channels that need LLM-readable output via
MCP should implement `RenderableProjection`.

#### 4.2a Debate — multi-agent, multi-turn, document-scoped

- **Home:** `casehub-drafthouse`
- **Naming:** `drafthouse/debate/d-{UUID}`
- **Participants:** REV, IMP, SUPERVISOR, MODERATOR, SELECTOR roles
- **Turn structure:** round-based, explicit round numbers
- **Entry types:** RAISE, AGREE, COUNTER, DISPUTE, QUALIFY, FLAG_HUMAN, DECLINED,
  MEMO, SUB_TASK_REQUEST, SUB_TASK_FINDING, SUB_TASK_ERROR, RESTART_CONTEXT
- **Constraint enforcement:** protocol-layer (DebateProtocol.META_SENTINEL), not Qhorus allowedTypes
- **State:** folds into `ReviewState` via `DebateChannelProjection`
- **Semantic:** APPEND
- **FIPA:** No equivalent — closest ancestor is argumentation frameworks (Dung 1995)

#### 4.2b Review — single reviewer, reactive, document-scoped

- **Home:** `casehub-drafthouse`
- **Participants:** one human, one LLM reviewer (auto-responds via `ReviewerChannelBackend`)
- **Turn structure:** reactive — LLM auto-invoked on QUERY
- **State:** folds into `ReviewState` via `ReviewChannelProjection`
- **Semantic:** APPEND
- **FIPA:** Query (QUERY → analysis → RESPONSE, but with judgment semantics)

#### 4.2c Negotiation (open — not yet implemented)

Two or more agents reaching agreement through proposal/counter-proposal exchange.
Iterative — proposals are refined until convergence or deadlock.

- **Semantic:** APPEND. Alternative: COLLECT (fan-in proposals before evaluation).
- **Turn structure:** proposal/counter-proposal, iterative
- **Lifecycle:** session-scoped (open negotiation → agreement or deadlock → close)
- **Participants:** agent↔agent or agent↔human
- **FIPA:** Contract Net / Iterated Contract Net — structurally equivalent message flow

**Probable ChannelBackend shape:**

```
NegotiationChannelBackend implements ChannelBackend
  - post(): records proposal, counter-proposal, accept, reject
  - Projects via NegotiationProjection → NegotiationState
    - proposals: List<Proposal> (proposer, terms, round)
    - currentRound: int
    - status: OPEN | AGREED | DEADLOCKED | EXPIRED
    - agreement: Terms (null until AGREED)

On agreement → fires CDI event (NegotiationCompletedEvent)
  - participants, agreed terms, round count
  - Output feeds into coordination channels (task assignments)
```

#### 4.2d Planning (open — not yet implemented)

Structured decomposition of a goal into an ordered task graph through discourse.
A supervisor proposes a breakdown, participants critique or refine, the group
converges on a plan. Output feeds into coordination channels.

- **Semantic:** APPEND
- **Turn structure:** proposal/critique, iterative
- **Lifecycle:** session-scoped (goal stated → plan converged → close)
- **Participants:** supervisor + contributing agents
- **FIPA:** No single protocol — combines Contract Net (propose/critique)
  with Request-When (trigger on goal)

**Probable ChannelBackend shape:**

```
PlanningChannelBackend implements ChannelBackend
  - post(): records goal, decomposition, critique, refinement
  - Projects via PlanningProjection → PlanState
    - goal: String
    - tasks: List<PlannedTask> (description, dependencies, assignee, status)
    - critiques: List<Critique> (taskRef, agent, concern, resolution)
    - status: DECOMPOSING | UNDER_REVIEW | CONVERGED | ABANDONED

On convergence → fires CDI event (PlanConvergedEvent)
  - goal, finalised task graph
  - Engine creates WorkItems from the task graph
```

#### Patterns promoted from Open Design Space

Negotiation (→ 4.2c), Consensus (→ 4.1c), and Planning (→ 4.2d) were previously
listed as open/unclassified. This spec classifies them within the taxonomy with
API sketches. The two remaining items from the original Open Design Space —
audit trail and broadcast — were evaluated and dismissed as cross-cutting
concerns, not distinct channel patterns:

- **Audit trail** — append-only channel as tamper-evident decision record. Already
  approximated by Qhorus message history + ledger integration. Not a distinct channel
  type — it's a property of any APPEND-semantic channel when combined with ledger
  capture. No separate pattern needed.
- **Broadcast** — platform-wide event fan-out to all interested consumers. Already
  implemented by casehub-ras (situational awareness via `@ObservesAsync CloudEvent`).
  Sits at the notification/infrastructure boundary. Not a distinct channel type — it's
  the CDI event bus, not a Qhorus channel.

The Open Design Space is now empty — all original items are either classified or
dismissed.

### 4.3 Signal Channels — case state mutation

One-way state-change notifications into running case instances.

- **Home:** Three entry points across two repos:
  - `CaseSignalSink` — SPI in `casehub-work-api`; called by casehub-work on SLA
    escalation; impl in `casehub-engine-work-adapter` calling `CaseHubRuntime.signal()`
  - `QhorusMessageSignalBridge` — in `casehub-engine` runtime; observes
    `@ObservesAsync MessageReceivedEvent` for commitment-resolving message types
  - Direct REST → `CaseHubRuntime.signal()` — in `casehub-engine` runtime
- **Direction:** external event → case context mutation
- **Turn structure:** one-way, no response expected
- **Semantic:** EPHEMERAL
- **FIPA:** Inform (but qhorus signals mutate case context directly — tighter
  coupling than FIPA's mentalistic semantics)

### 4.4 Notification Channels — external boundary

Channels bridging external systems into the platform (inbound) or the platform
out to external systems (outbound).

- **Home:** `casehub-connectors` (outbound delivery), `casehub-qhorus` `connector-backend`
  submodule (inbound bridge)
- **Semantic:** APPEND (persistent record). Alternative: EPHEMERAL (fire-and-forget).
- **FIPA:** No equivalent — FIPA assumed a closed agent ecosystem

**ChannelBackend SPI hierarchy matters here.** Notification channels implement
`HumanParticipatingChannelBackend` (extends `ChannelBackend`), not plain `ChannelBackend`.
This adds `normaliserFor(UUID channelId)` — per-channel inbound type inference that
converts raw human prose into typed `NormalisedMessage`. The qhorus backend SPI hierarchy:

```
ChannelBackend (base — backendId, actorType, open, post, close)
├── AgentChannelBackend (ActorType.AGENT; post() fatal on failure)
├── HumanObserverChannelBackend (ActorType.HUMAN; inbound capped to EVENT; unlimited per channel)
└── HumanParticipatingChannelBackend (ActorType.HUMAN; full speech acts; normaliserFor())
```

`ConnectorChannelBackend` and `SlackChannelBackend` both implement
`HumanParticipatingChannelBackend`. A new notification adapter (e.g., Discord)
plugs into the `connector-backend` submodule, implementing
`HumanParticipatingChannelBackend` — not core qhorus, and not plain `ChannelBackend`.

Examples:
- Slack webhook → InboundMessage → ConnectorChannelBackend → case signal
- Watchdog alert → WatchdogAlertEvent → ConnectorService.send()
- CloudEvent from casehub-iot / casehub-qhorus / casehub-connectors → casehub-ras

### 4.5 Infrastructure Channels — platform plumbing

Channels used internally for platform coordination, not visible to domain agents.

- **Fleet relay (claudony):** cross-node SSE tick delivery via FleetMessageRelayObserver
- **Channel sync (claudony):** POST /sync registers ClaudonyChannelBackend;
  POST /notify relays cross-node ticks
- **Semantic:** APPEND or EPHEMERAL depending on relay pattern
- **FIPA:** No equivalent — deployment concerns outside FIPA's scope

---

## 5. Discriminator Dimensions

Eight dimensions for classifying any channel pattern:

| Dimension | Values |
|-----------|--------|
| **Purpose** | coordination · deliberation · signal · notification · infrastructure |
| **Semantic** | APPEND · COLLECT · BARRIER · EPHEMERAL · LAST_WRITE |
| **Participants** | agent↔agent · human↔agent · agent→broadcast · system · M-of-N |
| **Turn structure** | unstructured · round-based · reactive · one-way · proposal/counter |
| **Constraint enforcement** | Qhorus allowedTypes · Qhorus deniedTypes · protocol-layer · none |
| **Lifecycle** | long-lived (task) · session-scoped (debate) · ephemeral (signal) · gated (consensus) |
| **Initiation** | COMMAND on /work · MCP tool · CDI event · external webhook · engine lifecycle |
| **FIPA protocol** | Request · Contract Net · Propose · Subscribe · Query · — (no equivalent) |

---

## 6. Purpose × Semantic Matrix

Recommended ChannelSemantic for each channel pattern. **Bold** = primary
recommendation. (parentheses) = viable alternative.

| Channel Pattern | APPEND | COLLECT | BARRIER | EPHEMERAL | LAST_WRITE |
|----------------|--------|---------|---------|-----------|------------|
| 1a. Agent Mesh (work) | **✓** | | | | |
| 1a. Agent Mesh (observe) | **✓** | | | | |
| 1a. Agent Mesh (oversight) | **✓** | | | | |
| 1b. Ad-hoc Engine | **✓** | | | | |
| 1c. Consensus Gate | **✓** | | (✓) | | |
| 2a. Debate | **✓** | | | | |
| 2b. Review | **✓** | | | | |
| 2c. Negotiation | **✓** | (✓) | | | |
| 2d. Planning | **✓** | | | | |
| 3. Signal | | | | **✓** | |
| 4. Notification | **✓** | | | (✓) | |
| 5. Infrastructure | **✓** | | | (✓) | |

APPEND dominates — most conversation patterns accumulate history, and threshold
logic belongs in the application layer (backend/projection), not the transport
semantic. BARRIER is the N-of-N special case (unanimous consensus only). COLLECT
is an alternative for fan-in patterns but clears after delivery. LAST_WRITE has
no current primary use but is available for future blackboard-cell patterns.

---

## 7. FIPA Interaction Protocol Cross-Reference

| Channel Pattern | FIPA Protocol | Mapping | Divergence |
|----------------|---------------|---------|------------|
| 1a. Mesh /work | Request | COMMAND → agent → DONE/FAILURE/DECLINE | No explicit AGREE — acceptance implicit in starting work |
| 1a. Mesh /observe | Subscribe | EVENT broadcast to observers | Membership is structural (layout), not negotiated |
| 1a. Mesh /oversight | Request | COMMAND from engine → human → RESPONSE | FIPA doesn't distinguish human vs agent participants |
| 1b. Ad-hoc Engine | Request | Engine → worker dispatch | Ephemeral — opened per worker, not pre-declared |
| 1c. Consensus Gate | Propose (multi-party) | Independent accept/reject against threshold | No FIPA equivalent for M-of-N threshold semantics |
| 2a. Debate | — | No FIPA equivalent | Closest ancestor: argumentation frameworks (Dung 1995) |
| 2b. Review | Query | QUERY → analysis → RESPONSE | Reactive auto-invocation has no FIPA precedent |
| 2c. Negotiation | Contract Net | CFP → propose → accept/reject → iterate | Agent-to-agent vs FIPA's manager-to-contractors |
| 2d. Planning | — | No single FIPA protocol | Combines Contract Net + Request-When |
| 3. Signal | Inform | One-way state notification | Mutates case context directly — tighter than FIPA |
| 4. Notification | — | External boundary crossing | Outside FIPA's closed-ecosystem assumption |
| 5. Infrastructure | — | Platform plumbing | Outside FIPA's agent-layer scope |

CaseHub inherits from FIPA where patterns match (Request, Contract Net, Subscribe)
and diverges in three ways: (1) speech acts reduced to 9 from 22 — 14 merged, 8 dropped,
(2) purpose-based channel
classification is a layer FIPA doesn't have, (3) infrastructure and notification
categories address deployment realities FIPA never targeted.

---

## 8. The Layered Protocol Stack

Sander et al. (2026) predict that the agent protocol ecosystem will converge toward
federated, layered protocol stacks rather than monolithic standards. CaseHub's internal
architecture — separating transport semantics, orchestration topology, and application-domain
concerns — demonstrates this principle at the intra-platform level. The layers don't
correspond (Sander's stack is L1-Identity through L5-Deliberation across *protocol standards*;
CaseHub's is internal *architectural* layering), but both independently arrive at layered
separation of concerns for agent communication.

| Layer | Component | Owns |
|-------|-----------|------|
| **Transport + Semantics** | Qhorus | MessageType (speech acts), ChannelSemantic (data flow), allowedTypes/deniedTypes enforcement, ChannelBackend SPI, commitment lifecycle |
| **Orchestration + Layout** | Engine | CaseChannelLayout (topology), MeshParticipationStrategy (engagement), CaseChannelProvider (backend-agnostic ops), QhorusMessageSignalBridge (signal routing) |
| **Application + Domain** | Drafthouse, future apps | DebateChannelBackend, ReviewerChannelBackend, domain-specific projections, entry type systems |

**Architectural invariant:** each layer depends only downward. Drafthouse implements
Qhorus ChannelBackend — it doesn't know about engine's CaseChannelLayout. Engine
declares topology via Qhorus primitives — it doesn't know about drafthouse's ReviewState.

**Where new channel patterns plug in:**

- New **coordination** pattern (e.g., consensus gate) → engine layer, uses Qhorus APPEND semantic
  (threshold logic in the backend, not the transport layer)
- New **deliberation** pattern (e.g., negotiation) → application layer as a ChannelBackend,
  follows the drafthouse structural pattern (backend + projection + state type)
- New **notification** adapter (e.g., Discord) → `connector-backend` submodule, implementing
  `HumanParticipatingChannelBackend` (not core Qhorus — the SPI is in qhorus-api, but the
  adapter plugs into the separately-deployable connector-backend module)

---

## 9. Academic Lineage

The channel taxonomy draws on established multi-agent systems research:

- **FIPA ACL** (IEEE SC00037J, 2002) — 22 communicative acts based on speech act theory.
  Qhorus reduces to 9, relocating infrastructure, orchestration, and error-handling
  concerns to their appropriate stack layers.
- **Speech Act Theory** (Austin 1962, Searle 1969) — performatives as actions, not just
  information transfer. Qhorus MessageType values are performatives.
- **Contract Net Protocol** (Smith 1980) — task allocation via CFP/propose/accept. Maps
  directly to the negotiation channel pattern.
- **Argumentation Frameworks** (Dung 1995) — structured multi-party reasoning. Ancestor
  of the debate channel pattern.
- **Communication-Centric Survey** (Yan et al. 2025) — two-level analytical framework
  classifying multi-agent communication across system-level (architecture, goals, protocols)
  and system-internal (strategy, paradigm, objects, content) dimensions.
- **LLM Agent Communication Protocol Taxonomy** (Sander et al. 2026) — predicts federated
  layered protocol stacks rather than monolithic standards; CaseHub's internal architecture
  demonstrates this principle at the intra-platform level.

---

## 10. References

- `docs/CHANNELS.md` — current taxonomy (to be rewritten)
- `docs/PLATFORM.md` — Capability Ownership table
- `docs/LIFECYCLE.md` — state machine taxonomy (companion document)
- parent#93 — coordination channel extraction (CLOSED — shipped)
- parent#294 — Reusable Platform Primitives epic
- `casehub/garden: docs/protocols/casehub/qhorus-consumer-integration-pattern.md`
- [FIPA Communicative Act Library](http://www.fipa.org/specs/fipa00037/SC00037J.html)
- [Beyond Self-Talk: Communication-Centric Survey](https://arxiv.org/html/2502.14321v2)
- [Technical Taxonomy of LLM Agent Communication Protocols](https://arxiv.org/html/2606.19135)
