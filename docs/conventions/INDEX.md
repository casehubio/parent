# Cross-Module Implementation Conventions

One file per rule. Each file is self-contained and retrievable independently.

| File | Rule | Applies to |
|---|---|---|
| [sql-type-portability.md](sql-type-portability.md) | Use standard SQL types in all migrations | All modules with Flyway |
| [flyway-migration-rules.md](flyway-migration-rules.md) | Flyway namespace ranges, H2 mode, PostgreSQL testing | All modules with Flyway |
| [optional-module-pattern.md](optional-module-pattern.md) | Optional Jandex library module pattern | All optional feature modules |
| [quarkus-test-database.md](quarkus-test-database.md) | Database configuration for @QuarkusTest suites | All modules with @QuarkusTest |
