# Cross-Module Implementation Conventions

One file per rule. Each file is self-contained and retrievable independently.

| File | Rule | Applies to |
|---|---|---|
| [sql-type-portability.md](sql-type-portability.md) | Use standard SQL types in all migrations | All modules with Flyway |
| [flyway-migration-rules.md](flyway-migration-rules.md) | Flyway namespace ranges, H2 mode, PostgreSQL testing | All modules with Flyway |
| [optional-module-pattern.md](optional-module-pattern.md) | Optional Jandex library module pattern | All optional feature modules |
| [quarkus-test-database.md](quarkus-test-database.md) | Database configuration for @QuarkusTest suites | All modules with @QuarkusTest |
| [atomic-threshold-counters.md](atomic-threshold-counters.md) | OCC + policyTriggered flag for M-of-N completion without pessimistic locking | Any module tracking aggregate completion thresholds |
| [cdi-alternative-stores.md](cdi-alternative-stores.md) | Panache statics bypass CDI alternatives — use store/service layer in tests | All modules with `@Alternative` InMemory stores |
| [scheduler-test-isolation.md](scheduler-test-isolation.md) | `@Scheduled` runs in its own transaction; use `@TestTransaction` and unique names | All modules with `@Scheduled` beans |
| [managed-executor-cdi.md](managed-executor-cdi.md) | Inject `ManagedExecutor` for CDI context propagation on background threads | All modules with concurrent test scenarios |
