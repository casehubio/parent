# Platform Documentation Restructuring — LLM-Optimized Chunking and Audience Guides

**Date:** 2026-07-07
**Status:** Draft — awaiting adversarial review
**Tracking:** casehub/parent (doc audit + restructuring) — epic issue to be created before implementation begins

---

## Goals, Motivations, and What This Must Achieve

### The Problem

CaseHub has grown to 32 repos, ~206 BOM dependencies, and 27 repo deep-dives. The documentation was built for a smaller platform and has not kept pace with three kinds of growth:

1. **New capabilities undocumented.** Platform shipped a full notification/subscription system (platform#142-149). CBR integration now spans engine, neocortex, clinical, blocks. Blocks (Java) owns shared routing strategies, compliance record types, feature extraction SPIs, and agentic orchestration patterns. None of this is in PLATFORM.md or any single discovery point.

2. **UI layer invisible.** Five+ apps now have web UIs (AML, Claudony, Drafthouse, IoT, DevTown, Connectors). `casehub-pages` provides foundation web component infrastructure. `casehub-blocks-ui` provides 14 shared domain components. There is no UI architecture document, no `pages` deep-dive, and PLATFORM.md is entirely backend-focused. An LLM working in AML doesn't know `blocks-ui`'s `work-item-inbox` or `trust-score-panel` exist.

3. **Stale names and references.** CorpusStore → EmbeddingIngestor, casehub-neural-text → casehub-neocortex, melviz → casehub-pages, WorkBroker → AgentRoutingStrategy. Deep-dives reference types that no longer exist.

### The Consequence

LLM sessions in app repos hit blind spots: they rebuild shared UI components, duplicate routing infrastructure, miss platform capabilities, and produce inconsistent architectures. This is not a human readability problem — it's an LLM productivity problem. The docs are the primary mechanism by which LLM sessions across 26+ repos maintain coherence with each other.

### What Success Looks Like

After this restructuring:

1. **An LLM starting a new app (e.g. SOC) can discover in <200 lines of reading what exists across the entire platform** — shared Java patterns, shared UI components, platform SPIs to implement, and how other apps solved the same problems.

2. **An LLM in any app repo never rebuilds something that already exists in blocks, blocks-ui, or another app** — because the discovery index and app-builder guide make existing capabilities findable before the LLM starts designing.

3. **An LLM doing a spec review can check platform coherence by loading ~150 lines (INDEX.md) + the relevant topic chunks (~200-300 lines each)** instead of all of PLATFORM.md (685 lines of dense, cross-cutting content where most is irrelevant to the task at hand). The skill integration is efficient — the LLM loads only the chunks that matter.

4. **Cross-app learning is natural.** An LLM building oversight gates in SOC can see how AML and Clinical did it, what blocks provides, and what the common pattern is — all from a single pattern catalogue entry.

5. **New capabilities have a clear home.** When a new platform feature ships, there's an obvious chunk to update and an obvious place in the index to add it. No more "where in the monolith do I add this?"

6. **Documentation stays current.** Smaller, scoped files are easier to maintain than a monolith. Each chunk has a clear owner (the repo that owns the capability). Drift is localized rather than systemic.

### Assumptions We Are Making

**A1. LLMs benefit from smaller, topic-scoped documents over large monolithic ones.** We assume that loading 150 lines of index + 300 lines of relevant chunk is better than loading all 685 lines of PLATFORM.md where most content is irrelevant to the current task. This assumes LLMs have limited effective context and that irrelevant content degrades reasoning quality. The primary motivation is relevance, not raw line count.

**A2. Two audience journeys (app builder vs platform builder) capture the meaningful divide.** We assume the primary split is "using the platform" vs "extending the platform." An alternative would be three journeys (adding UI repos), or zero (everyone reads the same docs). Is two the right number?

**A3. The discovery index is the right dispatch mechanism for skills.** We assume skills can effectively use INDEX.md to identify relevant chunks. An alternative would be a structured metadata file (JSON/YAML) that skills parse programmatically rather than an LLM reading a markdown index.

**A4. Cross-app learning via a pattern catalogue is more valuable than per-repo isolation.** We assume that apps benefit from seeing how other apps solved problems. This creates a maintenance cost — every new app capability should be reflected in the catalogue. Is this cost worth the coherence benefit?

**A5. The extraction placement criteria (blocks scope) are correct and stable.** We rely on the existing blocks scope criteria (AI/LLM patterns, classical AI, cross-foundation composition) and the blocks-ui scope (platform-concept visualization). If these criteria are wrong, the guides will give wrong placement advice.

**A6. PLATFORM.md can be retired as a redirect.** We assume no external consumer depends on PLATFORM.md being a single file. GitHub raw URLs to PLATFORM.md exist in every repo's CLAUDE.md. The redirect must not break these.

**A7. Deep-dives at full SPI depth are worth the maintenance cost.** We're keeping full class names, method signatures, and invariants in deep-dives. This makes them authoritative but expensive to maintain. The alternative (trimming to family-awareness level, pushing detail to repo-owned DESIGN.md) was considered and rejected because deep-dives are the primary source LLMs use for cross-repo understanding.

### Open Questions for the Reviewer

**Q1. Chunk granularity.** We propose ~13 topic chunks in `platform/`. Is this the right granularity? Too many chunks means the index becomes a maze. Too few means chunks are still monolithic. Should some proposed chunks be merged (e.g. `auth.md` + `privacy.md` → `security.md`)? Should any be split further?

**Q2. Pattern catalogue maintenance.** The app-builder guide includes a pattern catalogue showing how each app implemented each capability. This is high-value but high-maintenance. When a new app adds trust routing, someone must update the catalogue. Is this realistic? Would a lighter-weight approach (just the capability matrix, no detailed patterns) be more sustainable?

**Q3. Does this actually prevent the blind spots we identified?** Walk through the specific scenarios:
- LLM in AML building a new UI view — does it find blocks-ui components?
- LLM in SOC starting from scratch — does it find the right app to copy?
- LLM in engine adding a new SPI — does it know to update INDEX.md and building-apps.md?
- LLM reviewing a spec — does the skill integration actually work better than loading PLATFORM.md?

**Q4. Protocol integration depth.** We propose protocols appearing in three places: INDEX.md (names inline with topics), topic chunks (summarized + linked), and garden INDEX.md (authoritative). Is the summary-in-chunk approach right, or should chunks just link to protocols without summarizing them? Summaries risk drift from the authoritative protocol text.

**Q5. CLAUDE.md update scope.** We propose updating ~26 repo CLAUDE.md files to point to the new structure. This is a massive cross-repo change. Is it worth doing atomically, or should we phase it (update parent docs first, then update CLAUDE.md files repo by repo)?

**Q6. Is the two-audience split sufficient for the UI dimension?** App builders who are doing Java backend work have different needs than app builders doing TypeScript UI work. Should building-apps.md have clear sections for "backend integration" vs "UI composition", or is the current structure (capability matrix + pattern catalogue covering both) sufficient?

**Q7. Deep-dive update verification.** We list 18 deep-dives as needing updates based on recent git activity. But git commits don't tell us exactly which deep-dive sections are stale. Should the implementation plan include a per-deep-dive verification step (read the deep-dive, read the current code, diff the gap), or is the commit-based gap list sufficient?

**Q8. How do we prevent this from going stale again?** This restructuring fixes the current state, but the same drift will recur. Should we propose a maintenance mechanism (e.g. a periodic doc-sync check, a skill that audits INDEX.md against actual repo state, a CI check)? Or is that out of scope for this design?

---

## Document Architecture

### Core Principle

The chunks are the source of truth. Human-readable aggregate views (web docs, exported PDFs) are composed downstream — not the other way round. Every file is designed for LLM consumption: self-contained, scoped, right-sized (200–500 lines), with a clear scope declaration at the top so an LLM can bail early if it loaded the wrong chunk.

### File Structure

```
docs/
├── INDEX.md                        # Discovery index (~150 lines)
│                                   # THE universal entry point for all LLM sessions
│                                   # Organized by CONCERN, not by repo
│
├── guides/
│   ├── building-apps.md            # App builder journey (~500 lines)
│   │                               # Capability matrix, pattern catalogue,
│   │                               # cross-app learning, placement criteria
│   │
│   └── building-platform.md        # Platform builder journey (~200 lines)
│                                   # Boundary rules, SPI design, protocols,
│                                   # "adding a new capability" checklist
│
├── platform/                       # Topic chunks (replaces monolithic PLATFORM.md)
│   ├── coherence-protocol.md       # Steps 1-6: the pre-implementation protocol
│   ├── capability-ownership.md     # "Where does X live?" lookup table
│   ├── dependency-map.md           # Cross-repo dependency impact analysis
│   ├── overview.md                 # Tier structure, repo map, build order
│   ├── boundary-rules.md           # ALL "do not" rules consolidated
│   ├── persistence.md              # Flyway, datasources, migration paths
│   ├── auth.md                     # Auth topology, roles, outbound credentials
│   ├── observability.md            # Tracing, audit trail, telemetry
│   ├── agent-identity.md           # DID format, SCIM2, eidos descriptors
│   ├── agent-mesh.md               # 3-channel layout, speech acts, commitments
│   ├── notifications.md            # NEW — subscription engine, delivery pipeline
│   ├── cbr.md                      # CBR capability map (absorbs CBR-CAPABILITY.md)
│   ├── routing.md                  # NEW — routing strategies, 4-layer ownership
│   ├── ui-architecture.md          # NEW — pages → blocks-ui → app UI layering
│   ├── privacy.md                  # GDPR erasure, PII sanitisation
│   ├── overlap-risks.md            # Known semantic collisions + placement violations
│   └── protocols.md                # Protocol summary, audience mapping, garden links
│
├── repos/                          # Per-repo deep-dives (updated + new)
│   └── (27 existing + 1 new: casehub-pages.md)
│
├── PLATFORM.md                     # REDIRECT — 5-line pointer to INDEX.md
├── APPLICATIONS.md                 # UPDATED — UI status, cross-references
├── ARCHITECTURE.md                 # KEEP — pattern reference
├── CHANNELS.md                     # KEEP — channel taxonomy
├── LIFECYCLE.md                    # KEEP — state machines
├── DSL-STYLE-GUIDE.md              # KEEP — API conventions
├── CBR-CAPABILITY.md               # RETIRE — absorbed into platform/cbr.md
├── config-architecture.md          # UPDATE — new topic ownership entries
├── new-repo-checklist.md           # KEEP
├── tutorial-strategy.md            # KEEP
├── use-case-analysis.md            # KEEP
└── prompt-snippets.md              # UPDATE — point to new structure
```

### Navigation Model

How an LLM finds what it needs:

```
Repo CLAUDE.md (always loaded)
  │
  ├─→ INDEX.md (~150 lines, organized by concern)
  │     ├─→ specific platform/ chunk (~200-300 lines)
  │     └─→ specific repos/ deep-dive (~200-500 lines)
  │
  └─→ appropriate guide (building-apps.md or building-platform.md)
        └─→ pattern catalogue, capability matrix, protocol mapping
```

**Relevance comparison:**
- **Before:** CLAUDE.md → PLATFORM.md (685 dense lines) → maybe a deep-dive (300 lines) = ~985 lines loaded, most of PLATFORM.md irrelevant to the current task
- **After:** CLAUDE.md → INDEX.md (150 lines) → one chunk (200-300 lines) → maybe a deep-dive (300 lines) = ~650-750 lines loaded, all relevant to the current task

The value is not raw line savings (~24% reduction) but relevance density: in the current model, an LLM working on persistence loads all 685 lines of PLATFORM.md to find the ~30 lines about Flyway conventions. In the new model, it loads `platform/persistence.md` (~200 lines, all persistence-related).

### Chunk Header Convention

Every chunk starts with a scope block so an LLM can bail immediately:

```markdown
# Persistence

> **Scope:** Flyway migration conventions, datasource naming, migration path scoping
> **Audience:** All (platform + app builders)
> **Key repos:** casehub-ledger, casehub-work, casehub-qhorus, casehub-engine
> **Protocols:** [flyway-repo-scoped-migration-path], [flyway-migration-rules],
>   [flyway-extension-migration-registration]
```

---

## INDEX.md Design

The index serves double duty: **discovery** for ad-hoc navigation AND **coherence dispatch** for skills.

A skill doing a spec review:
1. Loads INDEX.md (always — ~150 lines, cheap)
2. Scans for capabilities touched by the spec
3. Loads only the relevant chunks and protocols
4. Checks coherence against scoped content, not the entire platform

Skills that currently say "consult PLATFORM.md" get updated to say "consult INDEX.md + load relevant topic chunks." This is a skill-level wording change.

### INDEX.md Content Structure

```markdown
# CaseHub Platform Index

> Load this first. Find your topic, follow the link.
> For audience-specific guidance: [Building Apps](guides/building-apps.md)
> | [Building Platform](guides/building-platform.md)

## Orchestration & Cases
- **Engine** — case lifecycle, YAML DSL, blackboard, planning strategies
  → [repos/casehub-engine.md]
- **Work** — human task lifecycle, WorkItem inbox, SLA, delegation
  → [repos/casehub-work.md]
- **Routing** — trust-weighted, semantic, CBR-evidence agent selection
  → [platform/routing.md]
- **CBR** — case-based reasoning: retrieve, reuse, revise, retain
  → [platform/cbr.md]

## Agent Communication
- **Qhorus** — speech acts, commitments, channels, message delivery
  → [repos/casehub-qhorus.md]
- **Agent Mesh** — 3-channel normative layout, mesh participation
  → [platform/agent-mesh.md]
- **Channels taxonomy** — purpose categories, discriminator dimensions
  → [CHANNELS.md]

## Agent Identity & Behavior
- **Eidos** — structured identity, capability health, vocabulary
  → [repos/casehub-eidos.md]
- **Identity** — platform identity submodule (OIDC, SCIM, groups)
  → [repos/casehub-identity.md]
- **Agent Identity** — DID format, SCIM2, versioning
  → [platform/agent-identity.md]

## UI & Frontend
- **Pages** — web component framework, data pipelines, layouts
  → [repos/casehub-pages.md]
- **Blocks UI** — 14 shared domain components (work items, trust, SLA)
  → [repos/casehub-blocks-ui.md]
- **UI Architecture** — pages → blocks-ui → app UI layering
  → [platform/ui-architecture.md]
  → protocols: [custom-event-shadow-dom], [lit-immutable-collections]

## Shared Java Patterns
- **Blocks** — agentic orchestration, routing, oversight, conversation
  → [repos/casehub-blocks.md]
  → scope criteria, consolidation epic, placement decisions

## Persistence & Data
- **Persistence** — Flyway conventions, datasource naming
  → [platform/persistence.md]
  → protocols: [flyway-repo-scoped-migration-path],
    [flyway-extension-migration-registration], [flyway-migration-rules]
- **Ledger** — tamper-evident audit, Merkle, trust scoring
  → [repos/casehub-ledger.md]

## Infrastructure & Integration
- **Connectors** — Slack, Teams, email, chat platform SPI
  → [repos/casehub-connectors.md]
- **Workers** — HTTP, Camel, MCP, K8s, GitHub Actions dispatch
  → [repos/casehub-workers.md]
- **Worker API** — Worker, Capability, WorkerFunction primitives
  → [repos/casehub-worker.md]
- **IoT** — device abstraction, Matter-aligned, HA/OpenHAB providers
  → [repos/casehub-iot.md]
- **OpenClaw** — CaseHub ↔ OpenClaw bridge, worker provisioning
  → [repos/casehub-openclaw.md]

## Operations & Desired State
- **Desired State** — reconciliation runtime, goal compilation
  → [repos/casehub-desiredstate.md]
- **RAS** — situational awareness, event correlation, case triggers
  → [repos/casehub-ras.md]
- **Ops** — CaseHub deployment, infrastructure, compliance posture
  → [repos/casehub-ops.md]

## Cross-Cutting
- **Auth** — gateway topology, roles, outbound credentials
  → [platform/auth.md]
- **Notifications** — subscription engine, delivery, digest batching
  → [platform/notifications.md]
- **Privacy** — GDPR erasure, PII sanitisation
  → [platform/privacy.md]
- **Observability** — OTel tracing, audit entries, ledger correlation
  → [platform/observability.md]

## Platform Operations
- **Coherence Protocol** — 6-step pre-implementation protocol (run before any change)
  → [platform/coherence-protocol.md]
- **Capability Ownership** — "where does X live?" lookup table
  → [platform/capability-ownership.md]
- **Dependency Map** — cross-repo impact analysis for renames, removals, SPI breaks
  → [platform/dependency-map.md]

## Architecture & Conventions
- **Boundary Rules** — all "do not" rules across the platform
  → [platform/boundary-rules.md]
- **Overlap Risks** — known semantic collisions
  → [platform/overlap-risks.md]
- **Architecture** — tier patterns, dependency rule, selective event sourcing
  → [ARCHITECTURE.md]
- **DSL Style** — fluent API conventions
  → [DSL-STYLE-GUIDE.md]
- **Lifecycle** — state machines, terminal semantics
  → [LIFECYCLE.md]
- **Protocols** — implementation conventions (audience-mapped)
  → [platform/protocols.md]
  → full index: [garden protocols INDEX.md]

## Applications
- **App inventory** — all domain applications with status
  → [APPLICATIONS.md]
- **App builder guide** — capability matrix, pattern catalogue
  → [guides/building-apps.md]
```

---

## Audience Guides

### Protocol Integration

Protocols appear in three places with no content duplication:

| Location | What it shows | Purpose |
|---|---|---|
| INDEX.md | Protocol names inline with their topic | Discovery |
| Topic chunks | One-line scope statement + link to full protocol | In-context discovery |
| Garden INDEX.md | Full protocol catalogue with metadata | Authoritative |

Topic chunks do NOT summarize protocol rules — they provide a one-line scope statement ("what this protocol governs") and link to the authoritative text in garden. This prevents drift between the protocol source and embedded summaries. The same duplication avoidance principle that applies to guides ("neither guide contains substantive content") applies to topic chunks' protocol references.

Audience mapping lives in the guides — each guide lists the protocols relevant to its audience.

### `guides/building-apps.md`

The app-builder guide is the anti-blind-spot document. It prevents duplication by surfacing what exists before an LLM starts designing.

**Size constraint:** ~400 lines max. Per-app implementation details live in deep-dives, not here. If the guide grows past 400 lines, content has leaked from deep-dives — push it back.

**Structure:**

1. **The Pattern** — bring your domain, use the platform, modify nothing below. Link to boundary-rules.md. Link to AGENTIC-HARNESS-GUIDE.md for session conventions.

2. **App Capability Matrix** — grid of all apps × all capabilities, showing layer numbers and completion status. Two-part: shared building blocks (blocks + blocks-ui) first, then per-app implementation status. "Starting a new app?" decision tree based on domain similarity.

3. **Pattern Catalogue** — organized by concern (case types, trust routing, oversight gates, web UI composition, GDPR erasure, etc.). Each entry is compact:
   - **Shared pattern** — what blocks/blocks-ui/platform provides (one line + link to topic chunk)
   - **Per-app references** — brief links to the relevant deep-dive sections (no inline details)

4. **Where Does a Reusable Pattern Belong?** — placement criteria table covering blocks (Java), blocks-ui (TypeScript), platform, engine, and app repos. References blocks scope criteria. Includes worked examples from consolidation epic #28.

5. **Protocols for App Builders** — subset of protocols relevant to app development, grouped by concern.

6. **Layer Progression** — how apps build up capability by capability, with cross-references to each app's ARC42STORIES.MD §9.4.

### `guides/building-platform.md`

Lighter document — mostly navigation + boundary rules + "adding a new capability" checklist.

**Structure:**

1. **Architecture** — links to ARCHITECTURE.md and platform/overview.md.
2. **Boundary Rules** — links to boundary-rules.md and overlap-risks.md.
3. **SPI Design Conventions** — links to api-interface-taxonomy protocol, module-tier-structure protocol, DSL-STYLE-GUIDE.md.
4. **Adding a New Capability** — checklist: check INDEX.md, decide repo ownership, follow module-tier-structure, add to INDEX.md, update building-apps.md if app-facing.
5. **Cross-Cutting Concerns** — links to all platform/ chunks.
6. **All Protocols** — full protocol list (platform builders must know all).
7. **Application Impact** — when your platform change affects app builders, update building-apps.md, INDEX.md, and the relevant topic chunk.

### Duplication Avoidance

Neither guide contains substantive content — they are navigation + cross-references + tables. The actual content lives in topic chunks (`platform/*.md`) and deep-dives (`repos/*.md`). Both guides link to the same chunks with different framing.

Content unique to each guide:
- **building-apps.md:** Capability matrix, pattern catalogue, placement criteria, per-app deep-dive cross-references
- **building-platform.md:** "Adding a new capability" checklist, "application impact" reminder

---

## Staleness Prevention

The platform grew faster than its docs — this restructuring fixes the current state, but the same drift will recur without a mechanism to prevent it. Two complementary mechanisms:

### 1. Chunk Ownership in Headers

Every topic chunk declares its owning repos in its scope block header:

```markdown
> **Key repos:** casehub-ledger, casehub-work, casehub-qhorus, casehub-engine
```

Each repo's CLAUDE.md already says "read your deep-dive." Extend this to include relevant topic chunks:

```markdown
## Platform docs
Read at session start: `~/claude/casehub/parent/docs/INDEX.md`
Your deep-dive: `docs/repos/casehub-ledger.md`
Topic chunks relevant to this repo: `platform/persistence.md`, `platform/observability.md`
```

Sessions in ledger naturally load and read `platform/persistence.md`. If it's stale, the LLM notices during the Platform Coherence Protocol (Step 5 says "does this need a doc update?") and updates it in the same session. This is the same mechanism that keeps deep-dives current today — it works because sessions read the docs and flag discrepancies.

### 2. Implementation Doc-Sync Extension

The existing `implementation-doc-sync` step (prompt-snippets.md #6) checks whether docs need updating after implementation. Extend it to include chunk freshness:

> After implementing: check INDEX.md — does your change add a capability not in the index? Check your relevant topic chunks — does the content match the current code?

This is a wording change to prompt-snippets.md, not a new skill or tool. It piggybacks on the existing doc-sync discipline.

---

## Scope Transparency

This effort is approximately **30% content reorganization and 70% new content creation:**

- **Reorganized content (~360 lines):** coherence-protocol.md, capability-ownership.md, dependency-map.md, boundary-rules.md, and overlap-risks.md extract and restructure existing PLATFORM.md sections.
- **New content (~2,600 lines):** topic chunks covering capabilities not documented anywhere (notifications, routing, UI architecture), the discovery index (INDEX.md), audience guides, and the pattern catalogue.
- **Updated content (~18-27 deep-dives):** verification and updates to existing deep-dives against current code.

The restructuring label is accurate for the overall shape (monolith → chunks), but most of the work is writing new documentation for capabilities that have outgrown their current coverage.

---

## Content Audit — File-Level Changes

### New Files (21)

| File | Purpose | Est. lines |
|---|---|---|
| `docs/INDEX.md` | Discovery index, skill dispatch | ~150 |
| `docs/guides/building-apps.md` | App builder journey, cross-app patterns | ~400 |
| `docs/guides/building-platform.md` | Platform builder journey | ~200 |
| `docs/platform/coherence-protocol.md` | Steps 1-6 pre-implementation protocol (extracted from PLATFORM.md lines 13-98) | ~100 |
| `docs/platform/capability-ownership.md` | "Where does X live?" lookup table (extracted from PLATFORM.md lines 361-474) | ~120 |
| `docs/platform/dependency-map.md` | Cross-repo dependency impact analysis (extracted from PLATFORM.md lines 219-354) | ~140 |
| `docs/platform/overview.md` | Tier structure, repo map, build order | ~200 |
| `docs/platform/boundary-rules.md` | All "do not" rules | ~250 |
| `docs/platform/persistence.md` | Flyway, datasources, migrations | ~200 |
| `docs/platform/auth.md` | Auth topology, roles, outbound credentials | ~250 |
| `docs/platform/observability.md` | Tracing, audit trail, telemetry | ~150 |
| `docs/platform/agent-identity.md` | DID, SCIM2, eidos descriptors | ~150 |
| `docs/platform/agent-mesh.md` | 3-channel layout, mesh participation | ~200 |
| `docs/platform/notifications.md` | Subscription engine, delivery (NEW content) | ~200 |
| `docs/platform/cbr.md` | CBR capability map (absorbs CBR-CAPABILITY.md) | ~200 |
| `docs/platform/routing.md` | Routing strategies, 4-layer ownership (NEW content) | ~250 |
| `docs/platform/ui-architecture.md` | pages → blocks-ui → app layering (NEW content) | ~300 |
| `docs/platform/privacy.md` | GDPR erasure, PII sanitisation | ~100 |
| `docs/platform/overlap-risks.md` | Known collisions + placement violations | ~150 |
| `docs/platform/protocols.md` | Protocol summary, audience mapping | ~150 |
| `docs/repos/casehub-pages.md` | NEW deep-dive for pages | ~300 |

### Deep-Dive Disposition (all 27)

| File | Status | What's stale or missing |
|---|---|---|
| `casehub-blocks.md` | **UPDATE** | Says "scaffold" — needs full module structure, scope criteria, consumers, consolidation epic |
| `casehub-blocks-ui.md` | **UPDATE** | Missing notification-inbox, data-table, work-item-workbench, maturity levels |
| `casehub-platform.md` | **UPDATE** | Missing notification/subscription system, EventTypeRegistry, DataSource SPI |
| `casehub-engine.md` | **UPDATE** | Missing CBR bridge, types/labels, RoutingOutcomeRecorder, CaseDefinition classification |
| `casehub-neocortex.md` | **UPDATE** | Stale names (CorpusStore→EmbeddingIngestor), missing Matryoshka, quantization, CBR reconciliation |
| `casehub-eidos.md` | **UPDATE** | Missing behavioral contracts, semantic capability matching, capability descriptions |
| `casehub-connectors.md` | **UPDATE** | Missing ChatPlatform SPI, RichCard, chat demo, Discord translation |
| `casehub-workers.md` | **UPDATE** | Missing K8s worker dispatch, restart recovery, bindingName correlation |
| `casehub-work.md` | **UPDATE** | Missing types/labels, tenancy-aware query, work-rest module extraction |
| `casehub-ledger.md` | **UPDATE** | Missing ledger-rest extraction, cloud KMS signers (AWS/GCP/Azure/Vault) |
| `claudony.md` | **UPDATE** | Missing pages/Quinoa adoption, multi-tenancy, ProvisionerConfigRegistry |
| `casehub-drafthouse.md` | **UPDATE** | Missing replay adapter, WebSocket, section highlighting, Quinoa |
| `casehub-ras.md` | **UPDATE** | Needs verification against current code |
| `casehub-desiredstate.md` | **UPDATE** | Needs verification against current code |
| `casehub-ops.md` | **UPDATE** | Needs verification against current code |
| `casehub-clinical.md` | **UPDATE** | Missing CBR integration, feature extractor, REST precedent endpoints |
| `casehub-aml.md` | **UPDATE** | Missing web UI views (operations, accountability, investigations) |
| `casehub-devtown.md` | **UPDATE** | Missing governance workbench UI, WebSocket bridge |
| `casehub-qhorus.md` | **VERIFY** | Major recent work (slack channel backend, postgres broadcaster, inbound bridge) — verify current |
| `casehub-iot.md` | **VERIFY** | Bridge persistence, webapp, bridge-server, 6 deployment topologies — verify current |
| `casehub-identity.md` | **VERIFY** | Platform identity submodule — verify current; add to INDEX.md Agent Identity section |
| `casehub-worker.md` | **VERIFY** | Worker primitives — verify current against casehub-worker-api |
| `casehub-fsitrading.md` | **VERIFY** | Verify current against repo state |
| `casehub-life.md` | **VERIFY** | Verify current — recent RBAC, IoT ganglia, risk classification work |
| `casehub-openclaw.md` | **VERIFY** | Verify current — DirectCallBridge, AgentProvider integration |
| `casehub-soc.md` | **VERIFY** | Verify current against repo state |
| `quarkmind.md` | **VERIFY** | Verify current — engine migration, strategy trust routing |

### Cross-Cutting Name Fixes

| Old | New | Affected files |
|---|---|---|
| `CorpusStore` | `EmbeddingIngestor` | casehub-neocortex.md, any CBR references |
| `ReactiveCorpusStore` | `ReactiveEmbeddingIngestor` | casehub-neocortex.md |
| `QdrantCorpusStore` | `QdrantEmbeddingIngestor` | casehub-neocortex.md |
| `QdrantCaseRetriever` | `HybridCaseRetriever` | casehub-neocortex.md, CBR references |
| `casehub-neural-text` | `casehub-neocortex` | Any remaining references |
| `melviz` / `@melviz/*` | `casehub-pages` / `@casehubio/pages-*` | Any remaining references |
| `WorkBroker` | `AgentRoutingStrategy` | casehub-engine.md, any routing references |
| `CaseChannelLayout` location | moved to `casehub-engine-api` | claudony.md, agent-mesh references |

### Files to Retire or Redirect

| File | Action | Reason |
|---|---|---|
| `PLATFORM.md` | Redirect (5-line pointer to INDEX.md) | Content decomposed into platform/ chunks |
| `CBR-CAPABILITY.md` | Retire (content absorbed into platform/cbr.md) | Avoids two CBR documents |

### Non-Deep-Dive Updates

| File | Change |
|---|---|
| `APPLICATIONS.md` | Add UI status column, blocks-ui usage, cross-references to pattern catalogue |
| `ARCHITECTURE.md` | Update header — replace "Supplement to PLATFORM.md" with standalone description referencing the new structure |
| `config-architecture.md` | Remap all PLATFORM.md topic ownership entries to their new chunk locations (see §config-architecture.md Remapping below) |
| `prompt-snippets.md` | Update "consult PLATFORM.md" → "consult INDEX.md + relevant chunks" |

#### config-architecture.md Remapping

Every entry currently pointing to PLATFORM.md must be remapped:

| Topic | Current authoritative | New authoritative |
|---|---|---|
| Platform coherence protocol | PLATFORM.md | `platform/coherence-protocol.md` |
| SPI placement (§Step 4) | PLATFORM.md | `platform/coherence-protocol.md` (Step 4) |
| Capability ownership | PLATFORM.md | `platform/capability-ownership.md` |
| Named datasources (§Persistence) | PLATFORM.md | `platform/persistence.md` |
| Brainstorm before designing | One-line pointer in PLATFORM.md | `design-implementation.md` (already authoritative — remove PLATFORM.md secondary) |
| TDD/tests before implementing | One-line pointer in PLATFORM.md | `design-implementation.md` (already authoritative — remove PLATFORM.md secondary) |
| Never-dogma / challenge protocols | One sentence in PLATFORM.md | `design-implementation.md` (already authoritative — remove PLATFORM.md secondary) |
| Boundary rules | PLATFORM.md | `platform/boundary-rules.md` |
| Cross-repo dependency map | PLATFORM.md | `platform/dependency-map.md` |
| Known overlap risks | PLATFORM.md | `platform/overlap-risks.md` |
| Implementation protocols | PLATFORM.md | `platform/protocols.md` |
| Platform doc layer entry | PLATFORM.md | INDEX.md (new entry point; platform/ chunks are the authoritative locations per topic) |

### CLAUDE.md Updates (~26 repos)

Every repo's CLAUDE.md currently references PLATFORM.md. After restructuring:

**Platform/foundation repos** (platform, engine, ledger, work, qhorus, eidos, connectors, neocortex, workers, worker, iot, ras, desiredstate, ops, openclaw, flow) → point to INDEX.md + building-platform.md + own deep-dive

**Shared pattern repos** (blocks, blocks-ui, pages) → point to INDEX.md + building-platform.md + platform/ui-architecture.md + own deep-dive

**App repos** (aml, clinical, devtown, life, drafthouse, quarkmind, soc, fsitrading) → point to INDEX.md + building-apps.md + own deep-dive

**Integration repos** (claudony) → point to both guides (bridges foundation and app tiers)

### Files Unchanged

| File | Why |
|---|---|
| `AGENTIC-HARNESS-GUIDE.md` | App-repo session conventions — orthogonal to building-apps.md (which covers platform capabilities, not session discipline). building-apps.md links to this for harness-level conventions. |
| `CHANNELS.md` | Recently rewritten, authoritative |
| `LIFECYCLE.md` | State machine reference — small, correct |
| `DSL-STYLE-GUIDE.md` | API conventions — self-contained |
| `new-repo-checklist.md` | Operational — recently verified |
| `tutorial-strategy.md` | Planning — self-contained |
| `use-case-analysis.md` | Market analysis — self-contained |

---

## Tracking

This restructuring should be tracked as an epic in casehub-parent with sub-issues for major work streams:
- New file creation (INDEX.md, guides, topic chunks)
- Deep-dive updates and verification (18 UPDATE + 9 VERIFY)
- CLAUDE.md migration (~26 repos, phased: foundation repos first, then app repos)
- config-architecture.md remapping
- CBR-CAPABILITY.md retirement

## Scope Summary

| Category | Count |
|---|---|
| New files | 21 (3 extracted + 15 new content + 3 guides/index) |
| Deep-dives to update | 18 |
| Deep-dives to verify | 9 |
| Non-deep-dive updates | 4 |
| CLAUDE.md updates | ~26 repos (phased) |
| Files retired/redirected | 2 |
| Cross-cutting name fixes | 8 patterns across multiple files |
| Files unchanged | 7 |
