# Drill-Down — AI Knowledge & Learning

*Typed features, hybrid retrieval, outcome feedback, and seven memory backends — the machinery behind agents that learn.*

---

## Architecture Overview

AI knowledge and learning in CaseHub spans five subsystems, all in
the neocortex repository (61 modules). They share CDI decorator
chains, tenant scoping, fusion strategies, and contract test suites.

```
On-Device Inference ─── ONNX Runtime JNI
        │
        ▼
RAG Pipeline ──────── 3-leg hybrid search (dense + sparse + BM25)
        │
        ▼
CBR Engine ────────── Typed feature similarity + outcome feedback
        │
        ▼
Agent Memory ──────── 7 backends, salience ordering, GDPR erasure
        │
        ▼
Knowledge Graph ───── Thing model, dynamic types, derived edges
```

The learning loop connects them: execution outcomes feed CBR
confidence adjustment, which modulates retrieval scoring for future
routing and plan adaptation. Trust-weighted retrieval bridges
directly to the ledger's Bayesian EigenTrust model via
`AgentTrustProvider` SPI — CBR scores are not isolated numbers but
signals in the platform's composable routing pipeline.

---

## SPI Contracts

### Inference SPIs

| Interface | Methods | Governs |
|-----------|---------|---------|
| `InferenceEngine` | `infer(InferenceInput input, InferenceTask task)` | Model execution |
| `InferenceTask` | `adapt(OrtSession session, InferenceInput input)` → `InferenceOutput` | Task-specific tensor operations |
| `InferenceModelProvider` | `getModel(String name)` → `OrtSession` | Model loading and caching |

`InferenceInput` is a sealed hierarchy: `TextInput` (string-based
tasks) and `TensorInput` (raw tensor operations). Five typed task
adapters: NLI, Classification, Regression, SparseEmbedding (SPLADE),
CrossEncoderReranking.

`BGE-M3` produces dense + sparse + ColBERT vectors from a single
ONNX model run. The embedder implements both `EmbeddingModel`
(LangChain4j dense) and `SparseEmbeddingProvider` (CaseHub SPLADE)
interfaces, avoiding redundant model invocations.

### RAG SPIs

| Interface | Methods | Governs |
|-----------|---------|---------|
| `ContentStore` | `ingest(Document doc)`, `search(Query query)` | Corpus storage and retrieval |
| `FusionStrategy` | `fuse(List<ScoredResult> legs)` → `List<ScoredResult>` | Multi-leg score combination |
| `QueryExpander` | `expand(String query)` → `List<String>` | Query augmentation |
| `QualityGate` | `grade(ScoredResult result)` → `boolean` | Corrective RAG chunk filtering |
| `RetrievalTracker` | `track(Query, List<ScoredResult>, RetrievalContext)` | Feedback and analytics |

Three fusion strategies share the `FusionStrategy` enum with CBR:

| Strategy | Algorithm | Best for |
|----------|-----------|----------|
| `RRF` | Reciprocal Rank Fusion | Robust default, rank-based |
| `DBSF` | Distribution-Based Score Fusion | Score-aware, handles different scales |
| `CONVEX` | Convex Combination | Weighted blending with per-query multipliers |

Query expansion strategies: HyDE (hypothetical document embedding),
step-back (abstract the query), multi-query (generate variations).
All implement `QueryExpander` and compose in pipeline.

### CBR SPIs

| Interface | Methods | Governs |
|-----------|---------|---------|
| `CaseStore` | `store(Case c)`, `retrieve(Features query, RetrievalScope scope)` | Case persistence and retrieval |
| `FeatureSimilarity` | `similarity(FeatureValue a, FeatureValue b)` → `double` | Per-field similarity computation |
| `CbrPlanAdapter` | `adapt(Plan retrieved, Features newContext)` → `Plan` | Plan transformation for new cases |
| `CbrPlanEnsembleAnalyzer` | `analyze(List<AdaptedPlan> plans)` → `Plan` | Multi-plan consensus synthesis |
| `AgentTrustProvider` | `trustScore(AgentRef agent)` → `double` | Trust modulation of similarity scores |
| `OutcomeEvaluator` | `evaluate(Case c, Outcome o)` → `ConfidenceAdjustment` | Outcome feedback loop |

CDI decorator chain (8 decorators, priority 90 → 45):

| Priority | Decorator | Effect |
|----------|-----------|--------|
| 90 | Trend enrichment | Add trend features from recent case history |
| 85 | Scope decay | Distance-based decay for hierarchical scoping |
| 80 | Temporal decay | Age-based decay, configurable per domain |
| 65 | Outcome weighting | EMA confidence from execution results |
| 60 | Trust weighting | Modulate by source agent trust via `AgentTrustProvider` |
| 55 | Trajectory weighting | Trust trajectory (improving/declining) signal |
| 50 | Tracking | Record retrieval for analytics |
| 45 | Erasure notification | GDPR erasure event propagation |

### Agent Memory SPIs

| Interface | Methods | Governs |
|-----------|---------|---------|
| `MemoryStore` | `store(Memory m)`, `query(MemoryQuery q)` | Persistence and retrieval |
| `MemoryEmitter` | `emit(Memory m)` | Fire-and-forget emission with error isolation |
| `RetentionPolicy` | `shouldRetain(Memory m)` → `boolean` | Confidence-based purge scheduling |
| `Subject` | `subjectId()`, `subjectType()` | Cross-store entity references |

Seven backend implementations, each with contract test suite:

| Backend | Module | Feature |
|---------|--------|---------|
| In-memory | `memory-inmem` | Testing, lightweight deployments |
| JPA/PostgreSQL | `memory-jpa` | Full-text search via `tsvector` |
| SQLite | `memory-sqlite` | FTS5 for embedded deployments |
| Mem0 | `memory-mem0` | Vector-based memory |
| Graphiti | `memory-graphiti` | Temporal knowledge graph |
| Qdrant | `memory-qdrant` | Vector similarity |
| Spring JPA | `memory-spring-jpa` | Spring Boot deployments |

Ordering modes: chronological, relevance (embedding similarity),
salience (recency × confidence scoring).

### Knowledge Graph SPIs

| Interface | Methods | Governs |
|-----------|---------|---------|
| `Thing` | `id()`, `type()`, `properties()`, `traits()`, `is(String type)`, `as(Class<T> trait)` | Universal entity base |
| `MindMapStore` | `put(MindMapNode)`, `query(MindMapQuery)`, `traverse(...)` | Graph persistence |
| `TypeRegistry` | `registerType(...)`, `hierarchy(String type)` | Dynamic type system |
| `DerivedEdgeRule` | `evaluate(MindMapNode source)` → `List<Edge>` | Automatic relationship inference |
| `ConsolidationPipeline` | 5-phase: extract → schedule → merge → summarise → track | Knowledge maintenance |

`as()` creates a JDK Proxy mapping interface method names to
property lookups — zero-boilerplate typed access. Types are dynamic
strings stored in graph nodes, not a fixed enum. `TypeRegistry`
stores the hierarchy as graph data — type operations ARE graph
traversal.

---

## Data Model

### CBR Feature Type System

7 typed feature value types with 9 field types:

| Value type | Java type | Field types |
|------------|-----------|-------------|
| `StringVal` | `String` | Categorical, Ordinal, FreeText |
| `NumericVal` | `double` | Continuous, Discrete |
| `BooleanVal` | `boolean` | Boolean |
| `DateTimeVal` | `Instant` | DateTime |
| `StructVal` | `Map<String, FeatureValue>` | (nested) |
| `StringListVal` | `List<String>` | DiscreteSequence |
| `StructListVal` | `List<StructVal>` | TimeSeries |

Similarity algorithms per field type:

| Field type | Algorithm | Notes |
|------------|-----------|-------|
| Categorical | Exact match / taxonomy distance | Configurable taxonomy |
| Ordinal | Normalised rank distance | |
| Continuous | Gaussian / range-normalised | |
| FreeText | Embedding cosine similarity | Via RAG embeddings |
| DateTime | Temporal distance with decay | |
| TimeSeries | Dynamic Time Warping (DTW) | O(n) LB_Keogh pruning |
| DiscreteSequence | Edit distance (Levenshtein) | Plan steps, action chains |

### Knowledge Graph Node Model

`MindMapNode extends Thing` adds cognitive fields:

| Field | Type | Purpose |
|-------|------|---------|
| `confidence` | `Confidence` (value + origin + decay) | Belief strength with temporal decay |
| `emotions` | `PADVector` (pleasure, arousal, dominance) | Affective association |
| `temporalValidity` | `TemporalMark` (start, end, granularity) | Time-bounded knowledge |
| `provenance` | `ProvenanceChain` | Source attribution chain |
| `consolidationState` | enum | Tracks pipeline phase |

Built-in trait interfaces:

| Trait | Methods | Use |
|-------|---------|-----|
| `Personable` | `name()`, `role()`, `organisation()` | People and agents |
| `Projectlike` | `status()`, `deadline()`, `members()` | Projects and initiatives |
| `Organisational` | `parent()`, `children()`, `hierarchy()` | Org structure |
| `Eventlike` | `when()`, `where()`, `participants()` | Events and meetings |

### CBR Case Lifecycle

```
ACTIVE ←→ SUPERSEDED (with reason + audit trail)
   │           │
   └── REINSTATED (from superseded, with audit)
```

Supersession supports domain-specific reasoning: a newer, more
relevant case supersedes an older one, but the older case remains
available for retrieval if the supersession reason no longer applies.

---

## Runtime Behaviour

### RAG Retrieval Pipeline

```
Query
  │
  ├── QueryExpander (HyDE / step-back / multi-query)
  │     → expanded queries
  │
  ├── 3-leg parallel retrieval:
  │     ├── Dense embedding → Qdrant ANN search
  │     ├── SPLADE sparse → Qdrant sparse index
  │     └── BM25 keyword → Qdrant payload index
  │
  ├── FusionStrategy.fuse(3 result lists)
  │
  ├── CrossEncoderReranker.rerank(fused results)
  │
  ├── QualityGate.grade(each result)
  │     → reject low-quality chunks (corrective RAG)
  │
  ├── Matryoshka dimension reduction (optional)
  │
  └── RetrievalTracker.track(query, results, context)
```

Pre-ingestion dedup: cosine similarity check before indexing prevents
corpus bloat. Multi-corpus retrieval via `CaseContextRetriever`
provides per-corpus error isolation — a failing corpus does not block
retrieval from healthy ones.

### CBR Learning Loop

```
Execute task → Record outcome
                    │
                    ▼
            OutcomeEvaluator.evaluate()
                    │
                    ▼
            EMA confidence adjustment
                    │
                    ▼
            CaseStore.update(case, newConfidence)
                    │
   ┌────────────────┤
   ▼                ▼
Routing           Planning
(experience       (CbrPlanAdapter
 signal in         transforms
 compositor)       retrieved plan)
   │                │
   ▼                ▼
Next similar task retrieval
   │
   ▼
Trust-weighted similarity scoring
(AgentTrustProvider → ledger EigenTrust)
```

`AllInDomain` scope fans out across all Qdrant collections matching
a domain prefix for cross-domain retrieval. Domain-specific CBR
guides (AML, Clinical, DevTown, IoT, Life, Engine) provide tailored
feature schemas.

### Knowledge Consolidation Pipeline

Five phases run as background tasks:

| Phase | Operation | Trigger |
|-------|-----------|---------|
| 1. Extract | Pull knowledge from conversation transcripts | Post-conversation |
| 2. Schedule | Queue extracted entries for consolidation | Immediate |
| 3. Merge | Detect and merge duplicate/overlapping nodes | Scheduled |
| 4. Summarise | Generate community summaries from clusters | Post-merge |
| 5. Track | Update access-frequency for curiosity refresh | On query |

The pipeline feeds the cognitive architecture's curiosity drive —
knowledge gaps surface as exploration targets.

---

## Extension Points

| Extension | Mechanism | Effect |
|-----------|-----------|--------|
| Custom inference task | Implement `InferenceTask` with tensor adapter | Available via `InferenceEngine.infer()` |
| Custom fusion strategy | Implement `FusionStrategy` | Available in both RAG and CBR pipelines |
| Custom query expander | Implement `QueryExpander` CDI bean | Composes in RAG expansion pipeline |
| Custom quality gate | Implement `QualityGate` CDI bean | Applied after fusion in RAG |
| Custom feature similarity | Implement `FeatureSimilarity` for a field type | Available in CBR retrieval |
| Custom memory backend | Implement `MemoryStore`, validate with contract tests | Available alongside 7 built-in backends |
| Custom graph trait | Define Java interface | Available via `Thing.as(Trait.class)` proxy |
| Custom derived edge rule | Implement `DerivedEdgeRule` in YAML | Automatic relationship inference |
| Custom CBR decorator | CDI decorator with `@Priority` | Inserts into 8-decorator chain |

---

## Module Map

### On-Device Inference (7 modules)

| Module | Provides | Key types |
|--------|----------|-----------|
| `inference-api` | SPI contracts | `InferenceEngine`, `InferenceInput` (sealed), `InferenceTask` |
| `inference-runtime` | ONNX execution | `OrtSession` management, model caching |
| `inference-tasks` | Typed adapters | NLI, Classification, Regression adapters |
| `inference-splade` | Sparse embeddings | SPLADE token-level sparse vectors |
| `inference-bge-m3` | Multi-modal embedder | Dense + sparse + ColBERT from one model |
| `inference-inmem` | Test stubs | In-memory inference for test isolation |
| `inference-quarkus` | CDI wiring | `@InferenceModel` qualifier, Dev Services |

### Corpus & Retrieval / RAG (11 modules)

| Module | Provides | Key types |
|--------|----------|-----------|
| `rag-api` | SPI contracts | `ContentStore`, `FusionStrategy`, `QueryExpander`, `QualityGate` |
| `rag-core` | Pipeline runtime | 3-leg retrieval, fusion, reranking |
| `rag-tika` | Document parsing | Apache Tika integration for binary formats |
| `rag-crossencoder` | Reranking | Cross-encoder via inference engine |
| `rag-expansion` | Query augmentation | HyDE, step-back, multi-query |
| `rag-scoring` | Score analytics | ColBERT relevance, calibration |
| `rag-query-augmentation` | Advanced expansion | Multi-strategy composition |
| `rag-tracking` | Feedback | RetrievalAnalyzer, MinHash LSH clustering |
| `rag-cache` | Result caching | TTL-based retrieval cache |
| `rag-spring` | Spring integration | Spring Boot auto-configuration |
| `rag-main` | Quarkus assembly | Full pipeline wiring |

### Case-Based Reasoning / CBR (7 + shared)

| Module | Provides | Key types |
|--------|----------|-----------|
| `cbr-api` | SPI contracts | `CaseStore`, `FeatureSimilarity`, `CbrPlanAdapter` |
| `cbr-core` | Retrieval engine | 8-decorator chain, DTW, edit distance |
| `cbr-jpa` | JPA backend | PostgreSQL case storage |
| `cbr-inmem` | In-memory backend | Testing |
| `cbr-qdrant` | Qdrant backend | Vector similarity with typed features |
| `cbr-tracking` | Analytics | SQLite-backed adaptation and ensemble tracking |
| `cbr-spring-jpa` | Spring backend | Spring JPA case storage |
| `memory-api` | Shared types | `FeatureValue` hierarchy, `FusionStrategy` enum |

### Agent Memory (17 modules)

| Module | Provides | Key types |
|--------|----------|-----------|
| `memory-api` | SPI contracts | `MemoryStore`, `MemoryEmitter`, `RetentionPolicy`, `Subject` |
| `memory-core` | Framework-neutral runtime | Query execution, salience scoring |
| `memory-inmem` | In-memory backend | Testing |
| `memory-jpa` | PostgreSQL backend | `tsvector` FTS |
| `memory-sqlite` | SQLite backend | FTS5 |
| `memory-mem0` | Mem0 backend | Vector-based |
| `memory-graphiti` | Graphiti backend | Temporal knowledge graph |
| `memory-qdrant` | Qdrant backend | Vector similarity |
| `memory-spring` | Spring auto-config | Spring Boot wiring |
| `memory-spring-jpa` | Spring JPA backend | Spring deployments |

### Knowledge Graph (8 modules)

| Module | Provides | Key types |
|--------|----------|-----------|
| `mindmap-api` | SPI contracts | `Thing`, `MindMapStore`, `TypeRegistry` |
| `mindmap-core` | Graph runtime | Proxy generation, derived edges, consolidation |
| `mindmap-inmem` | In-memory backend | Testing |
| `mindmap-intelligence` | Cognitive extensions | `MindMapNode`, confidence, PAD, consolidation pipeline |
| `mindmap-sqlite` | SQLite backend | Embedded deployments |
| `mindmap-spring` | Spring auto-config | Spring Boot wiring |
| `mindmap-testing` | Contract test suite | 72-test verification |
| `mindmap-main` | Quarkus assembly | Full pipeline wiring |
