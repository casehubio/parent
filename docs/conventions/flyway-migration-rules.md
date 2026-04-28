# Convention: Flyway Migration Rules

**Applies to:** All modules with Flyway migrations  
**Severity:** Build-breaking if violated — version collisions fail at startup

## Namespace Ranges

Each module owns a version range. Scripts outside the assigned range conflict with other modules.

| Module | Version range | Example |
|---|---|---|
| `quarkus-work` runtime | V1 – V999 | `V19__business_hours.sql` |
| `quarkus-work-ledger` | V1000 – V1999 | `V1000__ledger_base.sql` |
| `quarkus-work-queues` | V2000 – V2999 | `V2001__queue_membership.sql` |
| `quarkus-work-notifications` | V3000 – V3999 | `V3000__notification_rules.sql` |
| `quarkus-work-ai` | V14 (within core range — exception, pre-namespace) | — |
| Optional modules (new) | V4000+ | Claim next available block |

New optional modules must claim a block by adding to this table before writing migrations.

## SQL Type Rules

See [sql-type-portability.md](sql-type-portability.md). Summary: use only standard ANSI types.

## H2 Test Configuration

All H2 test datasources must run in PostgreSQL compatibility mode:

```properties
quarkus.datasource.jdbc.url=jdbc:h2:mem:<module-name>;MODE=PostgreSQL;DB_CLOSE_DELAY=-1
```

Use a unique database name per module (e.g. `testdb`, `reportstest`) to prevent cross-module state leakage when running tests across modules in the same JVM.

## PostgreSQL Dialect Testing

Every module with Flyway migrations should have at least one test that runs the migrations against a real PostgreSQL instance using Testcontainers. See `quarkus-work/quarkus-work-reports` for the reference implementation (`PostgresTestResource` + dedicated Surefire execution).

The PostgreSQL test must run **before** H2 tests in the Surefire execution order — Quarkus augmentation bakes the JDBC driver at build time, and the first execution wins.
