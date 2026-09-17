# Documentation Alignment Guide

> **Scope:** Per-repo documentation architecture — what goes where, how to align, how to audit
> **Audience:** Any Claude session working in a casehubio repo
> **Goal:** Platform coherence — parallel Claude sessions across repos share a consistent worldview

---

## Documentation Hierarchy

Every casehubio repo follows the same four-document structure. Each level owns its content and points down for detail — never duplicates.

```
Parent (PLATFORM.md, INDEX.md)              ← platform-wide boundaries, capability ownership
  └→ Per-repo CLAUDE.md                     ← thin index, build commands, repo-specific gotchas
       └→ Per-repo ARC42STORIES.md          ← architecture, module layers, design decisions
            └→ contributor-guide.md          ← implementation: SPIs, handlers, test patterns
            └→ consumer-guide.md            ← usage: modules, APIs, quick start
```

### What lives where

| Document | Purpose | Content | Must NOT contain |
|----------|---------|---------|-----------------|
| **CLAUDE.md** | Auto-loaded every session — operational index | Project type, work tracking, build commands, documentation index table, 5-10 critical silent-failure gotchas | Architecture, SPI docs, record fields, YAML schemas, per-feature design |
| **ARC42STORIES.md** | Architecture reference (workspace) | Solution strategy, module layers, design decisions, anti-patterns table, glossary | Implementation detail — point to contributor guide |
| **contributor-guide.md** | Implementation detail (project repo) | Module table, SPI placement/addition, CDI conventions, test patterns, handler wiring, persistence | Architecture rationale — point to ARC42STORIES |
| **consumer-guide.md** | Usage guide (project repo) | Modules to depend on, APIs, YAML schema, quick start | Internal implementation detail |

### Why this structure

- **CLAUDE.md** is auto-loaded into every session's context window. A 1400-line CLAUDE.md consumes context that could be used for reasoning. A 150-line index leaves room.
- **ARC42STORIES** follows the Arc42Stories spec — a standardised architecture doc format with RAG-friendly section headers.
- **Contributor/consumer guides** are audience-specific. A consumer doesn't need SPI wiring details; a contributor doesn't need API quick start.
- **RAG on demand.** The CLAUDE.md documentation index maps topics to specific sections. Claude reads the index (always loaded), then reads only the section it needs for the current task.

---

## Alignment Procedure

Run this procedure to bring any casehubio repo's documentation into alignment. Can be executed by a Claude session.

### Step 1 — Assess current state

Read the repo's CLAUDE.md. Classify its content:

| Category | Belongs in | Action |
|----------|-----------|--------|
| Project type, work tracking, routing | CLAUDE.md | Keep |
| Build commands, version properties | CLAUDE.md | Keep |
| Critical gotchas (silent failures) | CLAUDE.md | Keep |
| Module structure, module descriptions | contributor-guide.md | Move |
| SPI documentation, CDI conventions | contributor-guide.md | Move |
| Architecture patterns, design rationale | ARC42STORIES.md | Move |
| Record field listings, YAML schemas | contributor-guide.md or delete (derivable from code) | Move or remove |
| Per-feature implementation detail | contributor-guide.md or delete | Move or remove |
| EventLog metadata schemas, event type listings | Delete (derivable from code) | Remove |

### Step 2 — Write the thin CLAUDE.md

Target: ~100-150 lines. Required sections:

```markdown
# CLAUDE.md
**Name:** <repo-name>

## Project Type
## Work Tracking
## Routing
## Documentation Index          ← table mapping topics to doc + section
## Build & Test                 ← commands, version properties
## <Repo-Specific Section>      ← e.g., Generated YAML Records, No Migration Tooling
## Critical Gotchas             ← only silent-failure items (5-10 max)
## IntelliJ MCP Tools           ← if applicable
## Writing Style Guide          ← if applicable
```

The **Documentation Index** is the key section. It's a table with columns: Topic, Document, Section. Every topic a session might need should have a row pointing to the right place.

### Step 3 — Update or create ARC42STORIES.md

Location: workspace repo (`wksp/ARC42STORIES.md`). Follow the [arc42stories spec](../arc42stories-spec.md) and [casehub profile](../arc42stories-casehub-profile.md).

Minimum sections to fill from displaced CLAUDE.md content:
- **§4 Solution Strategy** — architectural patterns, key design decisions
- **§5 Building Block View** — module layers (brief, point to contributor guide for details)
- **§8 Crosscutting Concepts** — protocol references + anti-patterns table
- **§13 Glossary** — key terms

Each section should point to the contributor guide for implementation detail: "See `docs/guides/contributor-guide.md` §Section for implementation details."

### Step 4 — Update contributor-guide.md

Location: project repo (`docs/guides/contributor-guide.md`).

Ensure these sections exist (used as RAG targets from CLAUDE.md index):
- **Module Structure** — current module table, grouped logically
- **Internal Architecture** — handler wiring, execution paths
- **CDI Conventions** — `@DefaultBean`, injection rules, strategy resolver
- **SPI Architecture** — placement rules, how to add new SPIs
- **Test Conventions** — naming, event testing, index dependencies, test classpath
- **Dependencies** — cross-repo dependency table

Section headers must be RAG-friendly — match the kind of question Claude would ask.

### Step 5 — Audit

Verify:
1. Every topic in CLAUDE.md's Documentation Index points to a section that exists
2. ARC42STORIES pointers to contributor-guide sections resolve
3. No stale references (renamed modules, deleted classes, old package paths)
4. No duplicate content across the three docs
5. Build commands and version properties match the POM

---

## Critical Gotcha Criteria

Only items that cause **silent failures** belong in CLAUDE.md's Critical Gotchas section. The test: "If Claude doesn't know this, will the build fail silently, tests pass falsely, or data be corrupted without an error message?"

Examples that qualify:
- Injecting by concrete class instead of SPI interface → two stores, silent tenant mismatch
- Test named `*IT.java` → failsafe picks it up, `Tests run: 0` with no error
- `@ObservesAsync` in `@QuarkusTest` → observer silently never invoked
- Missing index-dependency → CDI bean silently not discovered

Examples that don't qualify (loud failures or reference material):
- How to add a new SPI → compilation error if wrong
- SPI placement rules → dependency cycle caught by Maven
- Worker model details → type errors at compile time

---

## Platform Coherence

This documentation architecture serves platform coherence:

1. **Consistent structure.** Every repo follows the same pattern. A Claude session moving from engine to work to ledger knows where to find things.
2. **Minimal context load.** CLAUDE.md is ~150 lines, not ~1400. The session has context budget for reasoning.
3. **RAG-friendly.** Section headers match questions. The index maps topics to locations. Claude reads what it needs, when it needs it.
4. **No duplication.** Each fact has one authoritative home. Updates happen in one place.
5. **Cross-repo awareness.** ARC42STORIES §3 (Context and Scope) declares boundaries and dependencies. PLATFORM.md is the canonical cross-repo map.

When starting a session in any repo, Claude reads CLAUDE.md (auto-loaded), sees the documentation index, and can RAG into the right section for the task at hand. A session in engine knows what work and ledger own because ARC42STORIES §3 declares the boundaries, and PLATFORM.md is the canonical source.
