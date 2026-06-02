---
id: PP-20260525-5b1efa
title: "casehubio/parent issues are for coordinating simultaneous execution across 2+ repos"
type: rule
scope: platform
applies_to: "Any issue requiring changes spanning multiple casehubio repos"
severity: guidance
refs: []
violation_hint: "Filing a new-SPI implementation issue in casehubio/parent because 'multiple repos will consume it' — the implementation work is in one repo; file there. Only use parent when the work across repos must execute simultaneously and a blocker/blocked-by chain between repo issues is insufficient."
created: 2026-05-25
---

casehubio/parent is the coordination inbox for work that requires simultaneous execution across two or more repos — where a blocker/blocked-by chain between individual repo issues is not sufficient because everything must land together. Artifact renames that must propagate atomically, BOM updates affecting all consumers, CI pipeline changes, and platform-wide protocol sweeps are parent issues. A new SPI in casehub-qhorus that consuming repos will later implement is NOT a parent issue — the implementation work is in qhorus, and consumers follow sequentially. File in parent only when the work itself cannot be sequenced across repos.
