# Agentic Harness Guide

This document applies to every CaseHub application repo:
**casehub-aml, casehub-clinical, casehub-devtown, casehub-life, casehub-drafthouse, QuarkMind**

Read this at session start alongside your CLAUDE.md.

> **Transitional note:** The primary architectural record is **`ARC42STORIES.MD`** (Arc42Stories spec + CaseHub profile). This supersedes `LAYER-LOG.md` and `DESIGN.md`, which are absorbed into §9.4 and §10 respectively. Repos not yet migrated continue using LAYER-LOG.md — see [Migration](#migration-layer-log-to-arc42storiesmd) below. CLAUDE.md files in individual repos will be updated in a forthcoming mass update; where your CLAUDE.md still references LAYER-LOG.md, follow the ARC42STORIES.MD instructions in this guide instead.

---

## What You Are

You are a **domain application built on the CaseHub agentic harness** — the foundation
infrastructure (casehub-engine, casehub-ledger, casehub-work, casehub-qhorus,
casehub-connectors) that coordinates multiple agents (human and AI), enforces formal
accountability per interaction, adapts execution paths based on accumulated context, and
produces an independently verifiable audit trail. The domain varies; the harness
underneath is the same across all four apps.

See `docs/repos/{your-app}.md` in casehub-parent for your domain structure and architecture
layers. See `docs/tutorial-strategy.md §2.0` for the full agentic harness concept.

---

## Your Two Goals

**Primary — Reference architecture and industry engagement**

Build a production-grade application that demonstrates what CaseHub makes possible in
your domain. This is the primary goal. Every architectural decision serves a deployed,
real system — not a teaching scenario.

Audiences: practitioners in your field evaluating CaseHub, potential adopters, industry
partners. They need to see that CaseHub solves real compliance and coordination problems
they recognise from their own work.

**Secondary — Architectural documentation for understanding, evolution, and cross-domain reuse**

ARC42STORIES.MD, blog entries, and git history together form the
architectural record. Its primary documentation purpose is **understanding** — how the
system is structured and how its parts come together. This understanding is necessary
for humans and LLMs to refactor, improve, extend, and fix the system with confidence.

A further benefit: the patterns and architecture serve as a template for building CaseHub
harness applications in other domains. Not cloning this domain — an AML investigation
system or a clinical trial coordinator uses these architectural patterns (layer integration
sequence, CDI displacement, content-driven binding conditions) as a starting point for
their own implementation. The domain is different; the structural approach is reusable.

Spot tutorials and architectural highlights that explain specific techniques are extracted
from this record as separate artifacts — they are not the record itself.

**The constraint:** Do not design or architect for documentation. The record documents
what you built. Code that exists only to fill a documentation slot is wrong code.

**Domain entity discipline:** A domain entity is justified when it carries information or typed relationships the foundation primitives cannot represent — `ExternalActor` with trust dimensions, `ClinicalTrial` with protocol and IRB reference. These are permanent production types.

A domain entity is not justified when it duplicates a foundation primitive (`WorkItem`, `Commitment`, `CasePlanModel`) with only a few extra fields. At higher layers, the foundation primitive becomes the coordination record; a wrapper then sits alongside it as a redundant artifact. Carry domain-specific context in the primitive's `category`, `payload`, or scope, or wait until the domain design justifies a proper entity with genuine domain behaviour.

**The test:** if this entity could be removed at Layer 5 without losing domain-specific information that cannot be recovered from the foundation record, it is temporary scaffolding — do not create it. AML and devtown have no domain JPA entities; their domain concepts ARE cases and WorkItems.

**The production-first test — apply before writing any class:**
> "Would this class exist in a production system built to this layer and no further?"

If the answer is no, do not build it. Document the architecture in ARC42STORIES.MD instead.

**Anti-patterns that have appeared and are wrong:**

- **CDI priority gymnastics to let tutorial layers coexist.** Adding `@Alternative @Priority(N)`
  to a Layer 5 class so that a Layer 3 class (which never runs when Layer 5 is present) can
  also implement the same interface without causing `AmbiguousResolutionException`. If two
  implementations of the same port interface cannot coexist in a production deployment, only
  one of them is production code. The other is tutorial scaffolding.

- **`@Unremovable` on beans that Quarkus would legitimately optimize away.** If Quarkus bean
  removal wants to eliminate a bean because nothing injects it in production, that is a correct
  signal. Adding `@Unremovable` to override this signal is tutorial scaffolding disguised as
  configuration.

- **A separate service implementation per tutorial layer where the earlier layer is
  permanently dormant.** The `@DefaultBean` displacement pattern is production-valid — it
  provides a legitimate fallback when no other candidate is present. Displacement chains that
  require priority resolution (`@Alternative @Priority(N)` stacks) to let multiple
  non-`@DefaultBean` implementations coexist are not production patterns.

**What is acceptable:** The `@DefaultBean` on a baseline/fallback service, and a single
non-`@DefaultBean @ApplicationScoped` implementation that displaces it, is idiomatic Quarkus
CDI and production-valid. AML's Layer 1 → Layer 3 → Layer 5 chain works because at any given
maturity level there is exactly one non-`@DefaultBean` implementation in production. Two
non-`@DefaultBean` implementations of the same type in the same deployment is always a design
problem, not a CDI configuration problem.

---

## Build Order — Vertical Slice First

**The layer ordering in ARC42STORIES.MD §9.4 is for reading** — the sequence a developer
follows to understand the system. **Building follows vertical slices (Chapters):** identify a
Chapter (a user-visible capability), implement each layer it requires in turn, deliver
the Chapter end-to-end, then move to the next. Layers are the implementation unit;
Chapters are the planning and delivery unit.

Full guidance: `casehub/garden: docs/protocols/universal/vertical-slice-planning.md`

**ARC42STORIES.MD §9 structure:**
1. §9.2 Chapter Index at the top — what the system can DO at each milestone (the Vertical Slice Index)
2. §9.3 Chapter Entries — one per delivered capability, in delivery sequence
3. §9.4 Layer Entries — how each integration was built, with Chapter cross-references

**Retrospective note.** Devtown, AML, and clinical were built without Chapter planning.
The §9.2 Chapter Index should be added retrospectively (§9.4 Layer Entries do not need
rewriting — they map directly). Future work in all repos follows Chapter-first.

---

## What to Produce and Maintain

### ARC42STORIES.MD — the primary architectural record

One file at the workspace root. Follows the [Arc42Stories spec](arc42stories-spec.md) and the [CaseHub Application-tier profile](arc42stories-casehub-profile.md). This is the primary architectural record — the navigational hub for understanding what the system can do and how each integration was built. **A layer is not complete until its §9.4 Layer Entry is fully written — but entries are written incrementally, not all at once.**

**Chapters and layers are not the same thing.** Chapters (§9.3) organise work by delivery — what the system can do after each milestone. Layers (§9.4) organise knowledge by reading progression — the sequence in which a developer encounters the architecture to understand it. One layer may span several Chapters. Do not wait for a layer to be fully built before starting its entry — write what is known, mark pending sections with `🔲`, and let future sessions fill them in.

Layer entries in §9.4 are ordered for learning, not for chronology. Git history captures chronology; §9.4 captures the architectural layer progression.

Each §9.4 Layer Entry captures:
- What was built and what gap it closes
- Accountability gaps this layer closes
- Key wiring (the non-obvious configuration — not in the code, not in the docs)
- Gotchas (what went wrong, what would go wrong without prior knowledge)
- Pattern to replicate — domain-agnostic numbered steps an LLM can follow in a different domain
- Cross-references to commits, blog entries, issues, and design specs

See the full §9.4 Layer Entry format in `docs/arc42stories-spec.md §9.4`.

**Repos not yet migrated from LAYER-LOG.md** continue using LAYER-LOG.md until migration is complete — see [Migration](#migration-layer-log-to-arc42storiesmd) below.

---

## The Design System

Every harness application maintains two permanent documents and one ephemeral working doc:

| Document | What it captures | Granularity | Lives in |
|---|---|---|---|
| `ARC42STORIES.MD` | Primary architectural record — §9.2 Chapter Index, §9.3 Chapter Entries, §9.4 Layer Entries, §10 cross-cutting decisions | Application lifetime | workspace root |
| `design/JOURNAL.md` | Per-epic working doc — in-session design reasoning; ephemeral | Per epic | workspace `design/` |

**The flow at epic close:**
1. `design/JOURNAL.md` → distil what-was-built into §9.3 Chapter Entry and §9.4 Layer Entry
2. `design/JOURNAL.md` → distil cross-cutting architectural decisions into §10
3. Each §9.4 Layer Entry cross-references the relevant §10 decision for the *why*

**What goes where:**
- "We built `QhorusAmlInvestigator` to dispatch typed COMMANDs" → §9.4 Layer Entry
- "Why we put `SlaBreachPolicy` in `work-api` instead of `platform-api`" → §10
- "Session reasoning on whether to use `@DefaultBean` or `@Alternative`" → JOURNAL.md (not preserved)

### Artifacts maintained per session

| Artifact | Purpose | Where |
|----------|---------|-------|
| `ARC42STORIES.MD` | Primary architecture record (§9 + §10) | workspace root |
| `design/JOURNAL.md` | Per-epic working doc — feeds ARC42STORIES.MD at close | workspace `design/` |
| Blog/diary entries | Narrative context per session | workspace `blog/` |
| `CLAUDE.md` | Session conventions, always current | project root |
| GitHub issues/epics | Work tracking | GitHub |
| ADRs | Significant architectural decisions requiring formal record | `docs/adr/` |

Blog entries complement ARC42STORIES.MD — narrative for humans; the architectural record is structured for LLMs. Both are needed.

---

## Retroactive Work

When starting a new session in an app that has existing code but no ARC42STORIES.MD (or one that needs its §9 populated):

### Step 1 — Establish what has been built

```bash
# Project repo git history
git log --oneline | head -40

# GitHub issues
gh issue list --state closed --repo casehubio/{app}
gh issue list --state open --repo casehubio/{app}
```

### Step 2 — Find blog and diary entries

Check in this order:
1. Workspace `blog/` directory — primary location
2. `~/claude/mdproctor.github.io/` — published notes (look for `notes-{app}.md`
   or dated entries referencing this app)
3. `~/mdproctor.github.io/` — secondary published location

**If entries are missing or you can't find enough to reconstruct a layer confidently —
stop and ask the user before writing the log.** Do not reconstruct from incomplete
information; gaps in the log are better than wrong entries.

### Step 3 — Map commits and entries to layers

Remember: epics and layers are different. One layer may span multiple epics. Organize
by layer (reading unit — architectural concern), not by epic (build unit).

For each layer that has any work done (see your repo deep-dive for the layer table):
- Which commits correspond to this layer?
- Is there a blog entry covering it?
- Is there a GitHub issue that was closed for it?
- What is still pending within this layer?

If the layer table shows all layers as "pending" but epics are closed, **the layer table
is wrong**. Update it: closed epics represent progress within a layer, even if the layer
is not fully complete.

### Step 4 — Populate ARC42STORIES.MD §9

If ARC42STORIES.MD already exists, populate the §9.2 Chapter Index and §9.4 Layer Entries. If it doesn't exist, create it using the CaseHub Application-tier preamble template from `docs/arc42stories-casehub-profile.md`, then populate §9.

One §9.4 Layer Entry per layer that has any work done — including in-progress layers. Use git history, blog entries, and issues as source material. Mark sections that cannot yet be written with `🔲` — include the expected content or pointer so future sessions can fill them in without context reconstruction.

If the repo has an existing LAYER-LOG.md, use it as source material — the entry format maps directly to §9.4. See [Migration](#migration-layer-log-to-arc42storiesmd) below.

### Step 5 — Identify the current Chapter

From the layer table in your repo deep-dive: what is the next layer to complete?
Create a GitHub issue for it if none exists (check Epics for this layer first).

---

## Ongoing Maintenance (per layer)

ARC42STORIES.MD §9.4 has two triggers per layer:

- **When work begins:** start the §9.4 entry — add what is known, `🔲` the rest with context
- **When code ships:** fill the entry — complete all `🔲` sections, set **Completed** date

When a layer's code ships:

1. Fill all remaining `🔲` sections in the §9.4 Layer Entry before closing the issue
2. Add or update the §9.3 Chapter Entry for any Chapter that completes with this layer
3. The completed entries are part of the PR / commit, not a follow-up
4. Update your repo deep-dive in casehub-parent — change layer status from `pending`
   to `in progress` or `complete` (create issue on casehubio/parent if you cannot
   commit there directly)
5. Write a blog entry for the session
6. Check CLAUDE.md for drift

---

## Layer Structure Reference

Your layer structure is defined in two places:
- `docs/repos/{your-app}.md` in casehub-parent — Architecture layers table with status
- `docs/tutorial-strategy.md §{N}` in casehub-parent — layer objectives and code
  sketches per layer

**Reference implementation:** casehub-devtown `ARC42STORIES.MD` — see `docs/arc42stories-casehub-profile.md §Reference Implementations` for the current pointer.

---

## Agentic Harness Protocols

Before implementing any layer, read:

1. `casehub/garden: docs/protocols/universal/INDEX.md` in casehub/garden — universal Java/Quarkus conventions
2. `casehub/garden: docs/protocols/casehub/HARNESS-INDEX.md` in casehub/garden — CaseHub app conventions

Key protocols that apply immediately:
- `docs/arc42stories-spec.md` + `docs/arc42stories-casehub-profile.md` — ARC42STORIES.MD as definition of done
- Hexagonal module placement (pending — follow AML's pattern: `api/` JPA-free, `app/` owns use-case orchestration)
- casehub-work Hibernate scan packages (pending — see AML LAYER-LOG.md Layer 2 §Key wiring until AML migrates to ARC42STORIES.MD)

---

## Migration — LAYER-LOG to ARC42STORIES.MD

For repos still using LAYER-LOG.md and DESIGN.md, migrate when starting substantive new work in the repo. Do not migrate mid-epic.

### What maps where

| Old artifact | Maps to |
|---|---|
| LAYER-LOG.md Vertical Slice Index | ARC42STORIES.MD §9.2 Chapter Index |
| LAYER-LOG.md layer entries | ARC42STORIES.MD §9.4 Layer Entries (same fields; see format below) |
| DESIGN.md cross-cutting decisions | ARC42STORIES.MD §10 Architectural Decisions |
| `design/JOURNAL.md` | unchanged — still the per-epic working doc |

### Field mapping — LAYER-LOG entry → §9.4 Layer Entry

| LAYER-LOG field | §9.4 field |
|---|---|
| Summary | What it adds |
| Accountability gaps closed | Accountability gaps closed |
| Key wiring | Key wiring |
| Architectural decisions | Architectural decisions |
| Pattern introduced | Pattern introduced |
| Pattern anchor | Pattern anchor |
| Gotchas | Gotchas |
| Pattern to replicate | Pattern to replicate |
| Navigation / git log | Navigation |
| Key files | Key files |

The §9.4 format adds: **Participates in chapters**, **Key protocols**, **Design refs**, **Blog**, **Improvement refs**, **Completed**. Populate from LAYER-LOG cross-references and issue refs.

### Migration steps

1. Create `ARC42STORIES.MD` at workspace root using the Application-tier preamble template from `docs/arc42stories-casehub-profile.md`
2. Complete §1–§8 (§8 inherits from the profile; add project-specific anti-patterns inline)
3. Build §9.2 Chapter Index from the LAYER-LOG Vertical Slice Index (or reconstruct from git history if absent)
4. Convert each LAYER-LOG layer entry to a §9.4 Layer Entry using the field mapping above
5. Move cross-cutting decisions from DESIGN.md to §10
6. Delete or archive LAYER-LOG.md and DESIGN.md — add a one-line forwarding comment at their former location if needed: `# Archived — see ARC42STORIES.MD §9.4 and §10`
7. Update CLAUDE.md to reference ARC42STORIES.MD (coordinate with the mass CLAUDE.md update if in progress)
