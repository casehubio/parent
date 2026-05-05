# HANDOFF — Fork Consolidation and Garden
2026-05-05

## What changed this session

**Fork consolidation:** All casehubio repos now forked to mdproctor and cloned
to `~/claude/casehub/`. Newly added: `flow`, `connectors`, `assisteddev`.
All repos have `origin = mdproctor/<repo>` and `upstream = casehubio/<repo>`.

Repos NOT forked (deferred): `quarkus-langchain4j`, `demo-repository`.

**Garden:** GE-20260505-ea8485 submitted — `gh repo list --json parent` is
unreliable for fork detection; use `gh repo view` per-repo instead.

## Current CI state

*Unchanged — `git show HEAD~1:HANDOFF.md`*

Work ❌ — `BusinessHoursIntegrationTest.createWithClaimDeadlineBusinessHours` fails Friday evenings. Fix: `isBefore(before.plus(3, DAYS))` at line 82.

Claudony ❌ — engine PR #224 added `UUID caseId` to `WorkerContextProvider.buildContext()`. Fix: update `ClaudonyWorkerContextProvider` signature to `buildContext(String workerId, UUID caseId, WorkRequest task)`.

## Immediate next action

Verify the work and claudony fixes were applied, then trigger
`incremental-full-stack-build.yml` on `casehubio/parent` to confirm full
chain green.

## References

| Item | Location |
|---|---|
| Casehub local repos | `~/claude/casehub/` |
| Incremental build workflow | `.github/workflows/incremental-full-stack-build.yml` |
| Previous full handover | `git show HEAD~1:HANDOFF.md` |
