---
id: PP-20260521-f86f68
title: "Peer repo Claude sessions must file issues on parent — never commit directly"
type: rule
scope: platform
applies_to: "All casehub peer repo Claude sessions (engine, ledger, work, qhorus, clinical, devtown, aml, claudony)"
severity: important
refs:
  - CLAUDE.md
violation_hint: "Commits appearing on parent/main from a peer session's workspace branch; parent session needing to cherry-pick or apply changes that arrived without a parent issue"
created: 2026-05-21
---

Each casehub repo has its own Claude session and git identity. When a peer session discovers a change needed in another repo — protocol gaps, cross-repo dependency map updates, PLATFORM.md corrections — it files a GitHub issue on the target repo rather than committing directly. Direct cross-repo commits bypass branch scaffolding, skip the parent session's review, and create commits the target session cannot trace to a local issue. The one-way exception: the parent session may commit to `docs/protocols/` on behalf of all sessions, since parent owns the platform protocol layer.
