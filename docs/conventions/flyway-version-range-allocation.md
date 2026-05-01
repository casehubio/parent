# Convention: Flyway Migration Version Range Allocation

**Applies to:** All casehub modules using Flyway  
**Severity:** Critical — overlapping ranges cause startup failures across modules

## Problem

Multiple optional modules in the same deployment each own a Flyway migration range. Overlap causes `FlywayException: Found more than one migration` at startup.

## Rule

Each module owns an exclusive thousand-block:

- V1–V999 — core runtime tables
- V2000–V2999 — queues / ledger integration module
- V3000–V3999 — notifications module
- V4000–V4999 — AI module
- New modules take the next free thousand block

## Example

Naming a migration in the notifications module:

```sql
-- V3001__add_notification_rule.sql
```
