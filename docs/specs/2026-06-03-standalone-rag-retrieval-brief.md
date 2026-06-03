# Standalone RAG/Retrieval Module — Design Brief

**Date:** 2026-06-03  
**Status:** Pre-design brief  
**Consumers:** casehub (all application and foundation repos), Hortora  
**Tracking:** casehubio/parent#158

---

## Why Standalone

Both casehub and Hortora need retrieval infrastructure. Designing it inside casehub and having Hortora take a dependency on casehub would import a large, domain-specific surface (ledger, engine, qhorus) into a project that needs none of it.

The correct approach: design this as a self-contained library with zero casehub-domain dependencies in the core. casehub takes a dependency on it; Hortora takes the same dependency. Both get retrieval without coupling to each other's runtimes.

This also makes the module independently useful — any Quarkus application, or any JVM application, could use it.

---

## What it Does

Ground AI agent responses in a persistent, queryable body of organisational knowledge.

**The gap it fills:** `CaseMemoryStore` is short-term operational context, case-scoped, queryable by an agent during a running case. The retrieval corpus is long-lived, organisation-scoped, and indexed by content — it is the knowledge the organisation has accumulated, not the context of a specific running case.

---

## Core Pipeline

```
Document → [Ingester] → [Chunker] → [EmbeddingProvider] → [VectorStore]
                                                                  ↑
Query → [EmbeddingProvider] → [VectorStore.query()] → [RankedChunks] → [ContextAssembler] → Prompt context
```

Each stage is an SPI. The pipeline coordinates them; it does not implement any stage.

---

## SPI Definitions (retrieval-api — zero dependencies)

```java
// What goes in
interface DocumentIngester {
    IngestedDocument ingest(RawDocument doc);  // extract text, metadata, source ref
}

// How to split
interface Chunker {
    List<Chunk> chunk(IngestedDocument doc, ChunkingConfig config);
}

// How to represent
interface EmbeddingProvider {
    List<float[]> embed(List<String> texts);  // batch — minimise API calls
}

// Where to store and query
interface VectorStore {
    void upsert(List<EmbeddedChunk> chunks);
    List<RankedChunk> query(float[] queryEmbedding, VectorQuery query);
    void delete(String documentId);
}

// How to rank and filter results
interface RetrievalStrategy {
    List<RankedChunk> rank(List<RankedChunk> candidates, RetrievalContext context);
}

// How to present to an LLM
interface ContextAssembler {
    String assemble(List<RankedChunk> chunks, AssemblyConfig config);
}
```

Domain types: `RawDocument`, `IngestedDocument`, `Chunk`, `EmbeddedChunk`, `RankedChunk`, `VectorQuery`, `RetrievalContext`, `AssemblyConfig`. All pure Java records. No framework types.

---

## Module Structure

```
retrieval-api/
  — Pure Java, zero external dependencies
  — All SPIs + domain types
  — Suitable as a compile dep for any JVM project

retrieval-core/
  — Pipeline coordination: ingestion → chunking → embedding → store
  — Default chunking implementations (fixed-size, sentence-boundary, paragraph)
  — Default context assembly (markdown, numbered, with source citations)
  — Depends on: retrieval-api only

retrieval-quarkus/
  — CDI @DefaultBean wiring for all SPIs
  — @QuarkusTest support (in-memory store activated by test profile)
  — Quarkus config integration (chunk size, overlap, embedding model, etc.)
  — Depends on: retrieval-core + Quarkus

retrieval-pgvector/
  — VectorStore implementation using PostgreSQL pgvector extension
  — Flyway migration for vector column setup
  — Depends on: retrieval-api + Hibernate Reactive / JDBC

retrieval-inmem/
  — In-memory VectorStore (cosine similarity over ArrayList — test and development only)
  — Depends on: retrieval-api only

retrieval-langchain4j/
  — EmbeddingProvider backed by LangChain4j ChatModel
  — Works with any LangChain4j-compatible provider (OpenAI, Claude, local)
  — Depends on: retrieval-api + langchain4j-core (no specific provider lock-in)
```

---

## Repo Decision

Two options:

**Option A — New standalone repo** (`mdproctor/quark-retrieval` or similar)
- Pros: clear boundary, both casehub and Hortora take a versioned artifact dep; no casehub repo awareness needed in Hortora
- Cons: another repo to maintain, CI, publish pipeline

**Option B — casehub-retrieval module in casehubio/parent BOM, extracted if needed**
- Pros: simpler initially; casehub CI handles it; extract to standalone repo when Hortora integration is ready
- Cons: Hortora would depend on casehubio artifact, which may feel wrong even if the code has zero casehub domain deps

**Recommendation:** Start as `casehub-retrieval` under casehubio, with the explicit design constraint of zero casehub-domain dependencies in `retrieval-api` and `retrieval-core`. Extract to a standalone repo when Hortora integration is ready. The zero-domain-dep constraint is enforceable via ArchUnit from day one.

---

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `casehub-platform CaseMemoryStore` | Different scope: CaseMemoryStore is short-term, case-scoped operational context. Retrieval corpus is long-lived, org-scoped knowledge. They are complementary — an agent might use both in the same step. |
| `casehub-artifacts` (#157) | Artifact pipeline feeds retrieval ingestion. An ingested document is an artifact. They are separate concerns: artifacts own lifecycle and storage; retrieval owns chunking, embedding, and query. |
| `casehub-eidos AgentGraphStore` | Agent task history, not knowledge corpus. Unrelated. |
| `casehub-engine WorkOrchestrator` | Engine dispatches a retrieval step as a QuarkusFlow Worker or directly injects retrieval context into LLM prompt compilation (via fact space — see AI Fusion brief). |

---

## What Hortora Gets

Hortora takes `retrieval-api` + `retrieval-core` as dependencies. It brings its own:
- `EmbeddingProvider` implementation (or uses `retrieval-langchain4j` with its own model config)
- `VectorStore` implementation (or uses `retrieval-pgvector` / `retrieval-inmem`)
- Whatever runtime wiring fits Hortora's framework

Hortora does not take `retrieval-quarkus`. It does not take any casehub-domain module. The boundary is clean.

---

## Sequencing Relative to AI Fusion

The retrieval module is independent of the typed fact space (AI Fusion brief). Both are needed; neither blocks the other. Suggested order:

1. AI Fusion typed fact space (higher priority — enables Drools + QuarkusFlow + LLM synthesis)
2. Retrieval module (enables knowledge-grounded LLM reasoning; also unblocks Hortora need)
3. Artifact pipeline (feeds retrieval; can be delivered incrementally)
