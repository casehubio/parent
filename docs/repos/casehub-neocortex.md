# casehub-neocortex — Platform Deep Dive

**GitHub:** [casehubio/neocortex](https://github.com/casehubio/neocortex) (local: `~/claude/casehub/neocortex`)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Three related capabilities in one repo:

**Neural Text Inference** — a standalone, general-purpose ONNX inference layer for JVM projects. Zero casehub domain dependencies in `inference-api`, `inference-runtime`, `inference-tasks`, and `inference-splade`. Shared with Hortora. Fills the gap LangChain4j leaves: NLI, classification, regression, SPLADE sparse embeddings, cross-encoder reranking.

**RAG Integration** — casehub-specific LangChain4j RAG pipeline wiring. Tenancy-isolated Qdrant corpus storage, hybrid dense+sparse search via RRF fusion. Exposes `EmbeddingIngestor` and `CaseRetriever` SPIs for use by engine case steps and the typed fact space.

**Agent Memory** — queryable, permission-aware, persistent agent memory. `CaseMemoryStore` SPI with multiple backends (in-memory, JPA/PostgreSQL, SQLite, Mem0, Graphiti, Qdrant). Migrated from `casehub-platform` in neocortex#56 — memory is a cognitive capability that belongs alongside inference and RAG, not in the foundational SPI layer.

---

## Module Structure

| Module | artifactId | Type | Purpose |
|--------|-----------|------|---------|
| `inference-api/` | `casehub-neocortex-inference-api` | Pure Java, zero deps | `InferenceModel` SPI, `InferenceInput`, `InferenceOutput`, `InferenceException` |
| `inference-runtime/` | `casehub-neocortex-inference-runtime` | JVM library | ONNX Runtime JVM + HuggingFace Tokenizers JNI; `OnnxInferenceModel`, `ModelConfig`, `ModelLoadException`; session management, tokenization |
| `inference-tasks/` | `casehub-neocortex-inference-tasks` | JVM library | `NliClassifier`, `TextClassifier`, `ScalarRegressor`, `CrossEncoderReranker` |
| `inference-splade/` | `casehub-neocortex-inference-splade` | JVM library | SPLADE sparse embeddings (`Map<Integer, Float>`); log-saturation + threshold |
| `inference-inmem/` | `casehub-neocortex-inference-inmem` | Test library | Deterministic `InferenceModel` stubs; no JNI; safe in all test contexts |
| `inference-quarkus/` | `casehub-neocortex-inference-quarkus` | Quarkus extension | CDI wiring, `@InferenceModel` qualifier, Dev Services, `@QuarkusTest` support |
| `rag-api/` | `casehub-neocortex-rag-api` | Pure Java, Mutiny provided | `EmbeddingIngestor` SPI, `CaseRetriever` SPI (blocking); `ReactiveEmbeddingIngestor`, `ReactiveCaseRetriever` (Mutiny `Uni<T>` variants — Mutiny `provided` scope per module-tier-structure protocol); `RetrievedChunk`, `CorpusRef`; `MetadataExtractor` SPI — extracts body + metadata from document content; `CursorStore` SPI — pluggable cursor persistence |
| `rag/` | `casehub-neocortex-rag` | Quarkus module | LangChain4j pipeline, Qdrant, hybrid RRF fusion, tenancy isolation; `BlockingToReactiveRagBridge @DefaultBean` wraps blocking adapters as reactive; `CorpusIngestionService` — `@Scheduled` polling bridge (`ChangeSource` → `CorpusReader` → `MetadataExtractor` → chunk → `EmbeddingIngestor`); `CorpusBindingProducer` — config-driven binding creation (design debt: extract to `corpus-quarkus/` when second consumer appears); `YamlFrontmatterExtractor @DefaultBean` `MetadataExtractor`; `FileCursorStore @DefaultBean` file-based cursor persistence. Dependency: `langchain4j` full artifact (replaces `langchain4j-core`) for `DocumentSplitters`; `quarkus-scheduler` for `@Scheduled` polling; `MatryoshkaEmbeddingModel` — truncating `EmbeddingModel` decorator (config-driven via `casehub.rag.matryoshka.dimension`); `DenseQuantization` enum — binary/scalar quantization config for Qdrant dense vector params; `RagBeanProducer` — CDI producer that conditionally wraps `EmbeddingModel` in `MatryoshkaEmbeddingModel` and passes quantization config to both `QdrantEmbeddingIngestor` (collection creation: type + alwaysRam) and `HybridCaseRetriever` (search-time: type + oversampling); `ReactiveRagBeanProducer` — same conditional Matryoshka wrapping and quantization wiring for reactive implementations (`ReactiveQdrantEmbeddingIngestor`, `ReactiveHybridCaseRetriever`), gated by `casehub.rag.reactive.enabled=true`. |
| `rag-testing/` | `casehub-neocortex-rag-testing` | Test library | In-memory `EmbeddingIngestor` + `CaseRetriever` + reactive stubs for `@QuarkusTest`; `InMemoryCursorStore @Alternative @Priority(1)` test stub |
| `rag-tika/` | `casehub-neocortex-rag-tika` | JVM library | Apache Tika document parser — `TikaDocumentParser` extracts text + metadata from binary documents (PDF, DOCX, etc.) for RAG ingestion |
| `rag-crag/` | `casehub-neocortex-rag-crag` | JVM library | Corrective RAG — `CorrectiveCaseRetriever` + `ReactiveCorrectiveCaseRetriever` wrapping `CaseRetriever` with `CrossEncoderRelevanceEvaluator` relevance gating; irrelevant chunks filtered before LLM context injection. `CragBeanProducer` CDI wiring; `CragConfig` for threshold tuning |
| `rag-expansion/` | `casehub-neocortex-rag-expansion` | JVM library | Query expansion — `QueryExpandingCaseRetriever` + `ReactiveQueryExpandingCaseRetriever` wrapping `CaseRetriever` with multi-query retrieval. Expander implementations: `LlmQueryExpander` (LLM-generated reformulations), `TemplateQueryExpander` (pattern-based), `StepBackQueryExpander` (abstraction-based). `ExpansionConfig` for tuning |
| `corpus-api/` | `casehub-neocortex-corpus-api` | Pure Java, Mutiny provided | Corpus storage and change-tracking SPIs — `CorpusStore`, `CorpusReader`, `ChangeSource` (polling), `WatchableChangeSource` (push), `ChangeListener`; reactive mirrors: `ReactiveCorpusStore`, `ReactiveCorpusReader`, `ReactiveChangeSource`; types: `ChangeSet`, `ChangedEntry`, `ChangeType`, `VersionInfo`; `CorpusIntegrity` SPI + `IntegrityReport`, `IntegrityIssue`, `Severity` for corpus health checks |
| `corpus/` | `casehub-neocortex-corpus` | JVM library | Corpus storage implementations — `ZipCorpusStore` (append-only zip archive with rollover + `MasterIndex` + `ChainManifest`), `FlatCorpusStore` (directory-based), `CompositeCorpusStore` (multi-backend); `ZipChangeSource`, `FlatChangeSource`, `CompositeChangeSource` change tracking; `Compactor` + `CompactionMode` for archive maintenance; `CorpusMigrator` for format upgrades; `ZipIntegrityChecker` for corpus health; blocking-to-reactive bridges |
| `memory-api/` | `casehub-neocortex-memory-api` | Pure Java | `CaseMemoryStore`, `ReactiveCaseMemoryStore`, `GraphCaseMemoryStore` SPIs; value types: `Memory`, `MemoryInput`, `MemoryQuery`, `EraseRequest`, `MemoryDomain`, `MemoryCapability`; `MemoryPermissions` utility; `CbrCaseMemoryStore` in `cbr/` subpackage. Package: `io.casehub.neocortex.memory`. Migrated from `casehub-platform-api` (neocortex#56). |
| `memory/` | `casehub-neocortex-memory` | CDI module | `NoOpCaseMemoryStore @DefaultBean`, `BlockingToReactiveBridge @DefaultBean`, `CaseEnrichmentDecorator`; `NoOpCbrCaseMemoryStore @DefaultBean` in `cbr/runtime/` |
| `memory-inmem/` | `casehub-neocortex-memory-inmem` | Backend | @Alternative @Priority(1) volatile ConcurrentHashMap — test-scope for isolation; compile for ephemeral |
| `memory-jpa/` | `casehub-neocortex-memory-jpa` | Backend | @ApplicationScoped JPA/PostgreSQL + Flyway + FTS via websearch_to_tsquery |
| `memory-sqlite/` | `casehub-neocortex-memory-sqlite` | Backend | @Alternative @Priority(1) SQLite + HikariCP WAL + FTS5 |
| `memory-mem0/` | `casehub-neocortex-memory-mem0` | Backend | @Alternative @Priority(1) Mem0 REST adapter — vector embeddings + semantic search |
| `memory-graphiti/` | `casehub-neocortex-memory-graphiti` | Backend | @Alternative @Priority(2) Graphiti REST GraphCaseMemoryStore — temporal knowledge graph |
| `memory-qdrant/` | `casehub-neocortex-memory-qdrant` | Backend | Qdrant vector store backend |
| `memory-cbr-inmem/` | `casehub-neocortex-memory-cbr-inmem` | Backend | In-memory CBR case memory store |
| `memory-testing/` | `casehub-neocortex-memory-testing` | Test library | Test stubs for memory SPIs |
| `examples/example-text-analysis` | — | Standalone Java demos | NLI, zero-shot classification, scoring, reranking, SPLADE demos (no Quarkus) |
| `examples/example-rag-pipeline` | — | Quarkus demos | Corpus ingestion, hybrid search with RRF fusion, cross-encoder reranking. Maven profiles: `-Pexamples-smoke` (in-memory stubs), `-Pexamples` (real ONNX models + Testcontainers Qdrant) |

---

## Key Abstractions

### InferenceModel / Task Adapters

`InferenceModel` SPI — runs any ONNX model: `run(InferenceInput)` / `runBatch(List<InferenceInput>)`. Callers work through typed task adapters in `inference-tasks`, never raw tensors.

| Adapter | Model type | Use case |
|---------|-----------|----------|
| `NliClassifier` | NLI | Hallucination detection — scores LLM output faithfulness against facts |
| `TextClassifier` | Classification | Action risk classification in casehub-openclaw |
| `ScalarRegressor` | Regression | Epistemic domain confidence estimation in casehub-eidos |
| `CrossEncoderReranker` | Cross-encoder | Precision-mode reranking — top-N from top-K candidates |

### SparseEmbedder (inference-splade)

`SparseEmbedder.embed(String text)` → `Map<Integer, Float>` — sparse term weights after log-saturation (`log(1 + relu(weight))`) and threshold filtering. Output is suitable for direct Qdrant named vector space upsert. Forms the sparse leg of hybrid search in `casehub-neocortex-rag`.

### EmbeddingIngestor / CaseRetriever (rag-api)

`EmbeddingIngestor` — ingest pre-chunked text into vector store (embedding + storage), delete and list by source document. Tenancy-scoped; `CorpusRef` carries tenant ID + corpus name.

`CaseRetriever` — retrieval entry point for case steps and the fact space. `retrieve(query, CorpusRef)` → `List<RetrievedChunk>`. Hybrid search: LangChain4j `OnnxEmbeddingModel` (dense) + `SparseEmbedder` (sparse) fused via RRF. Reranked by `CrossEncoderReranker` in precision mode. Reactive variant: `ReactiveCaseRetriever` — `retrieve()` → `Uni<List<RetrievedChunk>>`; `BlockingToReactiveRagBridge @DefaultBean` in `rag/` wraps blocking impl.

`HybridCaseRetriever` (and `ReactiveHybridCaseRetriever`) accept `DenseQuantization` type and optional oversampling. When quantization is active (`DenseQuantization != NONE`) and `casehub.rag.quantization.oversampling` is set, the dense prefetch leg applies `QuantizationSearchParams` with the configured oversampling factor + `rescore=true`. Compensates for quantization precision loss by fetching more candidates from the quantized index before rescoring against full-precision vectors. Sparse prefetch is unaffected — sparse vectors are not quantized. See [`casehub-neocortex/ARC42STORIES.MD` §6](https://github.com/casehubio/neocortex/blob/main/ARC42STORIES.MD#6-runtime-view) for the oversampling design rationale.

### MatryoshkaEmbeddingModel (rag)

`MatryoshkaEmbeddingModel` — truncating `EmbeddingModel` decorator in `rag/`. Takes a delegate model and `targetDimension`, truncates the output vector to the first N dimensions and L2-renormalizes. Config-driven: active when `casehub.rag.matryoshka.dimension` is set. Reports `modelName()` as `delegate/matryoshka-N`. Validates that target dimension is positive and does not exceed delegate dimension.

The decorator pattern is architecturally significant: `dimension()` returns the truncated size, which flows transparently to `ensureCollection()` — collection vector dimensions are automatically correct without separate dimension tracking. See [`casehub-neocortex/ARC42STORIES.MD` §4](https://github.com/casehubio/neocortex/blob/main/ARC42STORIES.MD#4-solution-strategy) for the dual-vector tiered search alternative that was evaluated and rejected.

### DenseQuantization (rag)

`DenseQuantization` — enum in `rag/` with values `NONE`, `BINARY`, `SCALAR`. Configures Qdrant quantization on the **dense vector params** at collection creation time — applied to `denseParamsBuilder` specifically, not to the entire collection (sparse vectors are not quantized). `BINARY` applies `BinaryQuantization`; `SCALAR` applies `ScalarQuantization` with `Int8` type. Both respect `casehub.rag.quantization.always-ram` (default `true`). Config: `casehub.rag.quantization.type` (default `NONE`).

Named `DenseQuantization` rather than `QuantizationType` because the Qdrant client already defines `io.qdrant.client.grpc.Collections.QuantizationType` — both enums appear in `ensureCollection()` / `buildCreateRequest()` and sharing the name would create ambiguous unqualified usage (see [`casehub-neocortex/ARC42STORIES.MD` §8](https://github.com/casehubio/neocortex/blob/main/ARC42STORIES.MD#8-crosscutting-concepts)).

### Corpus Ingestion Bridge (neocortex#19)

Config-driven polling bridge that populates a RAG corpus from external sources. Ships in `rag/`.

| Component | Purpose |
|---|---|
| `CorpusIngestionService` | Orchestrator — `@Scheduled` polling with reconciliation mode |
| `CorpusIngestionBinding` | Per-corpus descriptor (name, corpusRef, changeSource, reader, extractor) |
| `CorpusBindingProducer` | Config-driven binding creation (design debt: extract to `corpus-quarkus/` when second consumer appears) |
| `MetadataExtractor` SPI | Extracts body + metadata from document content |
| `CursorStore` SPI | Pluggable cursor persistence for incremental polling |
| `YamlFrontmatterExtractor` | `@DefaultBean` `MetadataExtractor` |
| `FileCursorStore` | `@DefaultBean` file-based cursor persistence |
| `InMemoryCursorStore` | `@Alternative @Priority(1)` test stub in `rag-testing` |

Also includes an `assertTenant` fix extending protocol PP-20260529-57cc3b to RAG adapters (neocortex#21).

---

## Relationship to LangChain4j

This module sits **below** LangChain4j for inference, and **above** LangChain4j for RAG:

| Capability | Where it lives |
|---|---|
| Dense float-vector embeddings | LangChain4j `OnnxEmbeddingModel` |
| RAG pipeline, chunking, vector stores | LangChain4j |
| Sparse embeddings (SPLADE) | `inference-splade` (this module) |
| NLI, classification, regression | `inference-tasks` (this module) |
| Cross-encoder reranking | `inference-tasks` (this module) |
| casehub-specific RAG wiring + tenancy | `rag` / `rag-api` (this module) |
| Matryoshka dimension reduction + L2 renorm | `rag` (this module) — decorator above LangChain4j `EmbeddingModel` |
| Dense vector quantization (binary/scalar) + search-time oversampling | `rag` (this module) — Qdrant collection config + search params |

---

## Shared with Hortora

`inference-api`, `inference-runtime`, `inference-tasks`, `inference-splade`, `inference-inmem` have zero casehub/Quarkus/LangChain4j dependencies. Hortora depends on these directly and wires them into their own stack.

`rag-api`, `rag`, and `rag-testing` are now also consumed by Hortora (neocortex#35): Hortora's garden retrieval engine replaces its duplicated Qdrant/ingestion code with these modules. Tenancy enforcement is optional — active when `CurrentPrincipal` is on the classpath, no-ops when absent via `TenantGuard` (neocortex#36). Consumers without `casehub-platform-api` get `TenantGuard.noOp()` — retrieval proceeds without tenant scoping.

ArchUnit enforced from day one: zero-domain-dep constraint on all `inference-*` modules.

---

## Native Image — JVM Mode by Design

The inference service is long-running — native image's fast startup provides no benefit, and HotSpot's JIT optimisation outperforms AOT for sustained workloads. `inference-*` modules operate in JVM mode.

The C2 native image gate passed (ONNX Runtime JNI + HuggingFace Tokenizers JNI both work in Quarkus native image on macOS ARM). Reachability metadata ships in `inference-quarkus` for downstream consumers that distribute as native binaries.

---

## Depends On

| Repo / Library | Module | How |
|---|---|---|
| `casehub-platform-api` | `rag` | `CurrentPrincipal`, `TenancyConstants` — tenant isolation |
| LangChain4j (full artifact) | `rag` | RAG pipeline, `OnnxEmbeddingModel`, Qdrant `EmbeddingStore`, `DocumentSplitters` |
| `io.qdrant:client` | `rag` | Qdrant REST client for direct named-vector-space queries (sparse leg of hybrid RRF search — until langchain4j#4994 ships) |
| `quarkus-scheduler` | `rag` | `@Scheduled` polling for `CorpusIngestionService` |
| `casehub-neocortex-corpus` | `rag` | `CorpusBindingProducer` only (design debt — extract when second consumer appears) |
| ONNX Runtime JVM | `inference-runtime` | Model session management |
| HuggingFace Tokenizers JNI | `inference-runtime` | Tokenization |

## Depended On By (future)

| Repo | Module | How |
|---|---|---|
| `casehub-eidos` | `runtime` | `ScalarRegressor` for dynamic epistemic confidence |
| `casehub-openclaw` | `casehub` | `TextClassifier` for `ActionRiskClassifier` SPI |
| `casehub-engine` | `runtime` | `NliClassifier` for hallucination detection (#154) |
| `casehub-engine` | `runtime` | `CaseRetriever` for fact space prompt compilation |

---

## Current State

C3–C7 complete (neocortex#3, neocortex#7). All inference and RAG modules shipped:

| Chapter | What shipped |
|---------|-------------|
| C3 — SPI Foundation | `InferenceModel` SPI, `InferenceInput`, `InferenceOutput`, `InferenceException`; `OnnxInferenceModel`, `ModelConfig`, `ModelLoadException`; `InMemoryInferenceModel` stubs; C2 bridge classes deleted |
| C4 — Task Adapters | `NliClassifier`, `TextClassifier`, `ScalarRegressor`, `CrossEncoderReranker` in `inference-tasks` |
| C5 — Quarkus CDI wiring | `@InferenceModel` qualifier, `InferenceModelProducer`, Dev Services, `@QuarkusTest` support in `inference-quarkus` |
| C6 — SPLADE | `SparseEmbedder` in `inference-splade` — log-saturation output for Qdrant named vector spaces |
| C7 — RAG Pipeline | `EmbeddingIngestor` SPI, `CaseRetriever` SPI, `QdrantEmbeddingIngestor`, `HybridCaseRetriever` in `rag`; `rag-testing` in-memory stubs; storage/search optimization (neocortex#31): `MatryoshkaEmbeddingModel` (truncating decorator), `DenseQuantization` (binary/scalar dense vector params config), search-time oversampling on quantized dense prefetch, `RagBeanProducer` / `ReactiveRagBeanProducer` CDI wiring — both blocking and reactive implementations carry all features |

Native image gate passed (C2). Service deploys in JVM mode by design — long-running workloads benefit from HotSpot JIT over AOT. Reachability metadata retained for downstream native consumers.

Design specs:
- `docs/specs/2026-06-03-ai-fusion-hybrid-fact-space.md` (typed fact space + RAG context)
- `docs/specs/2026-06-03-standalone-rag-retrieval-brief.md` (inference module design)
- `Hortora/spec: docs/superpowers/specs/2026-06-03-onnx-inference-module-design.md` (authoritative inference design)

---

## Design Documents

- [casehubio/parent#158](https://github.com/casehubio/parent/issues/158) — casehubio/neocortex tracking issue
- [casehubio/parent#164](https://github.com/casehubio/parent/issues/164) — casehub-neocortex-rag tracking issue
- [Hortora/spec#15](https://github.com/Hortora/spec/issues/15) — Hortora alignment
- [casehubio/neocortex ARC42STORIES.MD](https://github.com/casehubio/neocortex/blob/main/ARC42STORIES.MD) — authoritative architecture record (Matryoshka §4, oversampling §6, dimension consistency §7, naming §8)
