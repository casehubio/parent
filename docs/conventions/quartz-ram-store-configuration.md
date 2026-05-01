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
