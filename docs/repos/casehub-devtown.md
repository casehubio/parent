# casehub-devtown

**GitHub:** [casehubio/devtown](https://github.com/casehubio/devtown)
**Tier:** Application
**Status:** Layers 1, 3, 4, 5, 6 complete; Layer 2 code complete (LAYER-LOG entry pending engine#326)

## What It Is

A software engineering coordination application built on the CaseHub agentic harness. Coordinates specialist code reviewers (security, architecture, test coverage), human review task gates with SLA, and adaptive PR routing based on code content — producing a tamper-evident review record where every missed finding is traceable. Field showcase and tutorial for Java developers in software engineering and DevOps.

This is the CaseHub answer to Gastown — same domain (software engineering coordination), but built on the domain-agnostic foundation rather than baked into infrastructure. See `docs/gastown-casehub-analysis-v2.md` in this repo for the full architectural comparison.

## Tutorial Layers

The tutorial structure emerges from the natural adoption sequence. Each layer adds one foundation module and makes its value tangible relative to the previous layer. The code at every layer is production-grade. See `../parent/docs/tutorial-strategy.md §7.5` for teaching objectives per layer.

LAYER-LOG.md in the project root is the authoritative layer-by-layer record with cross-references, key wiring, and gotchas. Update it when a layer completes or makes significant progress.

| Layer | Adds | Gap it closes | Status |
|-------|------|---------------|--------|
| 1 | Naive Java — no CaseHub | Baseline: direct service calls to analysis agents, no accountability | ✅ complete — scaffold (#8), vocabulary (#9), naive service (#27) |
| 2 | casehub-work | No formal SLA for reviewer response; reviewer assignments not tracked | **in progress** — devtown#41 ✅ devtown#42 ✅; LAYER-LOG entry pending engine#326 |
| 3 | casehub-qhorus | No formal obligation per specialist reviewer; DECLINE when outside expertise | ✅ complete — devtown#52 + devtown#64; LAYER-LOG entry complete. `QhorusPrReviewService` sets `allowedWriters=ORCHESTRATOR` on all three channels; `requireContract()` validates both `allowedTypes` and `allowedWriters`. DONE/DECLINE dispatches use ORCHESTRATOR sender (agents will use own identity in Layer 6). |
| 4 | casehub-ledger | No tamper-evident review record; cannot trace production incident to missed finding | ✅ complete (devtown#5, devtown#73, devtown#74) — `MergeDecisionLedgerEntry`, `MergeDecisionObserver`, `CodeReviewComplianceResource`, `domainContentBytes()` override; V2003: index on `(repository, pr_number)` + dropped `tenancy_id` from join table; `ErasureReceiptLedgerEntry` (JOINED, V2004) + `GdprErasureService` + `GdprErasureResource` (`POST /api/actors/{actorId}/erasure`) |
| 5 | casehub-engine | Fixed review pipeline; no adaptive routing on security flags or architecture changes | ✅ complete — PR review CasePlanModel (#10); 38 tests. **Extension (devtown#56):** `DevtownActionRiskClassifier` oversight gate — `ActionRiskClassifier` SPI (engine#402), 8 action types, 4 classification categories, Preference-driven thresholds, `HumanOversight.GENERAL` catch-all group |
| 6 | Trust routing | No trust model; experienced security reviewers not prioritised on sensitive PRs | ✅ complete — devtown#57; LAYER-LOG entry complete |
| 7 | Comparison vs naive AI code review | — | pending |

## What It Owns

- Capability tag definitions for the software development domain (`code-analysis`, `security-review`, `architecture-review`, `style-review`, `test-coverage`, `merge-executor`, etc.)
- Trust dimension definitions (`review-thoroughness`, `false-positive-rate`, `scope-calibration`)
- Routing thresholds per capability (e.g. `security-review` requires ≥ 0.70 trust)
- PR review `CasePlanModel` — goals, bindings, content-driven routing from code analysis findings
- `PrReviewCaseDefinition` (promoted to `review/src/main/` in devtown#60) — fluent DSL factory with `LambdaExpressionEvaluator` for binding conditions; uses `HumanTaskTarget.inline()` for human-approval binding; `PrReviewCaseDefinitionEquivalenceTest` verifies structural parity with YAML
- Merge queue `CasePlanModel` (casehub-refinery) — batch-then-bisect strategy as binding conditions
- Cross-repo coordinated merge — parent case + per-repo sub-cases with automatic rollback on fault
- Trust-weighted selection strategy for code review domain. See docs/DESIGN.md for implementation detail.
- Post-merge trust feedback — FLAGGED attestation when production incident traced to missed review
- **`DevtownRoles`** — 5-role RBAC model: `ADMIN` ("devtown-admin"), `ENGINEER` ("devtown-engineer"), `AUDITOR` ("devtown-auditor"), `DATA_CONTROLLER` ("devtown-data-controller"), `SERVICE` ("devtown-service"). `@RolesAllowed` on: `GovernanceResource` (ADMIN+ENGINEER+AUDITOR), `IncidentFeedbackResource` (ADMIN), `GdprErasureResource` (ADMIN+DATA_CONTROLLER), `MemoryAdminResource` (ADMIN)
- **`POST /api/actors/{actorId}/erasure`** (devtown#74) — GDPR Art.17 erasure: pseudonymises actor identity in ledger, cleans `CaseMemoryStore` (`contributor:` + `reviewer:` prefixes), persists tamper-evident `ErasureReceiptLedgerEntry` (V2004). SHA-256 hash fallback when no `ActorIdentity` mapping exists. Compliance report cross-reference via token-to-token matching.
- **`POST /api/incident-feedback`** (devtown#5, devtown#73) — records FLAGGED attestations against agents whose PR reviews missed issues found in production incidents. `IncidentFeedbackService` + `IncidentFeedbackResource` with `@RolesAllowed("admin")`. Idempotent via `findAttestationsByAttestorIdAndCapabilityTag` (tokenisation-proof). New domain types: `IncidentSeverity` (severity→confidence mapping), `IncidentFeedback`, `IncidentFeedbackResult`, `FlaggedAgent`, `ReviewDomain.REVIEW_CAPABILITIES` validation set. V2003 migration: index on `(repository, pr_number)` for PR lookup; dropped `tenancy_id` column from `merge_decision_ledger_entry` join table (field shadowing removal per ledger#131).
- **`DevtownActionRiskClassifier @RiskClassifier` (devtown#56):** Layer 5 extension; implements engine's `ActionRiskClassifier` SPI (engine#402). 8 `DevtownActionType` constants, 4 classification categories. `DevtownRiskClassifierProducer @RiskClassifier @ApplicationScoped` CDI adapter. PreferenceProvider-driven thresholds at scope `casehubio/devtown/risk/<actionType>`. `BooleanPreference` added to domain/preferences/. `HumanOversight.GENERAL` added as catch-all oversight group. Gate operates through engine's `ActionGateWorkItemHandler` lifecycle (classifier → PendingActionGate → WorkItem → human approval → resume) — no new REST endpoints.
- GitHub integration — PR webhook receiver, CI status reader, merge executor worker
- **CaseMemoryStore integration (devtown#43):** contributor history, reviewer agent context, and code-area history injected before PR review case starts; review outcomes written to memory at case close.
  - New domain types: `DevtownMemoryDomain`, `DevtownMemoryKeys`, `ReviewOutcome`, `ModulePathNormalizer` (devtown-domain)
  - New review types: `ReviewCompletedEvent`, `MemoryContext` (devtown-review)
  - New CDI components: `ReviewOutcomeObserver`, `CaseMemoryEmitter`, `CaseMemoryRecaller` (devtown-app)
  - `PrPayload` enhanced with `contributor` + `changedPaths`
  - Emission flow: `PlanItemCompletedEvent` → `ReviewOutcomeObserver` → `ReviewCompletedEvent` → `CaseMemoryEmitter` → `storeAll()`
  - Recall: `CaseMemoryRecaller` called before `PrReviewCaseService.startCase()`
  - Known tech debt: `CrossTenantCaseInstanceRepository` in async observer (engine#429 tracks fix)
  - Follow-up: engine#428–430, qhorus#251, devtown#65–68
- **CBR Phase 1 — PR similarity model (devtown#130, devtown#131):**
  - `PrFeatureVector` — structured feature extraction from PRs (file paths, modules, languages, change size, contributor)
  - `WeightedJaccardSimilarity` — 5-dimension weighted scoring with per-dimension breakdown
  - `CbrRetrievalService` — precedent retrieval from `CaseMemoryStore` (scan → score → rank → enrich)
  - `FeatureVectorEmitter` — stores case-scoped feature vectors as memory facts at case open
  - `Precedent` — past case with similarity score, feature vector, and capability outcomes
  - `MemoryContext` now includes `List<Precedent> precedents` alongside existing `contributorHistory` and `codeAreaHistory`
  - Uses `CaseMemoryStore` (not `CbrCaseMemoryStore`) due to four platform gaps documented in the spec; migration path to `CbrCaseMemoryStore` when neocortex gains `FeatureField.SetValued`
  - Epic #129 Phase 1 complete; Phase 2 (#132, #133) unblocked

## Merge Queue Implementation

Full merge queue lifecycle in `queue/`, `merge/`, and `app/` modules.

**Batch composition** (`DefaultBatchCompositionPolicy`): priority scoring via `QueuePriorityCalculator` (lane weight * 1000 + trust * 100 + wait decay), risk-aware grouping, adaptive sizing. `BatchFormationContext` carries `maxBatchSize`, `minBatchSize`, `decayRatePerHour`, `recentFailureRate`, `repository`, `targetBranch`, `riskLevel`, `bisectionStrategy`.

**Adaptive batch sizing**: `adaptiveMax = max(minBatchSize, floor(minTrust * maxBatchSize * (1 - recentFailureRate)))`. `MergeQueueService.formBatchesTransactional()` calls `store.recentBatchFailureRate(repository, failureRateWindow)`. `FailureRateAlertEvent` fired when per-repo rates exceed threshold.

**Bisection strategies**: `BinarySplitStrategy` (simple binary split), `PrecedentBisectionStrategy` (risk-score-sorted, high-risk in left slice), `TrustWeightedSplitStrategy` (trust-weighted split), `IsolateOutlierStrategy` (outlier isolation). All implement `BisectionSplitStrategy` interface.

**Precedent-based routing** (`CbrBatchRiskAssessor`): CBR-based batch risk scorer using precedent lookup from `CaseMemoryStore`. Implements `BatchRiskAssessor` interface.

**SLA**: per-priority-lane SLAs in `MergeQueuePreferenceKeys` — `SLA_CRITICAL` = PT1H, `SLA_HIGH` = PT4H, `SLA_NORMAL` = PT8H. `MergeQueueSlaBreachObserver` observes breaches. `DefaultSlaBreachPolicy` handles escalation.

**Persistence**: `JpaMergeQueueStore` with `BatchEntity` and `QueuedPrEntity`. `MergeQueuePort` hexagonal port interface, `MergeQueueStore` persistence interface.

**Batch retention/expunge**: `BatchRetentionJob` (`@Scheduled(cron = "0 0 3 * * ?")`) calls `store.expungeCompletedBefore(cutoff)` with configurable retention days (default 30 via `BATCH_RETENTION_DAYS`).

## CBR-Enhanced Reviewer Matching (devtown#133)

CBR integrated into reviewer selection via `cbrWeight` on `TrustRoutingPolicy`. `DevtownTrustRoutingPolicyProvider` provides per-capability CBR weights (defaults: security-review=0.2, architecture-review=0.2, style-review=0.2). Engine-ledger's `TrustWeightedAgentStrategy` uses `AgentRoutingContext.experiences()` (populated from `RetrievedExperience` and `ExperiencePlanStep`) to apply CBR bonus. `CbrReviewerMatchingIntegrationTest` proves an agent with lower trust but higher precedent match wins over higher-trust no-precedent agent.

**CBR domain** (`domain/cbr/`): `PrFeatureVector`, `Precedent`, `WeightedJaccardSimilarity` (5-dimension weighted scoring), `SimilarityGate`, `CbrWeightAdjuster` (dynamic weight adjustment), `PrecedentActivationPolicy`, `ActivationThreshold`, `CapabilityOutcome`. Config via `CbrPreferenceKeys` (K_LIMIT, MIN_THRESHOLD, TIME_WINDOW_DAYS, weights).

**Retrieval**: `CbrRetrievalService` interface, `DefaultCbrRetrievalService` implementation (scan case-vector memories → similarity gate → score → enrich with capability outcomes → compute completion times).

## Trust-Weighted Routing Closed Loop

**`report_incident` MCP tool** (`DevtownMcpTools`): reports a production incident against a merged PR — writes FLAGGED attestation against the reviewer's trust score. Parameters: repository, prNumber, incidentId, severity, description, reviewCapability, caseId (optional). `IncidentFeedbackService` resolves merge decision from ledger, finds worker decisions, writes FLAGGED attestations with trust dimension `REVIEW_THOROUGHNESS`. `TrustFeedbackClosedLoopTest` provides E2E proof of the full chain.

## EvidentialChecker V1-V4 Integration

`EvidentialAttestationPolicy` (`@Alternative @Priority(2)`) consumes `EvidentialChecker` from `io.casehub.qhorus.runtime.audit`. Runs all four benchmark variants: V1 (artefact check), V2 (channel check), V3 (correlation check), V4 (token check with content). Checks run only for configured phases per capability. `EvidentialViolationStore` stores violation records. MCP tool: `get_evidential_violations` lists violations from FLAGGED attestations.

## SLA Calibration

`SlaEstimator` (`domain/sla/`): computes SLA estimate from similar past review assignments using CBR precedents (`List<Precedent>`). Returns `SlaEstimate(median, precedentCount, min, max)` — median completion time from similar cases. `SlaEstimate.toContextMap()` injects calibration data into case context (medianSeconds, precedentCount, minSeconds, maxSeconds).

## Cursor-Based Pagination

`PagedResult<T>` (`app/governance/`): generic cursor-based pagination with Base64-encoded offset cursors, configurable limit (max 200). Used by `GovernanceResource` REST endpoints: `GET /api/governance/problems`, `/reviews`, `/reviewers`, `/triage` — all accept `cursor` and `limit` query params.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `get_prior_decisions` | Find prior review decisions for a repository and file path |
| `search_memory_by_contributor` | Search case memory for a contributor's review history |
| `search_memory_by_capability` | Search case memory for entries related to a review capability |
| `report_incident` | Report production incident against merged PR — writes FLAGGED attestation |
| `get_evidential_violations` | List evidential benchmark violations from FLAGGED attestations |
| `find_similar_cases` | CBR similarity search — ranked precedents with scores and capability outcomes |
| `get_cbr_weight_status` | Show current CBR similarity weights and dynamic adjustments |
| `get_agent_messages` | Agent channel message history for a case — dispatch, completion, decline, failure events |

## Governance Workbench UI

Web UI built with casehub-pages DSL. Six views:

**Operations** — operational metrics dashboard (throughput, latency, error rates)

**Reviews** — PR review case workbench with inbox and detail tabs

**Merge Queue** — merge batch status, SLA tracking, batch composition

**Reviewers** (governance workbench) — reviewer trust management:
- List view: all reviewers with trust scores table (by capability: code-analysis, security, architecture, style), open commitments, total decisions, maturity phase
- Profile view: detailed reviewer breakdown with trust charts (by capability and by dimension), decision history, commitment timeline
- Dataset: `reviewers` (powered by `GovernanceQueryService`)

**Triage** — incident feedback and FLAGGED attestation entry for production incidents traced to missed reviews

**System** — configuration, diagnostics, health checks

**GovernanceQueryService** — aggregates reviewer health metrics from ledger, trust scores, and commitment state. Queries used by Reviewers view.

**GovernanceEventBridge** (`@ServerEndpoint("/governance/events")`) — WebSocket endpoint for real-time reviewer status updates. Broadcasts reviewer trust score changes, commitment lifecycle events, and attestation submissions to connected clients.

## What It Does NOT Own

Everything below belongs in the foundation:
- Trust scoring computation (casehub-ledger)
- Commitment lifecycle (casehub-qhorus)
- Case engine and blackboard (casehub-engine)
- WorkItem inbox (casehub-work)
- Notification delivery (casehub-connectors)

## Dependencies

```
casehub-devtown
  → casehub-engine   (CasePlanModel, sub-cases, bindings)
  → casehub-engine-ledger           (TrustWeightedAgentStrategy, CBR cbrWeight routing)
  → casehub-ledger   (Merkle audit, trust scoring, GDPR)
  → casehub-work     (human review WorkItem, SLA, escalation)
  → casehub-qhorus   (COMMAND/RESPONSE per reviewer, commitment lifecycle, EvidentialChecker)
  → casehub-connectors (Slack/Teams for review assignments and failures)
  → casehub-platform-memory-inmem  (in-memory CaseMemoryStore for @QuarkusTest isolation)
  → casehub-platform-oidc          (OidcCurrentPrincipal, @RolesAllowed enforcement)
  → casehub-engine-work-adapter    (ActionRiskClassifier oversight gate — devtown#56)
```

## Key Epics

1. Project scaffold
2. Domain model — capability tags, trust dimensions, routing thresholds
3. PR review CasePlanModel — content-driven routing and parallel checks
4. Merge queue (casehub-refinery) — batch-then-bisect
5. Cross-repo coordinated merge
6. Trust-weighted reviewer routing and post-merge feedback
7. Failure handling — DECLINED vs FAILED routing
8. GitHub integration
9. Notification wiring
10. Observability and operational tooling

Issues: https://github.com/casehubio/devtown/issues?label=epic
