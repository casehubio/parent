# Platform Coherence Analysis — Design Spec
**Date:** 2026-05-23
**Issue:** casehubio/parent#4
**Branch:** issue-4-platform-coherence-audit

## Context

Issue #4 documented 32 cross-repo capability findings across the CaseHub platform. The top 8
findings each had GitHub issues created; 6 of those are now closed. This analysis covers the
remaining 23 findings (17 medium, 6 lower priority) that have no issues yet.

## Goal

For each remaining finding, produce three things in sequence:
1. **Verify** — confirm the gap still exists in current code
2. **Depth** — establish root cause, blast radius, and implementation guidance
3. **Issue** — file a GitHub issue in the appropriate repo

## Approach: theme-batched within priority tier

Findings are processed in priority order (medium before lower), but adjacent findings that share
a structural theme are batched together and worked as a group. This loads theme context once and
surfaces cross-finding relationships before any issues are filed.

## Batch Structure

### Medium Priority

| Batch | Theme | Findings | Repos |
|-------|-------|----------|-------|
| M1 | Worker selection intelligence | 2, 14, 15 | engine, work, work-ai, ledger |
| M2 | Audit trail documentation | 4, 6 | engine, work, ledger |
| M3 | Notification + signal silo | 8, 9, 24, 25 | qhorus, engine, work, connectors |
| M4 | Integration boundary semantics | 16, 17 | work, engine, qhorus |
| M5 | SpawnGroup / Stage gap | 20 | work, engine |
| M6 | Provenance + observability | 23, 29 | work, qhorus, engine |
| M7 | Architecture placement | 26 | claudony, engine |
| M8 | Normative enforcement | 30, 32 | qhorus, ledger, engine, work |

### Lower Priority

| Batch | Theme | Findings | Notes |
|-------|-------|----------|-------|
| L1 | Verification required | 5 | Uncertain — needs a test to confirm the bug exists |
| L2 | Documentation + patterns | 11, 12 | claudony auth gateway, @Alternative inversion |
| L3 | Structural debt | 13, 19, 27 | Cross-repo transactions, deadline duplication, inbound connector |

## Per-Finding Template

Each finding produces a section in `docs/audit/2026-05-23-coherence-analysis.md`:

```markdown
## Finding N — <title>

**Status:** Confirmed | Stale | Resolved
**Batch:** M1–M8 | L1–L3
**Repos:** <list>

### Verification
- **Code read:** <specific classes / interfaces / call sites examined>
- **Evidence:** <what the code shows>

### Root Cause
<Why the gap exists. One short paragraph.>

### Blast Radius
<What degrades or becomes impossible if left unaddressed.>

### Implementation Guidance
<Key classes/interfaces that change, direction of change, sequencing dependencies.>

### Scale / Complexity
**Scale:** XS | S | M | L | XL
**Complexity:** Low | Med | High

### Issue
<GitHub issue link, or `Resolved — no issue filed`>
```

## Verification Rules

1. Read code, not docs — verify against current source regardless of the audit description
2. Follow the call path — trace from emission to expected consumer for wiring gaps; confirm
   both structures exist in current code for structural gaps
3. Resolve uncertainty before filing — mark `Stale` with a note if ambiguous; file a narrower
   issue scoped to what's confirmed

## Issue Filing Rules

- Issues go in the repo where the fix lives, not where the gap is observed
- For multi-repo changes, file in the repo where the architectural decision lives
  (engine > work/qhorus/claudony for orchestration; qhorus > work for commitment/normative)
  and cross-reference the other repos in the issue body
- Root cause + blast radius go in the issue body; implementation guidance goes in
  `## Implementation notes`
- File the issue immediately after completing a finding's depth section — don't batch

## Output Artifacts

**Analysis doc:** `docs/audit/2026-05-23-coherence-analysis.md` in project repo
- Status table at top updated per completed batch
- Finding sections appended in batch order, never rewritten once committed

**Commit cadence:** one commit per completed batch
- Format: `audit(coherence): M1 worker-selection — findings 2, 14, 15`

**Session handoff:** JOURNAL.md records current batch and last finding completed;
HANDOFF.md records the analysis doc path for fast orientation next session.
