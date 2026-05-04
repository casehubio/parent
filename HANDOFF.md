# HANDOFF — Platform Positioning and Incremental Build
2026-05-04

## What changed this session

**Incremental full-stack build:** `scripts/incremental-build-decision.sh` (pure bash, no side effects) + 49-test bats suite. `incremental-full-stack-build.yml` workflow: SHA-keyed BUILD/TEST/SKIP per module, two-key cache (full key for SKIP, source key for TEST), failure-aware state persistence using `actions/cache/restore` + `actions/cache/save` separately.

**Gastown gap analysis revised:** Doltgres (PostgreSQL-compatible Dolt, Beta 2025) closes time-travel/branching/rollback gaps. Merkle MMR + Doltgres are complementary not competing. GDPR Art.17 erasure is the one genuine trade-off: PII persists in git history after row deletion. `docs/gastown-casehub-analysis-v2.md` updated throughout. P1.5 roadmap item added.

**Use case analysis:** `docs/use-case-analysis.md` — 10 candidates scored across Market Fit (/25) and Community Fit (/25) in separate tables. Selected: Clinical Trials (market entry, 24 market) + AML Investigation (Java tutorial, 22+22=44 all-rounder).

**Tutorial strategy:** `docs/tutorial-strategy.md` — layered module progression, AML as primary tutorial (Layer 1–7), clinical trials as market showcase. Key correction: LangChain4j patterns are NOT CaseHub patterns — they operate at the innermost agent reasoning layer. Three-sentence summary: "LangChain4j makes each agent smart. Quarkus Flow makes each step durable. CaseHub makes the investigation accountable."

**CLAUDE.md updated:** incremental-full-stack-build.yml added to CI/CD table; Scripts section added for `incremental-build-decision.sh` and bats tests.

## Current CI state

*Unchanged — `git show HEAD~1:HANDOFF.md`*

Work ❌ — `BusinessHoursIntegrationTest.createWithClaimDeadlineBusinessHours` fails Friday evenings. Fix: `isBefore(before.plus(3, DAYS))` at line 82.

Claudony ❌ — engine PR #224 added `UUID caseId` to `WorkerContextProvider.buildContext()`. Fix: update `ClaudonyWorkerContextProvider` signature to `buildContext(String workerId, UUID caseId, WorkRequest task)`.

## Immediate next action

Tell work Claude and claudony Claude the fixes above, then trigger `incremental-full-stack-build.yml` to verify full chain green.

## References

| Item | Location |
|---|---|
| Use case analysis | `docs/use-case-analysis.md` |
| Tutorial strategy | `docs/tutorial-strategy.md` |
| Gastown gap analysis | `docs/gastown-casehub-analysis-v2.md` |
| Incremental build workflow | `.github/workflows/incremental-full-stack-build.yml` |
| Decision script + tests | `scripts/incremental-build-decision.sh`, `scripts/tests/incremental-build-decision.bats` |
| Blog entry | `blog/2026-05-04-mdp01-platform-positioning-incremental-build.md` |
