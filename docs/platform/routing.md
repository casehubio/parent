# Routing

> **Scope:** Agent routing strategies — trust-weighted, semantic, LLM-reasoned, CBR-evidence
> **Audience:** All (app builders configure routing; platform builders extend strategies)
> **Key repos:** casehub-ledger (score computation), casehub-blocks (policy config + AI strategies), casehub-engine (classical strategy execution)

## Overview

The routing system selects which agent (human or AI worker) should handle a task. It spans four layers, from trust score computation through to final assignment. Each layer has a clear owner and defined SPI contracts.

## Four-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│ 1. Score Computation (casehub-ledger)          │
│    TrustScoreRoutingPublisher                   │
│    Computes trust scores from ledger entries    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 2. Policy Configuration (casehub-blocks)        │
│    TrustRoutingPolicyResolver                   │
│    Loads policy from preferences                │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 3. Classical Strategy Execution (casehub-engine)│
│    TrustWeightedAgentStrategy                   │
│    SemanticAgentRoutingStrategy                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 4. AI Strategy Execution (casehub-blocks)       │
│    LlmAgentRoutingStrategy                      │
│    CbrAgentRoutingStrategy                      │
└─────────────────────────────────────────────────┘
```

**Ownership principle:** Each layer lives where its differentiating dependency lives. Trust-weighted strategy lives in engine-ledger because it depends on ledger APIs. LLM strategy lives in blocks because it depends on AgentProvider (platform AI runtime). Semantic strategy lives in engine-ai because it depends on embedding models.

## Layer 1: Score Computation (ledger)

**Owner:** casehub-ledger

**Key class:** `TrustScoreRoutingPublisher`

Computes trust scores from ledger entries and publishes them as events. The scoring algorithm is Bayesian Beta — each outcome (success/failure) updates the prior, and the score is the posterior mean.

**Output:** Trust scores keyed by `(actorId, contextKey, capabilityName)` — one score per agent-context-capability triple.

**Where scores come from:** Outcome attestations recorded in the ledger. Every time a task completes, the outcome (success/failure, confidence, compliance) is written to the ledger. The scorer aggregates these outcomes into a Beta distribution per actor-context-capability.

## Layer 2: Policy Configuration (blocks + engine-api)

**Owners:** casehub-blocks (utilities) + domain repos (implementation)

**Key classes:**
- `TrustRoutingPolicyKeys` (blocks) — shared preference key constants
- `TrustRoutingPolicyResolver` (blocks) — loads policy from preference store
- `TrustRoutingPolicyProvider` (engine-api SPI) — domain repos implement this

**What it does:** Converts user preferences into a `TrustRoutingPolicy` object. Policy includes:
- Bootstrap escalation threshold — when to escalate if only BOOTSTRAP candidates exist
- Borderline inclusion flag — whether to include BORDERLINE candidates in the eligible pool
- Phase 2B/3 exclusion thresholds — trust score thresholds for excluding candidates

**Domain responsibility:** Each domain repo (aml, devtown, clinical, life, ops) implements `TrustRoutingPolicyProvider` to configure policy parameters for its use cases. The policy is domain-specific (fraud investigations have different thresholds than clinical trials), but the loading mechanism is shared.

## Layer 3: Classical Strategy Execution (engine)

**Owner:** casehub-engine

Two built-in strategies:

### TrustWeightedAgentStrategy

**Location:** engine-ledger module

**Priority:** `@Priority(1)` — runs first if ledger is on the classpath

Applies trust-based filtering using the four-phase trust maturity model:

1. **Classify candidates** — via `TrustCandidateClassifier.classify()`, returns classification per candidate (BOOTSTRAP, BORDERLINE, QUALIFIED, EXCLUDED_PHASE2B, EXCLUDED_PHASE3)
2. **Bootstrap guard** — if `bootstrapEscalationRequired = true` and only BOOTSTRAP candidates exist, escalate with `EscalationReason.NO_QUALIFIED_AGENT`
3. **Filter eligible pool** — exclude BORDERLINE (unless policy allows), EXCLUDED_PHASE2B, EXCLUDED_PHASE3, and BOOTSTRAP (if bootstrap escalation is required)
4. **If empty after filtering** — delegate to `TrustCandidateClassifier.decide()` to choose escalation vs fallback
5. **Otherwise** — select from the eligible pool (currently: highest trust score; future: weighted random)

**Trust maturity phases:**
- **BOOTSTRAP** — new agent with <10 samples, score unknown
- **BORDERLINE** — score exists but fails qualification threshold
- **QUALIFIED** — meets qualification threshold
- **EXCLUDED_PHASE2B** — explicitly excluded via preference (user-configured blocklist)
- **EXCLUDED_PHASE3** — score exists, known poor performer (failed outcome threshold)

### SemanticAgentRoutingStrategy

**Location:** engine-ai module

**Priority:** `@Priority(2)` — runs if engine-ai is on the classpath and trust strategy is absent or declined

Embedding-based re-ranking. Compares the task description embedding to agent capability embeddings and ranks candidates by cosine similarity.

**When to use:** Tasks where semantic match matters more than historical trust (e.g. "find an agent who understands Rust async runtime internals" — exact trust history may not exist, but embedding similarity can identify the right specialist).

## Layer 4: AI Strategy Execution (blocks)

**Owner:** casehub-blocks (routing.agent package)

Two AI-powered strategies that optionally compose with trust classification:

### LlmAgentRoutingStrategy

**Operation modes:**
- **Pure LLM mode** — when trust services are unavailable, delegates selection entirely to the LLM
- **Trust-filtered LLM mode** — when trust services are present, applies trust-based pre-screening before LLM selection

**Flow (trust-filtered mode):**

1. Classify all candidates via `TrustCandidateClassifier`
2. Apply bootstrap guard and filter eligible pool (same logic as `TrustWeightedAgentStrategy`)
3. If eligible pool is empty after filtering, delegate escalation decision to `TrustCandidateClassifier.decide()`
4. Otherwise, invoke LLM with the filtered pool:
   - Assemble prompt via `RoutingPromptAssembler` (composable enrichment)
   - Invoke LLM via `AgentProvider`
   - Parse response via `RoutingSupport.parseSelection()`
5. If LLM invocation fails or response is unparseable:
   - If trust classification is available, delegate to `TrustCandidateClassifier.decide()`
   - Otherwise, return `AgentAssignment.unresolvable()`

**Prompt enrichment:** `RoutingPromptAssembler` composes all `RoutingPromptSection` SPI implementations (discovered via CDI). Each section contributes a snippet (e.g. CBR history, past failures, trust tier). The assembler concatenates them into the final prompt.

### CbrAgentRoutingStrategy

**Flow:**

1. Extract features from the routing context via `RoutingFeatureExtractor.extractFeatures()`
2. Query `CbrRetrievalService` for similar past cases
3. If no similar cases found → fallback to `LlmAgentRoutingStrategy`
4. Otherwise:
   - Build prompt enriched with CBR evidence (past outcomes, agent performance on similar cases)
   - Invoke LLM via `AgentProvider`
   - Parse response
5. Record outcome via `CbrRoutingOutcomeRecorder` for future retrieval

**Integration with trust:** CBR strategy can optionally compose with `TrustCandidateClassifier` (same trust-filtering logic as LLM strategy). If trust services are available, CBR retrieval is constrained to QUALIFIED candidates only.

## SPIs and Extension Points

### RoutingFeatureExtractor

Extracts features from the routing context for CBR similarity queries.

```java
public interface RoutingFeatureExtractor {
    Map<String, Object> extractFeatures(AgentRoutingContext context);
    @Nullable String extractProblem(AgentRoutingContext context);
}
```

**Default implementation:** `TextOnlyFeatureExtractor` — extracts text from the case context JSON and returns a single feature map.

**Domain extension:** Implement this SPI to extract domain-specific features (e.g. transaction pattern cluster for AML, adverse event type for clinical, opponent race for QuarkMind).

### RoutingPromptSection

Contributes a prompt section for LLM-based routing.

```java
public interface RoutingPromptSection {
    @Nullable String render(AgentRoutingContext context, List<AgentCandidate> eligible);
}
```

**Built-in implementation:** `CbrRoutingPromptSection` — renders past CBR outcomes as a prompt section.

**How it works:** All `RoutingPromptSection` beans are discovered via CDI and composed by `RoutingPromptAssembler`. Each section returns a string (or null if it has nothing to contribute). The assembler concatenates them with newline separators.

**Domain extension:** Implement this SPI to add domain-specific context (e.g. "past fraud patterns on similar transactions", "adverse events on similar trial arms").

### RoutingOutcomeRecorder

Records routing outcomes for future CBR retrieval.

**Built-in implementation:** `CbrRoutingOutcomeRecorder` — writes outcomes to `CbrRetrievalService` (backed by `CaseMemoryStore`).

**What gets recorded:**
- Features extracted by `RoutingFeatureExtractor`
- Selected agent ID
- Outcome (success/failure, if available)
- Timestamp

## Strategy Selection

The engine invokes `AgentRoutingStrategy` beans in priority order (`@Priority` annotation). The first strategy to return a definitive assignment wins.

**Typical priority order:**

1. `TrustWeightedAgentStrategy` (`@Priority(1)`) — if ledger is on classpath
2. `SemanticAgentRoutingStrategy` (`@Priority(2)`) — if engine-ai is on classpath
3. `LlmAgentRoutingStrategy` (`@Priority(100)`) — default AI fallback
4. `CbrAgentRoutingStrategy` (`@Priority(101)`) — CBR-first routing

**Escape hatch:** If no strategy returns a definitive assignment, the engine escalates with `EscalationReason.NO_ROUTING_STRATEGY`.

## Configuration

### Trust Policy (per domain)

Each domain repo implements `TrustRoutingPolicyProvider` and loads policy from preferences:

```java
@ApplicationScoped
public class AmlTrustRoutingPolicyProvider implements TrustRoutingPolicyProvider {
    @Inject PreferenceService preferences;

    @Override
    public Optional<TrustRoutingPolicy> getPolicy(String tenancyId) {
        return TrustRoutingPolicyResolver.resolve(preferences, tenancyId);
    }
}
```

**Policy parameters:**
- `casehub.trust.bootstrap-escalation-required` — boolean, default true
- `casehub.trust.borderline-inclusion-allowed` — boolean, default false
- `casehub.trust.phase2b-exclusion-list` — comma-separated agent IDs
- `casehub.trust.phase3-outcome-threshold` — double, default 0.3 (exclude if trust score < 30%)

### LLM Routing Configuration

LLM strategies require `AgentProvider` (platform-agent module). If not available, they return `unresolvable`.

**Model selection:** `AgentProvider` configuration is global (platform-level). Apps do not configure which model the routing LLM uses — that's a platform concern.

### CBR Configuration

CBR strategy requires:
- `CbrRetrievalService` (engine module)
- `CaseMemoryStore` (platform module, with adapter: memory-jpa, memory-mem0, or memory-graphiti)

**Similarity function:** Pluggable via `CbrRetrievalService` configuration (cosine similarity, Euclidean distance, or custom).

## Protocols

Trust maturity model: [`casehub/garden: trust-maturity-model.md`](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/trust-maturity-model.md)

## Testing

### Strategy Tests

- `TrustWeightedAgentStrategyTest` — trust classification scenarios (bootstrap guard, filtering, escalation)
- `LlmAgentRoutingStrategyTest` — pure LLM mode, trust-filtered mode, fallback on LLM failure
- `CbrAgentRoutingStrategyTest` — CBR retrieval, prompt enrichment, outcome recording

### Contract Tests

- `AgentRoutingStrategyContractTest` — validates all strategy implementations against the SPI contract

## See Also

- [Trust Ledger](https://github.com/casehubio/ledger) — outcome attestation and trust score computation
- [Case Memory](https://github.com/casehubio/platform) — `CaseMemoryStore` and adapters
- [CBR Capability](cbr.md) — full CBR architecture (Retrieve, Reuse, Revise, Retain)
