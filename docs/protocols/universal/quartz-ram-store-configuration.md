---
id: PP-20260508-6d1f5d
title: "Use Quartz RAM store — no JDBC store, no Quartz tables"
type: rule
scope: universal
applies_to: "All casehub modules using Quartz scheduling"
severity: important
refs: []
violation_hint: "JDBC store requires schema tables and a datasource; misconfiguration causes startup failure or stale job state"
created: 2026-05-08
---

# Convention: Use Quartz RAM Store — No JDBC Store, No Quartz Tables

**Applies to:** All casehub modules using Quartz scheduling  
**Severity:** Important — JDBC store requires schema tables and a datasource; RAM store is correct for stateless jobs

## Problem

Quartz defaults to JDBC store in some configurations, requiring schema setup. casehub modules use Quartz for triggering only, not for durable job persistence.

## Rule

Always configure Quartz with RAM store. Never add Quartz tables to Flyway migrations.

```properties
quarkus.quartz.store-type=ram
```
