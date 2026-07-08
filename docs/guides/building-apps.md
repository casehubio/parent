# Building Apps

> **Scope:** App builder journey — capability matrix, pattern catalogue, cross-app learning
> **Audience:** App builders (Java + TypeScript)
> **Discovery:** Load this after [INDEX.md](../INDEX.md) when starting a new app or adding a major capability

---

## The Pattern

Bring your domain. Use the platform. Modify nothing below.

Every CaseHub application follows this pattern:
- **Your domain** — AML investigation, clinical trial, PR review, household management, SOC triage
- **Your case models** — adaptive paths in YAML or Java DSL, domain-specific routing conditions
- **Your risk classifiers** — gate consequential actions through human oversight
- **Platform foundation** — engine, ledger, work, qhorus, eidos unchanged

**Boundary enforcement:** [boundary-rules.md](../platform/boundary-rules.md)  
**Session conventions:** [AGENTIC-HARNESS-GUIDE.md](../AGENTIC-HARNESS-GUIDE.md)

---

## App Capability Matrix

### Shared Building Blocks

**Before implementing a new capability, check what blocks + blocks-ui provide.**

| Capability | blocks (Java) | blocks-ui (TS) | Notes |
|---|---|---|---|
| **Routing** | `TrustRoutingPolicyResolver`, `TrustRoutingPolicyKeys`, LLM/CBR agent routing | — | Preference-to-policy; AI-powered strategies |
| **Oversight gates** | `ActionRiskClassifier` SPI, `ChainedReactiveActionRiskClassifier` | `approval-gate` | Gate lifecycle + risk classification |
| **Structured conversation** | `ConversationProtocol`, `ConversationProjection`, fold state, renderer | — | Multi-agent deliberation channels |
| **Work item inbox** | — | `work-item-inbox`, `work-item-detail`, `work-item-workbench` | Queue pill bar, scope context, SSE lifecycle |
| **Data tables** | — | `data-table` | Auto/paginated/scroll, virtual scroll, ARIA grid, 2D nav |
| **Trust visualisation** | — | `trust-score-panel` | Bayesian Beta scores, trend lines, per-capability |
| **Channel activity** | `ChannelAgentDispatcher`, `ChannelMessageMeta` | `channel-activity` | Message stream, commitment status, speech acts |
| **SLA indicators** | — | `sla-indicator` | Countdown, breach state, escalation badge |
| **Case timelines** | — | `case-timeline` | Status progression, milestones, agent activity |
| **KPI metrics** | — | `kpi-metric-row` | Responsive grid, sparklines, trends, status colours |
| **Agentic orchestration** | `Patterns` DSL (Supervisor, Sequence, Loop, Parallel, Voting, Debate, Conditional, HTN) | — | Compositional orchestration framework |

**Placement rule:** If 2+ apps need the same component, extract to blocks (Java) or blocks-ui (TS). If app-specific, keep it in the app repo.

### Per-App Implementation Status

| App | Layers | Trust | CBR | Oversight | Web UI | GDPR | Notifications | Notes |
|---|---|---|---|---|---|---|---|---|
| **AML** | 1–6, 8, 9 | ✅ L6 | ✅ L8 (memory) | ✅ L9 (`AmlActionRiskClassifier`) | pending | L4 erasure | L2 SLA | SAR filing gate; entity context injection |
| **Clinical** | 1–10 | ✅ L7 | ✅ L8 (patient/site) | ✅ L8 (SUSAR criteria) | pending | ✅ L8 (Art.17) | ✅ (AE, PI) | IND deadline; regulatory submission |
| **DevTown** | 1, 3, 4, 5, 6 | ✅ L6 | ✅ (contributor/reviewer) | ✅ L5 (PR actions) | ✅ (governance) | ✅ (actor erasure) | pending | PR review gates; incident feedback |
| **Life** | 2, 3, 4, 5, 6, 8 | ✅ L6 | planned | ✅ L5 (actions) | pending | ✅ L4 (actor) | planned | Household task gates; RBAC |
| **Drafthouse** | — | — | — | — | pending | — | — | Document review; qhorus channels |
| **QuarkMind** | 2–7 | ✅ L6 (strategy) | — | — | ✅ (3D SC2) | — | — | Real-time game AI; living lab |
| **SOC** | scaffold | — | planned | planned | planned | planned | planned | Cyber incident response |
| **FSI Trading** | scaffold | — | planned | planned | planned | planned | planned | Trading automation |

**Legend:** ✅ complete, L# = layer number, — = N/A or not started

### Starting a New App?

1. **Check domain similarity** — which existing app is closest to your domain?
   - **Regulated enterprise** (compliance audit, SLA) → start from AML or Clinical
   - **Human task coordination** (approval workflows) → start from Clinical or Life
   - **Real-time agent coordination** (no human gates) → start from QuarkMind
   - **Content review / deliberation** → start from Drafthouse or DevTown

2. **Read the deep-dive** — [repos/casehub-{closest-app}.md](../repos/)

3. **Follow the layer progression** — see §Layer Progression below

4. **Check placement criteria** — see §Where Does a Reusable Pattern Belong? below

---

## Pattern Catalogue

### Case Types

**Shared pattern:** CaseHub apps define case models via YAML (`YamlCaseHub`) or Java DSL (`TypedCaseHub`). Engine executes them.  
→ [repos/casehub-engine.md](../repos/casehub-engine.md)

**Per-app:**
- **AML:** [casehub-aml.md](../repos/casehub-aml.md) — investigation case with adaptive paths (entity type, PEP detection)
- **Clinical:** [casehub-clinical.md](../repos/casehub-clinical.md) — trial coordination, AE escalation, protocol deviation, eligibility screening, regulatory submission, protocol amendment
- **DevTown:** [casehub-devtown.md](../repos/casehub-devtown.md) — PR review with content-driven routing (security flags, architecture changes)
- **Life:** [casehub-life.md](../repos/casehub-life.md) — 6 case hubs (appointment, home maintenance, travel, care, contractor, financial review)
- **QuarkMind:** [quarkmind.md](../repos/quarkmind.md) — per-tick agent dispatch via blackboard

### Trust Routing

**Shared pattern:** Bayesian Beta scoring (ledger) + preference-driven policy (blocks) + classical strategies (engine) + AI strategies (blocks).  
→ [platform/routing.md](../platform/routing.md)

**Per-app:**
- **AML:** [casehub-aml.md](../repos/casehub-aml.md) §Layer 6 — `AmlTrustRoutingPolicyProvider`, per-capability thresholds
- **Clinical:** [casehub-clinical.md](../repos/casehub-clinical.md) §Layer 7 — safety monitoring threshold 0.75, quality floor 0.70
- **DevTown:** [casehub-devtown.md](../repos/casehub-devtown.md) §Layer 6 — `review-thoroughness`, `false-positive-rate`
- **Life:** [casehub-life.md](../repos/casehub-life.md) §Layer 6 — `deadline-reliability`, `cost-accuracy`
- **QuarkMind:** [quarkmind.md](../repos/quarkmind.md) §Layer 6 — strategy routing by opponent context

### Oversight Gates

**Shared pattern:** `ActionRiskClassifier` SPI (blocks) → `ActionGateWorkItemHandler` (engine-work-adapter) → WorkItem → resume.  
→ [repos/casehub-blocks.md](../repos/casehub-blocks.md) §Oversight package

**Per-app:**
- **AML:** [casehub-aml.md](../repos/casehub-aml.md) §Layer 9 — PEP entities gate to compliance review; TRANSACTION_BLOCKING inverts (gates on low confidence)
- **Clinical:** [casehub-clinical.md](../repos/casehub-clinical.md) §Layer 8 — SUSAR criteria evaluation; `ClinicalActionRiskClassifier`
- **DevTown:** [casehub-devtown.md](../repos/casehub-devtown.md) §Layer 5 — 8 action types (merge, deploy, schema, infra, secrets, approve-pr, label-pr, comment); 4 categories
- **Life:** [casehub-life.md](../repos/casehub-life.md) §Layer 8 — RBAC-differentiated thresholds (admin elevated, junior always-gate)
- **SOC:** planned — containment actions (block IP, quarantine host, revoke creds)

### Web UI Composition

**Shared pattern:** Quinoa serves pages webapp → YAML dashboard → `hostPanel` embeds blocks-ui + app panels → SSE updates.  
→ [platform/ui-architecture.md](../platform/ui-architecture.md)

**Per-app:**
- **AML:** [casehub-aml.md](../repos/casehub-aml.md) — planned: operations, accountability, investigations views
- **Clinical:** pending
- **DevTown:** [casehub-devtown.md](../repos/casehub-devtown.md) — governance workbench, WebSocket bridge
- **Drafthouse:** [casehub-drafthouse.md](../repos/casehub-drafthouse.md) — document review panels (before/after, diff viewer, reviewer LLM agents)
- **QuarkMind:** [quarkmind.md](../repos/quarkmind.md) — Three.js 3D visualiser, 65+ sprites, Electron wrapper

**Component examples:**
- **AML:** `work-item-inbox` (blocks-ui) + `aml-transaction-graph` (aml-specific) + `trust-score-panel` (blocks-ui) + `approval-gate` (blocks-ui)
- **DevTown:** `work-item-inbox` + `devtown-pr-diff` + `channel-activity` + `trust-score-panel`
- **Drafthouse:** `work-item-inbox` + `drafthouse-content-viewer` + `case-timeline` + `approval-gate`

### GDPR Erasure

**Shared pattern:** `LedgerErasureService.erase()` (ledger) tokenises identities; apps sanitise domain context; write `ErasureReceiptLedgerEntry`.  
→ [platform/privacy.md](../platform/privacy.md)

**Per-app:**
- **AML:** [casehub-aml.md](../repos/casehub-aml.md) §Layer 4 — transaction PII erasure
- **Clinical:** [casehub-clinical.md](../repos/casehub-clinical.md) §Layer 8 — patient ID pseudonymisation, memory erasure, `ConsentWithdrawalLedgerEntry`
- **DevTown:** [casehub-devtown.md](../repos/casehub-devtown.md) §Layer 4 — actor erasure: ledger + `CaseMemoryStore` (`contributor:` + `reviewer:` prefixes)
- **Life:** [casehub-life.md](../repos/casehub-life.md) §Layer 4 — external actor erasure, `LifeGdprErasureService`

### Notifications

**Shared pattern:** Apps inject `NotificationDispatcher` (platform) → connectors deliver via Slack/Teams/email/SMS.  
→ [platform/notifications.md](../platform/notifications.md)

**Per-app:**
- **AML:** [casehub-aml.md](../repos/casehub-aml.md) §Layer 2 — SAR assignment notifications
- **Clinical:** [casehub-clinical.md](../repos/casehub-clinical.md) §Layer 2 — AE to safety officers, PI deviation to sponsor (durable retry), exhausted retries → WorkItem
- **Life:** planned

### CBR (Case-Based Reasoning)

**Shared pattern:** `CaseMemoryStore` (platform) + `CbrRetrievalService` (engine) + domain feature extractors → inject context before case starts; record outcomes after.  
→ [platform/cbr.md](../platform/cbr.md)

**Per-app:**
- **AML:** [casehub-aml.md](../repos/casehub-aml.md) §Layer 8 — prior entity context injected; SAR outcomes written to memory
- **Clinical:** [casehub-clinical.md](../repos/casehub-clinical.md) §Layer 8 — patient/site domains; AE reports + outcomes, deviation reports + PI decisions
- **DevTown:** [casehub-devtown.md](../repos/casehub-devtown.md) — contributor history, reviewer context, code-area history
- **Life:** planned

---

## Where Does a Reusable Pattern Belong?

| Criteria | Destination | Examples |
|---|---|---|
| **Needs an LLM in the loop** | blocks (Java) | LLM routing, debate protocol, prompt enrichment |
| **Uses classical AI** | blocks (Java) | Bayesian routing, CBR feature extraction |
| **Composes qhorus + engine + work** | blocks (Java) | Oversight gate lifecycle, channel agent dispatch |
| **Platform-concept visualisation** | blocks-ui (TS) | `trust-score-panel`, `channel-activity`, `work-item-inbox` |
| **Infrastructure (data pipeline, layout)** | pages (TS) | `SSEManager`, YAML parser, `DataSet` model |
| **Foundation primitive** | platform, engine | Notification engine, blackboard, case lifecycle |
| **App-specific domain logic** | app repo | AML transaction graph, clinical SUSAR criteria |

**Worked examples from consolidation epic #28:**

| Pattern | Was duplicated in | Extracted to | Issue |
|---|---|---|---|
| Trust routing policy loading | aml, devtown, clinical, life | blocks (routing package) | blocks#17 |
| Debate channel infrastructure | drafthouse | blocks (conversation package) | blocks#22 |
| Oversight gate lifecycle | openclaw, engine-api | blocks (oversight package) | blocks#23 |
| AI routing strategies (LLM, CBR) | — | blocks (routing.agent package) | blocks#30 |

**Reference:** [casehub-blocks.md](../repos/casehub-blocks.md) §Blocks Scope Criteria

---

## Protocols for App Builders

**Grouped by concern:**

| Concern | Protocols | Notes |
|---|---|---|
| **Build** | `module-tier-structure`, `pom-consolidation`, `hexagonal-application-service-placement` | Maven structure, tier placement |
| **Migration** | `flyway-repo-scoped-migration-path`, `flyway-migration-rules`, `flyway-extension-migration-registration` | Flyway conventions |
| **UI** | `custom-event-shadow-dom`, `lit-immutable-collections` | Web component communication |
| **Testing** | `quarkus-test-h2-ledger`, `drain-pattern-async-memory-observers` | Test isolation |
| **Trust** | `trust-maturity-model` | BOOTSTRAP / QUALIFIED / BORDERLINE / EXCLUDED phases |
| **GDPR** | — | See [platform/privacy.md](../platform/privacy.md) |
| **Notifications** | — | See [platform/notifications.md](../platform/notifications.md) |

**Full index:** [garden protocols INDEX.md](../../garden/docs/protocols/INDEX.md)

---

## Layer Progression

Apps build capability by layer — each layer adds one foundation module. The tutorial structure is for **understanding** (reading order); **implementation** follows vertical slices (Chapters). See [AGENTIC-HARNESS-GUIDE.md](../AGENTIC-HARNESS-GUIDE.md) for detailed session conventions.

**Common layer sequence:**

| Layer | Adds | Gap it closes |
|---|---|---|
| 1 | Naive Java — no CaseHub | Baseline: direct service calls, no SLA, no audit |
| 2 | casehub-work | No formal SLA; no human task lifecycle |
| 3 | casehub-qhorus | No formal obligation per specialist interaction |
| 4 | casehub-ledger | No tamper-evident audit trail; no GDPR erasure |
| 5 | casehub-engine | Fixed pipeline; no adaptive paths |
| 6 | Trust routing | No trust model; random agent selection |
| 7 | Comparison vs baseline | — |
| 8 | CaseMemoryStore (CBR) | No prior context; outcomes not fed back |
| 9 | ActionRiskClassifier (oversight gates) | No risk classification for consequential actions |
| 10+ | Domain-specific extensions | — |

**Per-app deep-dives with full layer details:**

- **AML:** [casehub-aml.md](../repos/casehub-aml.md) — Layers 1–6, 8, 9 complete
- **Clinical:** [casehub-clinical.md](../repos/casehub-clinical.md) — Layers 1–10 complete
- **DevTown:** [casehub-devtown.md](../repos/casehub-devtown.md) — Layers 1, 3, 4, 5, 6 complete
- **Life:** [casehub-life.md](../repos/casehub-life.md) — Layers 2, 3, 4, 5, 6, 8 complete
- **Drafthouse:** [casehub-drafthouse.md](../repos/casehub-drafthouse.md) — early phase
- **QuarkMind:** [quarkmind.md](../repos/quarkmind.md) — Layers 2–7 complete

**Cross-app learning:** Read the layer sections in each deep-dive to see how different domains solve the same integration challenges (CDI wiring, YAML bindings, preference loading).

---

## See Also

- **Platform builder guide:** [building-platform.md](building-platform.md)
- **Discovery index:** [INDEX.md](../INDEX.md)
- **Boundary rules:** [platform/boundary-rules.md](../platform/boundary-rules.md)
- **Session conventions:** [AGENTIC-HARNESS-GUIDE.md](../AGENTIC-HARNESS-GUIDE.md)
- **Application inventory:** [APPLICATIONS.md](../APPLICATIONS.md)
- **blocks scope criteria:** [casehub-blocks.md](../repos/casehub-blocks.md) §Blocks Scope Criteria
- **blocks-ui design philosophy:** [casehub-blocks-ui.md](../repos/casehub-blocks-ui.md) §Design Philosophy
- **UI architecture:** [platform/ui-architecture.md](../platform/ui-architecture.md)
- **Routing:** [platform/routing.md](../platform/routing.md)
- **CBR:** [platform/cbr.md](../platform/cbr.md)
