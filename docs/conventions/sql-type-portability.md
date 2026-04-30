# Convention: SQL Type Portability

**Applies to:** All modules with Flyway migrations  
**Severity:** Critical — wrong types fail silently on H2 but break production PostgreSQL deployments

## Rule

Use only standard ANSI SQL types in Flyway migration scripts. Never use H2-specific type aliases.

## Type Mapping

| Use this | Never use | Reason |
|---|---|---|
| `DOUBLE PRECISION` | `DOUBLE` | H2 accepts bare `DOUBLE`; PostgreSQL does not |
| `SMALLINT` | `TINYINT` | PostgreSQL has no `TINYINT`; H2 disallows it in PostgreSQL mode |
| `TIMESTAMP` | `DATETIME` | PostgreSQL uses `TIMESTAMP`; `DATETIME` is MySQL/H2-specific |
| `TEXT` | `CLOB`, `MEDIUMTEXT`, `LONGTEXT` | PostgreSQL uses `TEXT` for unbounded strings |
| `BYTEA` | `BINARY`, `VARBINARY`, `BLOB` | PostgreSQL uses `BYTEA` for binary data |

## Enforcement

All test datasources must include `MODE=PostgreSQL` in the H2 JDBC URL:

```properties
quarkus.datasource.jdbc.url=jdbc:h2:mem:testdb;MODE=PostgreSQL;DB_CLOSE_DELAY=-1
```

In PostgreSQL mode, H2 rejects non-standard types at test time, converting a silent production failure into an immediate build failure.

## Why H2 alone is not enough

H2 is designed for developer convenience and accepts many non-standard type aliases. A migration that passes H2 with no error can still fail on PostgreSQL at deployment time. The type compatibility issue is silent — no warning, no deprecation notice, just a `PSQLException` in production.

## Discovered in

`casehub-work` V13, `casehub-ledger` V1000–V1002: bare `DOUBLE` columns failed with `PSQLException: type "double" does not exist` on first PostgreSQL deployment. Fixed in casehub-work#146 and casehub-ledger#66.
