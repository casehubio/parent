---
theme: default
title: CaseHub — Reference Architectures
info: |
  CaseHub application reference architectures.
  The problems they solve, the differentiators they deliver.
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
controls: false
---

# CaseHub Reference Architectures

## Proven in the domains where accountability matters most.

*Written by LLMs, for LLMs.*  
*An accelerant for AI-Fusion driven digital transformations.*

---
layout: center
---

# Why Reference Architectures?

The platform is the foundation.  
The reference architectures are the reason to care.

Each one demonstrates CaseHub solving a real, regulated, high-stakes domain — where accountability is not optional, where AI cannot simply "try its best," and where existing tools structurally fail.

**If CaseHub can coordinate AML investigators, clinical trial sites, and code reviewers — it can coordinate your domain.**

---
layout: section
---

# Anti-Money Laundering

*casehub-aml*

---

# AML: The Problem

**Financial crime investigations today are broken at the foundation.**

Every major bank runs some variant of this:
- Analysts manually reviewing thousands of transaction alerts
- Coordination via email and spreadsheet — no formal record of who committed to what
- SAR (Suspicious Activity Report) decisions with no tamper-evident audit trail
- Agent routing based on availability, not expertise or track record
- When regulators ask "who decided this and why?" — the answer is often a guess

**The regulatory cost is real.** FinCEN (the US Financial Crimes Enforcement Network) requires provable audit chains. GDPR Art.17 requires that PII can be erased without destroying the audit record. Most systems fail both.

**The AI problem is worse.** LLM-assisted AML systems can reason about transactions — but they cannot *commit* to outcomes. There is no formal record that Agent X promised to investigate Pattern Y by Deadline Z.

---

# AML: Why Existing Approaches Fail

<div class="grid grid-cols-2 gap-8 mt-2">
<div>

**Workflow platforms (Pega, Appian)**
- Audit trail exists — but not cryptographically tamper-evident
- Human-only workflows — AI agents are bolted on, not first-class
- No adaptive routing — senior investigators get routed same as junior
- Compliance bolt-on, not structural

**Raw LLM agents**
- No formal commitment lifecycle
- No SLA enforcement on investigation tasks
- Cannot produce a FinCEN-defensible audit chain
- Hallucination risk with no accountability gate

</div>
<div>

**Custom-built systems**
- High cost, high maintenance
- FinCEN compliance requires constant audit work
- GDPR erasure destroys audit records — or isn't implemented

**IBM AMLSim (open source baseline)**
- Simulation only — not a coordination platform
- No commitment lifecycle, no trust routing
- No human oversight gates for high-risk decisions

CaseHub closes all of these gaps **structurally** — invariants guaranteed by the foundation, not features bolted on.

</div>
</div>

---

# AML: What CaseHub Delivers Differently

**Tamper-evident accountability, from investigation trigger to SAR filing.**

**Cryptographic audit chain**  
Every agent action, every human decision, every SAR filing is recorded as a Merkle Mountain Range entry — independently verifiable, GDPR-erasure-safe, FinCEN-defensible.

**Formal commitment lifecycle**  
Agents don't just "work on" cases. They *commit* to outcomes with deadlines. COMMAND → investigation accepted. DONE → findings reported. DECLINE → case rerouted. Every interaction is a speech act with a formal record.

**Trust-weighted routing**  
Bayesian Beta trust scores, built from SAR outcomes, route complex cases (PEP detection, high-risk entities) to the agents with the strongest track records. The system gets smarter with every investigation.

**Human oversight gates**  
Consequential actions — SAR filing, entity link creation — require human approval before proceeding. The gate is a formal WorkItem with a 30-day FinCEN SLA. Missed deadlines trigger escalation automatically.

**Adaptive investigation paths**  
Entity type, risk score, and PEP detection determine which specialist agents are engaged — dynamically, not by fixed rules.

---

# AML: Evidence

**Market fit score: 44/50** — strongest of all evaluated use cases, strong on both market relevance and community fit.

**Java developer audience** — the primary financial services development language. Same stack, same patterns, zero platform mismatch.

**Comparison baseline: IBM AMLSim** (industry-standard simulation dataset)  
CaseHub provides what AMLSim cannot: a production-grade coordination harness, not just a simulation.

**Compliance gaps closed structurally:**
- FinCEN tamper-evident audit chain
- GDPR Art.17 token-severing erasure without breaking the audit record
- Formal agent obligations (COMMAND creates Commitment — DECLINE ≠ FAILED)
- 30-day SAR SLA with automatic escalation
- PEP and high-risk-score oversight gates

**The flywheel:** each SAR outcome writes a trust attestation. Future investigations route to higher-trust agents. The platform gets more effective with every case.

---
layout: section
---

# Clinical Trial Coordination

*casehub-clinical*

---

# Clinical Trials: The Problem

**Running a clinical trial across multiple sites is a coordination crisis waiting to happen.**

A Phase III trial might span 20+ sites, hundreds of patients, and dozens of investigators. The regulatory requirements are non-negotiable:

- **GCP (Good Clinical Practice):** Every protocol deviation requires named PI (Principal Investigator) authorisation — formal, documented, traceable
- **FDA (US Food and Drug Administration) / EMA:** Tamper-evident audit trail for every AI-agent decision
- **CTCAE Grade 4+ adverse events (life-threatening):** Escalation to Data Safety Monitoring Board within defined windows
- **IND expedited safety reporting:** Unexpected adverse events require regulatory notification within 7–15 days
- **GDPR Art.17:** Patient consent withdrawal must erase PII without destroying the trial audit record

**Today this coordination happens via email, phone calls, and paper forms.** Sites miss escalation windows. Protocol deviations go undocumented. DSMB rollups across sites are manual aggregations in spreadsheets. The result: regulatory risk, patient safety risk, and trial delays.

---

# Clinical Trials: What CaseHub Delivers Differently

**GCP and FDA compliance structurally guaranteed — not audited for after the fact.**

**24-hour SLA enforcement**  
Serious adverse events trigger a WorkItem for the safety monitor with a hard 24-hour GCP deadline. Miss it — automatic escalation. Every step is a formal commitment with a ledger entry.

**Adaptive protocol paths**  
CTCAE Grade 4 events route to senior monitors and DSMB in parallel. Grade 3 with unexpected pattern routes to IND expedited reporting. The routing is declared in the case plan — not hardcoded in imperative logic.

**Multi-site DSMB rollup**  
When multiple sites hit Grade 4+ events simultaneously, a trial-level case aggregates the signals and triggers the Data Safety Monitoring Board review automatically.

**Cryptographic audit trail**  
Every AI-agent decision carries an EU AI Act Art.12 `ComplianceSupplement`. The complete audit chain — from adverse event report to PI authorisation to DSMB decision — is a Merkle-verifiable record.

**Trust-weighted safety routing**  
Safety agents build Bayesian Beta trust scores from case outcomes. Complex, high-acuity cases route to the agents with the strongest safety track records.

**Comparison baseline:** ClinicalAgent (arXiv 2404.14777) — peer-reviewed open-source clinical AI. CaseHub provides 10 capabilities ClinicalAgent structurally cannot.

**Market fit score: 24/25** — highest of all evaluated use cases.

---
layout: section
---

# Software Development Coordination

*casehub-devtown*

---

# Software Development: The Problem

**Code review today has no accountability.**

A developer opens a pull request. Three colleagues click "approve." The PR merges. Six months later, a production incident is traced back to a security vulnerability that was present in that PR.

Who reviewed it? What did they look for? What did they miss? What was the security reviewer's track record on Rust code specifically?

**The honest answer: nobody knows.**

Current tools (GitHub, GitLab) record that approval happened. They do not record:
- What the reviewer *committed* to review
- Whether they have the expertise for this type of change
- Their track record on similar reviews
- A tamper-evident chain linking the review decision to the production incident

**When security issues reach production, organisations cannot trace them.** They cannot demonstrate to auditors what review occurred. They cannot learn systematically from reviewer gaps.

---

# Software Development: What CaseHub Delivers Differently

**Formal reviewer accountability — from PR to production incident.**

**Trust-weighted reviewer selection**  
Review thoroughness, false-positive rate, and scope calibration dimensions are tracked per reviewer. Security-sensitive PRs route to reviewers with proven security track records. Architecture changes route to architects. The system learns from outcomes.

**Formal commitment per review**  
Reviewers don't just click approve. They accept a COMMAND commitment. DECLINE when outside their expertise triggers rerouteing — not silent rejection. Every review is a formal act with a ledger entry.

**Tamper-evident review record**  
Every merge decision is a Merkle Mountain Range entry. When a production incident occurs, the audit chain shows exactly what was reviewed, by whom, with what track record, and what the reviewer committed to.

**Production incident feedback loop**  
When a production incident is traced to a missed finding, a FLAGGED attestation is written against that reviewer for that capability. Their trust score drops. Future security reviews route away from them. The system gets harder to fool over time.

**GDPR-compliant actor erasure**  
Reviewer identities can be pseudonymised without destroying the audit record — essential for right-to-erasure compliance in jurisdictions where reviewers are EU employees.

---
layout: section
---

# Multi-Participant Document Review

*casehub-drafthouse*

---

# Document Review: The Problem

**LLM document review today is one opinion with no accountability.**

You send a document to an LLM. It tells you what it thinks. You either trust it or you don't. There is no record of what it examined, what it concluded, or what it missed. If a second LLM disagrees, you have two opinions and no resolution mechanism.

**Human document review is a bottleneck.** Senior reviewers are expensive. Reviews are subjective. There is no structured record of which critique was addressed, which was rejected and why, or what the final rationale was.

**The gap:** no existing tool provides structured, accountable, multi-participant review where every critique is a formal speech act grounded in the document, and the complete review record is auditable.

---

# Document Review: What CaseHub Delivers Differently

**Structured multi-LLM debate — every critique a formal speech act.**

**Multi-participant debate loop**  
Multiple LLM reviewers critique the same document. Each critique is a QUERY or COMMAND — a formal speech act with a Qhorus commitment. Other reviewers respond to critiques. The debate is structured, not a pile of opinions.

**Document-grounded review**  
Review is grounded in document diffs and specific sections, not in the reviewer's general knowledge. Critiques reference exactly what they're commenting on.

**Structured debate manifest**  
The complete review — every critique, every response, every resolution — is a deterministic `ChannelProjection<ReviewState>`. Human reviewers see a structured record, not a transcript.

**MCP tool surface**  
`start_review`, `update_selection`, `query_review`, `end_review` — LLM agents participate via MCP tools. Any MCP-capable agent can join the review.

**Ledger record**  
The final review decision is a ledger entry — tamper-evident, auditable, linkable to the document version reviewed.

---
layout: section
---

# Personal Life Automation

*casehub-life*

---

# Life Automation: The Problem

**The same coordination problems that plague enterprises also exist at home.**

Household management, elder care, health tracking, financial obligations, legal compliance — these are coordination problems. Tasks need SLAs. Commitments need tracking. Escalation needs to happen when something is missed.

**Today:** notes apps, calendar reminders, text messages. None of these enforce anything. None have formal accountability. A carer misses a medication window — there is no audit trail. A financial obligation is missed — no escalation fires. An elder care task expires — nobody knows.

The gap between "I meant to do this" and "this was done, by whom, by when, with what outcome" is exactly the gap CaseHub was built to close.

---

# Life Automation: The Vision

**The same foundation that coordinates clinical trial investigators and AML analysts — applied to household coordination.**

- Household tasks have WorkItems with SLAs and formal escalation chains
- OpenClaw agents (5,400+ pre-built skills) execute tasks as workers
- IoT devices (Home Assistant, OpenHAB) trigger case creation when something goes wrong
- Trust-weighted routing assigns experienced agents to complex tasks
- The same accountability primitives that close FinCEN SARs track your financial obligations

**Why it matters:** CaseHub proves the harness is domain-agnostic. Game AI at millisecond granularity. FDA-regulated clinical trials. Household chores. Same foundation. That is the argument for adopting it in *your* domain.

---
layout: section
---

# StarCraft II Game AI

*quarkmind — the living lab*

---

# Quarkmind: Proof of Generality

**If the harness holds at millisecond game-loop granularity — it holds everywhere.**

StarCraft II is a real-time strategy game. The game loop runs every 22 milliseconds. Agent decisions must be made at that cadence. Coordination between strategy, economics, tactics, and scouting agents must be instantaneous.

**This is the most demanding timing environment possible.** If CaseHub can coordinate agents here, it can coordinate agents anywhere.

**What quarkmind demonstrates:**

- `StrategyTrustRouter` — Bayesian Beta maturity model (BOOTSTRAP → QUALIFIED → BORDERLINE → EXCLUDED) routing among competing strategy implementations
- `GameOutcomeRecorder` — trust attestations written on every game end; strategy routing improves with every match
- Three.js 3D visualiser — 65+ unit sprites, fog of war, replay scrub — proving the platform generates observable, verifiable agent behaviour
- Validated against 30 IEM10 replays across PvT / PvZ / PvP matchups

**The clinical trial took days. QuarkMind runs in milliseconds. Same harness. Same SPIs. Same accountability model.**

That is the proof. The platform is not domain-specific. It is infrastructure.

