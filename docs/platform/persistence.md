# Persistence

> **Scope:** Flyway migration conventions, datasource naming, migration path scoping
> **Audience:** All (platform + app builders)
> **Key repos:** casehub-ledger, casehub-work, casehub-qhorus, casehub-engine
> **Protocols:** [flyway-repo-scoped-migration-path](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/flyway-repo-scoped-migration-path.md), [flyway-migration-rules](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/flyway-migration-rules.md), [flyway-extension-migration-registration](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/flyway-extension-migration-registration.md)

## Flyway Migration Conventions

### Version Ranges

| Concern | Owner | Range | Location |
|---|---|---|---|
| Base ledger tables | `casehub-ledger` | V1000–V1007 | `classpath:db/ledger/migration` |
| WorkItem tables | `casehub-work` runtime | V1–V999 | `classpath:db/work/migration` |
| Qhorus tables | `casehub-qhorus` | V1–V14, V2000 | `classpath:db/qhorus/migration` |
| Engine tables | `casehub-engine` | — | Hibernate `drop-and-create` (no migrations yet) |
| Ledger subclass join tables | Each consumer | V2000+ | Consumer-owned Flyway path |

**Flyway numbering rule:** casehub-ledger owns V1000–V1007 at `classpath:db/ledger/migration`. Domain: V1–V999. Ledger subclass joins: V2000+ (provides safe buffer above the ledger base range). Qhorus reference: V1–V14 domain migrations, V2000 subclass join; next domain migration V15.

Consumers must add `classpath:db/ledger/migration` to their Flyway locations alongside their own path.

### Path Scoping Rule

**Every module must ship migrations under a repo-scoped path** — `db/<reponame>/migration/`, never the generic `db/migration/`.

**Why:** Flyway scans recursively. Subdirectories of `db/migration/` are visible to any datasource scanning the parent path. A migration at `db/migration/qhorus/V2000__*.sql` will be executed by **every** datasource pointing at `db/migration`, not just Qhorus.

**Example:**
```
✅ Correct:
  db/work/migration/V1__create_workitem.sql
  db/qhorus/migration/V1__create_channel.sql

❌ Wrong:
  db/migration/work/V1__create_workitem.sql   ← visible to all datasources
  db/migration/qhorus/V1__create_channel.sql  ← visible to all datasources
```

Consumers must configure `quarkus.flyway.locations=classpath:db/<repo>/migration` explicitly — Quarkus has no runtime auto-registration mechanism.

See protocol: [flyway-repo-scoped-migration-path](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/flyway-repo-scoped-migration-path.md)

### Extension Migration Registration

Extensions with a named datasource must scope migrations to `db/<module>/migration/` and configure Flyway locations explicitly.

Quarkus does not auto-discover Flyway migrations from classpath JARs at runtime. The consuming application must declare:

```properties
quarkus.flyway.locations=classpath:db/work/migration
```

For native builds, add `NativeImageResourcePatternsBuildItem` in the extension's deployment module:

```java
@BuildStep
NativeImageResourcePatternsBuildItem registerMigrations() {
    return NativeImageResourcePatternsBuildItem.builder()
        .includeGlob("db/work/migration/*.sql")
        .build();
}
```

See protocol: [flyway-extension-migration-registration](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/flyway-extension-migration-registration.md)

## Datasource Naming

### Named Datasources

| Module | Datasource name | Use case |
|---|---|---|
| `casehub-qhorus` | `qhorus` | Channel, message, commitment tables |
| `claudony` | `claudony` + `qhorus` | Separate persistence units |

**Named datasource rule:** Qhorus always runs on named `qhorus` datasource. Domain tables never mix with Qhorus tables.

### Default Datasource

All other modules (ledger, work, engine, platform) use the default datasource unless explicitly configured otherwise.

## Ledger Subclass Extension Pattern

Consumers extending `LedgerEntry` via JPA JOINED inheritance:

1. **Base table:** owned by `casehub-ledger` (V1000–V1007)
2. **Join table:** owned by consumer (V2000+ migration)
3. **Migration path:** consumer's own `db/<consumer>/migration/` path
4. **Domain-agnostic leaf hash:** subclass-specific fields are excluded from the Merkle hash

**Example:** Qhorus extends `LedgerEntry` with `MessageLedgerEntry`. Base table is `ledger_entry` (ledger V1000), join table is `message_ledger_entry` (qhorus V2000).

Consumers must configure Flyway to scan both paths:

```properties
quarkus.flyway.locations=classpath:db/ledger/migration,classpath:db/qhorus/migration
```

See protocol: [ledger-subclass-extension](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/ledger-subclass-extension.md) *(link placeholder — create when extracting from PLATFORM.md)*

## SQL Type Portability

Use portable SQL types across all migrations:

- `DOUBLE PRECISION` not `DOUBLE`
- `SMALLINT` not `TINYINT`

This ensures migrations work on PostgreSQL and H2 without modification.

## Test Database Configuration

### H2 Mode

All H2 test URLs must declare `MODE=PostgreSQL`:

```properties
quarkus.datasource.jdbc.url=jdbc:h2:mem:test;MODE=PostgreSQL
```

### Testcontainers for Dialect Validation

Use Testcontainers for integration tests that validate PostgreSQL-specific behaviour (full-text search, LISTEN/NOTIFY, JSON operators).

See protocol: [quarkus-test-database](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/quarkus-test-database.md) *(link placeholder)*

## Persistence Backend Patterns

### CDI Priority Ladder

Persistence backend activation follows a consistent CDI priority pattern:

1. `@DefaultBean` — no-op or mock implementation
2. `@ApplicationScoped` — default production backend (e.g. JPA)
3. `@Alternative @Priority(1)` — alternative backend (e.g. MongoDB, in-memory)

Backends activate by classpath presence. No consumer code changes required.

**Example:** `CaseMemoryStore`
- `NoOpCaseMemoryStore @DefaultBean` in `casehub-neocortex-memory`
- `JpaCaseMemoryStore @ApplicationScoped` in `memory-jpa/`
- `InMemoryCaseMemoryStore @Alternative @Priority(1)` in `memory-inmem/`

Add `memory-jpa` to activate JPA; add `memory-inmem` to use in-memory. The in-memory implementation beats JPA when both are on classpath.

See protocol: [persistence-backend-cdi-priority](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/persistence-backend-cdi-priority.md)

### Module Separation Rule

**JPA entities must not co-locate with domain SPIs** — forces all consumers to configure a datasource.

**Pattern:** Three-tier module structure:
1. **Pure-Java SPI** (no JPA, no Quarkus runtime) — `api/`
2. **Core library** (CDI + Mutiny, no JPA) — `runtime/`
3. **Full extension** (JPA entities, Flyway) — `persistence-jpa/`

Consumers needing only the SPI depend on `api/`. Consumers needing persistence activate it by adding `persistence-jpa` as a compile dependency.

See protocol: [module-tier-structure](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/module-tier-structure.md)

## Reactive Service Build Gating

Extensions providing reactive persistence services gate the reactive tier via build-time configuration:

```java
@BuildStep
@Record(ExecutionTime.STATIC_INIT)
void registerReactiveService(
    @IfBuildProperty(name = "casehub.<module>.reactive.enabled", stringValue = "true")
    BeanContainerListener beanContainerListener) {
    // ...
}
```

Default: `false`. Blocking-only consumers pay no Hibernate Reactive cost.

Every `Reactive*Service` must mirror its blocking counterpart. Write methods use `@WithTransaction`; no `withSafeContext` wrapper needed with Panache repos.

See protocol: [reactive-service-build-gating](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/reactive-service-build-gating.md)
