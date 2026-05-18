---
id: PP-20260518-475994
title: "Epic close requires code merged to project main before EPIC-CLOSED.md or issue close"
type: rule
scope: platform
applies_to: "All casehub repos — project branch of every epic"
severity: important
refs:
  - docs/protocols/casehub/flyway-version-range-allocation.md
violation_hint: "EPIC-CLOSED.md present and GitHub issue closed, but git log main..<branch> --oneline shows commits. The fix was never merged."
created: 2026-05-18
---

Before marking an epic as closed — either by adding EPIC-CLOSED.md or closing the GitHub issue — every commit on the project epic branch must be reachable from `main`. Verify with `git log main..<branch> --oneline`; if any commits appear, the code has not been merged. Merge or cherry-pick the missing commits first, then close. Closing an issue without merging the code leaves the fix permanently on an orphaned branch where it will not appear in builds, will not be installed to `.m2`, and will be invisible to downstream repos. Discovery at a later session requires a branch hygiene scan.
