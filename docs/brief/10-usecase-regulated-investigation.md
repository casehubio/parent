# Use Case — Regulated Investigation

*Anti-money laundering from alert to SAR filing — 14 platform
capabilities composing across the full lifecycle spine.*

---

## The Business Problem

Financial crime investigation is a structural accountability
problem disguised as a workflow problem.

Regulators (FinCEN, FCA, AUSTRAC) require that every investigation
decision is traceable, every agent selection is defensible, and the
entire evidence chain is independently verifiable. The SAR filing
deadline is typically 30 calendar days from initial detection. Miss
it, and the institution faces enforcement action — not because the
investigation was wrong, but because the process couldn't prove it
was right.

Today's approach stitches together case management (Pega, Appian),
AI agents (LangChain, custom Python), audit logging (Splunk, ELK),
and human task queues (Jira, ServiceNow). Each tool owns a fragment
of the lifecycle. The result:

- **No end-to-end accountability.** The AI agent that flagged an
  entity as a PEP produces a log entry. The human analyst who
  cleared the flag produces a different log entry in a different
  system. Connecting the two requires manual correlation. Neither
  log is tamper-evident.
- **No learning from outcomes.** When a SAR verdict comes back
  UPHELD or WITHDRAWN, nothing feeds that outcome into future
  triage decisions or agent selection. The same mistakes repeat.
- **No adaptive routing.** Agent assignment is static — configured
  in a routing table, not learned from performance. An agent that
  consistently misclassifies PEP entities gets the same work
  volume as one that doesn't.
- **No rejection handling.** If the compliance officer rejects a
  SAR filing, the workflow typically dead-ends or requires manual
  re-routing. The adversarial path — where the system disagrees
  with the initial recommendation — is an afterthought.

The CaseHub AML application solves this with structural
accountability, not logging. Every decision is a Merkle-chained
ledger entry. Trust scoring learns from outcomes. Rejection routing
is a first-class YAML-declared path.

---

## The Lifecycle in Action

<!-- SVG: aml-lifecycle-flow -->

### Declaration

The entire investigation is declared in two YAML case definitions:

- **Main investigation** — 13 capabilities, 20 bindings, 4 goals
- **Oversight sub-case** — 3 capabilities, 3 bindings, 1 goal

No Java code decides what happens next. Binding conditions are JQ
expressions evaluated against the working layer of the case
blackboard. When a PEP entity is detected, the binding that routes
to a senior analyst fires because the data matches the condition —
not because a developer wrote an if-statement.

The 9-layer tutorial structure shows how this declaration grows
progressively: Layer 1 is a flat case with three workers and no
accountability. By Layer 9, the same case definition includes trust
routing, CBR-informed triage, oversight gates, GDPR erasure, and
compliance evidence — all declared, not coded.

### Intelligence

16 specialist workers analyse the investigation across six domains:
entity resolution, pattern analysis, OSINT screening, PEP detection,
SAR narrative drafting, and compliance review. Each worker is a CDI
bean — stateless, testable, independently deployable.

Case-Based Reasoning enters at triage. After an activation threshold
of 30 resolved cases, CBR retrieves similar past investigations
and injects them as context for downstream workers. SAR narrative
drafting receives sanitised precedent text from similar past filings,
with PII protection via `ContentSanitiser`. The system improves
with every investigation it completes.

### Control

Trust-weighted routing selects which agent handles each capability.
Three trust dimensions — investigation accuracy, PEP clearance
reliability, and scope awareness — produce independent Bayesian Beta
scores seeded with domain-appropriate priors. Agents below a
capability threshold are excluded from selection entirely.

When the investigation recommends SAR filing, a `PlannedAction`
triggers an oversight gate. The compliance officer receives a
WorkItem with a 30-day FinCEN SLA. This is not a notification —
it is a commitment lifecycle tracked through the Agentic
Communications Mesh.

Every step produces a Merkle-chained ledger entry with
`causedByEntryId` linking each finding to the commitment that
produced it. Independent verification is a single API call:
`GET /ledger/verify` returns the Merkle root;
`GET /audit/entries/{id}/proof` returns the inclusion proof for
any individual entry. The audit trail is cryptographic, not textual.

### Convergence

If the compliance officer rejects the SAR, CaseHub does not
dead-end. The rejection routing path — itself 5 capabilities and
~8 bindings, all YAML-declared — fires:

1. Senior analyst reviews the rejection rationale
2. Re-triage evaluates the case with new context
3. If triage still recommends filing, escalation to head of
   compliance
4. Re-drafting with the rejection feedback incorporated
5. If stalled, the case enters a monitored holding state with
   escalation timers

The adversarial path is not an exception handler. It is a
full case flow with the same accountability guarantees as the
happy path.

### Operations

When a SAR verdict arrives (UPHELD, WITHDRAWN, or FLAGGED), the
outcome feeds back into three systems:

- **Trust scoring** — agent trust dimensions adjust based on the
  verdict. An agent whose investigation led to a WITHDRAWN SAR
  sees its accuracy score decay. Future routing adapts.
- **CBR case base** — the complete investigation trace (problem
  description, solution steps, outcome) is retained as a precedent.
  Future triage retrieves it.
- **W3C PROV-DM export** — the full investigation lineage is
  available as a standards-compliant provenance record for
  regulatory submission.

The feedback loop closes. Every investigation makes the next one
better.

---

## Step-by-Step Flow

<!-- SVG: aml-step-flow-diagram -->

| Step | What happens | Platform capability |
|------|-------------|-------------------|
| 1 | Transaction monitoring flags suspicious activity | External trigger |
| 2 | Investigation case opens via YAML case definition | Case Orchestration Engine |
| 3 | CBR retrieves similar past investigations (if ≥30 resolved cases) | Case-Based Reasoning |
| 4 | Entity resolution worker identifies beneficial ownership chain | Worker execution |
| 5 | PEP detection routes to senior analyst automatically (binding condition evaluates entity data) | Composable signal routing |
| 6 | Pattern analysis and OSINT screening workers fire in parallel | Case Orchestration Engine (parallel dispatch) |
| 7 | Trust-weighted routing selects agents per capability (3 trust dimensions) | Trust & Accountability Ledger |
| 8 | Investigation triage evaluates findings with CBR adjustment | Case-Based Reasoning |
| 9 | SAR narrative drafted with seeded text from similar past SARs (PII sanitised) | Agent Memory, CBR |
| 10 | `PlannedAction(SAR_FILING)` triggers oversight gate | Oversight Gates |
| 11 | Compliance officer claims WorkItem (30-day FinCEN SLA) | Human Task Management |
| 12 | Every decision recorded as Merkle-chained ledger entry with `causedByEntryId` | Trust & Accountability Ledger |
| 13a | **If approved:** SAR filed, compliance review WorkItem opened | Human Task Management |
| 13b | **If rejected:** Rejection routing fires (5 capabilities) — senior review → re-triage → escalation → re-draft | Case Orchestration Engine |
| 14 | SAR outcome verdict (UPHELD / WITHDRAWN / FLAGGED) received | External event |
| 15 | Trust scores adjust from verdict feedback | Trust & Accountability Ledger |
| 16 | Complete investigation trace retained in CBR case base | Case-Based Reasoning |
| 17 | W3C PROV-DM provenance export available for regulatory submission | Compliance Evidence |
| 18 | GDPR Art.17 erasure available at any point with tamper-evident receipts | GDPR Erasure |

---

## Capabilities in Play

14 distinct platform capabilities from 10 foundation modules
participate in a single investigation:

| Capability | Module | Role in this use case |
|-----------|--------|----------------------|
| Case Orchestration | engine | 2 YAML case definitions drive the entire investigation lifecycle |
| Trust & Accountability | ledger | Merkle chain, Bayesian Beta routing, SAR outcome attestations |
| Human Task Management | work | 30-day FinCEN SLA, MLRO oversight gates, escalation tiers |
| Oversight Gates | engine | 5 action types gated by risk classification |
| Case-Based Reasoning | neocortex | Triage adjustment, path advice, SAR narrative seeding |
| Agent Memory | neocortex | Prior entity context across investigations, 3 memory domains |
| Agentic Communications | qhorus | COMMAND/RESPONSE/DECLINE per specialist agent |
| GDPR Erasure | ledger | Actor-level + entity-level erasure with tamper-evident receipts |
| Compliance Evidence | ledger | 4 requirement-scoped evidence records, Merkle inclusion proofs |
| W3C Provenance | ledger | PROV-DM JSON export of investigation lineage |
| Simulation & Scenarios | platform | 6 YAML scenarios for testing and demonstration |
| @McpDomain Tri-Channel | platform | 3 API surfaces (REST + GraphQL + MCP) from one interface |
| Notification Pipeline | platform | Compliance escalation routing |
| Shared Platform Services | platform | Preferences, identity, tenancy, expressions |

No integration glue. Every capability is a CDI bean sharing the
same lifecycle, tenancy model, and event system. The investigation
doesn't "call" the ledger — it emits lifecycle events, and the
ledger observes them.

---

## Without CaseHub

Building this with today's tools means assembling five or more
systems and accepting the gaps between them:

| Concern | Typical approach | What's missing |
|---------|-----------------|---------------|
| Case lifecycle | Camunda BPMN / Pega / Appian | DAG workflows can't express adaptive binding conditions — the PEP route is a pre-designed branch, not a reactive response to data. Rejection paths require explicit modelling for every scenario. |
| AI agents | LangChain / LlamaIndex / custom | No trust feedback loop. Agent selection is configured, not learned. No SAR outcome → agent score update path. |
| Audit trail | Splunk / ELK / custom logging | Append-only logs, not Merkle-chained. No independent verification. No `causedByEntryId` linking decisions to their evidence. Cannot prove records haven't been modified. |
| Human tasks | Jira / ServiceNow | No typed SLA breach algebra. No rejection routing. No commitment lifecycle. "Assign and wait" — no adaptive escalation. |
| Learning | Manual analyst training | No CBR. No precedent retrieval. Every investigation starts from scratch. Past SAR outcomes don't inform future triage. |
| Compliance evidence | Manual report generation | No structured evidence records. No Merkle inclusion proofs. Audit preparation is a multi-week project, not an API call. |
| Privacy | Manual data management | No structured GDPR erasure. No tamper-evident erasure receipts. Entity deletion is a database operation, not an auditable process. |

The fundamental gap is that these tools don't share a data model,
event system, or accountability chain. Connecting AI agent output
to a human approval gate to a tamper-evident audit record requires
custom integration code at every boundary. That integration code
is itself unaudited.

CaseHub eliminates these boundaries. The same CDI event that fires
when a worker completes is observed by the ledger (audit), qhorus
(communication), and work (human task creation) — simultaneously,
with no integration layer.

---

## What This Proves

The AML application is CaseHub's most complete reference
architecture — all 130 issues closed, 14 platform capabilities
exercised, and a 9-layer tutorial showing progressive platform
adoption. It demonstrates that structural accountability (Merkle
chain, Bayesian trust, oversight gates) is not a performance tax
bolted onto a workflow — it is the architecture itself. The same
platform that routes AI agents routes human compliance officers,
and every routing decision leaves a cryptographic proof that it
happened exactly as recorded.

---

*Next: [Clinical Trial Safety](11-usecase-clinical-trial-safety.md)
— multi-site coordination with GCP/FDA compliance.*
