---
id: PP-20260604-820c35
title: "Every @QuarkusTest that starts an engine investigation must drain to 'completed' before returning"
type: rule
scope: application
applies_to: "Any casehub application @QuarkusTest that starts a case via AmlEngineCoordinator, CaseHubRuntime, or a REST endpoint backed by the engine"
severity: important
refs:
  - ledger-hash-chain-disabled-in-h2-tests.md
violation_hint: "Tests that assert partial progress (e.g. 'senior-analyst scheduled') and return early leave pending Quartz jobs; those jobs write to ledger concurrently with the next test's investigation, causing the Merkle frontier violation (see ledger-hash-chain-disabled-in-h2-tests) or poisoning the EntityManager so the next case startup returns 500"
created: 2026-06-04
---

An engine investigation spawns multiple asynchronous Quartz jobs (one per worker capability). If a test returns before those jobs complete, they overlap with the next test's investigation. Even with the hash chain disabled, an EntityManager left in a non-clean state by a partially-drained investigation can cause subsequent `startCase()` calls to fail. Every `@QuarkusTest` that starts an investigation must call a drain helper — polling `GET /api/layer6/investigations/{id}` until `status = "completed"` — before the test method returns. The `"completed"` status is set only when the sar-drafting WorkerDecisionEntry is written, confirming all Quartz jobs for that case have finished their ledger writes. Tests that assert partial progress (e.g. "senior analyst was scheduled") must still add the drain as a final step.
