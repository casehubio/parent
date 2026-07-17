# Case-Based Reasoning (CBR)

> **Scope:** The 4 CBR steps (Retrieve, Reuse, Revise, Retain) and their platform homes
> **Audience:** All
> **Key repos:** casehub-neocortex (retrieval), casehub-engine (reuse), casehub-ledger (retain), casehub-blocks (feature extraction)

## Overview

CaseHub is named for *cases* — and now it does true Case-Based Reasoning. Every task is an opportunity to learn from analogous past experience. Rather than choosing from a fixed menu of strategies, the system retrieves similar past cases, adapts their solutions to the current context, and records the outcome for future retrieval.

## Why CBR

Traditional routing is a lookup table: given `(actorId, contextKey)`, replay the historical win rate. This works when the same problem repeats. It fails when the problem is *similar* but not identical — a new opponent race in QuarkMind, a novel transaction pattern in AML, a rare adverse event in clinical trials.

CBR closes that gap. It retrieves cases by feature-vector similarity, not exact key match. A Zerg roach-rush game inherits strategy from past Zerg all-in games, even if the exact build order differs. An AML investigation inherits escalation structure from past confirmed fraud cases with similar transaction patterns, even if the entities are new.

## The Four CBR Steps

Classic CBR (Aamodt & Plaza, 1994) has four steps: Retrieve, Reuse, Revise, Retain. Each step has a clear owner in the CaseHub platform.

```
Problem (CaseFile features)
        ↓
┌──────────────────────────────┐
│ 1. RETRIEVE                  │  casehub-neocortex
│    HybridCaseRetriever       │  CbrRetrievalService
│    Find k most similar cases │
└──────────────────────────────┘
        ↓ top-k cases
┌──────────────────────────────┐
│ 2. REUSE                     │  casehub-engine
│    Select solution from      │  casehub-blocks
│    retrieved cases           │  (routing strategies)
└──────────────────────────────┘
        ↓ chosen solution
┌──────────────────────────────┐
│ 3. REUSE (Plan Adaptation)   │  casehub-neocortex
│    Adapt retrieved plan to   │  PlanAdapter SPI
│    current context           │  AdaptedPlan
└──────────────────────────────┘
        ↓ adapted solution + outcome
┌──────────────────────────────┐
│ 4. REVISE (Outcome Feedback) │  Application tier
│    Record outcome, adjust    │  RoutingOutcomeRecorder
│    case memory               │  CaseOutcomeObserver
└──────────────────────────────┘
        ↓ outcome recorded
┌──────────────────────────────┐
│ 5. RETAIN                    │  casehub-neocortex
│    Record as new retrievable │  CaseMemoryStore
│    case via MemoryEmitter    │  (memory backends)
└──────────────────────────────┘
```

### 1. Retrieve — Find Similar Past Cases

**Owner:** casehub-neocortex

**Key classes:**
- `HybridCaseRetriever` / `ReactiveHybridCaseRetriever` — hybrid retrieval: semantic search + metadata filtering
- `CbrRetrievalService` (casehub-engine) — routing-specific wrapper, queries `CaseMemoryStore` with feature vectors
- `CbrSimilarityScorer` — pluggable per-field similarity with configurable weights (categorical exact match, numeric linear decay, text exact match)
- `FeatureValue` — sealed type hierarchy: `Boolean`, `NumericList`, `TimeSeries`, `DiscreteSequence` (replaces `Map<String, Object>`)
- `SimilaritySpec` — sealed interface for per-type similarity computation (DTW for `TimeSeries`, edit distance for `DiscreteSequence`, Jaccard for sets)
- `TrendAnalyzer` — derives Numeric features from TimeSeries data; `TrendSpec` declares extraction rules; `TrendEnrichmentDecorator` injects trends at retrieval time
- `CbrQuery` — gains `weights` and `vectorWeight` for per-field weight configuration

**How it works:**

1. Extract features from the current case via `RoutingFeatureExtractor.extractFeatures(context)` — returns typed `FeatureValue` instances
2. Query `CaseMemoryStore` for cases with similar feature vectors (semantic + metadata hybrid search)
3. Rank by weighted per-field similarity score — each field uses its appropriate `SimilaritySpec` (exact match for categoricals, DTW for temporal sequences, linear decay for numerics)
4. Apply trend enrichment — `TrendEnrichmentDecorator` derives trend features from `TimeSeries` values before scoring
5. Return top-k cases with their features, solution, and outcome

**Feature extraction:** Domain-specific. Apps implement `RoutingFeatureExtractor` to extract features relevant to their domain. Features are now typed via `FeatureValue` sealed hierarchy — structured case fields support nested objects and list containment.

**Examples:**

- **QuarkMind:** `[opponent_race, detected_build_order, enemy_posture, game_phase, army_size_ratio]`
- **AML:** `[transaction_pattern_cluster, entity_risk_tier, prior_outcomes_on_similar_profiles]`
- **Clinical:** `[adverse_event_type, trial_arm, patient_risk_profile, protocol_phase]`

**Similarity functions:**

- **Categorical features** — exact match (1.0) or no match (0.0), with optional decay based on feature importance
- **Numeric features** — Gaussian decay, step function, or exponential decay
- **Text features** — embedding cosine similarity (via `HybridCaseRetriever`)

**Hybrid retrieval:** `HybridCaseRetriever` combines semantic search (embedding-based) with metadata filtering (structured features). The engine queries both, merges results, and re-ranks by weighted similarity.

**Per-leg embedding separation (casehubio/neocortex#113):** When a case has multiple text legs (e.g. problem description + solution description), each leg gets its own embedding. Retrieval can match on either leg or both (weighted).

### 2. Reuse — Select a Solution from Retrieved Cases

**Owner:** casehub-engine (worker routing), casehub-blocks (implementation routing, in progress)

Two distinct sub-problems:

#### 2a. Routing Between Workers (Implemented)

**Owner:** casehub-engine

**Key classes:**
- `TrustWeightedAgentStrategy` (engine-ledger) — trust-based worker selection
- `CbrAgentRoutingStrategy` (blocks) — CBR-evidence worker selection

**How it works:**

1. Retrieve similar past cases (via step 1)
2. Filter cases by trust classification (QUALIFIED candidates only, if trust is available)
3. Build prompt enriched with CBR evidence: past outcomes, agent performance on similar cases
4. Invoke LLM via `AgentProvider` to select the winner
5. Return `AgentAssignment.assign(workerId, rationale)`

**Trust integration:** `CbrAgentRoutingStrategy` optionally composes with `TrustCandidateClassifier`. If trust services are available, CBR retrieval is constrained to QUALIFIED candidates only (trust score above threshold). This prevents the LLM from selecting a historically poor performer just because they handled a similar case once.

**Prompt enrichment:** `CbrRoutingPromptSection` (blocks) renders past CBR outcomes as a prompt section. Example:

```
Past similar cases:
- Case A (similarity: 0.87): Agent X succeeded (trust: 0.72)
- Case B (similarity: 0.81): Agent Y failed (trust: 0.45)
- Case C (similarity: 0.76): Agent X succeeded (trust: 0.78)

Recommendation: Agent X has the strongest track record on similar cases.
```

The LLM sees this evidence and makes the final selection.

#### 2b. Routing Between Implementations (Gap — In Progress)

**Owner:** casehub-engine (target), currently app-layer workaround

**Current gap:** When multiple `TaskDefinition` implementations register for the same capability (e.g. `DroolsStrategyTask`, `EarlyPressureStrategyTask`, `EconomicExpansionStrategyTask` all implementing `StrategyTask`), the engine currently runs all of them (every `canActivate()` returning true gets a PlanItem).

**Workaround (QuarkMind):** `StrategyTrustRouter` + `StrategySelector` select the winner and gate the others via `canActivate()`. This belongs in the engine, not the application.

**Target:** `casehub-engine` should provide an `ImplementationRoutingStrategy` SPI — symmetric to `AgentRoutingStrategy` but operating over competing `TaskDefinition` implementations. The trust-maturity four-phase model (BOOTSTRAP / BORDERLINE / QUALIFIED / EXCLUDED) applies identically.

**Status:** Tracked via casehubio/engine (pending issue creation).

### 3. Reuse (Plan Adaptation) — Adapt the Solution to Current Context

**Owner:** casehub-neocortex (`PlanAdapter` SPI)

**Key classes:**
- `PlanAdapter` SPI — transforms a retrieved plan for the current context. Domain-specific — each app provides its own adapter.
- `AdaptedPlan` — the result of adaptation, carrying the modified plan and rationale.
- `LifePlanAdapter` (casehub-life) — reference implementation with 6 domain-specific `LifeAdaptationRule` implementations (appointment, contractor, financial, health, home-maintenance, travel).

**How it works:**

1. Top-k retrieved cases are passed to the domain's `PlanAdapter`
2. The adapter evaluates the current context against retrieved solutions
3. Domain-specific adaptation rules modify plan parameters (e.g., adjust SLA, substitute workers, re-weight priorities)
4. The `AdaptedPlan` is injected into the case context before engine execution

**Status:** ✅ Shipped. `PlanAdapter` SPI in casehub-neocortex. Reference implementation in casehub-life with 6 adaptation rules. The previous gap (binary solution selection, no parameterisation) is closed.

### 3b. Revise (Outcome Feedback) — Record and Learn from Outcomes

**Owner:** Application tier + casehub-blocks

**Key classes:**
- `RoutingOutcomeRecorder` (blocks) — records agent routing outcomes into CBR memory
- `CaseOutcomeObserver` (blocks) — records case-level completion outcomes
- `CbrCaseMemoryStore` (neocortex) — CBR-specific memory store wrapper for outcome recording

**How it works:**

1. After task completion, the outcome recorder captures the result (success/failure/confidence)
2. Features extracted at decision time are stored alongside the outcome
3. Active memory management applies temporal decay — older cases lose relevance over time
4. Supersession SPI allows newer cases to explicitly supersede older ones

**Adopted by:** devtown (contributor/reviewer history), aml (entity context + SAR outcomes), clinical (patient/site/AE), life (6 domain schemas), iot (device situations), desiredstate (fault/situation response).

### 4. Retain — Store the Outcome as a Retrievable Case

**Owner:** casehub-ledger (trust scores) + casehub-neocortex (`CaseMemoryStore`)

Two complementary stores:

| Store | What it holds | Use for CBR |
|-------|--------------|-------------|
| `casehub-ledger` | Tamper-evident outcome attestations, trust scores (Bayesian Beta), decision records | Trust credence — "this strategy won 70% of similar games" |
| `CaseMemoryStore` (neocortex) | Queryable, permission-aware case memories; adapters: `memory-jpa`, `memory-mem0`, `memory-graphiti`, `memory-qdrant`, `memory-cbr-inmem` | Full case representation — problem features + solution + outcome, retrievable by semantic similarity |

**Both are needed.** The ledger provides the compliance record and trust signal. The memory store provides the rich case representation for retrieval.

**What gets recorded:**

- **Features** — extracted via `RoutingFeatureExtractor` at decision time as typed `FeatureValue` instances
- **Solution** — which agent/implementation was chosen, with rationale
- **Outcome** — success/failure, confidence, compliance (if available)
- **Timestamp** — when the decision was made

**MemoryEmitter (neocortex):** `@ApplicationScoped` fire-and-forget CDI wrapper around `CaseMemoryStore.store()`. Replaces boilerplate (null-check, build `MemoryInput`, try-catch) with a single `emit()` call. Used by aml, clinical, devtown, life, and iot for CBR outcome recording.

**Outcome recording:** `RoutingOutcomeRecorder` (blocks) and `CaseOutcomeObserver` (blocks) write outcomes to CBR memory. The recorder is invoked after task completion, not at routing time.

**Active memory management:** Temporal decay — older case memories lose relevance over time. Supersession SPI — newer cases explicitly supersede older ones. CBR reconciliation provides batch upsert, orphan cleanup, and disaster recovery for Qdrant-backed stores.

**Ledger integration:** When ledger is present, trust scores are also recorded. The trust score is a credence signal (Bayesian Beta posterior mean). The case memory is the full case representation.

## Component Map

### CaseMemoryStore (platform)

**Purpose:** Queryable, permission-aware case memory persistence.

**Adapters:**
- `memory-jpa` — PostgreSQL backend with vector extension (pgvector)
- `memory-mem0` — Mem0 cloud service (managed vector DB)
- `memory-graphiti` — Graphiti graph-augmented memory (under evaluation)

**Operations:**
- `store(case)` — persist a new case
- `retrieve(features, k)` — retrieve top-k similar cases
- `update(caseId, outcome)` — update outcome after task completion

**Permission model:** Cases are tenancy-scoped. Retrieval respects tenancy boundaries (a user in Tenancy A cannot retrieve cases from Tenancy B).

### HybridCaseRetriever (neocortex)

**Purpose:** Hybrid retrieval: semantic search + metadata filtering.

**How it works:**

1. **Semantic search** — embed the query text, find top-n cases by cosine similarity
2. **Metadata filtering** — filter by structured features (e.g. `opponent_race = "Zerg"`)
3. **Merge and re-rank** — combine results, re-rank by weighted similarity (semantic + metadata)

**Per-leg embedding:** Cases with multiple text legs (problem + solution) have separate embeddings. Retrieval can match on either leg or both (weighted).

**Similarity spec:** `CbrSimilarityScorer` resolves a `SimilaritySpec` per feature. Spec includes:
- **Categorical** — exact match table, optional decay
- **Gaussian** — mean, stddev, weight
- **Step** — threshold, weight
- **Exponential** — decay rate, weight

**Example (QuarkMind):**

```json
{
  "opponent_race": { "type": "categorical", "weight": 0.3 },
  "army_size_ratio": { "type": "gaussian", "mean": 1.0, "stddev": 0.2, "weight": 0.4 },
  "game_phase": { "type": "step", "threshold": 500, "weight": 0.3 }
}
```

### CbrRetrievalService (engine)

**Purpose:** Routing-specific wrapper around `CaseMemoryStore` and `HybridCaseRetriever`.

**Operations:**
- `retrieve(features, k)` → top-k similar cases
- `recordOutcome(caseId, outcome)` → update outcome after completion

**Integration with routing:** `CbrAgentRoutingStrategy` (blocks) calls this service at routing time.

### RoutingFeatureExtractor (blocks SPI)

**Purpose:** Extract features from the routing context for CBR similarity queries.

```java
public interface RoutingFeatureExtractor {
    Map<String, Object> extractFeatures(AgentRoutingContext context);
    @Nullable String extractProblem(AgentRoutingContext context);
}
```

**Default implementation:** `TextOnlyFeatureExtractor` — extracts text from the case context JSON and returns a single feature map.

**Domain extension:** Implement this SPI to extract domain-specific features (e.g. transaction pattern cluster for AML, adverse event type for clinical, opponent race for QuarkMind).

### CbrRoutingOutcomeRecorder (blocks)

**Purpose:** Record routing outcomes for future CBR retrieval.

**What gets recorded:**
- Features extracted by `RoutingFeatureExtractor`
- Selected agent ID
- Outcome (success/failure, if available)
- Timestamp

**When it records:** After task completion, not at routing time. The recorder observes `TaskCompletedEvent` (or equivalent) and writes to `CbrRetrievalService`.

## Current State

| CBR step | Current implementation | Gap |
|----------|----------------------|-----|
| Retain | casehub-ledger trust scores (trust credence only) | No full case representation stored for similarity retrieval — `CaseMemoryStore` adapters exist but no harness has wired for CBR yet |
| Retrieve | `HybridCaseRetriever` (neocortex), `CbrRetrievalService` (engine) | SPIs exist, not yet wired to CBR retrieval in any harness |
| Reuse (workers) | `CbrAgentRoutingStrategy` (blocks) | Implemented, not yet deployed in any harness |
| Reuse (implementations) | Application-layer workarounds (QuarkMind `StrategyTrustRouter`) | `ImplementationRoutingStrategy` missing from engine |
| Revise | Not implemented | Adaptive plan templates not defined |

## Trust Integration

CBR and trust are complementary, not competing. Trust provides a credence signal (how confident are we in this agent?). CBR provides a similarity signal (how similar is this case to past cases?).

**Composition:**

1. **Retrieve** — find similar past cases (CBR)
2. **Filter by trust** — exclude BOOTSTRAP/BORDERLINE/EXCLUDED candidates (trust)
3. **Enrich prompt with CBR evidence** — past outcomes on similar cases (CBR)
4. **Select** — LLM chooses from the trust-filtered, CBR-enriched pool

**Why both:** Trust alone cannot generalise to novel situations. CBR alone cannot filter out historically poor performers. Together, they provide robust routing.

## Reference Implementation — QuarkMind

QuarkMind is the first and most demanding CBR test case: millisecond game-loop granularity, real win/loss feedback from the SC2 API, and multiple competing strategy implementations with measurable outcomes.

**Current state:**

| CBR step | QuarkMind status |
|----------|-----------------|
| Retain | Ledger outcome recording (trust scoring) — no `CaseMemoryStore` writes yet |
| Retrieve | Exact match only (`opponentContext` = PvT/PvZ/PvP) — no feature-vector retrieval |
| Reuse (implementation) | Application-layer workaround: `StrategyTrustRouter` + `StrategySelector` |
| Reuse (worker) | N/A — QuarkMind has no human/AI worker routing |
| Revise | Not implemented |

**Target state:**

| CBR step | QuarkMind target |
|----------|----------------|
| Retain | Add `CaseMemoryStore` writes at game end capturing full game context (opponent features, strategy chosen, outcome) |
| Retrieve | Implement `CaseRetriever` integration — retrieve top-k similar past games by feature vector |
| Reuse (implementation) | Migrate `StrategyTrustRouter` logic to `casehub-engine ImplementationRoutingStrategy` |
| Revise | Parameterise strategy selection from retrieved case blend (long-term) |

## Configuration

### CaseMemoryStore Adapter Selection

Set the active adapter via application.properties:

```properties
casehub.memory.adapter=jpa  # or mem0, graphiti
```

**Adapter-specific config:**

```properties
# JPA (pgvector)
quarkus.datasource.db-kind=postgresql
casehub.memory.jpa.vector-dimension=1536  # OpenAI embedding dim

# Mem0
casehub.memory.mem0.api-key=${MEM0_API_KEY}
casehub.memory.mem0.organisation-id=${MEM0_ORG_ID}
```

### Similarity Spec Configuration

Each domain configures its similarity spec (per feature):

```yaml
# aml/src/main/resources/cbr-similarity.yaml
features:
  transaction_pattern_cluster:
    type: categorical
    weight: 0.4
  entity_risk_tier:
    type: step
    threshold: 0.5
    weight: 0.3
  prior_fraud_rate:
    type: gaussian
    mean: 0.1
    stddev: 0.05
    weight: 0.3
```

## Extension Points

### Custom Feature Extractors

Implement `RoutingFeatureExtractor` for your domain:

```java
@ApplicationScoped
public class AmlFeatureExtractor implements RoutingFeatureExtractor {
    @Override
    public Map<String, Object> extractFeatures(AgentRoutingContext context) {
        var caseFile = context.caseContext();
        return Map.of(
            "transaction_pattern_cluster", extractCluster(caseFile),
            "entity_risk_tier", extractRiskTier(caseFile),
            "prior_fraud_rate", extractPriorFraudRate(caseFile)
        );
    }
}
```

### Custom Similarity Functions

Extend `CbrSimilarityScorer` to add new similarity functions (e.g. edit distance, Jaccard).

### Custom Outcome Recorders

Implement `RoutingOutcomeRecorder` (hypothetical SPI, not yet defined) to record outcomes to additional stores (e.g. MLflow, custom analytics DB).

## Testing

### Retrieval Tests

- `HybridCaseRetrieverTest` — semantic + metadata filtering, per-leg embedding
- `CbrRetrievalServiceTest` — routing context → features → retrieval

### Routing Tests

- `CbrAgentRoutingStrategyTest` — CBR retrieval, prompt enrichment, outcome recording
- `CbrRoutingPromptSectionTest` — prompt rendering with past outcomes

### Contract Tests

- `CaseMemoryStoreContractTest` (future) — JUnit 5 `@TestTemplate` for all memory adapters

## Migration Note — casehub-poc Retirement

`casehub-poc` (GroupId: `io.casehub`, artifactId: `casehub-core:1.0.0-SNAPSHOT`) is retiring — no new features. CBR capabilities belong in `casehub-engine` (casehubio/engine), not in casehub-poc.

QuarkMind currently depends on casehub-poc. Before CBR retrieval or implementation routing can be properly wired, QuarkMind must migrate its `CaseEngine` dependency from casehub-poc to `casehub-engine`.

## See Also

- [Routing](routing.md) — agent routing strategies and trust integration
- [Trust Ledger](https://github.com/casehubio/ledger) — outcome attestation and trust score computation
- [Case Memory](https://github.com/casehubio/platform) — `CaseMemoryStore` and adapters
- [Neocortex](https://github.com/casehubio/neocortex) — `HybridCaseRetriever` and RAG infrastructure
- Aamodt, A., & Plaza, E. (1994). Case-based reasoning: Foundational issues, methodological variations, and system approaches. AI Communications, 7(1), 39-59.
