# Pending Module CLAUDE.md Updates

Each entry below identifies a new platform convention and the module CLAUDE.md sections
that should later be replaced with a reference to the parent convention file.

## maven-module-scoping.md
- casehub/work/CLAUDE.md — "Build Discipline" section, bullet starting "Never run mvn..."
- casehub/work/CLAUDE.md — helper scripts section (`scripts/mvn-test`, `scripts/mvn-install`, etc.)
- casehub/engine/CLAUDE.md — any section describing Maven command discipline
- casehub/ledger/CLAUDE.md — any section describing Maven command discipline

## flyway-version-range-allocation.md
- casehub/work/CLAUDE.md — section describing V1–V999 migration range ownership
- casehub/ledger/CLAUDE.md — section describing V2000–V2999 migration range ownership
- casehub/connectors/CLAUDE.md — section describing module migration range ownership
- casehub/qhorus/CLAUDE.md — section describing module migration range ownership

## configmapping-javadoc-requirement.md
- casehub/work/CLAUDE.md — any note about `@ConfigMapping` Javadoc compile errors
- casehub/engine/CLAUDE.md — any note about `@ConfigMapping` Javadoc compile errors
- casehub/qhorus/CLAUDE.md — any note about `@ConfigMapping` Javadoc compile errors

## h2-reserved-word-columns.md
- casehub/work/CLAUDE.md — any note about H2-reserved column name failures in tests
- casehub/ledger/CLAUDE.md — any note about H2-reserved column name failures in tests
- casehub/connectors/CLAUDE.md — any note about H2-reserved column name failures in tests

## quarkus-integration-test-module-separation.md
- casehub/work/CLAUDE.md — section describing `integration-tests/` submodule layout
- casehub/engine/CLAUDE.md — section describing `integration-tests/` submodule layout
- casehub/qhorus/CLAUDE.md — section describing `integration-tests/` submodule layout

## quarkus-scheduled-interval-syntax.md
- casehub/work/CLAUDE.md — any note about `@Scheduled` `every` attribute `${}` syntax
- casehub/engine/CLAUDE.md — any note about `@Scheduled` `every` attribute `${}` syntax

## panache-find-whereclause-syntax.md
- casehub/work/CLAUDE.md — any note about Panache `find()` bare field name requirement
- casehub/ledger/CLAUDE.md — any note about Panache `find()` bare field name requirement
- casehub/engine/CLAUDE.md — any note about Panache `find()` bare field name requirement

## cdi-observesasync-transactional-delegation.md
- casehub/ledger/CLAUDE.md — section describing `@ObservesAsync` + `@Transactional` delegation pattern
- casehub/work/CLAUDE.md — any note about async observer transactional delegation

## cdi-fireasync-transaction-boundary.md
- casehub/work/CLAUDE.md — any note about `fireAsync()` dispatching before commit
- casehub/ledger/CLAUDE.md — any note about `fireAsync()` dispatching before commit
- casehub/engine/CLAUDE.md — any note about `fireAsync()` dispatching before commit

## quarkus-broadcastprocessor-backpressure.md
- casehub/work/CLAUDE.md — any note about `BroadcastProcessor.onNext()` throwing on no subscribers
- casehub/engine/CLAUDE.md — any note about `BroadcastProcessor.onNext()` throwing on no subscribers
- casehub/qhorus/CLAUDE.md — any note about `BroadcastProcessor.onNext()` throwing on no subscribers

## quartz-ram-store-configuration.md
- casehub/work/CLAUDE.md — any note about `quarkus.quartz.store-type=ram`
- casehub/engine/CLAUDE.md — any note about `quarkus.quartz.store-type=ram`
- casehub/claudony/CLAUDE.md — any note about `quarkus.quartz.store-type=ram`

## spi-testing-alternative-inner-classes.md
- casehub/work/CLAUDE.md — section describing `@Alternative` static inner class test doubles
- casehub/engine/CLAUDE.md — section describing `@Alternative` static inner class test doubles
- casehub/claudony/CLAUDE.md — section describing `@Alternative` static inner class test doubles

## quarkus-test-naming-convention.md
- casehub/work/CLAUDE.md — any note about `*IT.java` vs `*Test.java` naming
- casehub/ledger/CLAUDE.md — any note about `*IT.java` vs `*Test.java` naming
- casehub/engine/CLAUDE.md — any note about `*IT.java` vs `*Test.java` naming
- casehub/qhorus/CLAUDE.md — any note about `*IT.java` vs `*Test.java` naming

## quarkus-dev-mode-websocket-restart.md
- casehub/work/CLAUDE.md — any note about WebSocket hot-reload failure in dev mode
- casehub/qhorus/CLAUDE.md — any note about WebSocket hot-reload failure in dev mode
- casehub/claudony/CLAUDE.md — any note about WebSocket hot-reload failure in dev mode

## quarkus-test-stateful-bean-isolation.md
- casehub/work/CLAUDE.md — section describing stateful bean reset hooks between test classes
- casehub/engine/CLAUDE.md — section describing stateful bean reset hooks between test classes
- casehub/claudony/CLAUDE.md — section describing stateful bean reset hooks between test classes

## quarkus-reactive-datasource-h2-tests.md
- casehub/work/CLAUDE.md — any note about `%test.quarkus.datasource.reactive=false`
- casehub/ledger/CLAUDE.md — any note about `%test.quarkus.datasource.reactive=false`
- casehub/qhorus/CLAUDE.md — any note about `%test.quarkus.datasource.reactive=false`

## quarkus-conditional-bean-build-time-only.md
- casehub/qhorus/CLAUDE.md — section describing `@IfBuildProperty` build-time evaluation limitation
- casehub/work/CLAUDE.md — any note about `@IfBuildProperty` / `@UnlessBuildProperty` test profile limitations
- casehub/engine/CLAUDE.md — any note about `@IfBuildProperty` / `@UnlessBuildProperty` test profile limitations

## quarkus-named-datasource-schema-generation.md
- casehub/qhorus/CLAUDE.md — section describing named PU explicit schema generation config
- casehub/claudony/CLAUDE.md — any note about named persistence unit Flyway config

## git-worktree-absolute-path-maven.md
- casehub/work/CLAUDE.md — any note about absolute paths in worktree Maven commands
- casehub/qhorus/CLAUDE.md — any note about absolute paths in worktree Maven commands
- casehub/engine/CLAUDE.md — any note about absolute paths in worktree Maven commands
