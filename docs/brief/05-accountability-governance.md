# Accountability & Governance

*How do I know agents are doing the right thing?*

Most platforms treat accountability as a logging concern — append events
to a database, query them later. CaseHub treats accountability as an
architectural concern. Every agent decision is cryptographically
committed to a tamper-evident ledger. Every agent message is a formal
speech act with enforceable obligations. Every agent interaction is
monitored by watchdogs that detect pathologies before they cause harm.

Accountability in CaseHub isn't a feature you enable. It's the
architecture you build on. And every part of it is automatable —
the entire platform is scriptable via playbooks, making governance
itself a reproducible, testable, auditable process.

---

## Tamper-Evident Audit Trail

Every agent decision, human action, and system event is
cryptographically committed to an append-only ledger built on Merkle
Mountain Range (RFC 9162). Each entry is hash-chained to the previous
one — tampering with any entry invalidates the chain from that point
forward. O(log N) inclusion proofs allow any entry to be independently
verified.

Ed25519 signed checkpoints establish cryptographic milestones. Cloud
KMS signing (AWS KMS, GCP Cloud KMS, Azure Key Vault, HashiCorp Vault
Transit) ensures private keys never leave the HSM. Peer attestation
allows agents and humans to attest to the quality of any ledger entry
as SOUND, FLAGGED, ENDORSED, or CHALLENGED — and those attestations
are themselves part of the chain.

This is not a separate audit system. The ledger is the platform's
event backbone. Every subsystem — engine, work, qhorus, connectors —
writes to the same `LedgerAppender` SPI with one consistent API. A
case transition, a worker completion, a message dispatch, and a trust
score update all produce entries in the same Merkle chain.

**What makes this different:** Competing platforms use appendable
databases for audit trails. Appendable means mutable — entries can be
silently altered or deleted. CaseHub's Merkle MMR makes any tampering
cryptographically detectable. This is the same data structure used in
certificate transparency (RFC 9162), applied to enterprise agent
operations.

---

## Bayesian Trust Scoring

Trust is scored, not assumed. CaseHub computes agent reliability using
Bayesian Beta reputation with exponential decay — recent performance
matters more than historical, and negative signals persist longer than
positive ones (asymmetric valence). This matches real-world trust
dynamics: trust is earned slowly and lost quickly.

Four score types provide different lenses:

| Score Type | What it measures |
|------------|-----------------|
| **GLOBAL** | Overall agent reliability across all interactions |
| **CAPABILITY** | Reliability within a specific capability domain |
| **DIMENSION** | Quality along a named dimension (accuracy, timeliness, completeness) |
| **QUALITY** | Outcome quality for a specific type of work |

EigenTrust power iteration computes transitive trust across the agent
mesh — an agent trusted by trusted agents inherits credibility.
Materialized snapshots enable low-latency trust lookups for routing
decisions without recomputing on every request.

Trust scores feed directly into the engine's composable signal routing.
When selecting a worker for a case step, trust is one of five signal
providers (alongside workload, CBR experience, personality, and
semantic match). A worker with declining trust is automatically
deprioritised — no manual intervention, no threshold rules, just
continuous Bayesian recomputation from attestation history.

**What makes this different:** Competing platforms either don't score
trust at all (fire-and-forget) or use simple threshold rules (agent
trust > 0.7 → allow). CaseHub's Bayesian model with EigenTrust is the
kind of reputation system used in peer-to-peer networks, applied to
enterprise agent coordination. The asymmetric valence — negative
evidence decays more slowly — prevents a few good outcomes from
washing away a pattern of poor performance.

---

## Agentic Communications Mesh

The Agentic Communications Mesh is the normative communication
infrastructure for multi-agent systems. Every agent interaction is a
formal speech act — not a bare message, but an accountable act with
semantic obligations.

### Speech Act Messaging

Ten message types, each carrying specific obligations:

| Type | Obligation |
|------|-----------|
| **QUERY** | Recipient should respond |
| **COMMAND** | Recipient should execute |
| **PROPOSE** | Recipient should accept, counter, or decline |
| **RESPONSE** | Fulfils an obligation from QUERY |
| **STATUS** | Informational — no obligation created |
| **DECLINE** | Terminates an obligation |
| **HANDOFF** | Transfers obligation to another agent |
| **DONE** | Marks obligation as fulfilled |
| **FAILURE** | Marks obligation as failed |
| **EVENT** | System-generated, no direct obligation |

These aren't labels — the platform enforces their semantics. A COMMAND
creates a trackable commitment. A DONE without a matching commitment
is a protocol violation. A PROPOSE that is neither accepted nor
declined within its deadline triggers escalation.

### Commitment Store

Behind every speech act is a commitment lifecycle: OPEN →
ACKNOWLEDGED → terminal state (FULFILLED, FAILED, DECLINED,
DELEGATED, EXPIRED). The commitment store tracks every obligation
across the mesh — 29 store interfaces providing typed access to
commitments, messages, channels, protocols, watchdog state, and
compliance evidence.

Automatic deadline enforcement means expired commitments don't just
log — they trigger escalation paths. Delegation chains are tracked
end-to-end. The commitment store is the ground truth for "what was
promised, by whom, and whether it was delivered."

### Channels

Typed channels with six semantics (APPEND, COLLECT, BARRIER,
EPHEMERAL, LAST_WRITE, BROADCAST), hierarchical spaces, topics,
reactions, and presence tracking. A channel gateway provides
backend-agnostic fan-out with AT_LEAST_ONCE delivery, cursor tracking,
and reconciliation.

Three backend types — agent, human-participating, human-observer —
determine how messages are delivered. External platforms (Slack,
Discord, Teams) bridge into mesh channels via the connector SPIs,
meaning the same governance applies to messages sent through Slack as
to messages sent between AI agents.

**What makes this different:** LangChain, CrewAI, and AutoGen use
fire-and-forget messaging. An agent sends a message; the framework
delivers it; nobody tracks whether the recipient acted on it. CaseHub
makes every message an accountable speech act with enforceable
obligations. No other agent framework offers commitment tracking,
deadline enforcement, or delegation chain visibility on agent
communication.

---

## Protocol Enforcement

Channel protocols define the rules of engagement for agent
conversations. Four built-in protocols:

| Protocol | What it enforces |
|----------|-----------------|
| **REQUEST_RESPONSE** | Every request must receive exactly one response |
| **TASK_COMPLETION** | Work must be committed or declined within a deadline |
| **ROUND_ROBIN** | Each participant must contribute before any repeats |
| **CONTRIBUTION_REQUIRED** | All members must contribute before proceeding |

Protocols are pluggable — applications define their own via CDI. Each
protocol can operate in three enforcement modes:

- **Advisory** — violations are logged but not blocked. Useful during
  development or when agents are learning a new interaction pattern.
- **Blocking** — violations prevent the message from being dispatched.
  The agent receives an error and must comply.
- **Quarantine** — violations are captured for review. The message is
  held pending human approval, enabling oversight without interrupting
  the agent's flow.

Severity-aware escalation means a protocol can start in advisory mode
and automatically escalate to blocking if violations exceed a
threshold. This enables progressive trust — new agents operate under
advisory governance and earn their way to reduced oversight.

**What makes this different:** No other agent framework validates
message sequences against configurable protocols. This is governance
over agent conversations — not just logging what was said, but
enforcing rules about what can be said, when, and by whom.

---

## Communication Watchdogs

Eleven watchdog types actively monitor agent coordination for
pathologies:

| Watchdog | What it detects |
|----------|----------------|
| **Barrier Stuck** | A barrier channel has been waiting too long for all participants |
| **Approval Pending** | An oversight gate has been open past its SLA |
| **Agent Stale** | An agent hasn't produced output within expected time |
| **Channel Idle** | No activity on a channel that should be active |
| **Queue Depth** | Message backlog exceeding capacity thresholds |
| **Context Pressure** | Channel context approaching memory limits |
| **Loop Detected** | Cyclic message patterns between agents |
| **Obligation Fan-Out** | Too many commitments created in a short period |
| **Conversation Stall** | Discussion proceeding without convergence |
| **Echo Chamber** | Agents reinforcing each other without substantive contribution |
| **Circular Delegation** | Obligations being passed in circles |

Watchdogs produce CDI events that feed into the platform's
notification pipeline and can trigger case actions. An echo chamber
detected in a debate orchestration can automatically introduce a
dissenting agent. A circular delegation can escalate to a human
supervisor. A conversation stall can inject a convergence prompt.

**What makes this different:** Most platforms detect failures after
they happen. CaseHub detects coordination pathologies as they form —
before they produce bad outcomes.

---

## Oversight Gates

M-of-N quorum approval for consequential actions. When an agent
attempts a high-risk operation — approving a financial transaction,
deploying to production, closing a compliance case — the platform
gates the action behind human approval.

`ActionRiskClassifier` CDI beans determine whether an action requires
oversight. Multiple classifiers compose with most-restrictive-wins
semantics: if any classifier says "gate required," the gate opens.
Applications inject domain-specific classifiers alongside platform
defaults.

Gate context is serialized as Java Properties into Qhorus COMMAND
messages, making gates crash-safe — they survive application restarts
because the pending approval is persisted in the communications mesh,
not in-memory state.

Design choices for edge cases:
- **Fail-open on infrastructure errors** — if the gate infrastructure
  itself is unavailable, the agent continues. An unreachable gate
  should not deadlock operations.
- **Fail-safe on classifier errors** — if a classifier throws an
  exception, the gate is required. Unknown risk is treated as high
  risk.

---

## Structural Completion Signaling

ADR-0004 establishes a principle unique to CaseHub: agents explicitly
declare their state transitions via MCP tool calls. There is no text
classification, no output parsing, no heuristics.

When an agent completes a task, it calls `commitment_fulfill`. When it
escalates, it calls `commitment_escalate`. When it needs human
approval, it calls `oversight_gate_open`. Every state transition is a
deliberate, auditable action — not an inference from natural language
output.

This matters because text-based completion detection is inherently
unreliable. An agent that says "I'm done" might be summarizing, might
be hallucinating, might be expressing a sub-task completion. Structural
signaling eliminates this ambiguity. The commitment store records
exactly what the agent declared, when, and with what context.

18 operations are exposed via the @McpDomain SPI — the first CaseHub
repo to adopt tri-channel API generation, producing REST, GraphQL, and
MCP endpoints from a single source definition. This pattern is now
available for all CaseHub repos.

---

## EU AI Act Art.12 Compliance

The platform generates compliance evidence automatically. The
compliance reporting module produces:

- **Attribution reports** — who (agent or human) made each decision
- **Obligation reports** — what commitments were created and their
  outcomes
- **Violation reports** — protocol violations with context and
  enforcement actions taken
- **Trust history** — per-agent trust score evolution over time
- **Provenance chains** — full causal chain from triggering event
  through agent decisions to outcome
- **Judgment reports** — decision rationale with input context

Reports are rendered via Qute templates to PDF/A-2b (long-term
archival format) with PAdES digital signatures, or exported as
JSON/CSV with CAdES detached signatures. The signing infrastructure
uses the same cloud KMS providers as the ledger.

---

## GDPR Privacy by Design

Privacy is structural, not policy-based. Human actor identities are
automatically pseudonymised via token-based Art.17 erasure:

1. A token maps a human identity to their ledger entries
2. On erasure request, the token-to-identity mapping is severed
3. Ledger entries remain — permanently anonymous, Merkle chain intact
4. The erasure operation itself produces a tamper-evident receipt

Decision context sanitisation is pluggable via SPI — applications
define what constitutes personally identifiable information in their
domain and provide sanitisers. The platform enforces that sanitisation
runs before any persistence.

This means the audit trail is simultaneously tamper-evident AND
privacy-compliant. Entries cannot be deleted (they're part of the
Merkle chain), but they can be made anonymous (the identity link is
severed). The erasure receipt proves that privacy rights were
exercised — and that receipt is itself part of the chain.

---

## Architecture

![Accountability Architecture](images/brief/05-accountability-arch.svg)

The accountability infrastructure is not a layer — it is woven through
every interaction. The 12-step dispatch gate pipeline in the
communications mesh ensures that every message passes through ACL,
rate limiting, trust gating, protocol evaluation, and ledger
commitment before fan-out. No bypass path exists.

---

## Extent

| Component | Scale |
|-----------|-------|
| Ledger | 14 modules, 11 SPI interfaces, 28+ service classes, 4 cloud KMS providers × 3 flavours |
| Communications Mesh | 23 modules, 29 store interfaces, 30 SPI interfaces, 12-step dispatch pipeline |
| Execution Bridge | 5 deliverables (3 Maven + TS plugin + Python SDK), 18 MCP operations |
| Compliance | EU AI Act Art.12, PDF/A-2b + PAdES, JSON/CSV + CAdES, 6 report types |
| Privacy | Token-based pseudonymisation, pluggable sanitisation, tamper-evident erasure receipts |

---

## What the Shared Platform Provides

Every CDI event across CaseHub automatically produces a ledger entry
because every subsystem uses the same event model. Trust scores are
available to every routing decision because the same `CurrentPrincipal`
identity model flows through every SPI call. Protocol enforcement
applies to every channel — including bridged external platforms like
Slack and Teams — because connectors integrate at the mesh layer, not
at the application layer.

The annotation-driven audit (`@Audited`, `@Attested`,
`@ComplianceSupplement`) means any CDI or Spring method can be made
accountable with a single annotation. Zero-code audit trail for any
business operation — the same build-time validation and runtime
interception used across the platform.

---

## Connections to Other Areas

| Area | Connection |
|------|-----------|
| [Enterprise Execution](04-enterprise-execution.md) | Trust scores feed composable signal routing for worker selection. Oversight gates are evaluated during case step execution. |
| [Agentic Orchestration](02-agentic-orchestration.md) | Orchestration patterns observe commitment state changes to make coordination decisions. Debate and voting patterns use speech act semantics. |
| [Convergence & Situational Awareness](06-convergence-situational-awareness.md) | Watchdog alerts can trigger situation detection. Reconciliation actions are audited through the same ledger. |
| [Agent Identity & Cognition](07-agent-identity-cognition.md) | Behavioural contracts from agent identity are enforced via protocol rules. Trust scores feed personality evolution. |
| [The Shared Foundation](08-shared-foundation.md) | Identity, tenancy, event model, and expression engines are shared infrastructure. Cloud KMS signing uses platform credential resolution. |
