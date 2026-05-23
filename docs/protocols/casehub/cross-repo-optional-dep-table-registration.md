---
id: PP-20260523-605b90
title: "Register optional cross-repo dependencies in both the build order and the dependency table"
type: rule
scope: platform
applies_to: "All casehubio repos when adding an optional cross-repo compile dependency"
severity: important
refs:
  - PLATFORM.md
violation_hint: "Dependency present in build-order comment with 'optionally' but no corresponding row in the Cross-Repo Dependency Map table"
created: 2026-05-23
---

When an optional cross-repo dependency is added, update two places in PLATFORM.md: the build-order comment (to ensure correct publish ordering) and the Cross-Repo Dependency Map table (to register the dep for impact analysis). The build-order comment serves CI; the dependency table serves propagation scans — a dep missing from the table is invisible when the artifact is renamed, removed, or its SPI is broken. The `Nature` column must indicate the dependency is optional and name its purpose (e.g. `optional capability probe — AgentDescriptor on Worker`).
