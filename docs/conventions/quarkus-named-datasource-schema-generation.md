# Convention: Named Persistence Units Require Explicit Schema Generation Config

**Applies to:** All modules with multiple named Hibernate ORM persistence units  
**Severity:** Important — schema generation silently skipped for named PUs without explicit config

## Problem

`quarkus.hibernate-orm.database.generation` and `quarkus.flyway.migrate-at-start` apply to the default persistence unit only. Named persistence units (e.g. `qhorus`) need their own explicit configuration.

## Rule

For every named PU, replicate the schema generation and migration config under the named prefix:

```properties
# For a PU named "qhorus"
quarkus.hibernate-orm.qhorus.datasource=qhorus
quarkus.hibernate-orm.qhorus.database.generation=none
quarkus.flyway.qhorus.migrate-at-start=true
```
