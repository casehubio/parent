---
id: PP-20260525-cd463f
title: "Do not use @Transactional at the application coordinator level when the method spans multiple datasources"
type: rule
scope: application
applies_to: "Any CaseHub application coordinator (AmlInvestigationCoordinator, ClinicalCoordinator, etc.) that delegates to services on more than one persistence unit"
severity: important
refs:
  - repos/casehub-aml.md
violation_hint: "QuarkusTest fails with 'Unable to acquire JDBC Connection [Exception in association of connection to existing transaction]' after adding @Transactional to a coordinator method — symptom looks like pool exhaustion but is actually XA enlistment failure"
created: 2026-05-25
---

Application coordinators in the CaseHub stack delegate to services backed by two persistence units — `default` (casehub-work) and `qhorus` (casehub-qhorus / casehub-ledger). Adding `@Transactional` at the coordinator level creates a JTA transaction that attempts to enlist both datasources as XA participants; H2 (used in @QuarkusTest) does not support this, and production PostgreSQL XA is fragile. Each service already owns its transaction boundary — `WorkItemService.create()` and `LedgerWriteService` are both individually `@Transactional`. If cross-datasource atomicity is ever required, use a saga/outbox pattern, not a coordinator-level annotation.
