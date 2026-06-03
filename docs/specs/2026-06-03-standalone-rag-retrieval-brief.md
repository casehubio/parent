# Universal RAG/Retrieval Library — Design Brief

**Date:** 2026-06-03  
**Status:** Pre-design — pending Hortora validation  
**Consumers:** casehub (all tiers), Hortora  
**Tracking:** casehubio/parent#158

---

## What This Is

A standalone, framework-agnostic retrieval library. Not casehub-specific. Both casehub and Hortora are consumers — neither owns it. It is a universal RAG primitive that any JVM project can depend on.

Hortora already runs this technology stack in production: **Tika + ONNX + SPLADE + Qdrant**. The goal is an SPI-based library around that proven stack that both projects share — casehub taking it as a foundation dependency, Hortora adopting or aligning with it as a standardised interface over its existing implementation.

**Hortora must validate the SPI design before implementation begins.** See the validation checklist below.

---

## Why Standalone

If this is built inside casehub, Hortora takes a dependency on casehub. That imports casehub-ledger, casehub-engine, and the full domain surface — none of which Hortora needs. The boundary collapses.

The correct structure: a neutral library that both projects depend on. `retrieval-api` and `retrieval-core` have zero framework and zero domain dependencies. Each project brings its own CDI wiring or framework adapter. The shared code is the SPI contract and pipeline coordination, not the runtime.

---

## The Technology Stack

These are not decisions to be made — they are the known proven stack from Hortora's production usage:

| Technology | Role | Why |
|------------|------|-----|
| **Apache Tika** | `DocumentIngester` | 1000+ formats: PDF, Word, Excel, HTML, email, images, audio, video. OCR via Tesseract. Language detection. Metadata extraction. |
| **ONNX Runtime (JVM)** | `EmbeddingProvider` (dense) | No API call. No Python. Deterministic. Any ONNX-format model. Runs air-gapped — required for regulated deployments (clinical, AML, financial). |
| **SPLADE** | `EmbeddingProvider` (sparse) | Lexical + expansion. Better than BM25 for regulatory and clinical text where terminology carries precise weight. Interpretable — which terms drove the match. Auditable. |
| **Qdrant** | `VectorStore` | Named vector spaces — stores both dense (ONNX) and sparse (SPLADE) vectors per document. Payload filtering for tenancy isolation. Production-grade. |

**The hybrid architecture:** every document gets two vector representations. Qdrant stores both in named vector spaces per point. Retrieval uses either or both, depending on query type. Dense for semantic similarity; sparse for terminology-precise domains. This is already how Hortora works.

---

## SPI Design (retrieval-api — zero dependencies)

The core is technology-agnostic. The stack above is the reference implementation tier.

```java
// What gets ingested
interface DocumentIngester {
    IngestedDocument ingest(RawDocument doc);
    // Tika implementation: universal format extraction + metadata
}

// How documents are split
interface Chunker {
    List<Chunk> chunk(IngestedDocument doc, ChunkingConfig config);
    // Default impls: fixed-size, sentence-boundary, paragraph
}

// How chunks become vectors
interface EmbeddingProvider {
    EmbeddingType type();                                          // DENSE | SPARSE
    List<float[]> embed(List<String> texts);                      // ONNX dense
    List<Map<Integer,Float>> embedSparse(List<String> texts);     // SPLADE sparse
}

// Where vectors are stored and queried
interface VectorStore {
    void upsert(List<EmbeddedChunk> chunks);
    List<RankedChunk> query(VectorQuery query);   // carries both dense + sparse vectors
    void delete(String documentId);
    // Qdrant impl: named vector spaces, payload filtering, tenant isolation
}

// How results are ranked and fused
interface RetrievalStrategy {
    List<RankedChunk> rank(List<RankedChunk> candidates, RetrievalContext context);
    // Default: RRF fusion of dense + sparse results
}

// How results become LLM context
interface ContextAssembler {
    String assemble(List<RankedChunk> chunks, AssemblyConfig config);
    // Formats chunks into prompt-injectable context with source citations
}
```

Domain types: `RawDocument`, `IngestedDocument`, `Chunk`, `EmbeddedChunk`, `RankedChunk`, `VectorQuery`, `RetrievalContext`, `EmbeddingType`, `AssemblyConfig`. All pure Java records. No framework types, no casehub types.

---

## Module Structure

```
retrieval-api/          — zero deps: all SPIs + domain types
retrieval-core/         — pipeline coordination, default chunkers, default context assembly
retrieval-tika/         — DocumentIngester backed by Apache Tika + Tesseract
retrieval-onnx/         — EmbeddingProvider (DENSE) backed by ONNX Runtime JVM
retrieval-splade/       — EmbeddingProvider (SPARSE) via SPLADE model loaded through ONNX
retrieval-qdrant/       — VectorStore backed by Qdrant (REST + gRPC); named vector spaces
retrieval-inmem/        — in-memory VectorStore (cosine similarity) for testing only
retrieval-quarkus/      — CDI @DefaultBean wiring + @QuarkusTest support (casehub only)
```

Hortora takes: `retrieval-api` + `retrieval-core` + whichever impl modules it needs.  
Hortora does **not** take: `retrieval-quarkus`.

ArchUnit rule enforced from day one: `retrieval-api` and `retrieval-core` have no dependencies on any casehub artifact, Quarkus, or Spring. Compile-time guarantee of the clean boundary.

---

## CaseHub Use Cases

Beyond document retrieval for LLM context grounding, the stack applies across the future capability roadmap:

**Typed fact space (AI Fusion brief)**  
Qdrant stores historical case fact vectors — enables retrieval of "cases with similar fact patterns" as context for the current case. This is distinct from the live fact space (in-memory/JPA). The retrieval module provides the historical pattern layer.

**Policy engine (#155) — SPLADE for interpretable policy matching**  
Agent actions described in natural language matched against a policy corpus using SPLADE sparse retrieval. The interpretability of which terms drove the match is a compliance audit requirement in regulated deployments.

**AI observability (#154) — ONNX for local hallucination detection**  
`HallucinationDetectionHook` SPI implementation using an ONNX NLI model — scores LLM output faithfulness against input facts. No API call. Deterministic. Runs on every inference in production.

**casehub-openclaw ActionRiskClassifier**  
The current stub (always AUTONOMOUS) replaced with a per-deployment ONNX classifier evaluating agent output risk without API dependency. Fine-tuned per domain (clinical vs AML vs enterprise).

**casehub-eidos epistemic confidence estimation**  
An ONNX model estimating dynamic epistemic domain confidence from agent output history — more accurate than statically-declared `epistemicDomains` values. Feeds into `CapabilityHealth.probe()`.

**AML + clinical — SPLADE for regulatory text**  
SAR typology matching, clinical protocol retrieval, regulatory clause lookup — SPLADE's lexical precision outperforms dense embeddings in terminology-precise regulatory domains.

---

## Hortora Validation Checklist

Before implementation begins, Hortora should validate:

1. Does the SPI design match how Hortora currently uses Tika, ONNX, SPLADE, and Qdrant — or would adopting this require changing Hortora's retrieval approach?
2. Is the hybrid dense+sparse architecture (named vector spaces in Qdrant) consistent with Hortora's Qdrant collection structure?
3. Are there chunking or context assembly strategies Hortora uses that the default implementations in `retrieval-core` should cover?
4. Does Hortora have SPLADE model distribution or packaging patterns worth standardising in `retrieval-splade`?
5. Any Qdrant collection management patterns (index config, quantisation, tenant isolation) worth standardising in `retrieval-qdrant`?
6. Is the `EmbeddingProvider` split between DENSE and SPARSE the right interface shape, or does Hortora's usage suggest a different decomposition?

---

## Repo Decision

**Start as `casehub-retrieval` under casehubio.** ArchUnit enforces zero-domain-dep constraint on `retrieval-api` and `retrieval-core` from day one. Extract to standalone repo (e.g. `mdproctor/quark-retrieval`) when Hortora integration is ready — at that point the boundary is already proven clean and the extraction is mechanical.

---

## Sequencing

1. **Typed fact space** (AI Fusion brief) — higher priority; enables Drools + QuarkusFlow + LLM synthesis
2. **This module** — unblocks both casehub knowledge grounding and Hortora alignment
3. **Artifact pipeline (#157)** — feeds retrieval ingestion; delivers incrementally

Hortora validation should happen in parallel with the typed fact space work so the retrieval module design is confirmed before implementation begins.
