# Use Case: Clinical Trial Safety Monitoring

*Multi-site adverse event detection, cross-site pattern aggregation,
and GCP/FDA-compliant oversight — orchestrated by YAML case
definitions, enforced by the platform.*

<!-- SVG: step-flow-diagram -->

---

## The Problem

A Phase III oncology trial runs across three hospital sites. A
patient at Site A reports a Grade 3 adverse event. At the same time,
a patient at Site B reports a Grade 4 event on the same study drug.
Neither site's investigator has visibility into the other. Without
cross-site aggregation, the safety signal goes undetected until the
next DSMB meeting — weeks later.

This is the central failure mode in clinical trial safety: **no
single system connects adverse event detection, cross-site pattern
recognition, investigator accountability, and regulatory deadline
enforcement into one auditable flow.**

Today's landscape:

- **EDC systems** (Medidata Rave, Oracle InForm) capture data. They
  don't orchestrate responses. An adverse event is a form submission,
  not a case that routes to the right agent, enforces deadlines, and
  produces Merkle-verifiable audit records.
- **CTMS tools** (Veeva Vault, Medidata) manage sites and timelines.
  They have no concept of trust-weighted agent routing, case-based
  reasoning from prior AE outcomes, or blackboard aggregation that
  detects cross-site patterns.
- **Custom integration** stitches EDC, CTMS, email alerts, and
  spreadsheets together with glue code. Compliance verification
  becomes a manual retrospective exercise. Nothing is independently
  verifiable.

The regulatory stakes are severe. GCP (ICH E6(R3)) mandates
24-hour reporting for Grade 3+ adverse events. FDA 21 CFR Part 312
requires 7-day IND submission for fatal events, 15-day for serious
ones. Missed deadlines trigger regulatory holds — the trial stops.

CaseHub's clinical application demonstrates that a single platform
can handle the entire lifecycle: from adverse event detection through
cross-site aggregation, through investigator accountability, through
regulatory submission — with every step tamper-evident and
independently verifiable.

---

## How CaseHub Composes Capabilities

The clinical use case exercises 17 platform capabilities across all
five lifecycle stages. The key architectural insight: **blackboard
aggregation detects cross-site safety signals without any single
agent having global visibility.**

### Declaration

Seven YAML case definitions declare the clinical trial's operational
logic — AE escalation, deviation review, SUSAR oversight, regulatory
submission, eligibility screening, protocol amendment, trial
coordination. Each case definition specifies capabilities, bindings,
goals, and completion criteria in declarative YAML. The case engine
parses and activates them at startup.

Grade-based routing is structural, not configured: `CtcaeGrade.sla()`
returns the regulatory SLA directly from the grade enum. The
compliance specification IS the code.

### Intelligence

Five LLM agents (eligibility screening, SUSAR criteria evaluation,
safety signal analysis, trial supervision, protocol amendment) are
registered via the Agent Infrastructure SPI. Trust-weighted routing
selects the most reliable agent for each task based on accumulated
attestation evidence across three trust dimensions:
safety-accuracy, eligibility-precision, and protocol-adherence.

Six Case-Based Reasoning domains learn from every outcome. AE
trajectory monitoring uses Dynamic Time Warping to detect when a
patient's adverse event progression deviates from similar historical
patterns — an early warning that the current case may escalate
differently than precedent suggests.

### Control

The Case Orchestration Engine coordinates the response. Binding
conditions fire capabilities based on context state — a Grade 4+
event triggers DSMB rollup automatically; a protocol deviation
routes to the named PI with a formal COMMAND and deadline. Oversight
gates classify every consequential action (5 types are ALWAYS-gated)
through the Action Risk Classifier — no agent can bypass them.

Human Task Management enforces SLA: 24h for Grade 3, 1h for
Grade 5, with two-tier breach escalation. IND deadlines use
absolute dates computed from `expiresAtExpression` against the
WORKING layer — 15-day for Grade 3, 7-day for fatal events. These
are not relative timers that drift; they are exact regulatory
deadlines.

### Convergence

Trial-level blackboard aggregation detects cross-site safety
patterns. When Site A reports a Grade 3 event and Site B reports a
Grade 4 event on the same drug, a binding guard on the trial-level
case checks aggregate state. No individual site agent has global
visibility — the blackboard pattern lets the trial-level case
detect the cluster without centralising site data.

`TrialSafetyAggregationJob` enriches the signal.
`LlmSafetySignalAnalyzer` produces a DSMB narrative.
`DsmbSafetySignalEvent` fires the notification chain. The platform
converges on the safety signal through structured composition, not
ad-hoc alerting.

### Operations

Regulatory compliance monitoring runs continuously. SLA breach
policies escalate automatically. EU AI Act Art.12 compliance
supplements attach `InvocationMetrics` to every LLM invocation in
the Merkle chain — model identifier, token counts, latency,
confidence. Decision narratives produce human-readable accountability
explanations for every routing and escalation decision.

The feedback loop closes: CBR stores every AE outcome — the
escalation plan, the routing decisions, the resolution. The next
similar adverse event retrieves learned precedent. Routing
improves. Escalation adapts. The trial gets safer over time.

---

## Step-by-Step: Cross-Site AE Cluster Detection

A concrete walkthrough of CaseHub's clinical application handling
simultaneous adverse events across two sites, triggering DSMB
review and PI accountability.

<!-- SVG: clinical-step-flow -->

1. **Adverse event reported at Site A** — clinician submits Grade 3
   AE on study drug. `AdverseEventService` creates a WorkItem with
   24h SLA, writes `AdverseEventLedgerEntry` to the Merkle chain.
   *[Human Task Management, Tamper-Evident Audit]*

2. **AE escalation case activates** — `ae-escalation.yaml` fires.
   The Case Orchestration Engine evaluates binding conditions
   against grade and context.
   *[Case Orchestration Engine]*

3. **CBR retrieves similar past events** — six CBR domains searched.
   AE trajectory domain uses DTW to match temporal progression
   patterns. Results injected as context for downstream agents.
   *[Case-Based Reasoning]*

4. **Trust-weighted routing selects safety agent** — three trust
   dimensions evaluated. Agent with highest `safety-accuracy` score
   and above 0.75 threshold selected. Score computed from Bayesian
   Beta distribution with exponential decay.
   *[Trust & Accountability Ledger]*

5. **LLM SUSAR criteria evaluation** — selected agent assesses
   causality per ICH E2A criteria. `ComplianceSupplement` attaches
   model metrics to the ledger entry. Finding: possibly related,
   unexpected.
   *[Agent Infrastructure, EU AI Act Compliance]*

6. **Grade 4 AE reported at Site B** — same study drug, different
   patient. Same flow initiates independently at Site B. The site
   agent has no visibility into Site A's event.
   *[Case Orchestration Engine]*

7. **Trial-level blackboard aggregation fires** — a binding guard on
   the trial coordination case checks aggregate AE state across all
   sites. Two events on the same drug within 48 hours exceeds the
   cluster threshold. No site agent triggered this — the blackboard
   pattern detected it.
   *[Case Orchestration Engine — Blackboard Architecture]*

8. **DSMB batch signal notification** — `TrialSafetyAggregationJob`
   detects the cross-site cluster. `LlmSafetySignalAnalyzer`
   generates a DSMB narrative. `DsmbSafetySignalEvent` fires.
   *[Agent Infrastructure, Notification Pipeline]*

9. **Protocol deviation created** — the cluster triggers a protocol
   deviation case. A formal COMMAND is sent to the named PI at
   Site A via Agentic Communications Mesh with a 24h deadline.
   This is a commitment lifecycle — not a notification.
   *[Agentic Communications Mesh]*

10. **PI responds** — structured JSON response through
    `ClinicalInboundNormaliser`. The PI's assessment is a formal
    speech act with audit trail, not an email reply.
    *[Agentic Communications Mesh]*

11. **CRITICAL severity triggers IRB gate** — the deviation is
    classified CRITICAL. An IRB review WorkItem is created with
    72h SLA. The case suspends until the IRB decides.
    *[Human Task Management, Oversight Gates]*

12. **IND deadline computation** — Grade 4 triggers a 7-day
    absolute deadline. `expiresAtExpression` evaluates against the
    WORKING layer context panel. Not a relative timer — the exact
    FDA submission date.
    *[Human Task Management — SLA Enforcement]*

13. **IRB approves with conditions** — the IRB decision is recorded
    as an `IrbDecisionLedgerEntry` in the Merkle chain. Case
    resumes with conditions applied to the protocol amendment
    case.
    *[Tamper-Evident Audit, Case Orchestration Engine]*

14. **Safety signal analysis** — `LlmSafetySignalAnalyzer`
    evaluates the full cluster with cross-site context.
    `ClinicalNarrativeSignalStrategy` produces a human-readable
    decision trace explaining the routing and escalation logic.
    *[Agent Infrastructure, Decision Narratives]*

15. **Regulatory submission** — `regulatory-submission.yaml` case
    fires. IND expedited safety report generated per 21 CFR
    Part 312. The report references specific Merkle inclusion
    proofs for each evidence point.
    *[Case Orchestration Engine, Regulatory Reporting]*

16. **Trust attestation** — `SusarAgentAttestationWriter` writes
    attestations anchored to `WorkerDecisionEntry`. The safety
    agent's trust score updates. Future similar events route more
    effectively.
    *[Trust & Accountability Ledger]*

17. **CBR retains outcome** — the full plan trace — escalation
    path, routing decisions, agent selections, PI response, IRB
    decision, regulatory outcome — is stored as precedent. Learned
    escalation plans are available for retrieval on the next
    similar cluster.
    *[Case-Based Reasoning]*

18. **Patient memory updated** — four structured memory domains
    (patient, site, drug, IRB) updated via Agent Memory SPI.
    The next event for this patient carries full prior context.
    *[Agent Memory]*

---

## Capabilities in Play

| Step | Capability | Role in this flow |
|------|-----------|-------------------|
| 1 | Human Task Management | Grade-keyed WorkItem with SLA |
| 1 | Tamper-Evident Audit | Merkle-chained AE ledger entry |
| 2 | Case Orchestration Engine | YAML case definition activation |
| 3 | Case-Based Reasoning | 6-domain precedent retrieval with DTW |
| 4 | Trust & Accountability | Bayesian trust routing (3 dimensions) |
| 5 | Agent Infrastructure | LLM SUSAR evaluation |
| 5 | EU AI Act Compliance | Invocation metrics on every LLM call |
| 7 | Blackboard Architecture | Cross-site cluster detection |
| 8 | Notification Pipeline | DSMB batch signal notification |
| 9 | Agentic Communications | PI COMMAND with commitment lifecycle |
| 11 | Oversight Gates | ALWAYS-gated IRB review |
| 12 | SLA Enforcement | Absolute IND deadline (7-day / 15-day) |
| 13 | Tamper-Evident Audit | IRB decision in Merkle chain |
| 14 | Decision Narratives | Human-readable escalation explanation |
| 15 | Regulatory Reporting | IND safety report with Merkle proofs |
| 16 | Trust Scoring | Agent attestation, score update |
| 17 | Case-Based Reasoning | Full outcome retained as precedent |
| 18 | Agent Memory | 4 structured domains updated |

17 platform capabilities compose in one flow — from adverse event
to regulatory submission to learning from the outcome.

---

## Without CaseHub

The same scenario in today's clinical trial infrastructure:

**Detection:** Adverse events are submitted through EDC forms.
Cross-site correlation happens at the next DSMB meeting — weeks
later — by a human reviewing spreadsheets. The Grade 3 at Site A
and Grade 4 at Site B are not connected until someone manually
notices the pattern.

**Routing:** Assignment is manual or round-robin. No trust scoring.
No CBR-enhanced selection. The safety monitor who reviews the case
has no track record of accuracy, and no mechanism to improve
selection from outcomes.

**Compliance:** SLA tracking is a spreadsheet or calendar reminder.
IND deadlines are manually computed. The 7-day clock starts when
someone notices the event requires expedited reporting — not
automatically from the grade classification. Missed deadlines are
discovered during regulatory audits, not prevented by the system.

**Audit:** Audit trails are appendable database records. They can be
silently modified or deleted. FDA inspectors must trust the
operator's integrity rather than independently verify the chain.
No inclusion proofs. No cryptographic tamper detection.

**PI accountability:** Protocol deviations are communicated via email.
There is no formal commitment lifecycle — no deadline, no structured
response, no audit trail of the obligation and its resolution. The
PI's verbal agreement at a site meeting is the entire accountability
mechanism.

**Learning:** Each trial starts cold. Prior AE patterns, escalation
decisions, and routing outcomes are not systematically captured or
retrieved. A similar cluster in a future trial triggers the same
manual process from scratch.

**The gap is structural.** It's not that EDC/CTMS tools lack
features — it's that no single system connects detection,
coordination, accountability, compliance enforcement, and learning
into one auditable lifecycle. CaseHub doesn't replace EDC systems.
It provides the orchestration, accountability, and learning layer
that EDC systems were never designed to be.

---

## What the Platform Proves

The clinical trial use case demonstrates that **blackboard
aggregation can detect cross-site safety signals without
centralising patient data** — each site agent operates independently,
and the trial-level case detects patterns through reactive binding
evaluation. It proves that **regulatory compliance can be structural
rather than procedural** — GCP SLA enforcement is anchored in the
grade enum, IND deadlines are computed expressions, and every
decision point is Merkle-chained with independently verifiable
inclusion proofs. And it proves that **CBR learning compounds across
trials** — six domains of case-based reasoning ensure that every
adverse event, every escalation decision, and every routing outcome
makes the next trial safer.

The peer-reviewed baseline (ClinicalAgent, arXiv 2404.14777) cannot
provide SLA enforcement, formal PI obligation, consent withdrawal,
multi-site rollup, FDA tamper-evident audit, trust-weighted routing,
adaptive protocol paths, IND deadline enforcement, or CBR precedent
retrieval. CaseHub provides all ten.
