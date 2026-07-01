# neocortex deep-dive sync — Matryoshka + quantization

**Date:** 2026-06-27
**Issue:** [casehubio/parent#315](https://github.com/casehubio/parent/issues/315)
**Source:** [casehubio/neocortex#31](https://github.com/casehubio/neocortex/issues/31)
**ARC42STORIES ref:** `casehub-neocortex/ARC42STORIES.MD` §4 (Matryoshka embeddings), §6 (search-time oversampling), §7 (embedding dimension consistency), §8 (DenseQuantization naming)

---

## Summary

Update `docs/repos/casehub-neocortex.md` to reflect four features shipped in neocortex#31: `MatryoshkaEmbeddingModel`, `DenseQuantization` enum, search-time oversampling on quantized vectors, and CDI producer wiring for both. All features exist in both blocking and reactive implementations. Also fix stale class names from the #17 refactor (CorpusStore → EmbeddingIngestor, QdrantCorpusStore → QdrantEmbeddingIngestor, QdrantCaseRetriever → HybridCaseRetriever) and update the EmbeddingIngestor description to match the interface.

## Approach

Inline additions to the existing document structure (Approach A). No new top-level sections — features are documented where they integrate. Stale class names fixed in every section they appear (Edit 7 is the single authority for all renames).

## Edits

### 1. Key Abstractions — two new ### subsections after EmbeddingIngestor / CaseRetriever, before Corpus Ingestion Bridge

Use `###` subsection headers to match the existing pattern (`### InferenceModel / Task Adapters`, `### SparseEmbedder`, etc.). Body text leads with backticked class name, matching existing entries.

#### ### MatryoshkaEmbeddingModel (rag)

`MatryoshkaEmbeddingModel` — truncating `EmbeddingModel` decorator in `rag/`. Takes a delegate model and `targetDimension`, truncates the output vector to the first N dimensions and L2-renormalizes. Config-driven: active when `casehub.rag.matryoshka.dimension` is set. Reports `modelName()` as `delegate/matryoshka-N`. Validates that target dimension is positive and does not exceed delegate dimension.

The decorator pattern is architecturally significant: `dimension()` returns the truncated size, which flows transparently to `ensureCollection()` — collection vector dimensions are automatically correct without separate dimension tracking. See [`casehub-neocortex/ARC42STORIES.MD` §4](https://github.com/casehubio/neocortex/blob/main/ARC42STORIES.MD#4-solution-strategy) for the dual-vector tiered search alternative that was evaluated and rejected.

#### ### DenseQuantization (rag)

`DenseQuantization` — enum in `rag/` with values `NONE`, `BINARY`, `SCALAR`. Configures Qdrant quantization on the **dense vector params** at collection creation time — applied to `denseParamsBuilder` specifically, not to the entire collection (sparse vectors are not quantized). `BINARY` applies `BinaryQuantization`; `SCALAR` applies `ScalarQuantization` with `Int8` type. Both respect `casehub.rag.quantization.always-ram` (default `true`). Config: `casehub.rag.quantization.type` (default `NONE`).

Named `DenseQuantization` rather than `QuantizationType` because the Qdrant client already defines `io.qdrant.client.grpc.Collections.QuantizationType` — both enums appear in `ensureCollection()` / `buildCreateRequest()` and sharing the name would create ambiguous unqualified usage (see [`casehub-neocortex/ARC42STORIES.MD` §8](https://github.com/casehubio/neocortex/blob/main/ARC42STORIES.MD#8-crosscutting-concepts)).

### 2. CaseRetriever description — update existing paragraph

Update the `CaseRetriever` paragraph to note that `HybridCaseRetriever` (and `ReactiveHybridCaseRetriever`) now accept `DenseQuantization` type and optional oversampling. When quantization is active (`DenseQuantization != NONE`) and `casehub.rag.quantization.oversampling` is set, the dense prefetch leg applies `QuantizationSearchParams` with the configured oversampling factor + `rescore=true`. Compensates for quantization precision loss by fetching more candidates from the quantized index before rescoring against full-precision vectors. Sparse prefetch is unaffected — sparse vectors are not quantized. See [`casehub-neocortex/ARC42STORIES.MD` §6](https://github.com/casehubio/neocortex/blob/main/ARC42STORIES.MD#6-runtime-view) for the oversampling design rationale.

Search-time oversampling is documented here (not as a standalone Key Abstraction) because it is a parameter-driven behavior of the retriever, not an independent abstraction.

### 3. Module Structure table — update rag/ row (line 29)

Add to the rag/ module description: `MatryoshkaEmbeddingModel` — truncating `EmbeddingModel` decorator (config-driven via `casehub.rag.matryoshka.dimension`); `DenseQuantization` enum — binary/scalar quantization config for Qdrant dense vector params; `RagBeanProducer` — CDI producer that conditionally wraps `EmbeddingModel` in `MatryoshkaEmbeddingModel` and passes quantization config to both `QdrantEmbeddingIngestor` (collection creation: type + alwaysRam) and `HybridCaseRetriever` (search-time: type + oversampling); `ReactiveRagBeanProducer` — same conditional Matryoshka wrapping and quantization wiring for reactive implementations (`ReactiveQdrantEmbeddingIngestor`, `ReactiveHybridCaseRetriever`), gated by `casehub.rag.reactive.enabled=true`.

### 4. Relationship to LangChain4j table — two new rows

| Capability | Where it lives |
|---|---|
| Matryoshka dimension reduction + L2 renorm | `rag` (this module) — decorator above LangChain4j `EmbeddingModel` |
| Dense vector quantization (binary/scalar) + search-time oversampling | `rag` (this module) — Qdrant collection config + search params |

### 5. Current State — update C7 row

Add to the C7 description, distinguished as optimization features (not new SPIs): storage/search optimization via `MatryoshkaEmbeddingModel` (truncating decorator), `DenseQuantization` (binary/scalar dense vector params config), search-time oversampling on quantized dense prefetch, `RagBeanProducer` / `ReactiveRagBeanProducer` CDI wiring for both features. Both blocking and reactive implementations carry all features. Reference neocortex#31.

### 6. Design Documents — add ARC42STORIES.MD reference

Add to the Design Documents section (after the existing spec and issue references):

- [casehubio/neocortex ARC42STORIES.MD](https://github.com/casehubio/neocortex/blob/main/ARC42STORIES.MD) — authoritative architecture record (Matryoshka §4, oversampling §6, dimension consistency §7, naming §8)

### 7. Fix stale class names from #17 refactor

The #17 refactor (commit 2768c01, 2026-06-12) renamed rag-api SPIs to free the `CorpusStore` name for the corpus storage module (#18). The deep-dive still uses the old names. This edit is the **single authority** for all stale name fixes — Edits 3 and 5 handle only new #31 content.

Fix all occurrences:

| Stale name | Current name | Locations in deep-dive |
|---|---|---|
| `CorpusStore` (rag-api SPI) | `EmbeddingIngestor` | rag-api row (line 28), rag-testing row (line 30), Key Abstractions header (line 53), Key Abstractions body (line 55) |
| `ReactiveCorpusStore` | `ReactiveEmbeddingIngestor` | rag-api row (line 28) |
| `QdrantCorpusStore` | `QdrantEmbeddingIngestor` | C7 row (line 144) |
| `QdrantCaseRetriever` | `HybridCaseRetriever` | C7 row (line 144) |

Specific changes:

- **Key Abstractions header** (line 53): `### CorpusStore / CaseRetriever (rag-api)` → `### EmbeddingIngestor / CaseRetriever (rag-api)`
- **Key Abstractions body** (line 55): Update both name and description. The old text says "CorpusStore — ingest, delete, and list documents per tenant corpus." The #17 rename was motivated by the interface working with pre-chunked embeddings, not documents. Verified from `EmbeddingIngestor.java`: `ingest(CorpusRef, List<ChunkInput>)` takes pre-chunked text; `deleteDocument` and `listDocuments` operate at source document granularity. New text: `EmbeddingIngestor` — ingest pre-chunked text into vector store (embedding + storage), delete and list by source document. Tenancy-scoped; `CorpusRef` carries tenant ID + corpus name.
- **rag-testing module row** (line 30): `In-memory CorpusStore + CaseRetriever` → `In-memory EmbeddingIngestor + CaseRetriever`
- **rag-api module row** (line 28): `CorpusStore SPI, CaseRetriever SPI (blocking); ReactiveCorpusStore, ReactiveCaseRetriever` → `EmbeddingIngestor SPI, CaseRetriever SPI (blocking); ReactiveEmbeddingIngestor, ReactiveCaseRetriever`
- **C7 row** (line 144): `CorpusStore SPI, CaseRetriever SPI, QdrantCorpusStore, QdrantCaseRetriever in rag` → `EmbeddingIngestor SPI, CaseRetriever SPI, QdrantEmbeddingIngestor, HybridCaseRetriever in rag`
