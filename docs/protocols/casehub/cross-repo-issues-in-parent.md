---
id: PP-20260525-5b1efa
title: "Cross-repo tracking issues belong in casehubio/parent, not individual module repos"
type: rule
scope: platform
applies_to: "Any issue that spans or applies to multiple casehubio repos"
severity: guidance
refs: []
violation_hint: "A cross-repo tracking issue (e.g. 'apply X to all repos') is filed in casehubio/work or another module repo instead of casehubio/parent"
created: 2026-05-25
---

Issues that track work spanning multiple casehubio repos must be filed in `casehubio/parent` so the platform owner can triage and route them. Filing a cross-repo issue in an individual module repo (e.g. casehubio/work) makes it invisible to maintainers of other repos who have work to do — the parent repo is the shared inbox for platform-wide concerns. Individual module repos should only track issues scoped to that module; any issue with a "repos to review" list or cross-repo checklist belongs in parent.
