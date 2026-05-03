# CaseHub Use Case Analysis
## Market Entry and Tutorial Example Selection

> **Purpose:** Identify two use cases that (1) justify CaseHub as a market-ready platform in a regulated domain, and (2) serve as a compelling tutorial for Java/Quarkus developers. Two separate scoring tables reveal where use cases are strong vs where they fall away — a single combined score hides this.
>
> **Date:** 2026-05-03

---

## 1. What CaseHub Does That Competing Systems Do Not

Before scoring, the dimensions that matter are grounded in CaseHub's genuine structural capabilities — features that are essential to regulated multi-agent AI coordination, not cosmetic additions.

| Capability | What it means | Why it matters |
|---|---|---|
| **9-type speech-act normative layer** | Every agent message is typed: COMMAND, QUERY, RESPONSE, STATUS, DONE, FAILURE, DECLINE, HANDOFF, EVENT | Formal accountability — who asked, who committed, who failed, who handed off |
| **7-state commitment lifecycle** | OPEN → ACKNOWLEDGED → FULFILLED / DECLINED / FAILED / DELEGATED / EXPIRED | Obligation tracking: not just what happened, but who was accountable and whether they followed through |
| **Bayesian Beta trust scoring** | Auto-computed from attestation history; temporal decay; EigenTrust transitivity | Trust accumulates from evidence — routing improves without human stamps |
| **Adaptive Case Management** | Emergent paths from blackboard state — no fixed workflow declaration | Handles the unexpected: protocol amendments, adverse events, novel findings |
| **Human-in-the-loop with SLA** | WorkItem lifecycle with `claimDeadline`, escalation policy, delegation | Formal regulated HITL — not just "escalated to human" but with hard deadlines and audit trail |
| **Merkle tamper-evident audit** | Cryptographic inclusion proofs, Ed25519-signed checkpoints | Independently verifiable — regulator does not need server access to verify the record |
| **GDPR / EU AI Act compliance** | `LedgerErasureService`, `ComplianceSupplement`, `DecisionContextSanitiser` SPI | Purpose-built for regulated data — not bolted on |
| **Sub-case orchestration** | Cases spawn sub-cases with independent lifecycles and rollup | Multi-site trials, per-molecule pipelines, per-site enrollment — structural, not simulated |
| **LLM supervisor mode** | LLM reads CaseContext and selects next binding dynamically | Open-ended goals — next step cannot be determined without reasoning over current state |

**Key claim:** No existing open-source or published multi-agent LLM framework combines all nine. The research below maps existing systems against these capabilities.

---

## 2. Landscape Research

### 2.1 IT Domain Systems

| System | Type | Coordination | Key weaknesses vs CaseHub |
|---|---|---|---|
| **MyAntFarm** ([arXiv 2511.15755](https://arxiv.org/abs/2511.15755)) | Incident response orchestration | Centralised coordinator → specialist agents | No speech-act layer; no commitment lifecycle; no trust scoring; no HITL SLA; no compliance audit; fixed workflow only |
| **AutoReview** (FSE 2025) | Security-oriented code review | Sequential 3-agent pipeline | No normative layer; no commitment tracking; no human escalation; no regulatory compliance |
| **AutoSafeCoder** ([arXiv 2409.10737](https://arxiv.org/abs/2409.10737)) | Secure code generation | Collaborative feedback loops | No obligation semantics; no audit trail; fixed cycle |
| **i-GENTIC AI MedTech Suite** | FDA 510(k) submission consistency | Multi-layer compliance agents | Proprietary; no published commitment/trust framework; no Merkle audit |
| **DRF** ([arXiv 2509.05764](https://arxiv.org/abs/2509.05764)) | Trust-filtered multi-agent LLM | UCB-based reputation scoring | No speech acts; no commitment lifecycle; no compliance integration |
| **Nala framework** ([Springer 2023](https://link.springer.com/article/10.1007/s10472-023-09875-w)) | Commitment-based negotiation | Social commitment semantics | No trust scoring; no regulatory audit; not productionised |

### 2.2 Non-IT Domain Systems

| System | Type | Coordination | Key weaknesses vs CaseHub |
|---|---|---|---|
| **ClinicalAgent** ([arXiv 2404.14777](https://arxiv.org/abs/2404.14777), [GitHub](https://github.com/LeoYML/clinical-agent)) | Clinical trial coordination | Sequential specialist agents, GPT-4 + ReAct | No accountability; no SLA; no GCP compliance; no GDPR; no commitment lifecycle; single-case only |
| **TrialGenie** ([medRxiv 2025](https://www.medrxiv.org/content/10.1101/2025.04.17.25326033v1)) | Clinical trial design | Iterative refinement, Shapley attribution | No formal commitment model; no tamper-evident audit; no SLA escalation |
| **Prompt-to-Pill** ([Oxford Academic 2024](https://academic.oup.com/bioinformaticsadvances/article/6/1/vbaf323/8403080), [GitHub](https://github.com/ChatMED/Prompt-to-Pill)) | Drug discovery pipeline | 3-phase orchestration, dynamic agent selection | No trust scoring; no commitment tracking; no GxP/21 CFR compliance; no Merkle audit |
| **Tippy** ([arXiv 2507.09023](https://arxiv.org/abs/2507.09023)) | Drug discovery DMTA cycle | Supervisor + 4 specialists + guardrails | No inter-agent obligation lifecycle; no tamper-evident logging; no GxP compliance |
| **LegalAgentBench** ([ACL 2025](https://aclanthology.org/2025.acl-long.116.pdf), [GitHub](https://github.com/HKUST-KnowComp/MASLegalBench)) | Legal task evaluation | IRAC task decomposition | No privilege protection; no chain-of-custody; no audit trail; evaluation only |
| **MASLegalBench** ([arXiv 2509.24922](https://arxiv.org/abs/2509.24922)) | Legal reasoning benchmark | Deductive reasoning agents | Benchmark only; no accountability; no GDPR implementation |
| **Agentic AML (industry)** | AML investigation | ReAct-based transaction analysis + SAR drafting | No formal evidence chain (required by FinCEN 2024); append-only logs inconsistent; no commitment per investigation |
| **IBM AMLSim** ([GitHub](https://github.com/IBM/AMLSim/)) | Transaction simulation | Multi-agent transaction simulation | Simulation only; no LLM reasoning; no accountability layer |
| **Virtual Biotech** ([bioRxiv Feb 2026](https://www.biorxiv.org/content/10.64898/2026.02.23.707551v1)) | Drug discovery | Hierarchical CSO + scientist agents | Human-in-loop mentioned but no SLA/escalation formalism; no regulatory compliance |

### 2.3 What No Existing System Has

| Feature | Systems that have it |
|---|---|
| Formal speech-act protocol (9 types) | Nala (partial, negotiation-only) |
| 7-state commitment/obligation lifecycle | Nala (partial) |
| Bayesian Beta + EigenTrust trust scoring | DRF (UCB-based only, no transitivity) |
| Adaptive Case Management (emergent paths) | None |
| HITL with formal SLA + escalation | None |
| Merkle tamper-evident audit | None |
| GDPR/EU AI Act compliance | None |
| Sub-case orchestration | None |
| LLM supervisor mode (blackboard-driven) | None |

---

## 3. Ten Candidate Use Cases

| # | Use Case | Domain | Primary comparison target | Target open source? |
|---|---|---|---|---|
| 1 | Security incident response (CIRT) | IT | MyAntFarm ([arXiv 2511.15755](https://arxiv.org/abs/2511.15755)) | ✅ GitHub |
| 2 | Regulated software code review (DO-178C / FDA) | IT | AutoReview (FSE 2025) | ⚠️ Not yet |
| 3 | FDA 510(k) regulatory filing | IT/Pharma | i-GENTIC AI (Feb 2026) | ❌ Proprietary |
| 4 | Clinical trial coordination | Healthcare | ClinicalAgent ([arXiv 2404.14777](https://arxiv.org/abs/2404.14777)) | ✅ GitHub |
| 5 | Legal discovery & document review | Legal | LegalAgentBench ([ACL 2025](https://aclanthology.org/2025.acl-long.116.pdf)) | ✅ GitHub |
| 6 | Drug discovery pipeline | Pharma | Prompt-to-Pill ([Oxford 2024](https://academic.oup.com/bioinformaticsadvances/article/6/1/vbaf323/8403080)) | ✅ GitHub |
| 7 | Anti-money laundering investigation | Finance | IBM AMLSim + industry whitepapers | ✅ GitHub (simulation) |
| 8 | Insurance claims adjudication | Insurance | Accenture / V7 Labs case studies | ❌ Industry only |
| 9 | Scientific research pipeline | Academia | AutoGen / MetaGPT applied to research | ✅ GitHub |
| 10 | AI-assisted radiology triage | Healthcare | PMC multiagent AI survey | ❌ No flagship |

---

## 4. Evaluation Framework

### Dimension Definitions

**Market Fit** — can we justify entering this market with a genuinely differentiated offering?

| Dimension | Definition |
|---|---|
| **Platform differentiation** | CaseHub's distinctive features (speech acts, commitments, trust, ACM, compliance) are *essential*, not cosmetic. Score low if the feature set could be approximated by a simpler system. |
| **Compliance necessity** | Regulation *requires* the compliance capabilities — not optional. High = GCP, GxP, FinCEN, GDPR with real enforcement and legal consequences. |
| **Market entry gap** | Is there a real opening — no compliant incumbent, regulation not met by existing solutions? High = genuine gap. Low = crowded market (SOAR tools, CTMS vendors, XSOAR). |
| **Comparison richness** | Is there a peer-reviewed, open-source comparison target with clear documented weaknesses we can point to honestly and specifically? |
| **Market size** | Does winning here translate to meaningful commercial value? |

**Community Fit** — does this work as a Java/Quarkus tutorial that the target audience immediately connects with?

| Dimension | Definition |
|---|---|
| **Java/Quarkus developer relatability** | Would a Java enterprise developer immediately recognise this problem from their own industry and daily work? Banking → 5. Pharma wet lab → 1. |
| **Human relatability** | Does a general audience understand the stakes without domain knowledge? Life-or-death and financial consequences score higher. |
| **Tutorial teachability** | Can this be implemented as a coherent Quarkus demo/tutorial without domain expertise? Can you follow the scenario in 10 minutes without a PhD? |
| **LLM depth** | Does the use case genuinely exercise complex LLM reasoning — multi-step judgment, knowledge synthesis, adaptive decisions — not just classification? |
| **Accountability drama** | Is there a vivid, compelling failure mode that CaseHub prevents? Does the audience immediately feel "yes, that would be catastrophic"? |

---

## 5. Market Fit Scores

*5 dimensions × 5 max = 25 points*

| # | Use Case | Platform diff | Compliance necessity | Market entry gap | Comparison richness | Market size | **/25** |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | Clinical trial coordination | 5 | 5 | 4 | 5 | 5 | **24** |
| 6 | Drug discovery pipeline | 5 | 5 | 4 | 5 | 5 | **24** |
| 7 | AML investigation | 5 | 5 | 4 | 3 | 5 | **22** |
| 5 | Legal discovery | 4 | 5 | 3 | 4 | 4 | **20** |
| 1 | Security incident response | 4 | 3 | 2 | 5 | 5 | **19** |
| 8 | Insurance claims | 4 | 4 | 3 | 3 | 5 | **19** |
| 2 | Regulated code review | 4 | 5 | 3 | 4 | 3 | **19** |
| 10 | Radiology triage | 4 | 5 | 3 | 3 | 4 | **19** |
| 3 | FDA 510(k) filing | 3 | 5 | 2 | 2 | 3 | **15** |
| 9 | Scientific research | 3 | 2 | 2 | 3 | 3 | **13** |

**Key insight:** Drug discovery matches clinical trials on market fit but collapses in community fit — ruled out as a tutorial candidate. Security incident response scores only 2 on market entry: SOAR is dominated by Palo Alto XSOAR, Splunk SOAR, and IBM QRadar with deep integrations. MyAntFarm is a strong comparison target but does not represent a real market gap.

---

## 6. Community Fit Scores

*5 dimensions × 5 max = 25 points*

| # | Use Case | Java relatability | Human relatability | Tutorial teachability | LLM depth | Accountability drama | **/25** |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 8 | Insurance claims | 5 | 5 | 5 | 3 | 4 | **22** |
| 7 | AML investigation | 5 | 4 | 4 | 4 | 5 | **22** |
| 1 | Security incident response | 4 | 5 | 4 | 4 | 5 | **22** |
| 5 | Legal discovery | 3 | 4 | 3 | 5 | 5 | **20** |
| 4 | Clinical trial coordination | 2 | 5 | 2 | 5 | 5 | **19** |
| 2 | Regulated code review | 4 | 3 | 3 | 3 | 4 | **17** |
| 9 | Scientific research | 2 | 3 | 5 | 5 | 2 | **17** |
| 10 | Radiology triage | 1 | 5 | 2 | 4 | 5 | **17** |
| 6 | Drug discovery pipeline | 1 | 4 | 1 | 5 | 4 | **15** |
| 3 | FDA 510(k) filing | 1 | 2 | 1 | 3 | 2 | **9** |

**Key insight:** Clinical trials scores only 2 on Java relatability and 2 on tutorial teachability — it requires understanding GCP and clinical protocol structure to follow the scenario. Drug discovery is worse (1/1). Both are compelling market stories but poor tutorial candidates.

---

## 7. Combined View

| # | Use Case | Market /25 | Community /25 | Total /50 | Shape |
|---|---|:-:|:-:|:-:|---|
| 7 | **AML investigation** | 22 | 22 | **44** | ✅ Balanced — strong on both |
| 4 | **Clinical trial coordination** | **24** | 19 | **43** | Market-heavy |
| 1 | Security incident response | 19 | 22 | **41** | Community-heavy, weak market entry |
| 8 | Insurance claims | 19 | 22 | **41** | Community-heavy, weaker market story |
| 5 | Legal discovery | 20 | 20 | **40** | Balanced — moderate on both |
| 6 | Drug discovery | **24** | 15 | **39** | Market-heavy, unusable as tutorial |
| 2 | Regulated code review | 19 | 17 | **36** | Average on both |
| 10 | Radiology triage | 19 | 17 | **36** | Average on both |
| 9 | Scientific research | 13 | 17 | **30** | Weak market, acceptable tutorial |
| 3 | FDA 510(k) filing | 15 | 9 | **24** | Weak on both |

---

## 8. Selected Use Cases

### 8.1 Use Case 1: Clinical Trial Coordination

**Purpose:** Market entry argument — demonstrates CaseHub in a domain where compliance is mandatory and naive LLM approaches structurally fail.

**Comparison target:** ClinicalAgent ([arXiv 2404.14777](https://arxiv.org/abs/2404.14777), [GitHub](https://github.com/LeoYML/clinical-agent)) — peer-reviewed (ACM BCB '24), fully open-source, demonstrably lacking the capabilities CaseHub provides.

**The compliance gap ClinicalAgent cannot close by adding features:**

| GCP / ICH requirement | ClinicalAgent | CaseHub |
|---|---|---|
| **Adverse event SLA** — serious events reported within 24h, others within 7 days | No deadline tracking | WorkItem `claimDeadline` with auto-escalation |
| **Protocol deviation authorisation** — deviations require documented PI approval | Agent decides autonomously; no named responsible party | COMMAND from PI required; commitment lifecycle tracks acknowledgement and resolution |
| **Consent withdrawal cascade** — GDPR Art.17 erasure of patient data | No GDPR capability | `LedgerErasureService` + `DecisionContextSanitiser` SPI |
| **Multi-site independence** — 50+ sites with independent status rollup to trial level | Single-case linear pipeline | Sub-case orchestration per site with trial-level aggregation |
| **Tamper-evident audit** — FDA audit trail must be independently verifiable | No audit trail | Merkle Mountain Range + Ed25519-signed checkpoints |
| **Trust-weighted agent assignment** — safety-critical assessments routed to reliable agents | No trust model | Bayesian Beta + EigenTrust routing via `TrustWeightedSelectionStrategy` |

**The failure mode:** A patient is wrongly enrolled, or an adverse event is missed. At FDA audit, the sponsor must show the decision chain — who was notified, who acknowledged, who escalated, what they decided. ClinicalAgent produces none of this. The claim is not "CaseHub is better than ClinicalAgent" — it is "ClinicalAgent demonstrates that naive LLM coordination fails in regulated settings, and CaseHub is the foundation that makes it work."

**What this exercises on the platform:**
- Adaptive Case Management (protocol amendments trigger path changes)
- Sub-case orchestration (per-site, per-patient)
- WorkItem with SLA and escalation (IRB approvals, adverse event reporting)
- Full normative layer (COMMAND/RESPONSE/DONE between agents, DECLINE when eligibility fails)
- Commitment lifecycle (eligibility assessor commits to screening result)
- Trust scoring (reliable adverse-event agents get routed sensitive cases)
- GDPR Art.17 erasure and Merkle audit
- EU AI Act Art.12 ComplianceSupplement

---

### 8.2 Use Case 2: Anti-Money Laundering Investigation

**Purpose:** Tutorial/community example — demonstrates CaseHub in a domain every Java enterprise developer recognises, teaches all platform features in a scenario followable without domain expertise.

**Comparison targets:**
- IBM AMLSim ([GitHub](https://github.com/IBM/AMLSim/)) — open-source transaction simulation baseline
- AnChain / Sardine industry whitepapers — documented weaknesses in current agentic AML implementations
- FinCEN 2024 guidance — explicit compliance requirements that current systems do not meet

**Why Java/Quarkus developers immediately connect:**
Java dominates banking and financial services infrastructure. Enterprise Java developers at any major financial institution have built or integrated transaction monitoring systems, case management tools, and compliance reporting pipelines. They know the pain first-hand: audit trails that cannot reconstruct the decision chain, human escalation that fires too late or not at all, and SAR (Suspicious Activity Report) filings where nobody can say which agent recommended the outcome.

**The investigation flow (tutorial scenario):**

```
Transaction flagged (EVENT)
    ↓
[Entity Resolution Agent] — COMMAND: resolve beneficial ownership
    ↓ RESPONSE: entity graph
[Transaction Pattern Agent] — COMMAND: assess layering/structuring patterns
    ↓ RESPONSE: risk assessment
[OSINT Agent] — COMMAND: gather external evidence (sanctions lists, PEP databases)
    ↓ RESPONSE: adverse media findings
[Case Narrative Agent] — COMMAND: draft SAR narrative
    ↓ STATUS: narrative in progress
    ↓ DONE: narrative complete
[Compliance Officer] — WorkItem: review and sign SAR
    claimDeadline: 30 days (regulatory SLA)
    escalation: head of compliance if missed
    ↓ DONE: SAR filed / DECLINE: case cleared
[Ledger] — attestation written; trust scores updated
```

**The compliance gap current systems cannot close:**

| FinCEN/FATF requirement | Current agentic AML | CaseHub |
|---|---|---|
| **Auditable evidence chains** — who recommended what and why | Append-only logs inconsistent; no decision attribution | Commitment per agent task; `causedByEntryId` chains the full investigation |
| **Human sign-off on SAR filing** — compliance officer must verify | Ad-hoc escalation; no formal SLA | WorkItem with 30-day `claimDeadline`; auto-escalation to head of compliance |
| **GDPR on transaction data** — PII in financial records | Not addressed | `LedgerErasureService` + `DecisionContextSanitiser` |
| **Tamper-evident investigation record** — regulators and prosecutors need verifiable chain | No cryptographic audit | Merkle inclusion proofs; independently verifiable without server access |
| **Trust-weighted routing** — experienced AML analysts on complex cases | No trust model | Trust score from past investigation outcomes drives routing |

**What this exercises on the platform:**
- Speech-act normative layer (COMMAND/QUERY/RESPONSE between specialist agents)
- Commitment lifecycle (each agent task is a formal obligation with outcome tracking)
- Human-in-the-loop WorkItem with regulatory SLA and escalation
- Bayesian Beta trust scoring (agents with consistent SAR quality get routed complex cases)
- Adaptive Case Management (investigation path depends on findings — structuring vs sanctions vs PEP)
- GDPR erasure and Merkle tamper-evident audit
- LLM supervisor mode (case triage — which investigation path to pursue)

**Why this is the best tutorial case:**
Every CaseHub feature maps naturally onto a step the audience recognises. A Java developer who has built a transaction monitoring system immediately understands why the compliance officer sign-off needs an SLA, why the entity resolution agent's result needs to be attributed to that agent specifically, and why the audit trail needs to be independently verifiable — because they have personally dealt with the failure modes when these things are absent.

---

## 9. The Two-Table Argument in Summary

The split scoring reveals what a single combined score hides:

- **Clinical trials** and **drug discovery** score identically on market fit (24/25 each) — but drug discovery collapses in community fit (15/25) because no Java developer can follow a molecular simulation scenario without a biochemistry background. The split makes this visible; a combined score would not.

- **Security incident response** has the richest comparison target (MyAntFarm, fully open-source, peer-reviewed, 80× improvement claim) but scores only 2/5 on market entry gap — SOAR is a crowded incumbent market. The community fit is strong (22/25) but the market story is weak. This is a tutorial candidate, not a market entry candidate.

- **AML** is the only case scoring 22 on both tables simultaneously. It is the strongest all-rounder precisely because Java enterprise developers are the banking developers who have built these systems and know exactly what fails in practice.

- **Clinical trials** wins the market argument at 24/25 — regulatory requirements (GCP, FDA IND, EMA, GDPR) create hard constraints that workflow-based LLM systems structurally cannot meet. The market entry gap is real.

**The pair:** one regulated healthcare case that makes the market argument, one financial crime case that makes the platform argument to the audience who will build with it.

---

## 10. References

### Academic Papers
- ClinicalAgent: [arXiv 2404.14777](https://arxiv.org/abs/2404.14777) — ACM BCB '24, open source
- TrialGenie: [medRxiv 2025.04.17](https://www.medrxiv.org/content/10.1101/2025.04.17.25326033v1)
- LegalAgentBench: [ACL 2025 / arXiv 2412.17259](https://aclanthology.org/2025.acl-long.116.pdf) — open source
- MASLegalBench: [arXiv 2509.24922](https://arxiv.org/abs/2509.24922) — open source
- Prompt-to-Pill: [Oxford Academic / Bioinformatics Advances 2024](https://academic.oup.com/bioinformaticsadvances/article/6/1/vbaf323/8403080) — open source
- DrugAgent: [arXiv 2411.15692](https://arxiv.org/abs/2411.15692)
- Tippy: [arXiv 2507.09023](https://arxiv.org/abs/2507.09023)
- Virtual Biotech: [bioRxiv Feb 2026](https://www.biorxiv.org/content/10.64898/2026.02.23.707551v1)
- MyAntFarm: [arXiv 2511.15755](https://arxiv.org/abs/2511.15755) — open source
- AutoSafeCoder: [arXiv 2409.10737](https://arxiv.org/abs/2409.10737)
- DRF Trust Framework: [arXiv 2509.05764](https://arxiv.org/abs/2509.05764)
- Nala Commitment Semantics: [Springer 2023](https://link.springer.com/article/10.1007/s10472-023-09875-w)
- AI Agents Under EU Law: [arXiv 2604.04604](https://arxiv.org/abs/2604.04604)
- Multi-Agent Health AI: [PMC 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC12360800/)

### Regulatory References
- FinCEN 2024 AML Guidance — auditable evidence chains requirement
- ICH E6(R3) — Good Clinical Practice, adverse event reporting timelines
- EU AI Act Art.12 — high-risk AI system transparency requirements
- GDPR Art.17 — right to erasure
- NAIC AI Model Bulletin (Dec 2023) — insurer accountability for AI decisions
- EDPB 2025 Coordinated Enforcement Framework — Art.17 erasure compliance

### Industry Sources
- [AnChain Agentic AML](https://www.anchain.ai/blog/agentic-aml)
- [Sardine: Three Failure Modes of Agentic AI in Financial Crime](https://www.sardine.ai/blog/agentic-ai-financial-crime-failure-modes)
- [IBM AMLSim GitHub](https://github.com/IBM/AMLSim/)
- [i-GENTIC AI MedTech Suite](https://www.advamed.org/industry-updates/news/i-gentic-ai-launches-context-aware-medtech-agents-to-strengthen-fda-510k-submission-consistency)
- [V7 Labs AI Agents for Insurance Claims](https://www.v7labs.com/blog/automated-claims-processing-for-insurance)
- [Accenture Agentic AI Health Insurance](https://insuranceblog.accenture.com/agentic-ai-transforming-claims-health-insurance)
