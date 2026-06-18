# casehub-neural-text — Platform Deep Dive

**GitHub:** [casehubio/neural-text](https://github.com/casehubio/neural-text) (local: `~/claude/casehub/neural-text`)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Two related capabilities in one repo:

**Neural Text Inference** — a standalone, general-purpose ONNX inference layer for JVM projects. Zero casehub domain dependencies in `inference-api`, `inference-runtime`, `inference-tasks`, and `inference-splade`. Shared with Hortora. Fills the gap LangChain4j leaves: NLI, classification, regression, SPLADE sparse embeddings, cross-encoder reranking.

**RAG Integration** — casehub-specific LangChain4j RAG pipeline wiring. Tenancy-isolated Qdrant corpus storage, hybrid dense+sparse search via RRF fusion. Exposes `CorpusStore` and `CaseRetriever` SPIs for use by engine case steps and the typed fact space.

---

## Module Structure

| Module | artifactId | Type | Purpose |
|--------|-----------|------|---------|
| `inference-api/` | `casehub-inference-api` | Pure Java, zero deps | `InferenceModel` SPI, `InferenceInput`, `InferenceOutput`, `InferenceException` |
| `inference-runtime/` | `casehub-inference-runtime` | JVM library | ONNX Runtime JVM + HuggingFace Tokenizers JNI; `OnnxInferenceModel`, `ModelConfig`, `ModelLoadException`; session management, tokenization |
| `inference-tasks/` | `casehub-inference-tasks` | JVM library | `NliClassifier`, `TextClassifier`, `ScalarRegressor`, `CrossEncoderReranker` |
| `inference-splade/` | `casehub-inference-splade` | JVM library | SPLADE sparse embeddings (`Map<Integer, Float>`); log-saturation + threshold |
| `inference-inmem/` | `casehub-inference-inmem` | Test library | Deterministic `InferenceModel` stubs; no JNI; safe in all test contexts |
| `inference-quarkus/` | `casehub-inference-quarkus` | Quarkus extension | CDI wiring, `@InferenceModel` qualifier, Dev Services, `@QuarkusTest` support |
| `rag-api/` | `casehub-rag-api` | Pure Java, Mutiny provided | `CorpusStore` SPI, `CaseRetriever` SPI (blocking); `ReactiveCorpusStore`, `ReactiveCaseRetriever` (Mutiny `Uni<T>` variants — Mutiny `provided` scope per module-tier-structure protocol); `RetrievedChunk`, `CorpusRef`; `MetadataExtractor` SPI — extracts body + metadata from document content; `CursorStore` SPI — pluggable cursor persistence |
| `rag/` | `casehub-rag` | Quarkus module | LangChain4j pipeline, Qdrant, hybrid RRF fusion, tenancy isolation; `BlockingToReactiveRagBridge @DefaultBean` wraps blocking adapters as reactive; `CorpusIngestionService` — `@Scheduled` polling bridge (`ChangeSource` → `CorpusReader` → `MetadataExtractor` → chunk → `EmbeddingIngestor`); `CorpusBindingProducer` — config-driven binding creation (design debt: extract to `corpus-quarkus/` when second consumer appears); `YamlFrontmatterExtractor @DefaultBean` `MetadataExtractor`; `FileCursorStore @DefaultBean` file-based cursor persistence. Dependency: `langchain4j` full artifact (replaces `langchain4j-core`) for `DocumentSplitters`; `quarkus-scheduler` for `@Scheduled` polling. |
| `rag-testing/` | `casehub-rag-testing` | Test library | In-memory `CorpusStore` + `CaseRetriever` + reactive stubs for `@QuarkusTest`; `InMemoryCursorStore @Alternative @Priority(1)` test stub |
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

`SparseEmbedder.embed(String text)` → `Map<Integer, Float>` — sparse term weights after log-saturation (`log(1 + relu(weight))`) and threshold filtering. Output is suitable for direct Qdrant named vector space upsert. Forms the sparse leg of hybrid search in `casehub-rag`.

### CorpusStore / CaseRetriever (rag-api)

`CorpusStore` — ingest, delete, and list documents per tenant corpus. Tenancy-scoped; `CorpusRef` carries tenant ID + corpus name.

`CaseRetriever` — retrieval entry point for case steps and the fact space. `retrieve(query, CorpusRef)` → `List<RetrievedChunk>`. Hybrid search: LangChain4j `OnnxEmbeddingModel` (dense) + `SparseEmbedder` (sparse) fused via RRF. Reranked by `CrossEncoderReranker` in precision mode. Reactive variant: `ReactiveCaseRetriever` — `retrieve()` → `Uni<List<RetrievedChunk>>`; `BlockingToReactiveRagBridge @DefaultBean` in `rag/` wraps blocking impl.

### Corpus Ingestion Bridge (neural-text#19)

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

Also includes an `assertTenant` fix extending protocol PP-20260529-57cc3b to RAG adapters (neural-text#21).

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

---

## Shared with Hortora

`inference-api`, `inference-runtime`, `inference-tasks`, `inference-splade`, `inference-inmem` have zero casehub/Quarkus/LangChain4j dependencies. Hortora depends on these directly and wires them into their own stack.

`rag-api`, `rag`, and `rag-testing` are now also consumed by Hortora (neural-text#35): Hortora's garden retrieval engine replaces its duplicated Qdrant/ingestion code with these modules. Tenancy enforcement is optional — active when `CurrentPrincipal` is on the classpath, no-ops when absent via `TenantGuard` (neural-text#36). Consumers without `casehub-platform-api` get `TenantGuard.noOp()` — retrieval proceeds without tenant scoping.

ArchUnit enforced from day one: zero-domain-dep constraint on all `inference-*` modules.

---

## Native Image Gate

Two JNI layers must work in Quarkus native image on macOS ARM before `inference-quarkus` is used:
1. ONNX Runtime (`com.microsoft.onnxruntime`)
2. HuggingFace Tokenizers JNI

The prototype is the first deliverable. Until confirmed, all `inference-*` modules operate JVM-only. `casehub-rag` does not require native image.

---

## Depends On

| Repo / Library | Module | How |
|---|---|---|
| `casehub-platform-api` | `rag` | `CurrentPrincipal`, `TenancyConstants` — tenant isolation |
| LangChain4j (full artifact) | `rag` | RAG pipeline, `OnnxEmbeddingModel`, Qdrant `EmbeddingStore`, `DocumentSplitters` |
| `io.qdrant:client` | `rag` | Qdrant REST client for direct named-vector-space queries (sparse leg of hybrid RRF search — until langchain4j#4994 ships) |
| `quarkus-scheduler` | `rag` | `@Scheduled` polling for `CorpusIngestionService` |
| `casehub-corpus` | `rag` | `CorpusBindingProducer` only (design debt — extract when second consumer appears) |
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

C3–C7 complete (neural-text#3, neural-text#7). All inference and RAG modules shipped:

| Chapter | What shipped |
|---------|-------------|
| C3 — SPI Foundation | `InferenceModel` SPI, `InferenceInput`, `InferenceOutput`, `InferenceException`; `OnnxInferenceModel`, `ModelConfig`, `ModelLoadException`; `InMemoryInferenceModel` stubs; C2 bridge classes deleted |
| C4 — Task Adapters | `NliClassifier`, `TextClassifier`, `ScalarRegressor`, `CrossEncoderReranker` in `inference-tasks` |
| C5 — Quarkus CDI wiring | `@InferenceModel` qualifier, `InferenceModelProducer`, Dev Services, `@QuarkusTest` support in `inference-quarkus` |
| C6 — SPLADE | `SparseEmbedder` in `inference-splade` — log-saturation output for Qdrant named vector spaces |
| C7 — RAG Pipeline | `CorpusStore` SPI, `CaseRetriever` SPI, `QdrantCorpusStore`, `QdrantCaseRetriever` in `rag`; `rag-testing` in-memory stubs |

Native image prototype (Epic 2) gates `inference-quarkus` native deployment and Hortora's native binary goal — currently JVM-only.

Design specs:
- `docs/specs/2026-06-03-ai-fusion-hybrid-fact-space.md` (typed fact space + RAG context)
- `docs/specs/2026-06-03-standalone-rag-retrieval-brief.md` (inference module design)
- `Hortora/spec: docs/superpowers/specs/2026-06-03-onnx-inference-module-design.md` (authoritative inference design)

---

## Design Documents

- [casehubio/parent#158](https://github.com/casehubio/parent/issues/158) — casehubio/neural-text tracking issue
- [casehubio/parent#164](https://github.com/casehubio/parent/issues/164) — casehub-rag tracking issue
- [Hortora/spec#15](https://github.com/Hortora/spec/issues/15) — Hortora alignment
