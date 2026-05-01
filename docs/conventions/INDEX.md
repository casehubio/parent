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
| [maven-module-scoping.md](maven-module-scoping.md) | Always specify `-pl <module>` when running Maven commands | All multi-module casehub modules |
| [flyway-version-range-allocation.md](flyway-version-range-allocation.md) | Each module owns an exclusive Flyway thousand-block version range | All casehub modules using Flyway |
| [configmapping-javadoc-requirement.md](configmapping-javadoc-requirement.md) | Every method in a `@ConfigMapping` interface must have Javadoc | All Quarkus extensions with @ConfigMapping |
| [h2-reserved-word-columns.md](h2-reserved-word-columns.md) | Avoid H2-reserved words as column names in Flyway migrations | All modules with Flyway migrations |
| [quarkus-integration-test-module-separation.md](quarkus-integration-test-module-separation.md) | `@QuarkusIntegrationTest` must live in a dedicated `integration-tests/` submodule | All Quarkus extensions with integration tests |
| [quarkus-scheduled-interval-syntax.md](quarkus-scheduled-interval-syntax.md) | `@Scheduled` interval must use `${property}s` syntax, not `{property}s` | All modules with @Scheduled beans |
| [panache-find-whereclause-syntax.md](panache-find-whereclause-syntax.md) | Panache `find()` WHERE clauses use bare field names, not alias-prefixed names | All modules using Panache |
| [quarkus-junit-not-junit5.md](quarkus-junit-not-junit5.md) | Use `quarkus-junit` dependency, not deprecated `quarkus-junit5` | All modules with @QuarkusTest classes |
| [cdi-observesasync-transactional-delegation.md](cdi-observesasync-transactional-delegation.md) | `@ObservesAsync` methods must delegate transactional logic to a separate bean | All modules with CDI async observers |
| [cdi-fireasync-transaction-boundary.md](cdi-fireasync-transaction-boundary.md) | `fireAsync()` inside `@Transactional` dispatches immediately, not at commit | All modules using CDI async events |
| [quarkus-broadcastprocessor-backpressure.md](quarkus-broadcastprocessor-backpressure.md) | `BroadcastProcessor.onNext()` throws on no subscribers — catch and discard | All modules using reactive broadcast streams |
| [quartz-ram-store-configuration.md](quartz-ram-store-configuration.md) | Use Quartz RAM store — no JDBC store, no Quartz tables | All modules using Quartz scheduling |
| [spi-testing-alternative-inner-classes.md](spi-testing-alternative-inner-classes.md) | Test SPI wiring with `@Alternative` static inner classes, not Mockito | All modules with CDI SPI implementations |
| [quarkus-test-naming-convention.md](quarkus-test-naming-convention.md) | `@QuarkusTest` classes must be named `*Test.java`, never `*IT.java` | All modules with @QuarkusTest classes |
| [quarkus-dev-mode-websocket-restart.md](quarkus-dev-mode-websocket-restart.md) | Quarkus dev mode hot-reload breaks WebSocket endpoint registration — full restart required | All modules with WebSocket endpoints |
| [quarkus-test-stateful-bean-isolation.md](quarkus-test-stateful-bean-isolation.md) | Stateful `@ApplicationScoped` beans don't reset between `@QuarkusTest` classes | All modules with stateful beans and multiple test classes |
| [quarkus-reactive-datasource-h2-tests.md](quarkus-reactive-datasource-h2-tests.md) | Disable reactive datasource in H2 tests when `hibernate-reactive-panache` is on classpath | All modules with transitive reactive panache dependency |
| [quarkus-conditional-bean-build-time-only.md](quarkus-conditional-bean-build-time-only.md) | `@IfBuildProperty` / `@UnlessBuildProperty` are evaluated at build time only | All modules using conditional bean activation |
| [quarkus-named-datasource-schema-generation.md](quarkus-named-datasource-schema-generation.md) | Named persistence units require explicit schema generation config | All modules with multiple named Hibernate ORM PUs |
| [git-worktree-absolute-path-maven.md](git-worktree-absolute-path-maven.md) | Use absolute paths when running Maven in git worktrees | All modules using git worktrees |
| [spi-blocking-reactive-parity.md](spi-blocking-reactive-parity.md) | Reflection test to assert reactive SPI covers all blocking SPI methods | All modules with blocking + reactive SPI pairs |
