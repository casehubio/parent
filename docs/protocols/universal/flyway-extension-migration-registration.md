---
id: PP-20260528-flyway-ext-reg
title: "Quarkus extensions must use repo-scoped Flyway migration paths and register SQL resources for native image"
type: rule
scope: universal
applies_to: "Any Quarkus extension in the casehubio ecosystem that ships Flyway migrations"
severity: high
refs:
  - PP-20260525-607b33 (flyway-repo-scoped-migration-path)
  - ../../PLATFORM.md (Implementation Protocols table)
violation_hint: "Version collisions when multiple casehubio modules share the default classpath:db/migration — consumer startup fails with 'Found more than one migration with version 1'"
created: 2026-05-28
---

## Rule

Quarkus extensions that ship Flyway migrations must implement both of the following:

### 1. Repo-scoped migration path (mandatory)

Migrations live at `src/main/resources/db/<repo>/migration/` and are served at
`classpath:db/<repo>/migration`. Never `classpath:db/migration` (the Quarkus default) —
that path is scanned transitively across all JARs on the classpath, causing version
collisions when multiple casehubio modules are co-deployed. See PP-20260525-607b33.

**casehub-work:** `classpath:db/work/migration`
**casehub-ledger:** `classpath:db/ledger/migration`
**casehub-qhorus:** `classpath:db/qhorus/migration` (target — see casehubio/qhorus)

### 2. NativeImageResourcePatternsBuildItem (mandatory)

The extension's **deployment module** must produce a `@BuildStep` registering SQL bytes
for native image inclusion:

```java
@BuildStep
NativeImageResourcePatternsBuildItem registerMigrationResources() {
    return NativeImageResourcePatternsBuildItem.builder()
            .includeGlob("db/<repo>/migration/*.sql")
            .build();
}
```

Without this, native image builds do not include the SQL files and migrations fail silently.

### 3. FlywayConfigurationCustomizer (optional — non-Quarkus environments only)

Extensions MAY implement `io.quarkus.flyway.FlywayConfigurationCustomizer` as an
`@ApplicationScoped` CDI bean that adds `classpath:db/<repo>/migration` to whatever
locations are configured. This ONLY works in non-Quarkus Flyway environments.

**Quarkus architectural constraint:** Quarkus pre-registers migration file lists at
BUILD TIME in `FlywayProcessor.build()` from `quarkus.flyway.locations`. At JVM runtime,
`QuarkusPathLocationScanner` serves migrations from that pre-registered list ONLY.
`FlywayConfigurationCustomizer.customize()` runs at startup and can add location strings
to `FluentConfiguration`, but `QuarkusPathLocationScanner` has no pre-registered files
for runtime-added locations and returns empty. The additions are silently ignored.

If implementing `FlywayConfigurationCustomizer`, also register it as unremovable via the
deployment processor to prevent Quarkus's unused-bean pruning:

```java
@BuildStep
AdditionalBeanBuildItem registerMigrationCustomizer() {
    return AdditionalBeanBuildItem.builder()
            .addBeanClasses("io.casehub.<repo>.runtime.flyway.<Repo>MigrationCustomizer")
            .setUnremovable()
            .build();
}
```

## Consumer requirements

Quarkus applications embedding this extension MUST configure migration paths explicitly
in their build-time (or test) `application.properties`:

```properties
# Required — no auto-registration exists for Quarkus consumers
quarkus.flyway.locations=classpath:db/work/migration
# Add additional paths as needed:
# quarkus.flyway.locations=classpath:db/work/migration,classpath:db/ledger/migration
```

This applies to both JVM and native image modes.

## Co-deployed extensions that do not self-register

Some extensions ship Flyway migrations but do **not** produce a `NativeImageResourcePatternsBuildItem`
in their deployment module. Any extension that co-deploys them in native mode must add an
additional `includeGlob` for those paths.

**Known gap: `casehub-ledger`** — `LedgerProcessor` does not self-register `db/ledger/migration/*.sql`.
Any extension co-deploying casehub-ledger must add the ledger glob alongside its own:

```java
@BuildStep
NativeImageResourcePatternsBuildItem registerMigrationResources() {
    return NativeImageResourcePatternsBuildItem.builder()
            .includeGlob("db/<repo>/migration/*.sql")     // own migrations
            .includeGlob("db/ledger/migration/*.sql")     // casehub-ledger (does not self-register)
            .build();
}
```

Without the ledger glob, ledger tables are absent in native builds and the failure is silent until
Flyway runs at startup. See GE-20260530-0dc6de (garden jvm domain).

## Reference implementation

casehub-work:
- `WorkItemsMigrationCustomizer` — `FlywayConfigurationCustomizer` (runtime module)
- `WorkItemsProcessor.registerMigrationResources()` — `NativeImageResourcePatternsBuildItem`
- `WorkItemsProcessor.registerMigrationCustomizer()` — `AdditionalBeanBuildItem.setUnremovable()`

casehub-qhorus (casehubio/qhorus#219):
- `QhorusProcessor.registerMigrationResources()` — two globs: `db/qhorus/migration/*.sql` + `db/ledger/migration/*.sql`
