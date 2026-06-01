---
id: PP-20260601-90ace2
title: "Engine-ledger Flyway migrations that add columns to shared tables must use IF NOT EXISTS"
type: rule
scope: repo
applies_to: "casehub-engine-ledger — db/engine-ledger/migration/ — any migration adding columns to case_ledger_entry or worker_decision_entry"
severity: critical
refs:
  - flyway-ledger-migration-locations.md
  - ../../repos/casehub-engine.md
violation_hint: "Migration uses bare ADD COLUMN without IF NOT EXISTS — will fail in consumer repos that pre-added the column via their own migration"
created: 2026-06-01
---

Any `casehub-engine-ledger` Flyway migration that adds a column to a shared table (`case_ledger_entry`, `worker_decision_entry`) must use `ADD COLUMN IF NOT EXISTS` (not bare `ADD COLUMN`). Consumer repos such as `casehub-aml` may pre-add the same column via their own migrations before pulling the canonical engine-ledger migration. A bare `ADD COLUMN` would fail at deploy time in any consumer that already has the column. This rule applies to all column-adding statements in V2000+; use `CREATE TABLE` (not `CREATE TABLE IF NOT EXISTS`) only for the initial table creation where pre-existence would indicate a serious schema conflict. See V2002/V2003/V2004 for the reference pattern.
