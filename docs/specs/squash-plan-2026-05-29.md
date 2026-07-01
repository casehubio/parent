# Squash Plan — upstream/main..HEAD — 2026-05-29

**Range:** `upstream/main..HEAD`  
**Working branch:** `squash/wip-main-20260529-015357`  
**Original:** 30 commits → **22 commits** — 8 absorbed (no content lost)

---

## Already Clean — 22 commits (no action needed)

All KEEP commits assessed. All have either issue references, introduce new protocol/document files, or represent substantive restructures (≥ 20 lines in a single file).

| SHA | Subject |
|-----|---------|
| `8acb1c3` | chore(#78): register all ecosystem repos across CI, docs, and peer lists |
| `58063fa` | docs: tighten production-first rule in harness guide and devtown Layer 3 note |
| `b323942` | docs(#200): register casehub-qhorus-connectors → casehub-connectors-core in dependency table |
| `9de025b` | docs: add vertical-slice build order guidance to AGENTIC-HARNESS-GUIDE |
| `96149bf` | docs: restructure tutorial-strategy with taxonomy, vertical slice planning, spot tutorials |
| `ef494ce` | docs: add vertical-slice-planning protocol and tighten harness guide reference |
| `65370d6` | docs: tie ARCHITECTURE.md to vertical slice planning; add arch cross-referencing to LAYER-LOG protocol |
| `780874b` | docs: name the SIAL pattern; document three-document design system |
| `78a107a` | docs: rewrite SIAL protocol — clean language, no accumulated patchwork |
| `85e351c` | protocol(PP-20260528-6b1d80): cross-foundation-bridge-module-placement |
| `6fc667f` | docs: sync platform deep-dives for recent implementation work |
| `404ca02` | docs(platform#27): CaseMemoryStore capability, casehub-neocortex-memory repo, build order, dep map |
| `8703bee` | docs: Arc42Stories spec and CaseHub profile |
| `b708f76` | protocol: add flyway-extension-migration-registration (PP-20260528-flyway-ext-reg) |
| `045e9fc` | protocol(PP-20260528-ac6d93): reactive-pg-devservices-test-profile |
| `59c3bdd` | protocol(PP-20260529-35f3bd, PP-20260529-5c883f): LLM-pass structural fallback + renderer cache key format dimension |
| `6c348e6` | docs(#83): sync quarkmind.md for IEM10 command extraction and generalised validation harness |
| `60b732d` | docs(#85): sync casehub-platform deep-dive for CaseMemoryStore (platform#27) |
| `7dd783d` | docs(#86): sync casehub-life.md — Layer 2 complete, domain model correction |
| `ea7244d` | docs(#87,#88): PLATFORM.md, casehub-engine.md, casehub-work.md, APPLICATIONS.md |
| `52d4208` | protocol(PP-20260529-eb19c3,PP-20260529-19711d): qhorus store seam rule + InMemory aggregate delegation rule |
| `5ece3b0` | docs(#91): arc42stories spec and guide in-progress batch |

---

## Action Group 1 — SIAL Protocol Development Arc (4 commits → 1)

**Final message:** `docs: rewrite SIAL protocol — clean language, dual-purpose framing, slice/layer correction, Vertical Slices`

*`e8b9249` and `69ec4fd` appear chronologically BEFORE `78a107a` — rebase todo reorders them to appear as `squash` after `78a107a`'s `pick` line. `9b1cfb6` appears naturally after.*

| Commit | Lines | Action | Curated result |
|--------|-------|--------|----------------|
| `78a107a` docs: rewrite SIAL protocol | 239 | ✅ KEEP | *(see Final message above)* |
| `e8b9249` docs: restore dual-purpose framing to SIAL protocol | 39 | 🔽 SQUASH ↑ | *(absorbed — restores framing content lost in earlier iteration; context reflected in Final message)* |
| `69ec4fd` docs: fix slice/layer relationship — layers implement, slices deliver | 25 | 🔽 SQUASH ↑ | *(absorbed — corrections to framing in same file as rewrite)* |
| `9b1cfb6` docs: add Vertical Slices to arch pattern list in SIAL protocol | 4 | 🔽 SQUASH ↑ | *(absorbed — 4 lines, same file, 2 min after rewrite; ⏱ temporal cluster confirmed)* |

> **Result:** 1 commit. Reordering required: `pick 78a107a` before `squash e8b9249`, `squash 69ec4fd`, `squash 9b1cfb6`.

---

## Action Group 2 — Arc42Stories Spec Development (6 commits → 1)

**Final message:** `docs: Arc42Stories spec and CaseHub profile — full template with C4 extensions, missing fields, project artifact schema`

*All 5 follow-on commits appear chronologically after `8703bee` — normal squash ordering.*

| Commit | Lines | Action | Curated result |
|--------|-------|--------|----------------|
| `8703bee` docs: Arc42Stories spec and CaseHub profile | 422 | ✅ KEEP | *(see Final message above)* |
| `68ccab5` docs: arc42stories — add missing fields, C4 Mermaid guidance, sequencing rationale placement | 57 | 🔽 SQUASH ↑ | *(absorbed — substantial additions to initial spec; context reflected in Final message)* |
| `3ef4b1d` docs: arc42stories — C4 extension views, ARC42STORIES.MD naming | 147 | 🔽 SQUASH ↑ | *(absorbed — C4 views and naming convention added to initial spec)* |
| `a9f325a` docs: arc42stories — add four missing layer entry sections | 29 | 🔽 SQUASH ↑ | *(absorbed — adds Key files, Architectural decisions, Pattern, Pattern anchor sections to template)* |
| `96f8312` docs: arc42stories — add Improvement refs to layer entry template | 1 | 🔽 SQUASH ↑ | *(absorbed — 1 line, no issue ref)* |
| `d354cb0` docs: arc42stories — project artifact schema | 55 | 🔽 SQUASH ↑ | *(absorbed — project artifact schema table; rationale in commit body preserved in group)* |

📝 `d354cb0` body: "PREFIX-NNN is the universal pattern for improvement log entries; the PREFIX is project-specific. CaseHub profile adds the concrete schema table with all CaseHub artifact types."

> **Result:** 1 commit covering the complete Arc42Stories initial specification.

---

## AFTER

```
30 commits (original)
-8 absorbed by squash
──────────────────────
22 commits — no content lost

Sample (most recent 10 — estimated pre-execution):
  5ece3b0  docs(#91): arc42stories spec and guide in-progress batch
  52d4208  protocol(PP-20260529-eb19c3,PP-20260529-19711d)
  ea7244d  docs(#87,#88): PLATFORM.md, casehub-engine.md...
  7dd783d  docs(#86): sync casehub-life.md
  60b732d  docs(#85): sync casehub-platform deep-dive
  6c348e6  docs(#83): sync quarkmind.md
  59c3bdd  protocol(PP-20260529-35f3bd, PP-20260529-5c883f)
  045e9fc  protocol(PP-20260528-ac6d93)
  b708f76  protocol: add flyway-extension-migration-registration
  <squashed arc42stories>  docs: Arc42Stories spec and CaseHub profile — full template...
```
