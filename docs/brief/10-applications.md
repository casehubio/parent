# The Application Portfolio

*Six domain applications — one platform, same CDI model, same YAML
surface, same accountability.*

---

## What This Proves

These are not demos. They are production-grade reference architectures
built entirely on the CaseHub platform, each bringing its own domain
logic while relying on the shared foundation for orchestration,
accountability, agent coordination, trust scoring, and learning.
No application modifies anything below it. No application knows about
any other application.

The portfolio spans regulated finance, pharmaceutical trials, security
operations, software development, IoT device management, and trading
automation. The same blackboard architecture, the same Merkle ledger,
the same YAML case definitions, the same composable signal routing —
applied to domains that share nothing except their need for
structured, accountable automation.

This breadth with this consistency is the platform's strongest
argument. Domain experts swap the YAML; the platform provides
everything else.

---

## AML — Anti-Money Laundering Investigation

### What It Is

End-to-end anti-money laundering investigation platform. From initial
alert triage through entity resolution, evidence gathering, risk
assessment, and SAR (Suspicious Activity Report) filing — with full
FinCEN-compliant audit trail. The most comprehensive reference
architecture in the portfolio: all 130 GitHub issues closed, 9-layer
tutorial complete, 332 Java source files.

### Capabilities

- 13 case definition capabilities with 20 bindings and 4 goals
- 16 specialised workers covering alert triage, entity matching, PEP
  screening, transaction analysis, network mapping, risk scoring,
  SAR drafting
- Rejection routing with 5 capabilities — a first-class YAML-declared
  adversarial path for when the compliance officer disagrees with the
  initial recommendation
- @McpDomain migration complete — tri-channel API surface
  (REST + GraphQL + MCP)

### How It Uses CaseHub

Leverages 14 platform capabilities from 10 foundation modules —
the highest count of any application. LLM agents operate through
`StructuredAgentInvoker` for entity resolution, PEP screening, and
risk narrative generation. Trust-weighted routing ensures that agents
with better track records on specific investigation types receive
higher-priority assignments. CBR (Case-Based Reasoning) drives the
triage pipeline: past investigation outcomes feed back into future
routing decisions, so the system learns which investigation strategies
work for which alert patterns. The Merkle ledger captures every
decision as a tamper-evident entry — not just for audit compliance,
but as the structural guarantee that the investigation trail is
independently verifiable.

### What's Interesting

The rejection routing subsystem is a genuine differentiator — most
investigation platforms treat disagreement as an edge case that
dead-ends the workflow. CaseHub treats it as a first-class path:
the compliance officer's rejection triggers a structured re-routing
with its own case plan, evidence requirements, and accountability
chain. This is declared in YAML, not coded as exception handling.
The 9-layer tutorial makes AML the best starting point for anyone
learning how to build a CaseHub application.

---

## Clinical — Clinical Trial Coordination

### What It Is

Clinical trial coordination platform covering the full lifecycle from
protocol activation through patient enrolment, adverse event
monitoring, safety reporting, and regulatory submission. Handles
multi-site trials with independent sub-cases per site, IND
(Investigational New Drug) safety deadline enforcement, and
DSMB (Data Safety Monitoring Board) batch signal processing.
All 173 GitHub issues closed. 376 main + 191 test Java source files.

### Capabilities

- 7 YAML case definitions covering trial lifecycle, site management,
  patient enrolment, adverse event processing, safety reporting
- 15 entities for clinical data capture: lab results, vitals,
  medications, study drugs, visits
- 22 ledger entry types for tamper-evident clinical audit
- 16 @McpDomain SPI interfaces — full tri-channel API
- 5 LLM agents for adverse event classification, cross-site signal
  detection, safety narrative generation

### How It Uses CaseHub

The blackboard architecture is particularly powerful here: adverse
event signals detected at one site can trigger cross-site aggregation
patterns that emerge from the case data rather than being pre-coded
as explicit workflows. Multi-site coordination uses sub-case
architecture — each trial site is an independent case with its own
lifecycle, but roll-up reporting aggregates across all sites for
regulatory submission. IND safety deadline enforcement uses the
SLA engine with hard regulatory deadlines (15-day and 7-day
reporting windows). CBR drives cross-site pattern matching —
when an adverse event at Site A resembles a prior event at Site B,
the system surfaces the similarity and its resolution history.

### What's Interesting

Clinical trials are the hardest test of the platform's multi-tenancy
and accountability guarantees. Patient data is tenant-scoped with
GDPR erasure support that produces tamper-evident erasure receipts.
The SLA breach algebra enforces FDA deadlines with the same
structural guarantees it provides for financial compliance — the
engine doesn't care whether the deadline is FinCEN or FDA. The
DSMB batch signal processing is entirely undocumented despite being
a substantial capability, highlighting how much domain depth these
applications contain beyond what their guides describe.

---

## SOC — Security Operations Centre

### What It Is

Multi-agent cyber incident response platform. A 9-step investigation
pipeline takes incidents from initial alert through threat
intelligence enrichment, forensic analysis, containment, eradication,
and recovery verification. Upgraded from scaffold to active status
during the Wave 3 audit — all 5 architectural layers are now
complete. 171 main + 101 test Java source files.

### Capabilities

- 9-step investigation pipeline: alert ingestion, triage, threat
  intel enrichment, forensic analysis, impact assessment,
  containment, eradication, recovery, lessons learned
- Desired-state recovery verification: 8 sealed `NodeSpec` variants,
  `NodeProvisioner`, `ActualStateAdapter`, `FaultPolicyProducer`,
  `RecoveryVerificationListener`
- 7 @McpDomain APIs for security operations
- 3 containment connectors: CrowdStrike, Palo Alto Networks,
  Okta/Azure AD
- ATT&CK STIX 2.1 model with 7 record types for structured threat
  intelligence

### How It Uses CaseHub

Leverages 13 platform capabilities in a single incident flow — the
highest density of any application. The alert ingestion pipeline
bridges CloudEvents through RAS ganglion evaluation into case
creation. LLM agents handle threat intelligence enrichment and
forensic analysis with oversight gates on containment actions — no
agent can isolate a production system without M-of-N quorum
approval. The desired-state reconciliation framework verifies
recovery: after containment and eradication, the platform declares
the expected system state and continuously reconciles until reality
matches the declaration. Trust-weighted routing ensures agents
with domain expertise in specific threat types (ransomware vs.
supply chain vs. insider threat) receive appropriate assignments.

### What's Interesting

The desired-state recovery verification is the standout feature.
Most SOAR platforms declare an incident "resolved" when a playbook
completes. CaseHub declares a desired state and verifies it
continuously — if the compromised system drifts back, the platform
detects it and triggers corrective action. This is the same
reconciliation engine that manages infrastructure topology, applied
to security incident recovery. The ATT&CK STIX 2.1 integration
gives agents structured threat intelligence rather than text
summaries.

---

## FSI Trading — Financial Trading Incident Response

### What It Is

Multi-agent trading automation platform covering strategy evaluation,
overnight bot management, market situation detection and response,
and regulatory compliance across MiFID II, Dodd-Frank, and MAR
(Market Abuse Regulation). Upgraded from scaffold to active status.
231 main + 121 test Java source files.

### Capabilities

- 3 case definitions with 5 YAML playbooks for trading scenarios
- 7 strategy agents + 13 incident response agents (20 total)
- 5-level temporal summarisation for trading event narratives
- 11 @McpDomain APIs (~40 operations) — full tri-channel surface
- 2 dock-workbench pages with 25+ panels for trading operations
- Epistemic deliberation for collaborative decision-making under
  uncertainty

### How It Uses CaseHub

Leverages 16 platform capabilities. YAML playbooks declare response
strategies for different market scenarios — the playbooks are
CBR-enhanced, learning from past trading outcomes to select better
response strategies. The 5-level temporal summarisation system
(using the neocortex temporal summarisation module) compresses
trading event histories at progressively coarser granularity,
giving agents both immediate context and long-term trend awareness.
Epistemic deliberation enables multiple agents to assess a trading
situation, express confidence levels, and converge on a decision
through structured debate with full accountability trail.

### What's Interesting

The YAML playbook system is the clearest demonstration of the
YAML-CBR bridge working end-to-end. A playbook declares a response
strategy. The strategy executes. The outcome is recorded. CBR
retrieves similar past situations on the next trigger. The playbook
selection adapts. This is the adaptive learning loop applied to
financial markets. The regulatory compliance layer (MiFID II,
Dodd-Frank, MAR) generates compliance evidence automatically
through the same Merkle ledger infrastructure that serves AML —
different regulations, same structural guarantee.

---

## DevTown — AI-Assisted Software Development

### What It Is

Software development automation platform. Handles PR review with
trust-weighted reviewer routing, merge queue with adaptive batch
composition and bisection, capability tagging, and SLA enforcement.
7 modules. 283 main + 196 test Java source files.

### Capabilities

- 4 YAML case definitions for PR lifecycle management
- 6 LLM reviewer agents via `StructuredAgentInvoker` with
  specialised review strategies
- 14 capabilities across 5 @McpDomain typed API classes + 3 GraphQL
  resolvers (~25 operations, full tri-channel)
- Reusable PR review template (`templates/pr-review` module)
- Trust-weighted reviewer routing with CBR-enhanced matching

### How It Uses CaseHub

The PR review lifecycle is modelled as a case plan: opening a PR
creates a case, reviewer assignment uses composable signal routing
(trust scores, workload, CBR similarity to past reviews),
oversight gates enforce approval quorum before merge, and the
merge queue uses the planning module for adaptive batch composition.
LLM agents are genuine participants — they review code through
`StructuredAgentInvoker`, produce structured review output, and
their trust scores evolve based on whether their recommendations
are accepted or overridden by human reviewers.

### What's Interesting

DevTown is the application the platform uses to develop itself.
The Hive Mind vision (autonomous self-improvement through CI)
runs through DevTown — agents propose improvements, submit them
as PRs, and the same trust-weighted review process evaluates the
agent's contributions alongside human ones. The reusable
`templates/pr-review` module makes the PR review pattern
available to any CaseHub application that needs structured
code review as part of its workflow.

---

## IoT — Device Management

### What It Is

Full lifecycle management for IoT devices — from situation detection
through AI-assisted resolution to human escalation with CBR learning.
Supports Home Assistant and OpenHAB as device providers. 12 modules.

### Capabilities

- Home Assistant and OpenHAB provider implementations with wire
  protocol bridge (7 sealed message variants)
- Ganglion-based situation detection for device anomalies
- AI resolution pipeline with CBR-driven fault matching
- Human escalation workflow through the work module
- Simulation framework for device behaviour testing

### How It Uses CaseHub

IoT demonstrates the complete lifecycle arc applied to the physical
world. RAS ganglia monitor device telemetry and detect anomalous
situations. The engine creates cases for detected issues. LLM agents
attempt resolution using CBR-matched historical fixes. If AI
resolution fails, the work module escalates to human operators
with full context. Outcomes feed back into CBR for future matching.
The simulation framework enables testing of device scenarios without
physical hardware.

### What's Interesting

IoT is the strongest end-to-end lifecycle proof point in the
portfolio. It demonstrates all five lifecycle stages
(Declaration → Intelligence → Control → Convergence → Operations)
applied to the physical world, not just software abstractions.
The vision for desired-state reconciliation of physical devices
(firmware versions, calibration state, operational mode declared
in YAML and reconciled continuously) extends directly from the
existing IoT architecture.

---

## What the Portfolio Proves

Six reference architectures across six unrelated domains. Each one
built by swapping the YAML case definitions and domain workers while
the platform provides orchestration, accountability, agent
coordination, trust scoring, learning, situation awareness, and
reconciliation.

The consistency is structural, not cosmetic. Every application
shares:

- **The same CDI context** — capabilities compose at runtime without
  integration glue. An AML agent's trust score uses the same
  EigenTrust algorithm as a trading agent's.
- **The same YAML surface** — a clinical trial coordinator and an
  IoT device manager express intent in the same declaration
  language. The runtime beneath is identical.
- **The same accountability guarantees** — Merkle-chained audit
  entries in AML investigations use the same tamper-evident
  structure as SOC containment decisions.
- **The same learning loop** — CBR feedback from AML triage,
  clinical adverse events, SOC incident patterns, and trading
  strategy outcomes all flow through the same retrieval-adapt-apply
  cycle.

Domain experts bring the domain. The platform provides everything
else. That is the value proposition — and the portfolio is the
proof.
