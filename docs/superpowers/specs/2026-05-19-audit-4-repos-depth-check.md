# Audit 4 — repos/ Depth Check Design Spec

**Date:** 2026-05-19
**Issue:** casehubio/parent#31
**Epic:** Hortora/spec#14 — Hortora project knowledge methodology

## Goal

Trim all 9 `docs/repos/*.md` files to family-awareness level. No class names, method
signatures, field names, or implementation detail. Each file should answer: what does
this repo own, what does it NOT do, and who depends on it?

## Depth Rubric

The single test per sentence: *does a reader need this to understand what the repo
is, what it owns, and what it does not do?*

| Keep (family level) | Remove (class level) |
|---|---|
| Domain concept names as abstractions (Channel, Message, CaseInstance) | Specific class names (ChannelGateway, LedgerWriteService) |
| Module names and tier (api / core / runtime) | Method names and signatures |
| What the repo does NOT do | Field names and implementation detail |
| Who consumes this repo and why | Internal state counts (e.g. "7 states: OPEN → FULFILLED...") |
| Dependency graph | MCP tool method lists |
| SPI names at abstract level | Bean annotations, query method names |

**Removed content is not lost** — it is redirected to `docs/DESIGN.md` in the repo
that owns it. Each trimmed section adds: `See docs/DESIGN.md for [detail type].`

## Order of Operations

### Step 1 — Create DESIGN.md stubs for repos that lack one

Four repos have no `docs/DESIGN.md`: connectors, devtown, aml, clinical. Create a
minimal stub in each before touching the corresponding `repos/` file, so trimming
has somewhere to point.

Commit each stub to its repo: `chore: add DESIGN.md stub — Refs casehubio/parent#31`

Do not populate the stubs during this audit — content comes from real work sessions.

### Step 2 — Trim each repos/ file

Work in violation-count order (heaviest first to establish the rubric, easiest last
as a consistency check):

1. `casehub-qhorus.md` (64 class-refs)
2. `casehub-engine.md` (54)
3. `casehub-ledger.md` (44)
4. `casehub-work.md` (42)
5. `claudony.md` (36)
6. `casehub-clinical.md` (10)
7. `casehub-aml.md` (5)
8. `casehub-devtown.md` (3)
9. `casehub-connectors.md` (2)

For each file:
1. Read the full file
2. Apply the depth rubric sentence by sentence
3. For each removed block: replace with `See docs/DESIGN.md for [detail type].`
4. Commit to casehub-parent: `docs(audit-4): trim <repo> to family-awareness level — Refs #31`

### Step 3 — Protocol/garden scan (final pass)

After all 9 files are trimmed, one pass across the removed content:

1. **Universal pattern check** — did anything removed encode a universal pattern worth
   capturing? If yes → forage CAPTURE (garden if universal, protocol index if project-scoped)

2. **Reformulation candidates** — do any protocols referenced in the repos/ files pass
   the reformulation test (strip project-specific names; is the result still true and
   useful elsewhere)? If yes → flag for Audit 5 (protocol classification sweep, spec#14)

This step is deliberately separate from the trimming pass. Mixing "is this class-level?"
with "is this universal?" makes each file review twice as complex.

## Acceptance Criteria

- All 9 `docs/repos/*.md` files contain no class names, method signatures, or
  implementation detail
- Every trimmed section has a `docs/DESIGN.md` reference
- `docs/DESIGN.md` stubs committed to connectors, devtown, aml, clinical
- Protocol/garden scan complete; any candidates flagged for Audit 5
- casehubio/parent#31 closed
