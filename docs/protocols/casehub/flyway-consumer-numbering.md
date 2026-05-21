---
id: PP-20260521-659578
title: "Apps embedding casehub-work must start domain migrations at V100 or higher"
type: rule
scope: application
applies_to: "Any Quarkus app embedding casehub-work — clinical, aml, devtown, and any future harness"
severity: important
refs:
  - GE-20260511-a28064
  - docs/protocols/casehub/flyway-version-range-allocation.md
violation_hint: "V-number collision between casehub-work's V1–V21+ migrations and the app's own domain migrations. Symptom: Flyway reports duplicate version or applies wrong script — silent data corruption is possible."
created: 2026-05-21
---

Quarkus Flyway's `classpath:` location prefix uses `ClassLoader.getResources()` and scans all JARs on the classpath, including transitive dependencies. casehub-work ships migrations at `V1`–`V21+` (range still growing). An app that also starts its domain migrations at `V1` causes version collisions.

**Rule:** domain migrations in any app embedding casehub-work must start at **V100** or higher.

```
V1–V99      reserved — casehub-work domain tables (growing)
V100+       app domain migrations (clinical, aml, devtown, …)
V1000–V1003 reserved — casehub-ledger base tables
V1004+      consumer-owned ledger subclass join tables
```

**Current state:**

| Repo | Domain migration range | Status |
|------|----------------------|--------|
| casehub-clinical | V100–V105 | ✅ correct (as of 2026-05-11) |
| casehub-aml | none yet | ✅ no conflict yet — apply rule when first migration is added |
| casehub-devtown | TBD | ⚠️ verify before adding first migration |

**Root cause:** `WorkItemsProcessor.java` has a TODO for Flyway migration resource registration that is not yet implemented — consumers get no build-time warning about the collision.

**See also:** GE-20260511-a28064 — Quarkus Flyway classpath transitive scan gotcha.
