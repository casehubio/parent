# casehubio/parent — Open Issues

**Generated:** 2026-06-27 | **Total:** 22 open issues | **8 epics, 3 design-only, 1 docs-only**

---

## Summary Table

| # | Title | Scale | Complexity | Linked Repos (reason) | Notes |
|---|-------|-------|------------|----------------------|-------|
| **3** | feat: automate linked PR chain across ecosystem repos | L | High | ledger, work, qhorus, engine, claudony, connectors — all downstream dispatch targets | CI/CD automation. `CROSS_REPO_PAT` + `repository_dispatch` chain. Not blocked |
| **7** | epic: platform foundation roadmap — P0–P3 | XL | High | qhorus — commitment outcomes; ledger — ActorTypeResolver; engine — normative wiring, trust, OTel, HITL; claudony — concurrency, recovery; work — SLA, notifications; connectors — notification consolidation | **Epic.** Phased (P0–P3). Several child items still untracked |
| **13** | Epic: Cohesive Claude configuration design | XL | High | None (tooling/methodology — affects skills repos, global/project CLAUDE.md) | **Epic.** Config layer audit — dedup, restructure, layer discipline |
| **111** | feat: migrate actorId format to DID | XL | High | ledger — DID infra origin (ADR 0004); work — ledger entry writes; qhorus — message ledger writes; engine — case/plan audit; claudony — agent session actorId | Blocked by ledger#81 (DID infra) and parent#107 (SCIM2). Trust reset for all actors |
| **140** | audit: multi-tenancy state across all repos | XL | High | engine — 3 open issues (#411 HIGH); work — 10 entities, zero tenancy (HIGH risk); qhorus — 10 entities, zero tenancy (HIGH risk); claudony — protocol violation (#121); aml — partial; clinical — partial; ledger — not started (design needed) | **Permanent audit record.** Priority: claudony null-guard > engine#411 > work > qhorus |
| **154** | feat: AI observability module | L | High | engine — telemetry hooks; ledger — trust signal feed | New module. Token/inference/prompt telemetry. Design-first |
| **155** | feat: agent policy engine | L | High | engine — WorkOrchestrator integration; platform — rule-based auth layer | New module `casehub-policy`. YAML/Drools-backed. Compliance requirement |
| **156** | feat: platform-level evaluation infra | L | Med | engine — case/step eval; ledger — trust signal input; eidos — distinct from eidos-eval | New module `casehub-eval`. A/B routing, benchmarks |
| **157** | feat: artifact/content pipeline | XL | High | engine — cross-step artifact ref; neocortex — RAG feed | New module `casehub-artifacts`. Binary asset lifecycle |
| **158** | feat: casehubio/onnx-inference — standalone ONNX | XL | High | neocortex — inference-splade; openclaw — risk classification; engine — epistemic confidence | Shared with Hortora. 6 sub-modules. Native image gate. Blocks #164 |
| **164** | feat: casehub-neocortex-rag — LangChain4j RAG integration | XL | High | neocortex — CaseRetriever SPI; engine — fact space prompt compiler; openclaw — context window enrichment | Blocked by #158 (sparse leg). Tenancy-scoped corpora |
| **207** | arch: distributed ledger persistence | M | High | ledger — core library; engine — JOINED inheritance; devtown — MergeDecisionLedgerEntry; aml — AmlCaseOpenedLedgerEntry | **Design.** Not blocking today (embedded mode). 4 options evaluated, no decision |
| **227** | Epic: CBR as platform capability | XL | High | ledger — batch trust scoring; neocortex — CaseRetriever; engine — RoutingStrategy, OutcomeObserver; quarkmind — reference impl; aml, clinical, devtown — domain CBR | **Epic.** 4-wave. 10 child issues across 6 repos. Spec at `docs/CBR-CAPABILITY.md` |
| **233** | design: Goal as first-class platform concept | M | High | engine — CasePlanModel; work — WorkItems; desiredstate — GoalCompiler SPI; platform — Goal type home | **Design.** Unifies cases, desired-state, and tasks. Related to desiredstate#1, #25 |
| **234** | design: reactive case container | M | High | engine — sub-case templates; desiredstate — reconciliation loop | **Design.** Long-lived root case with repeatable sub-cases. Related to #233 |
| **255** | design: dependency decision graph | M | High | None (cross-cutting methodology — affects garden protocols) | **Design.** Argumentation framework for library choices. Brainstorm needed first |
| **258** | Epic: Adaptive agent routing | XL | High | eidos — capability sub-specialization; engine — routing strategy; ledger — DECLINE pattern retention via CBR | **Epic.** Extends #227. Builds on engine#501. 3 repos |
| **292** | Developer onboarding: Maven archetype + isx template | L | Med | None directly (consumes platform, ledger as deps) | Maven archetype `casehub-quickstart`. Zero-to-running-app. Not blocked |
| **294** | epic: Reusable Platform Primitives | XL | High | engine, qhorus, ledger, eidos, drafthouse, claudony, openclaw, desiredstate — all contribute or consume primitives | **Epic.** Vision/tracking. 10 built/in-progress, 7 new to design. Has child issues |
| **295** | epic: CloudEvent adapter consistency | S | Low | connectors — new adapter; iot — adapter fix; qhorus — adapter fix; platform — poll/camel conformance; work — WorkCloudEventAdapter | **Epic.** 3/7 closed. 5 open follow-ups across 4 repos |
| **310** | Epic: casehub-blocks — reusable building blocks | XL | High | openclaw — delete local OversightGateService; engine — move classification types; drafthouse — extract 6 patterns; claudony — depend on blocks; qhorus, work — blocks builds on their primitives | **Epic.** New repo. 11 blocks identified. Sequence: repo setup → oversight gate → drafthouse patterns |
| **315** | docs: sync casehub-neocortex deep-dive | XS | Low | neocortex — source of changes (Matryoshka + quantization, neocortex#31) | Docs-only. Update `docs/repos/casehub-neocortex.md`. Straightforward |

---

## Detailed Entries

### #3 — feat: automate linked PR chain across ecosystem repos

**Scale:** L | **Complexity:** High

**Linked repos:** ledger, work, qhorus, engine, claudony, connectors — all are downstream dispatch targets in the PR chain.

**Notes:** CI/CD automation to create linked PRs when parent POM changes. Requires `CROSS_REPO_PAT` org secret for `repository_dispatch`. Needs a chain-open script that opens PRs in dependency order. Not blocked by any other issue.

---

### #7 — epic: platform foundation roadmap — P0 through P3

**Scale:** XL | **Complexity:** High | **Labels:** `scale: XL`, `complexity: High`

**Linked repos:**
- qhorus — commitment outcome lifecycle
- ledger — ActorTypeResolver migration
- engine — normative wiring, trust routing, OTel, HITL integration
- claudony — concurrency throttling, recovery, causal chain display
- work — SLA scope propagation, notification consolidation
- connectors — notification infrastructure consolidation

**Notes:** Epic. Four phases: P0 = normative wiring (3–4 wk), P1 = scale & resilience, P2 = production quality, P3 = capability expansion. Several child items still untracked as issues. This is the master roadmap for foundation-level work.

---

### #13 — Epic: Cohesive Claude configuration design

**Scale:** XL | **Complexity:** High | **Labels:** `scale: XL`, `complexity: High`

**Linked repos:** None (tooling/methodology concern — affects cc-praxis/soredium skills repos, global and project CLAUDE.md files).

**Notes:** Epic. Audit and restructure Claude config layers — dedup between CLAUDE.md files, enforce layer discipline (global vs project vs session), consolidate reference docs. 7 acceptance criteria. Does not touch casehub peer repos directly.

---

### #111 — feat: migrate actorId format to DID across all casehub repos

**Scale:** XL | **Complexity:** High | **Labels:** `scale: XL`, `complexity: High`

**Linked repos:**
- ledger — DID infrastructure origin, ADR 0004 defines the format
- work — WorkItemLedgerEntry writes use actorId
- qhorus — MessageLedgerEntry writes use actorId
- engine — case/plan audit entries use actorId
- claudony — agent session actorId

**Notes:** Cross-repo migration. Blocked by ledger#81 (DID infrastructure) and parent#107 (SCIM2 integration). Trust baseline reset for all actors on migration. Format: `{model-family}:{persona}@{major}`.

---

### #140 — audit: multi-tenancy state across all casehubio repos

**Scale:** XL | **Complexity:** High

**Linked repos:**
- engine — 3 open issues (#411 HIGH priority, #406, #405)
- work — 10 entities with zero tenancy (HIGH risk)
- qhorus — 10 entities with zero tenancy (HIGH risk)
- claudony — protocol violation (#121)
- aml — partial (#48)
- clinical — partial, no issue filed
- ledger — not started, design needed
- platform — complete
- eidos — complete

**Notes:** Permanent audit record, not an action item itself. Extremely detailed per-repo state matrix. Priority order for fixes: claudony null-guard fix → engine#411 → work tenancy → qhorus tenancy. Most critical gaps are work and qhorus with zero tenancy on 10 entities each.

---

### #154 — feat: AI observability module

**Scale:** L | **Complexity:** High

**Linked repos:**
- engine — telemetry hooks for agent invocation
- ledger — trust signal feed from observability data

**Notes:** New module (`casehub-engine-ai-telemetry` or `casehub-insight`). Token tracking, inference latency, prompt telemetry. Originated from AI Fusion gap analysis. Design-first — needs brainstorming before implementation.

---

### #155 — feat: agent policy engine

**Scale:** L | **Complexity:** High

**Linked repos:**
- engine — WorkOrchestrator integration point
- platform — rule-based authorization layer

**Notes:** New module `casehub-policy`. Rule-based authorization for agent actions — YAML or Drools-backed policy definitions. Compliance requirement for AML and clinical domains. From AI Fusion gap analysis.

---

### #156 — feat: platform-level evaluation infrastructure

**Scale:** L | **Complexity:** Med | **Labels:** `scale: L`, `complexity: Med`

**Linked repos:**
- engine — case/step level evaluation
- ledger — trust signal input
- eidos — distinct from eidos evaluation capabilities

**Notes:** New module `casehub-eval`. A/B routing evaluation, regression test suites, benchmark datasets. From AI Fusion gap analysis. Lower complexity than #154/#155 because the evaluation pattern is well-understood.

---

### #157 — feat: artifact/content pipeline

**Scale:** XL | **Complexity:** High | **Labels:** `scale: XL`, `complexity: High`

**Linked repos:**
- engine — cross-step artifact reference in case plans
- neocortex — RAG feed from artifact content

**Notes:** New module `casehub-artifacts`. Binary asset lifecycle: ingest, version, transform, ACL. SPI-based storage backend. From AI Fusion gap analysis.

---

### #158 — feat: casehubio/onnx-inference — standalone ONNX inference module

**Scale:** XL | **Complexity:** High | **Labels:** `scale: XL`, `complexity: High`

**Linked repos:**
- neocortex — inference-splade for hybrid search sparse leg
- openclaw — action risk classification
- engine — epistemic confidence estimation

**Notes:** Shared between CaseHub and Hortora. 6 sub-modules. Native image gate is a hard prerequisite. Blocks #164 (casehub-neocortex-rag sparse leg needs SPLADE).

---

### #164 — feat: casehub-neocortex-rag — LangChain4j RAG integration module

**Scale:** XL | **Complexity:** High

**Linked repos:**
- neocortex — CaseRetriever SPI definition
- engine — fact space prompt compiler context injection
- openclaw — context window enrichment

**Notes:** New modules: `rag-api`, `rag`, `rag-testing`. Hybrid search (dense + sparse via RRF). Blocked by #158 (onnx-inference needed for SPLADE sparse leg). Tenancy-scoped corpora via platform-api.

---

### #207 — arch: distributed ledger — app-specific LedgerEntry persistence

**Scale:** M | **Complexity:** High

**Linked repos:**
- ledger — core library (JOINED inheritance model)
- engine — uses JOINED inheritance for CaseLedgerEntry
- devtown — MergeDecisionLedgerEntry
- aml — AmlCaseOpenedLedgerEntry
- clinical — future domain-specific ledger entries
- life — future domain-specific ledger entries

**Notes:** Design issue. Not blocking today — all harnesses run embedded with shared datasource. Becomes relevant when foundation modules run as separate services. 4 options evaluated (shared schema, per-app schema, event sourcing, domain-level ledger), no decision yet.

---

### #227 — Epic: CBR as platform capability

**Scale:** XL | **Complexity:** High

**Linked repos:**
- ledger — TrustGateService batch scoring for Retain
- neocortex — CaseRetriever contract for Retrieve
- engine — RoutingStrategy SPI for Reuse, OutcomeObserver SPI for Retain
- quarkmind — reference implementation at game-loop granularity
- aml — investigation CBR
- clinical — adverse event CBR
- devtown — PR review CBR

**Notes:** Epic. Four-step AI pattern: Retain, Retrieve, Reuse, Revise. 4-wave implementation plan. 10 child issues across 6 repos. Full spec at `docs/CBR-CAPABILITY.md`. QuarkMind is the reference implementation.

---

### #233 — design: Goal as first-class platform concept

**Scale:** M | **Complexity:** High

**Linked repos:**
- engine — CasePlanModel would implement Goal
- work — WorkItems as goal achievement units
- desiredstate — GoalCompiler SPI bridges goals to plans
- platform — potential home for the Goal type

**Notes:** Design issue. Unifies cases, desired-state, and tasks under a single Goal concept (invariant/achievement/composite taxonomy). Related to desiredstate#1 and #25. No implementation yet — needs brainstorming.

---

### #234 — design: reactive case container

**Scale:** M | **Complexity:** High

**Linked repos:**
- engine — sub-case templates, event-driven spawning
- desiredstate — reconciliation loop as a continuous process

**Notes:** Design issue. Long-lived root case with repeatable on-demand sub-cases. Not traditional CMMN case lifecycle. Related to desiredstate#25 and parent#233. No implementation yet.

---

### #255 — design: dependency decision graph

**Scale:** M | **Complexity:** High

**Linked repos:** None (cross-cutting methodology concern — affects garden protocols).

**Notes:** Design issue. Argumentation framework for library/dependency choices. Immediate gaps identified in work-start Step 3 and PLATFORM.md Step 4. Solution TBD — brainstorming needed before any implementation.

---

### #258 — Epic: Adaptive agent routing

**Scale:** XL | **Complexity:** High | **Labels:** `scale: XL`, `complexity: High`

**Linked repos:**
- eidos — capability sub-specialization metadata (CapabilitySpecializationStore)
- engine — routing strategy consumes richer context
- ledger — DECLINE/FAIL pattern retention via CBR subsystem

**Notes:** Epic. Learn from DECLINE/FAIL patterns across cases to improve routing. Extends #227 (CBR). Builds on engine#501. Crosses 3 repos. eidos#55 ships the CapabilitySpecializationStore SPI.

---

### #292 — Developer onboarding: Maven archetype + isx template

**Scale:** L | **Complexity:** Med

**Linked repos:** None directly (consumes platform, ledger as dependencies; isx is external tooling).

**Notes:** Maven archetype `casehub-quickstart` + isx template `tpl-casehub-app`. Zero-to-running-app in one command. 4 deliverables: archetype, isx template, Maven settings, DB dev services config. Not blocked.

---

### #294 — epic: Reusable Platform Primitives

**Scale:** XL | **Complexity:** High

**Linked repos:**
- engine — coordination channels, oversight gate, supervisor pattern
- qhorus — speech act lifecycle primitives
- ledger — trust routing (Bayesian Beta)
- eidos — adaptive routing
- drafthouse — debate channel pattern
- claudony — channel integration
- openclaw — oversight gate extraction
- desiredstate — reconciliation primitive

**Notes:** Epic. Vision and tracking issue. 10 primitives built or in-progress, 7 new primitives to design. Child issues: #93, #293, #227, #258, drafthouse#71, claudony#158. Channel taxonomy patterns documented and ready for implementation issues.

---

### #295 — epic: CloudEvent adapter consistency

**Scale:** S | **Complexity:** Low

**Linked repos:**
- connectors — new InboundMessage → CloudEvent adapter
- iot — IoTCloudEventAdapter fix
- qhorus — QhorusCloudEventAdapter fix + test migration alignment
- platform — poll/camel module conformance
- work — WorkCloudEventAdapter (shipped)

**Notes:** Epic. 3 of 7 issues closed. 5 open follow-ups across 4 repos. Garden protocol captured. Blog published. Mostly a consistency sweep — each repo adapter needs the same pattern.

---

### #310 — Epic: casehub-blocks — reusable building blocks

**Scale:** XL | **Complexity:** High

**Linked repos:**
- openclaw — delete local OversightGateService, depend on blocks instead
- engine — move ActionRiskClassifier types to blocks
- drafthouse — extract 6 patterns (debate, review, memo, subagent, round-bounded projection, restart-from-round)
- claudony — depend on blocks for debate capability
- qhorus — blocks builds on channels/commitments as primitives
- work — blocks builds on task lifecycle as primitives

**Notes:** Epic. New repo `casehubio/blocks`. Single Maven module depending on qhorus-api + work-api + engine-api. 11 blocks identified (7 coordination patterns, 4 infra utilities). Sequencing: repo setup → oversight gate extraction → drafthouse pattern extraction → new patterns.

---

### #315 — docs: sync casehub-neocortex deep-dive for Matryoshka + quantization

**Scale:** XS | **Complexity:** Low

**Linked repos:**
- neocortex — source of changes (Matryoshka embedding + dense quantization from neocortex#31)

**Notes:** Docs-only. Update `docs/repos/casehub-neocortex.md` RAG Integration section. 4 items to add: MatryoshkaEmbeddingModel, DenseQuantization enum, search-time oversampling, CDI producer wiring. Straightforward.
