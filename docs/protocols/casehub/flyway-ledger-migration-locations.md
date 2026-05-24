---
id: PP-20260524-10efef
title: "Include db/ledger/migration in Flyway locations for any module consuming casehub-ledger"
type: rule
scope: platform
applies_to: "Any module whose test classpath transitively includes casehub-ledger (directly or via casehub-work-ledger)"
severity: critical
refs:
  - ../repos/casehub-work.md
  - ../../PLATFORM.md
violation_hint: "Flyway startup fails with 'Table LEDGER_ENTRY not found' when running V2001+ migrations — the base ledger tables were never created because db/ledger/migration was not scanned"
created: 2026-05-24
---

Since casehub-ledger#95, base ledger migrations (ledger_entry, ledger_attestation, actor_trust_score tables) live at `classpath:db/ledger/migration`, not `classpath:db/migration`. Any module whose test classpath includes casehub-ledger must declare both locations in its test application.properties: `quarkus.flyway.locations=db/migration,db/ledger/migration`. Omitting the ledger path causes V2001+ subclass-join migrations to fail at Quarkus startup because the parent table does not exist. This applies to casehub-work-ledger consumers (including the examples module) and any future module that extends LedgerEntry.
