# Agent Reputation as a Service — Market Research (July 2026)

## Executive Summary

Agent reputation and trust infrastructure is emerging as a critical market gap. Enterprise AI agent adoption is accelerating (40% of apps will embed agents by end of 2026, up from <5% in 2025), but 80% of organizations deploying agents lack mature governance. The market is building identity (ERC-8004), payments (x402), and interoperability (A2A, MCP) — but **competence-based trust scoring backed by tamper-evident evidence** does not exist as a product. CaseHub is uniquely positioned to fill this gap.

---

## Market Size & Growth

- **AI agents market:** $7.63B (2025) → $182.97B (2033), CAGR 49.6%
- **Agentic AI infrastructure:** 17-22% of enterprise AI spend in 2026, projected 26-32% by 2027
- **Enterprise agent spend:** $1.4T forecast for 2027 (IDC midpoint)
- **Agent-native venture funding:** $4.7B in Q1 2026 alone (annualized $20B+)
- **Agentic commerce:** $8B transaction value in 2026, projected $3.5T by 2031
- 40% of companies have an AI agent budget over $1M; 1 in 4 large enterprises plan $5M+

Sources: [Grand View Research](https://www.grandviewresearch.com/industry-analysis/ai-agents-market-report), [Azumo AI Statistics](https://azumo.com/artificial-intelligence/ai-insights/ai-agent-statistics), [G2 AI Statistics](https://www.g2.com/articles/artificial-intelligence-statistics)

---

## The Trust Gap

The market is deploying agents faster than it can govern them:

- **80% of organizations** deploying agents have no mature governance model (Deloitte 2026)
- **Trust in autonomous agents declining:** 43% → 27% year-over-year
- **Only 25%** of AI initiatives deliver expected ROI; only 16% reach enterprise-wide scale
- **By 2028:** 25% of enterprise breaches will be traced to AI agent abuse (Gartner)
- **By 2028:** 40% of CIOs will demand "Guardian Agents" to oversee other agents (Gartner)
- **Only 18%** of security leaders are confident their IAM can manage agent identities
- **McKinsey 2026 AI Trust Maturity Survey:** average score 2.3/5.0

This is not a future problem — it is the primary constraint on scaling agentic AI today.

Sources: [Accelirate Agentic AI Statistics](https://www.accelirate.com/agentic-ai-statistics-2026/), [Enterprise AI Agents Statistics](https://paul-okhrem.com/enterprise-ai-agents-statistics-2026/), [Kai Waehner Enterprise Landscape](https://www.kai-waehner.de/blog/2026/04/06/enterprise-agentic-ai-landscape-2026-trust-flexibility-and-vendor-lock-in/)

---

## Current Landscape — Who's Building What

### Agent Identity

**ERC-8004 (Ethereum standard)**
- On-chain identity for AI agents — discovery, reputation, validation
- Developed by Ethereum Foundation, MetaMask, Google, Coinbase
- 20,000+ agents registered across 7+ chains since January 2026 mainnet launch
- Three core registries: identity (ERC-721), capability cards, feedback/reputation
- Risk: identity NFTs are transferable — reputation can be purchased
- Soulbound token layer (ERC-5192) emerging to address transferability

Source: [ERC-8004 Official](https://www.geterc8004.com/), [QuickNode Developer Guide](https://blog.quicknode.com/erc-8004-a-developers-guide-to-trustless-ai-agent-identity/)

**Know Your Agent (KYA)**
- WEF-backed framework (McGill University origin, February 2025)
- Five verification layers: developer provenance, user binding, permission scopes, behavior telemetry, continuous risk scoring
- Policy framework — not a product

Source: [KYA Network](https://knowyouragent.network/every-company-building-ai-agent-identity-in-2026)

### Agent Payments & Transaction Trust

**x402 Payment Protocol**
- HTTP-layer micropayments via stablecoins (USDC)
- Joined Linux Foundation April 2026 (AWS, Google, Stripe, Visa, Mastercard, AmEx)
- 499,000 payments in a single week; 100M+ payments in first 6 months
- Every payment builds on-chain reputation via ERC-8004 feedback

Source: [Coinbase x402](https://www.chainup.com/blog/x402-erc8004-ai-agent-payments-agentic-web/)

**ACHIVX**
- Wallet-based behavioral scoring across 7 dimensions (volume, reliability, disputes, tenure, feedback, counterparty diversity, consistency)
- Trust levels 1-5; level-5 agents pay 40% less for API calls
- Anti-gaming detection (Sybil attacks, velocity attacks)
- SDK for Express/Hono middleware
- **Limitation: scores transaction reliability, not task competence**

Source: [ACHIVX Platform](https://agents.achivx.com/), [ACHIVX x402 Integration](https://medium.com/@achivx/a-reputation-system-for-ai-agents-how-achivx-builds-trust-in-the-x402-ecosystem-83b48ecd946f)

### Agent Interoperability

**A2A Protocol (Google → Linux Foundation)**
- Agent-to-agent communication standard
- 150+ organizations, 22,000+ GitHub stars
- v1.0 shipped with Signed Agent Cards (trust primitive)
- Native in Azure AI Foundry, Amazon Bedrock AgentCore, Google Cloud
- IBM's ACP merged into A2A — effectively no alternative as of 2026
- SDKs: Python, JavaScript, Java, Go, .NET

Source: [Linux Foundation A2A Announcement](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year), [A2A Protocol](https://a2a-protocol.org/latest/)

**MCP (Model Context Protocol)**
- 9,652 registered servers, 15,926 GitHub repos with `mcp-server` topic
- Native in Claude, Cursor, Codex CLI, ChatGPT Desktop, Bedrock AgentCore
- **No reputation system** — servers are unverified by default
- Supply chain attacks already occurring (SmartLoader trojanized server, Feb 2026)
- DoD guidance (May 2026): treat every MCP server as potentially untrusted
- Next spec revision adds authorization hardening, but no trust scoring

Source: [MCP Adoption Statistics](https://www.digitalapplied.com/blog/mcp-adoption-statistics-2026-model-context-protocol), [DoD MCP Security Guidance](https://media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF)

### Academic

**AgentReputation (arXiv)**
- Decentralized reputation framework — evidence-based, contextual, decision-facing
- Warns against cross-domain aggregation (task-specific assessment required)
- Framework, not implementation

Source: [AgentReputation Paper](https://arxiv.org/html/2605.00073v1)

---

## What Nobody Has

The entire landscape scores agents on **transaction reliability** (did they pay? did they respond?) or **identity verification** (are they who they claim?). Nobody scores agents on **competence** — did they do good work, and how do we know?

| Capability | ERC-8004 | ACHIVX | A2A | KYA | CaseHub |
|-----------|----------|--------|-----|-----|---------|
| Agent identity | ✅ On-chain | Via wallet | Signed Agent Cards | Policy framework | Eidos descriptors |
| Transaction trust | Via x402 feedback | ✅ 7-dimension scoring | ❌ | ❌ | ❌ (not needed internally) |
| Capability-specific trust | ❌ | ❌ | ❌ | ❌ | ✅ Bayesian Beta per capability |
| Trust maturity model | ❌ | ❌ | ❌ | ❌ | ✅ 4-phase cold-start |
| Tamper-evident evidence | ❌ (mutable on-chain) | ❌ | ❌ | ❌ | ✅ Merkle Mountain Range |
| Behavioral signal accumulation | ❌ | Partial (disputes) | ❌ | Behavior telemetry (proposed) | ✅ DECLINE/FAIL/VIOLATED per capability |
| Outcome-based learning | ❌ | ❌ | ❌ | ❌ | ✅ CBR + attestation feedback loop |
| Explainable routing decisions | ❌ | ❌ | ❌ | ❌ | ✅ Full decision lineage (#363) |
| Cross-domain portability | ✅ (on-chain) | ✅ (wallet-based) | ✅ (A2A cards) | Proposed | ❌ (internal only — opportunity) |

**The gap CaseHub fills:** epistemic trust — "is this agent good at this specific task, based on evidence?" — as opposed to financial trust ("does this agent pay reliably?") or identity trust ("is this agent who it claims?").

---

## CaseHub's Competitive Position

### What already exists in the platform

| Component | Module | What it provides |
|-----------|--------|-----------------|
| Per-capability Bayesian Beta trust scores | `casehub-ledger` | Trust scoring from attestation evidence, not self-reported metrics |
| 4-phase trust maturity model | `casehub-ledger` | Cold-start handling — agents earn routing priority through demonstrated competence |
| Tamper-evident attestation chain | `casehub-ledger` | Merkle Mountain Range proof — trust evidence that can't be retroactively altered |
| Behavioral signal accumulation | `casehub-eidos` | DECLINE/FAIL/VIOLATED signals per capability with TTL — learned routing exclusion |
| Structured agent identity | `casehub-eidos` | 4-layer descriptor: identity, slot, capabilities, disposition |
| Vocabulary-based capability matching | `casehub-eidos` | Type-safe capability discovery with equivalence mapping |
| CBR case-based evidence | `casehub-neocortex` | Historical case outcomes informing future routing decisions |
| Outcome recording | `casehub-engine` | Case results feed back into trust scores and CBR case base |
| 7 domain applications generating evidence | Applications tier | Real trust data from AML, clinical, code review, life, SOC, trading, drafthouse |

### What would need to be built

1. **Standalone trust-scoring SDK** — extract Bayesian Beta + attestation model from ledger/eidos as a library with no CaseHub runtime dependency
2. **MCP observer proxy** — sits in front of any MCP server, observes tool call outcomes, feeds the scoring library
3. **A2A Agent Card extension** — publish CaseHub trust scores as part of an A2A Signed Agent Card
4. **Public trust dashboard** — visible proving ground showing trust scores for well-known agents in one domain
5. **Trust score portability API** — export/import trust evidence across CaseHub deployments and into external systems (ERC-8004 compatible)

### Go-to-market strategy

**Phase 1 — Prove it internally (now)**
- Seven domain apps already generate trust evidence
- Ship explainable decisions (#363) to make the evidence chain visible
- Publish trust score results from devtown scoring real GitHub code review bots

**Phase 2 — Standalone SDK (next)**
- Extract trust scoring as a standalone library
- MCP observer proxy as the first external integration point
- Target: enterprise teams choosing between competing AI tools with no basis for comparison

**Phase 3 — Ecosystem integration (later)**
- A2A Agent Card trust extension — CaseHub-attested trust scores in the interop standard
- ERC-8004 bridge — on-chain representation of off-chain competence evidence
- ACHIVX integration — financial trust (x402) + epistemic trust (CaseHub) = complete agent profile

**The flywheel:** More cases → better CBR retrieval → better routing → better outcomes → more trust evidence → stronger reputation signal → more adoption → more cases.

---

## Strategic Risks

1. **A2A v2 adds reputation natively** — Google could build trust scoring into the protocol. Counter: A2A's strength is interoperability, not domain-specific competence assessment. Generic trust is commodity; per-capability Bayesian scoring is not.

2. **ERC-8004 ecosystem converges on a reputation standard** — on-chain reputation could commoditize scoring. Counter: on-chain reputation is transaction-based. CaseHub's evidence comes from governed case outcomes — qualitatively different data.

3. **Single-vendor risk** — CaseHub is one team. Counter: the trust scoring math and attestation model could be open-sourced as a standalone library, building community before the platform is complete.

4. **Cold-start problem** — day one has zero agents and zero scores. Counter: bootstrap from existing agent ecosystems (MCP servers, GitHub bots) by observing outcomes, not requiring agents to join.

5. **Go-to-market gap** — this is a developer relations problem as much as a technical one. The tech is ready; the community is not.

---

## Key Takeaway

The $7.6B agent market is growing at 50% CAGR with an 80% governance gap. Everyone is building identity and payments. Nobody is building competence evidence. CaseHub has the only implementation of tamper-evident, per-capability, outcome-based trust scoring — and seven domain applications generating real data. The window is open but closing as the infrastructure layer solidifies around A2A + MCP + ERC-8004.
