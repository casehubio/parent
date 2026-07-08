# casehub-aml

**GitHub:** [casehubio/aml](https://github.com/casehubio/aml)
**Tier:** Application
**Status:** In progress — Layers 1–6, 8, 9 complete; Layer 7 pending

## What It Is

An AML investigation application built on the CaseHub agentic harness. Coordinates specialist agents (entity resolution, pattern analysis, OSINT screening), compliance officer human task gates, and adaptive investigation paths — producing a FinCEN-compliant, independently verifiable audit trail. Field showcase and tutorial for Java developers in financial services.

Scored 44/50 in the use-case analysis (22 market + 22 community) — the only use case strong on both dimensions simultaneously. Java dominates banking infrastructure; enterprise developers have built these systems and know what fails in practice.

See `docs/use-case-analysis.md` §8.2 and `docs/tutorial-strategy.md` §6 in this repo.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence — each layer adds one foundation module and makes its value tangible. The code at every layer is production-grade. See `docs/tutorial-strategy.md §6` for teaching objectives per layer.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive Java — no CaseHub | Baseline anti-pattern | ✅ complete |
| 2 | casehub-work | No formal SLA or human task lifecycle for compliance officer review | ✅ complete |
| 3 | casehub-qhorus | No formal obligation per specialist agent interaction | ✅ complete (2026-05-17) |
| 4 | casehub-ledger | No tamper-evident FinCEN audit trail | ✅ complete (2026-05-23) |
| 5 | casehub-engine | Fixed investigation pipeline; no adaptive paths | ✅ complete (2026-05-25) |
| 6 | Trust routing | No trust model; random agent selection | ✅ complete (2026-05-29) — known: engine#395 scoping fix pending |
| 7 | Comparison vs IBM AMLSim | — | pending |
| 8 | casehub-platform `CaseMemoryStore` | No prior entity context across investigations; SAR outcomes not fed back to memory | ✅ complete (2026-06-04, aml#32) — prior entity context injected before each investigation; SAR outcomes written to memory; trust seeder fixed (senior-analyst-agent Beta(10,1)); YAML binding split to prevent double-dispatch Merkle race |
| 9 | casehub-engine-work-adapter (`ActionRiskClassifier` oversight gate) | No human oversight gate for consequential agent actions (SAR filing, entity link creation) | ✅ complete (2026-06-10, aml#42) — `AmlActionRiskClassifier @RiskClassifier`; PEP and high-risk-score actions gate to compliance review; TRANSACTION_BLOCKING inverts (gates on low confidence); fail-closed preserves type metadata |

## Module Structure

Follows hexagonal architecture ([PP-20260512-9b8847](../protocols/casehub/hexagonal-application-service-placement.md)):
- `api/` — domain layer: pure Java records and service interfaces, zero framework dependencies
- `app/` — application + infrastructure layer: CDI beans, REST resources, Quarkus integration

## What It Owns

- AML domain model: `SuspiciousTransaction`, `AmlInvestigationCase`, `SuspiciousActivityReport`
- Capability tags: `entity-resolution`, `pattern-analysis`, `osint-screening`, `sar-drafting`, `compliance-review`, `senior-escalation`, `investigation-triage`, `entity-link-proposal`, `investigation-summary`
- Trust dimensions: `investigation-accuracy`, `pep-clearance`, `scope-awareness`
- Investigation `CasePlanModel` — adaptive paths based on entity type, risk score, PEP detection
- Compliance officer WorkItem with 30-day FinCEN SLA and head-of-compliance escalation
- 7-layer tutorial from naive Java through full adaptive case management
- Comparison baseline vs IBM AMLSim and industry whitepapers
- `AmlTrustRoutingPolicyProvider` — per-capability trust routing policies (Preferences API with AML defaults)
- `AmlTrustScoreSeeder` — seeds initial Beta(α,β) trust scores at startup
- `SarOutcomeFeedbackService` — writes `LedgerAttestation` on SAR outcome, closing the trust feedback loop
- `AmlLayer6Resource` — `/api/layer6/investigations` REST endpoints (async POST, polling GET, outcome POST)
- `AmlMemoryService`, `AmlPriorContext`, `AmlMemoryDomains` — Layer 8 entity context injection before each investigation
- `AmlSarOutcomeMemoryObserver`, `SarOutcomeRecordedEvent` — Layer 8 SAR outcome written to memory on case close
- `AmlCaseOpenedLedgerEntry`, `AmlComplianceReviewLedgerEntry` — replace `AmlInvestigationLedgerEntry` (finer-grained audit trail)
- Test protocols: PP-20260604-f45c95 (hash-chain disabled in H2 test scope), PP-20260604-820c35 (drain pattern for async memory observers)
- `AmlActionType`, `AmlGroups` — consequential action vocabulary; encodes gate policy (ALWAYS, RISK_SCORE_THRESHOLD, CONFIDENCE_THRESHOLD), reversible, candidateGroups, scope per action type
- `AmlActionRiskClassifier @RiskClassifier` — Layer 9 `ActionRiskClassifier` SPI implementation; fail-closed paths derive all gate metadata from domain type
- `AmlOversightCaseHub`, `AmlOversightCoordinator`, `AmlLayer9Resource` — Layer 9 oversight harness; demonstrates PEP entity gating and low-risk CORPORATE autonomous path

## Web UI (aml#91)

Lit-based web UI built with casehub-blocks-ui components and casehub-pages. Three views:

**Investigations view** — case workbench for AML investigations:
- `case-workbench` — split-pane layout with investigation list (left) and detail tabs (right)
- Five detail panels: investigation overview (transaction + prior context), findings (specialist results), routing (agent selection + gate cards), compliance (FinCEN requirements + SAR status + GDPR), audit trail (ledger entries + Merkle verification)
- Uses blocks-ui `data-table` for investigation list, `work-item-detail` for tabs, `audit-trail-viewer` for ledger entries

**Compliance view** — compliance officer work queue:
- `work-item-inbox` (blocks-ui) — compliance review WorkItems with 30-day FinCEN SLA
- Three-tab perspective (My Work / Claimable / All)
- SSE live updates for new SAR reviews

**Operations view** — operational dashboard with four tabs:
- Throughput metrics — investigation status breakdown (open, under review, SAR filed, closed)
- Trust scores — agent trust scores table (blocks-ui `trust-score-panel` with per-capability breakdown)
- Gates — oversight gate metrics (action type distribution, gate outcomes)
- Intervention — manual intervention reasons (flag distribution)

All views use blocks-ui `data-table` for tabular data. Built with Quinoa (Quarkus frontend integration) — TypeScript compiled with esbuild, hot-reload in dev mode.

## The Compliance Gap It Closes

Current agentic AML systems cannot provide:
- Auditable evidence chains (FinCEN requirement) — `causedByEntryId` chain per agent finding
- Formal obligation per investigation task — COMMAND creates Commitment, DECLINE ≠ FAILED
- GDPR Art.17 erasure on transaction PII — ledger erasure service. See docs/DESIGN.md for implementation detail.
- Tamper-evident investigation record — Merkle inclusion proofs, independently verifiable
- Trust-weighted routing — experienced analysts on complex cases, auto-updated from SAR outcomes

## Dependencies

```
casehub-aml
  → casehub-engine          (investigation CasePlanModel, adaptive paths)
  → casehub-engine-flow     (FuncWorkflowBuilder worker execution — `FlowWorkerExecutor @ApplicationScoped` displaces `NoOpWorkflowExecutor @DefaultBean`; enables `WorkerFunction.Flow` via quarkus-flow; aml#46, PP-20260531-worker-func-exec)
  → casehub-engine-ledger   (Layer 6: TrustWeightedAgentStrategy, WorkerDecisionEventCapture; engine#395 scoping fix pending)
  → casehub-ledger          (Merkle audit, FinCEN evidence chain, GDPR erasure, trust scoring)
  → casehub-work            (compliance officer WorkItem, 30-day SLA, escalation)
  → casehub-qhorus          (COMMAND/RESPONSE per specialist agent, commitment lifecycle)
  → casehub-connectors      (Slack/Teams for SAR assignment notifications)
  → casehub-platform-memory-jpa    (Layer 8: JPA-backed CaseMemoryStore for production)
  → casehub-platform-memory-inmem  (Layer 8: in-memory CaseMemoryStore for test isolation)
  → casehub-engine-work-adapter    (Layer 9: ActionGateWorkItemHandler + WorkItemLifecycleAdapter for oversight gate)
  → casehub-engine-blackboard      (Layer 9: BlackboardRegistry — required for gate signal routing; transitive via work-adapter)
```

## Key Epics

1. Project scaffold
2. Domain model — AML entities and capability tags
3. Investigation CasePlanModel — adaptive paths
4. Compliance officer WorkItem — 30-day FinCEN SLA
5. Failure handling — DECLINED vs FAILED routing
6. Trust-weighted routing and post-investigation feedback
7. GDPR and regulatory audit
8. LLM supervisor mode — investigation triage
9. Tutorial layers 1–7 (comparison showcase)
10. Operational tooling — MCP tools and observability

Issues: https://github.com/casehubio/aml/issues?label=epic
