---
id: PP-20260604-f45c95
title: "Disable Merkle hash chain in H2-backed @QuarkusTest suites"
type: rule
scope: application
applies_to: "Any casehub application @QuarkusTest suite that uses H2 as the test datasource and casehub-ledger JPA entities"
severity: important
refs:
  - ledger-test-profile-datasource.md
violation_hint: "UQ_MERKLE_FRONTIER_SUBJECT_LEVEL constraint violations under concurrent Quartz job execution; JTA rollback on qhorus datasource; subsequent case startups return 500 with 'CaseDefinition not found'"
created: 2026-06-04
---

H2 lacks PostgreSQL's row-level locking. When multiple Quartz workers run concurrently for the same investigation case (e.g. entity-resolution and pattern-analysis), both write a WorkerDecisionEntry that triggers a Merkle Mountain Range frontier update on the same subject_id + level. H2 raises UQ_MERKLE_FRONTIER_SUBJECT_LEVEL on the second write; the resulting JTA transaction rollback leaves the qhorus EntityManager in a poisoned state, corrupting subsequent case startups. Set `casehub.ledger.hash-chain.enabled=false` in the application's test `application.properties`. The hash chain is owned by casehub-ledger and tested there; consumer apps test that the correct entries are written with correct structure, not that the cryptographic chain is intact.
