---
id: PP-20260525-6442ba
title: "publish.yml must include repository_dispatch trigger for upstream-published events"
type: rule
scope: platform
applies_to: "Every casehubio repo with a publish.yml workflow"
severity: important
refs:
  - ../../new-repo-checklist.md
violation_hint: "A repo only rebuilds on direct push/PR but never when upstream dependencies publish new snapshots — stale artifacts accumulate silently"
created: 2026-05-25
---

Every casehubio repo's `publish.yml` workflow must declare `repository_dispatch: types: [upstream-published]` as a trigger alongside `push` and `pull_request`. Without it the repo never rebuilds when an upstream dependency publishes a new snapshot — only direct pushes trigger the build, causing silent accumulation of stale artifacts. The `Trigger downstream CI` step in upstream repos uses `gh api repos/casehubio/$repo/dispatches` with `GH_TOKEN: ${{ secrets.GH_PAT }}` (classic PAT required — `GITHUB_TOKEN` is repo-scoped and returns 403 on cross-repo dispatch). Omitting the trigger is the most commonly missed item when bootstrapping a new repo; `aml` was found violating this rule in 2026-05-25 (casehubio/aml#33).
