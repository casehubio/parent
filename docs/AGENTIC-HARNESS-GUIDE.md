# Agentic Harness Guide

This document applies to every CaseHub application repo:
**casehub-aml, casehub-clinical, casehub-devtown, casehub-life, casehub-drafthouse, QuarkMind**

Read this at session start alongside your CLAUDE.md.

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

ARC42STORIES.MD, LAYER-LOG.md, blog entries, and git history together form the
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

If the answer is no, do not build it. Document the architecture in LAYER-LOG.md instead.

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

**The layer ordering in LAYER-LOG.md is for reading** — the sequence a developer
follows to understand the system. **Building follows vertical slices:** identify a
slice (a user-visible capability), implement each layer it requires in turn, deliver
the slice end-to-end, then move to the next slice. Layers are the implementation unit;
slices are the planning and delivery unit.

Full guidance, planning criteria, and LAYER-LOG.md structure:
`docs/protocols/universal/vertical-slice-planning.md`

**LAYER-LOG.md structure** (applies to all harness apps):
1. Vertical Slice Index at the top — what the system can DO at each milestone
2. Layer entries below — how each capability was built, with slice cross-references

**Retrospective note.** Devtown, AML, and clinical were built without slice planning.
Each repo has an open issue to add the Vertical Slice Index retrospectively (the layer
entries do not need rewriting). Future work in all repos follows vertical slice first.

---

## What to Produce and Maintain

### LAYER-LOG.md — the primary architectural record

One file at the project root. A structured record that grows across sessions as each
layer is built. This is the primary architectural record — the navigational hub for
understanding what the system can do and how each integration was built. **A layer is not
complete until its LAYER-LOG.md entry is fully written — but entries are written
incrementally, not all at once.**

**Epics and layers are not the same thing.** Epics organize work by build convenience.
Layers organize knowledge by reading progression — the sequence in which a developer
encounters the architecture to understand it. One layer may span several
epics. Do not wait for a layer to be fully built before starting its log entry — write
what is known, mark pending sections with `🔲`, and let future sessions fill them in.

The layers in the log are ordered for learning, not for chronology. When generating
tutorials or how-tos, the order can be adjusted for the audience. Git history captures
chronology; LAYER-LOG.md captures the architectural layer progression.

Each entry captures:
- What was built and what gap it closes
- The accountability gaps documented in LAYER-LOG.md that this layer closes
- Key wiring (the non-obvious configuration — not in the code, not in the docs)
- Gotchas (what went wrong, what would go wrong without prior knowledge)
- Pattern to replicate — domain-agnostic numbered steps an LLM can follow in a
  different domain
- Cross-references to commits, blog entries, issues, and design specs — so future
  sessions and future LLMs can find the source material without reconstructing it

See `docs/protocols/universal/layer-log.md` in casehub-parent for the full format
including placeholder guidance.
See `LAYER-LOG.md` in casehub-aml for a reference implementation (Layers 1 and 2).

**Augmented format — each completed layer entry must include:**

```markdown
### Summary
What foundation module was integrated and what it enables (1 paragraph).

### Accountability gaps closed
| Gap | What breaks without it | Closed by |
|-----|----------------------|-----------|
| No formal deadline | Compliance reviews sit indefinitely | casehub-work WorkItem SLA |

### Key wiring
Non-obvious configuration — not visible in code, not in official docs.

### Architectural decisions
Why this approach, tradeoffs considered, alternatives rejected.

### Pattern introduced
The key pattern this layer establishes (named, referenceable).

### Pattern anchor
1–2 key reference points: class name + method. Not a code listing — a pointer.

### Gotchas
What went wrong, what would go wrong without prior knowledge.

### Pattern to replicate
Domain-agnostic numbered steps an LLM can follow in a different domain.

### Navigation
`git log --grep="#N" --oneline`
```

The existing sections (key files, pattern to replicate) are kept — this is additive.

---

## The Three-Document Design System

Every harness application maintains three design documents that form an explicit chain.
Understanding the chain prevents duplication and drift:

| Document | What it captures | Granularity | Lives in |
|---|---|---|---|
| `LAYER-LOG.md` | **SIAL** — what the system CAN DO, organized by vertical slice + layer; navigational hub | Application lifetime | project repo |
| `DESIGN.md` | **Decision record** — cross-cutting architectural decisions distilled from epics; the *why* behind specific technical choices | Per decision | workspace |
| `design/JOURNAL.md` | **Working doc** — in-session design reasoning for the current epic; ephemeral | Per epic | workspace |

**The flow at epic close:**
1. `design/JOURNAL.md` → distil what-was-built into the LAYER-LOG layer entry
2. `design/JOURNAL.md` → distil cross-cutting architectural decisions into `DESIGN.md`
3. Each LAYER-LOG layer entry cross-references the relevant `DESIGN.md` section for the *why*
4. Each `DESIGN.md` entry references the LAYER-LOG layer that generated it

**What goes where:**
- "We built `QhorusAmlInvestigator` to dispatch typed COMMANDs" → LAYER-LOG layer entry
- "Why we put `SlaBreachPolicy` in `work-api` instead of `platform-api`" → DESIGN.md
- "Session reasoning on whether to use `@DefaultBean` or `@Alternative`" → JOURNAL.md (not preserved)

**What DESIGN.md is not:** it is not a design spec (that lives in `docs/specs/`), not an ADR (that lives in `docs/adr/`), and not a session narrative (that is `blog/`). It is the accumulated record of cross-cutting decisions that would otherwise be lost between epics.

### Existing habits to maintain

| Artifact | Purpose | Where |
|----------|---------|-------|
| `LAYER-LOG.md` | SIAL — slice index + layer entries (primary architecture record) | project repo |
| `DESIGN.md` | Cross-cutting decision record — feeds LAYER-LOG; distilled from JOURNAL | workspace |
| `design/JOURNAL.md` | Per-epic working doc — feeds DESIGN.md + LAYER-LOG at close | workspace |
| Blog/diary entries | Narrative context per session | workspace `blog/` |
| `CLAUDE.md` | Session conventions, always current | project root |
| GitHub issues/epics | Work tracking | GitHub |
| ADRs | Significant architectural decisions requiring formal record | `docs/adr/` |

Blog entries correlate with LAYER-LOG.md but serve a different purpose — narrative for
humans; the log is structured for LLMs. Both are needed.

---

## Retroactive Work

When starting a new session in an app that has existing code but no LAYER-LOG.md:

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

### Step 4 — Write LAYER-LOG.md entries

One entry per layer that has any work done — including in-progress layers. Use git
history, blog entries, and issues as source material. Mark sections that cannot yet
be written with `🔲` — include the expected content or pointer so future sessions
can fill them in without context reconstruction. See the protocol for placeholder
guidance: `docs/protocols/universal/layer-log.md`.

### Step 5 — Identify the current layer

From the layer table in your repo deep-dive: what is the next layer to complete?
Create a GitHub issue for it if none exists (check Epics for this layer first).

---

## Ongoing Maintenance (per layer)

LAYER-LOG.md has two triggers per layer:

- **When work begins:** start the entry — add what is known, `🔲` the rest with context
- **When code ships:** fill the entry — complete all `🔲` sections, set **Completed** date

When a layer's code ships:

1. Fill all remaining `🔲` sections in the LAYER-LOG.md entry before closing the issue
2. The completed entry is part of the PR / commit, not a follow-up
3. Update your repo deep-dive in casehub-parent — change layer status from `pending`
   to `in progress` or `complete` (create issue on casehubio/parent if you cannot
   commit there directly)
4. Write a blog entry for the session
5. Check CLAUDE.md for drift

---

## Layer Structure Reference

Your layer structure is defined in two places:
- `docs/repos/{your-app}.md` in casehub-parent — Architecture layers table with status
- `docs/tutorial-strategy.md §{N}` in casehub-parent — layer objectives and code
  sketches per layer

**Reference implementation:** casehub-aml — Layers 1 and 2 complete. Read
`LAYER-LOG.md` in casehub-aml before writing your own. The AML log is the pattern.

---

## Agentic Harness Protocols

Before implementing any layer, read:

1. `docs/protocols/universal/INDEX.md` in casehub-parent — universal Java/Quarkus conventions
2. `docs/protocols/casehub/HARNESS-INDEX.md` in casehub-parent — CaseHub app conventions

Key protocols that apply immediately:
- `layer-log.md` — LAYER-LOG.md as definition of done
- Hexagonal module placement (pending — follow AML's pattern: `api/` JPA-free, `app/` owns use-case orchestration)
- casehub-work Hibernate scan packages (pending — see AML LAYER-LOG.md Layer 2 §Key wiring)
