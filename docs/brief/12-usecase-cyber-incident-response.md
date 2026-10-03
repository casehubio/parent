# Use Case: Cyber Incident Response

*From SIEM alert to verified containment — 13 platform capabilities
in a single incident flow, closing the loop from detection through
reconciliation to organisational learning.*

---

## The Business Problem

Security Operations Centers drown in alerts. A mid-sized SOC processes
10,000–50,000 alerts per day; large enterprises see ten times that. The
numbers that matter:

- **False positive rates of 40–60%.** Analysts spend most of their time
  dismissing noise, not investigating threats. Alert fatigue leads to
  real threats being deprioritised or missed entirely.
- **Mean Time to Detect (MTTD) measured in days.** IBM's 2024 Cost of a
  Data Breach report puts the global average at 194 days. Most of that
  time is wasted on triage, not investigation.
- **No verified containment.** SOAR tools execute containment actions
  (isolate a host, revoke credentials) but never verify the actions
  took effect. A firewall rule that silently fails leaves the
  organisation exposed while dashboards show green.
- **No learning loop.** Each incident starts from scratch. Analysts
  build institutional knowledge in their heads; when they leave, it
  leaves with them. Playbooks are static documents, not adaptive
  systems.
- **DORA pressure.** The Digital Operational Resilience Act requires
  documented response timelines and evidence that containment was
  effective. Manual spreadsheets and screenshot evidence don't meet the
  bar for auditors.

The fundamental gap: existing SOAR tools automate *response execution*
but not *response verification* or *response learning*. They tell you
what you did, not whether it worked or what you should do differently
next time.

---

## The CaseHub Approach

CaseHub treats incident response as a case lifecycle — a structured
progression through the platform's five lifecycle stages, where each
stage uses different platform capabilities and the outcome feeds back
into the next incident.

```
Declaration → Intelligence → Control → Convergence → Operations
     ↑                                                    │
     └────────────────── feedback loop ───────────────────┘
```

- **Declaration:** The incident investigation is a YAML case definition
  — 8 capabilities, 9 bindings, 3 goals. The entire response pipeline
  is declarative. New investigation steps are added by editing YAML,
  not writing Java.
- **Intelligence:** CBR retrieves similar past incidents. Dual
  rule-based and LLM workers investigate in parallel. ATT&CK STIX 2.1
  enriches with structural threat intelligence. RAG retrieves relevant
  prose from the internal knowledge corpus.
- **Control:** Trust-weighted routing selects the best worker for each
  step. Risk classification gates irreversible containment actions.
  Human analysts review with SLA-enforced work items. The Merkle-
  chained ledger records every decision.
- **Convergence:** After containment executes, a desired-state graph
  models the expected post-containment state. The reconciliation
  engine verifies each action took effect. Divergence triggers human
  review — not silent failure.
- **Operations:** Resolved incidents feed back into CBR for future
  triage. Post-mortem knowledge enters the RAG corpus. Trust
  attestations update worker reliability scores. The next incident
  starts smarter.

<!-- SVG: soc-lifecycle-spine -->

---

## Step-by-Step Flow

A critical SIEM alert arrives. Here is how it moves through the
platform — every numbered step maps to a specific capability.

**1. Alert ingestion.**
A SIEM/EDR platform publishes a CloudEvent. The alert lands in the
Situation Awareness pipeline.

**2. Situation detection.**
`SiemAlertGanglion` evaluates the alert — severity classification,
confidence scoring. A second ganglion (`BruteForceDetectorGanglion`)
watches for authentication anomaly patterns. Three situation
definitions cover the detection surface.

**3. Incident case creation.**
The situation threshold is met. The Case Orchestration Engine creates
an `incident-investigation` case from the YAML case definition. The
blackboard is initialised with alert metadata.

**4. CBR retrieval.**
The Case-Based Reasoning engine retrieves the 3 most similar past
incidents — matching on alert type, source, severity, IOC patterns,
and ATT&CK technique. Retrieved cases inject context into the
investigation pipeline for all downstream workers.

**5. IOC enrichment.**
A rule-based worker extracts indicators of compromise — IP addresses,
domains, file hashes. A parallel LLM worker provides complementary
analysis. Trust-weighted routing selects between them based on
accumulated attestation evidence.

**6. ATT&CK mapping.**
The ATT&CK STIX 2.1 model — ingested into the Knowledge Graph as a
navigable MindMap subgraph — maps extracted IOCs to techniques, tactics,
groups, and mitigations. `T1566.001 Spearphishing Attachment` is
identified under `TA0001 Initial Access`. Structural graph queries, not
string matching.

**7. RAG enrichment.**
The Corpus Knowledge & Retrieval engine pulls relevant threat
intelligence prose from two corpora: the ATT&CK reference corpus and
a per-tenant internal knowledge corpus built from past post-mortems.
Three-leg hybrid search (dense + sparse + reranking) ensures retrieval
quality.

**8. Containment recommendation.**
An investigation worker synthesises all enrichment (IOCs, ATT&CK
mapping, CBR precedents, RAG context) and produces a containment
recommendation. For this alert: `ISOLATE_HOST` with risk score 0.85.

**9. Risk classification gate.**
`SocActionRiskClassifier` evaluates the recommended action against 9
action types and 4 gate policies (`NEVER`, `ALWAYS`,
`RISK_SCORE_THRESHOLD`, `CONFIDENCE_THRESHOLD`). `ISOLATE_HOST` has
policy `ALWAYS` — every host isolation requires human approval,
regardless of confidence. Fail-closed semantics: unknown actions are
gated by default.

**10. Human approval.**
A WorkItem is created for the `soc-manager` role with a 30-minute P1
SLA. `SocSlaBreachPolicy` defines the escalation chain: P1 (30 min) →
P2 (1 hour) → P3 (4 hours), with tier-based routing to progressively
senior analysts. The analyst reviews the enriched context — IOCs,
ATT&CK narrative, CBR precedents, RAG intelligence — and confirms.

**11. Containment commitment.**
`SocContainmentCommitmentBridge` publishes the containment decision as
a qhorus speech act (`PROPOSE → DONE/DECLINE/STATUS`) on the oversight
channel. This is normative accountability — not just logging, but a
structured commitment lifecycle with audit semantics.

**12. Containment execution.**
The platform dispatches to the appropriate containment connector —
CrowdStrike Falcon for host isolation, Palo Alto for network
segmentation, Okta/Azure AD for credential revocation. Three
connectors, one dispatch SPI.

**13. Desired-state recovery verification.**
This is where CaseHub diverges from every SOAR tool.

After containment executes, a desired-state graph models the expected
post-containment state. `SocContainmentNodeSpec` — a sealed hierarchy
with 8 variants covering every containment action type — represents
each action as a reconciliation target. `SocActualStateAdapter` polls
the connector to determine whether the action actually took effect.
`SocRecoveryVerificationListener` (a `GlobalReconciliationListener`)
tracks convergence across all containment nodes and signals the case
when all nodes verify.

If a node diverges — the CrowdStrike API reports the host is still
reachable — `SocContainmentFaultPolicyProducer` creates a divergence
review node, gated for human investigation. The system does not
silently report success.

**14. Trust attestation.**
`SocAttestationService` writes an attestation anchored to the
investigation's ledger entry. Bayesian trust scores update for every
worker that participated. Workers whose enrichment proved accurate
gain trust; workers whose recommendations were overridden lose trust.
Future routing adapts.

**15. CBR retention.**
`SocCbrRetainService` stores the resolved incident with its full
problem/solution/outcome triple. The next similar alert will retrieve
this resolution — investigation plans, containment decisions, and
analyst rationale — as context for triage.

**16. RAG corpus ingestion.**
`SocKnowledgeIngestor` feeds the resolved incident into the internal
RAG corpus. Post-mortem analysis becomes searchable prose intelligence
for future investigations.

**17. Ledger seal.**
A `SocLedgerEntry` (JOINED inheritance from the platform's
`JpaLedgerEntry`) seals the full decision chain: `ALERT_TRIAGE →
INCIDENT_PROMOTED → CONTAINMENT_GATE_DECISION → CONTAINMENT_APPROVAL
→ CONTAINMENT_EXECUTED → INCIDENT_RESOLVED`. Every step is
Merkle-chained with independent verification. DORA response time
captured and reportable.

<!-- SVG: soc-step-flow-diagram -->

---

## Capabilities in Play

| Step | Capability | What it does |
|------|-----------|-------------|
| 1–2 | Situation Awareness | 2 ganglia classify alerts, 3 situation definitions cover the detection surface |
| 3 | Case Orchestration | YAML case definition creates investigation; blackboard initialised |
| 4 | Case-Based Reasoning | Retrieves similar past incidents; injects context for all downstream workers |
| 5 | Worker Infrastructure | Dual rule/LLM workers; trust-weighted routing selects best candidate |
| 6 | Knowledge Graph | ATT&CK STIX 2.1 as navigable MindMap subgraph; structural technique mapping |
| 7 | Corpus Knowledge & Retrieval | Three-leg hybrid search across ATT&CK and internal corpora |
| 8 | Worker Infrastructure | Investigation worker synthesises all enrichment into recommendation |
| 9 | Risk Classification | 9 action types, 4 gate policies, fail-closed semantics |
| 10 | Human Task Management | SLA-enforced WorkItem with P1/P2/P3 escalation chain |
| 11 | Agentic Communications Mesh | Containment decision as speech act on oversight channel |
| 12 | External Connectors | CrowdStrike, Palo Alto, Okta — one dispatch SPI |
| 13 | Desired-State Reconciliation | 8 NodeSpec variants model containment as reconciliation targets |
| 14 | Trust & Accountability Ledger | Bayesian trust update from attestations; routing adapts |
| 15–16 | Case-Based Reasoning + RAG | Resolved incident feeds CBR and knowledge corpus |
| 17 | Trust & Accountability Ledger | Merkle-chained decision record; DORA-reportable |

Thirteen distinct platform capabilities participate in a single
incident flow. No capability was built for SOC — each is a
domain-agnostic primitive that the SOC application composes through
YAML case definitions and CDI wiring.

---

## Without CaseHub

How does this flow look on existing SOAR platforms?

### Splunk SOAR / Palo Alto XSOAR / Microsoft Sentinel

| Capability | SOAR tools | CaseHub |
|-----------|-----------|---------|
| **Alert triage** | Rule-based playbooks. Static conditions. No learning from outcomes. | Dual rule/LLM workers with trust-weighted routing. CBR retrieves similar past incidents to inform triage. Routing improves with every resolution. |
| **Threat enrichment** | API integrations. Each integration is a bespoke connector with its own error handling. | ATT&CK as a navigable knowledge graph (not a tag taxonomy). RAG retrieval from internal post-mortems. Both are platform primitives, not SOC-specific code. |
| **Containment execution** | Playbook actions fire API calls. Success = HTTP 200. | Containment modelled as desired-state reconciliation. Success = actual state matches desired state, verified by polling. Divergence creates human-gated review. |
| **Post-containment verification** | Not modelled. Dashboards show action completion, not action effectiveness. | Desired-state reconciliation with 8 typed NodeSpec variants. Fault policies create divergence review nodes. Silent failure is structurally impossible. |
| **Accountability** | Audit log (append-only text). No cryptographic integrity. No attestation model. | Merkle-chained ledger with independently verifiable inclusion proofs. Trust attestations anchored to specific decisions. DORA-reportable. |
| **Organisational learning** | Static playbooks. Manual post-mortem documents. Knowledge lives in analysts' heads. | CBR stores every resolved incident with problem/solution/outcome. RAG ingests post-mortems. Trust scores update. Next incident starts with all prior institutional knowledge. |
| **SLA enforcement** | Timer-based alerts. No structured escalation policy. | Typed SLA breach policy with P1/P2/P3 escalation chains. Tier-based routing to progressively senior analysts. SLA compliance is auditable. |

The core gap: SOAR tools automate response *execution*. They do not
model response *verification*, response *learning*, or response
*accountability*. CaseHub does all three because they are platform
primitives — not SOC-specific features.

---

## What the Platform Proves

### Containment as Reconciliation

The standout capability in this use case is desired-state recovery
verification. No SOAR tool models post-containment state as a
reconciliation problem.

CaseHub's Desired-State Reconciliation engine was built for
infrastructure convergence — declaring what state you want and letting
the platform drive reality toward it. The SOC application reuses the
same engine, the same `NodeProvisioner` SPI, the same
`GlobalReconciliationListener` contract, and the same fault policy
model. The only SOC-specific code is the 8 `SocContainmentNodeSpec`
variants that describe what "contained" means for each action type.

This is the composability thesis in action. A capability built for
infrastructure management — with zero knowledge of security operations
— solves the hardest problem in incident response: knowing whether
your containment actually worked.

### Thirteen Capabilities, One Flow

The incident flow traverses 13 platform capabilities. Each capability
is a standalone module — Situation Awareness, Case Orchestration,
Case-Based Reasoning, Worker Infrastructure, Knowledge Graph, Corpus
Retrieval, Risk Classification, Human Task Management, Agentic
Communications, External Connectors, Desired-State Reconciliation,
Trust & Accountability Ledger. None was designed for SOC. All compose
through CDI wiring and YAML case definitions.

The SOC application itself is 272 Java files across 2 Maven modules.
The platform it stands on is 500+ modules. The ratio tells the story:
domain-specific code is thin because the platform provides the hard
parts — accountability, trust, learning, orchestration, reconciliation
— as shared infrastructure.

### The Feedback Loop

The lifecycle spine closes:

- **Operations → Intelligence:** Resolved incidents feed CBR and RAG.
  Future triage is informed by every past resolution.
- **Operations → Control:** Trust attestations update worker scores.
  Future routing reflects accumulated evidence about worker accuracy.
- **Operations → Declaration:** Persistent situations (brute force
  patterns, recurring threat sources) can trigger new case
  definitions — the platform adapts its own investigation templates.

Every incident makes the next one faster, more accurate, and more
accountable. This is not a feature — it is the architectural
consequence of building on a platform where learning, trust, and
accountability are structural primitives.
