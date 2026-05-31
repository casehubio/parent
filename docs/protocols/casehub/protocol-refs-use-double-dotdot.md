---
id: PP-20260531-proto-ref-depth
title: "Protocol refs from docs/protocols/casehub/ use ../../ to reach docs/ level"
type: rule
scope: platform
applies_to: "Any protocol file in docs/protocols/casehub/ with a refs: entry pointing to docs/repos/, PLATFORM.md, or repo-level docs"
severity: guidance
violation_hint: "refs: entry starting with ../repos/ or ../PLATFORM.md or ../casehub- — one level too shallow"
created: 2026-05-31
---

Protocol files live at `docs/protocols/casehub/`. To reach `docs/repos/<name>.md`,
the ref must be `../../repos/<name>.md`. To reach `PLATFORM.md`, use `../../PLATFORM.md`.
Using `../` alone resolves inside `docs/protocols/` which contains no repo docs.

Same-directory refs (other protocols in `docs/protocols/casehub/`) need no path prefix.

Cross-repo source code (files in other repos such as casehub-ledger) should use
absolute GitHub URLs rather than relative paths — relative paths are unresolvable
from the parent repo.

Add this to the doc-sync checklist: "Are all `refs:` entries in any protocols written
this session using `../../` from `docs/protocols/casehub/`?"
