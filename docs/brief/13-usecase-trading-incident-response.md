# Use Case: Trading Incident Response

*Flash crash overnight — how 16 platform capabilities coordinate
detection, deliberation, containment, and learning in 120 seconds.*

---

## The Business Problem

An algorithmic trading desk runs seven strategy agents overnight.
At 02:17 UTC, a regime shift drops the S&P 500 E-mini by 5.3% in
ninety seconds. Three problems hit simultaneously:

1. **Detection to response gap.** The desk's monitoring fires an
   alert. But the alert system doesn't know which positions are
   exposed, which strategies should halt, or which need human
   escalation. A human trader needs 5-10 minutes to triage — by
   then, the damage is done.

2. **Regulatory obligation.** MiFID II Art.17 requires that
   algorithmic trading firms maintain systems capable of responding
   to disorderly trading conditions. Dodd-Frank mandates pre-trade
   risk controls. Every decision in the response chain must produce
   a tamper-evident audit record — not a log file, a cryptographic
   proof. Regulators don't audit log files; they audit decision
   chains.

3. **Epistemic uncertainty.** During a flash crash, strategy agents
   disagree. The momentum agent wants to cut all positions. The
   mean-reversion agent sees a buying opportunity. The statistical
   arbitrage agent sees a spread collapse. A simple majority vote
   is dangerous — the disagreement itself is information. The
   response system needs structured deliberation, not aggregation.

Most trading platforms handle detection well and response poorly.
They fire alerts. Humans triage. The audit trail is whatever the
compliance team reconstructed after the fact. There is no
declarative playbook, no structured deliberation, no learning from
past incidents, and no way to prove to a regulator that the
response was systematic rather than ad hoc.

---

## The CaseHub Approach

CaseHub treats the flash crash as a case — a multi-step, multi-agent
coordination problem with accountability requirements at every
decision point. Five platform capabilities compose through the
lifecycle spine:

| Stage | What happens | Platform capability |
|-------|-------------|---------------------|
| **Declaration** | YAML playbooks define response procedures. Case definitions declare strategy evaluation, overnight incident, and oversight flows. | Declaration Surface |
| **Intelligence** | 7 strategy agents evaluate positions. LLM sentiment analysis from 3 perspectives. CBR retrieves past incident responses. 5-level temporal summarisation provides context. | AI Knowledge & Learning |
| **Control** | Trust-weighted arena selects strategies. Risk gates enforce pre-trade limits. Oversight gates escalate to humans. Order semaphores coordinate halt/release. | Enterprise Execution |
| **Convergence** | Epistemic deliberation with convergence detection resolves contested trades. Monitoring loop verifies position stabilisation. | Accountability & Governance |
| **Operations** | Post-mortem writes to CBR. P&L attestations update trust scores. Future similar incidents retrieve this response and adapt it. | The feedback loop closes. |

The entire response runs from a YAML playbook — `flash-crash-response.yaml`.
No developer writes Java to change the response procedure. A risk
manager edits the playbook, and the next flash crash follows the
new steps.

---

## Step-by-Step Flow

### Part 1: Detection and Playbook Activation

**1. Regime detection.** The 5-level temporal summarisation pipeline
compresses raw tick data into context: tick → 1-minute OHLCV →
5-minute trend → hourly regime → session narrative. The regime-level
summariser (computational, not LLM) detects a >5% drop. A
`RegimeChanged` event fires as a CDI event.

**2. Playbook activation.** The `flash-crash-response` playbook
activates with a 120-second deadline. The playbook is a YAML state
machine — steps, transitions, quorum gates, and parallel branches
declared in a `.step` file. The case engine dispatches it via
`StepFileCallableDispatcher`.

**3. Parallel risk assessment.** Two steps run concurrently: a
position-level risk assessment (MCP invoke to the risk service) and
a FIX session health check (REST invoke to the gateway). Results
land on the case blackboard.

**4. Order halt.** Based on risk results, the playbook engages an
order semaphore — all pending orders for exposed instruments are
suspended. The semaphore is a case-scoped coordination primitive,
not a global kill switch. Non-exposed instruments continue trading.

### Part 2: Multi-Agent Assessment

**5. Parallel LLM sentiment analysis.** Three LLM agents analyse
the situation from different perspectives: exposure risk, regulatory
risk, and execution risk. Each produces a structured assessment with
confidence scores and recommended actions. All three invoke via
the platform's `AgentProvider` SPI with model tier selection
(FLAGSHIP for risk assessment, STANDARD for monitoring).

**6. Strategy agent evaluation.** The trust-weighted arena pipeline
fires: 7 strategy agents are routed based on Bayesian Beta trust
scores learned from P&L attestations. Each agent evaluates its
active positions against current market conditions. Results feed
into per-instrument majority voting.

**7. Epistemic deliberation for contested positions.** Where
strategy agents disagree beyond a threshold, the system opens a
structured deliberation round via Qhorus channels. Agents submit
positions as speech acts. A convergence detector tracks the state
of the debate: CONSENSUS, DEADLOCK, PROGRESSING, DIMINISHING_RETURNS,
or CONVERGING. The debate continues for a configurable number of
rounds or until convergence is detected. This is not a simple vote
— it is a multi-round structured debate with common ground tracking.

**8. Risk gate evaluation.** Each position action passes through
`ActionRiskClassifier`. Three Dodd-Frank pre-trade controls apply:
position size vs. limit, daily loss vs. threshold, and net exposure
vs. cap. Actions exceeding thresholds are gated.

### Part 3: Human Escalation and Execution

**9. Gated positions escalate.** High-risk positions that fail the
risk gate generate `WorkItem` records for the on-call trader. Each
work item carries the deliberation context: which agents disagreed,
what the convergence state was, and what the LLM sentiment assessments
concluded. SLA tiers apply: P1 (15 minutes for >2% exposure), P2
(30 minutes), P3 (2 hours).

**10. Approved positions execute.** Positions that pass the risk
gate — or that the on-call trader approves — execute via the
trading gateway. Each execution produces an `OrderExecutionLedgerEntry`
in the Merkle chain. The MiFID II Art.17 audit trail now contains:
regime detection → assessment → deliberation → risk gate → execution,
each step linked by `causedByEntryId`.

**11. Monitoring loop.** The playbook enters a monitoring phase.
At configurable intervals, the system polls the risk service for
exposure. The loop continues until total exposure drops below the
threshold or the monitoring deadline expires.

**12. Orders released.** When the monitoring loop confirms
stabilisation, the order semaphore releases suspended instruments.
A `StrategyEvaluationLedgerEntry` records the release decision.

### Part 4: Learning and Feedback

**13. Post-mortem.** A post-mortem agent produces a structured
narrative of the incident: timeline, decisions, outcomes, P&L
impact. The narrative is written to the case context and exported
as a `DeliberationDecisionLedgerEntry`.

**14. CBR retention.** The full incident — problem features (market
conditions, exposure levels, regime type), solution (playbook steps,
human decisions, agent recommendations), and outcome (P&L impact,
response time, regulatory completeness) — is stored in the CBR
case base via `CaseRetriever`.

**15. Trust update.** P&L attestations update Bayesian Beta trust
scores for each strategy agent. The momentum agent that recommended
cutting positions during a V-shaped recovery gets a lower trust
score. The mean-reversion agent that correctly identified the buying
opportunity gets a higher one. Next time, routing adapts.

**16. Playbook adaptation.** CBR retrieval informs future playbook
selection. When the next overnight incident fires, the system
retrieves this response and adapts: if the V-shaped recovery pattern
was similar, it increases the deliberation time rather than cutting
immediately. The learning loop closes.

<!-- SVG: step-flow-diagram -->

---

## Capabilities in Play

| # | Capability | Role in this use case |
|---|-----------|----------------------|
| 1 | Case Orchestration | 3 case types: strategy-evaluation, overnight-incident, fsi-oversight |
| 2 | YAML Playbooks | `flash-crash-response.yaml` — state machine with parallel steps, quorum gates, monitoring loop |
| 3 | Temporal Summarisation | 5-level pipeline compresses tick data into regime-level context for detection |
| 4 | Trust-Weighted Routing | Bayesian Beta from P&L attestations selects strategy agents |
| 5 | Agent Deliberation | Multi-round Qhorus debate with epistemic convergence for contested trades |
| 6 | Risk Classification | Dodd-Frank pre-trade gates via `ActionRiskClassifier` chain |
| 7 | Human Task Management | On-call trader WorkItems with SLA tiers (P1/P2/P3) and deliberation context |
| 8 | Agent Infrastructure | 7 strategy + 13 incident agents via `AgentProvider` with model tier selection |
| 9 | LLM Sentiment Analysis | 3-perspective parallel assessment (exposure, regulatory, execution) |
| 10 | Case-Based Reasoning | Incident retention and retrieval; playbook adaptation from past outcomes |
| 11 | Tamper-Evident Ledger | MiFID II audit chain: detection → assessment → gate → execution, Merkle-linked |
| 12 | Situation Awareness | Regime detection via temporal summarisation pipeline, CDI event fire |
| 13 | Simulation Framework | 4 SPI decorators, 5 corpus files, 4 scenario profiles for incident replay |
| 14 | Pages Dashboard | 2 dock-workbench pages (Trading Desk + Ops Centre), 25+ panels, WebSocket push |
| 15 | @McpDomain Tri-Channel | 11 API classes (~40 operations) for REST + GraphQL + MCP access |
| 16 | Agent Identity | 7 strategy descriptors via Eidos with disposition profiles |

---

## Without CaseHub

A typical algorithmic trading desk handles flash crashes with a
patchwork:

| Concern | Typical approach | Gap |
|---------|-----------------|-----|
| **Detection** | Custom Python + Kdb+ monitoring scripts | Detection works. Response is the problem. |
| **Response** | Runbook wiki + phone calls to on-call trader | Manual, unstructured, no audit trail. Time to first action: 5-10 minutes. |
| **Audit trail** | Log files + post-hoc reconstruction | Not independently verifiable. Regulators must trust the firm's log integrity. |
| **Strategy disagreement** | Whoever shouts loudest, or a simple average | No structured deliberation. No record of why one strategy won. |
| **Risk gates** | Pre-trade limits in the OMS | Disconnected from the response flow. Gates fire but don't coordinate with the overall incident response. |
| **Learning** | Quarterly post-mortem meetings | Not systematic. Lessons learned exist in slide decks, not in the system. |
| **Playbook changes** | Developer implements in Python/Java | Days to weeks. Risk managers can't modify response procedures directly. |
| **Regulatory proof** | Compliance team reconstructs the timeline | Retrospective, error-prone, expensive. |

The structural problem: detection, assessment, deliberation,
execution, and learning are separate systems with separate data
models. Coordinating them requires integration code. Proving to a
regulator that the coordination happened correctly requires
reconstructing the timeline from multiple sources.

CaseHub replaces the patchwork with one declarative flow where
every decision is a ledger entry, every disagreement is a
structured debate, and every outcome feeds the next response.

---

## What the Platform Proves

**YAML playbooks for trading automation.** Response procedures are
not code — they are YAML state machines that risk managers can read,
review, and modify. The `flash-crash-response` playbook declares
parallel risk assessment, conditional order halts, monitoring loops,
and escalation paths in ~100 lines of YAML. Changing the response
procedure is a YAML edit, not a development sprint.

**Epistemic deliberation with convergence detection.** When
strategy agents disagree, the platform doesn't average — it
deliberates. Multi-round structured debate with five convergence
states (CONSENSUS, DEADLOCK, PROGRESSING, DIMINISHING_RETURNS,
CONVERGING) produces a decision with a recorded reasoning chain.
The deliberation itself becomes part of the audit trail.

**5-level temporal summarisation.** Raw tick data is useless for
decision-making. The summarisation pipeline — tick → OHLCV → trend
→ regime → narrative — produces context at the right abstraction
level for each consumer. The regime level triggers detection. The
narrative level feeds post-mortem. The same pipeline serves both
machine (computational summarisers) and human (LLM narrative
summarisers) consumers.

**Most comprehensive platform exercise.** FSI Trading exercises
more distinct platform capabilities than any other application —
16 in a single incident flow. This is not because trading is
special; it is because the platform's homogeneous consistency
makes it natural to compose capabilities without integration glue.
The same case engine that orchestrates clinical trials orchestrates
trading incidents. The same trust scores that route PR reviewers
route strategy agents. The same CBR that learns from AML
investigations learns from flash crashes.
