# Persistence Backend CDI Priority Ladder

**Applies to:** any casehubio module that ships a persistence SPI with multiple optional implementations

---

## The Pattern

CaseHub persistence backends activate by **classpath presence alone** — no consumer config, no feature flags. The three-tier CDI priority ladder makes this work:

| Tier | Annotation | When active | Purpose |
|------|-----------|-------------|---------|
| 0 — Zero-dep default | `@DefaultBean @ApplicationScoped` | Always, unless a higher tier is on classpath | No-op, in-memory, or mock; keeps the system functional with no external dependencies |
| 1 — Production default | `@ApplicationScoped` (no qualifier) | When the module is on classpath; beats `@DefaultBean` | Standard SQL/JPA implementation; requires a datasource |
| 2 — Override | `@Alternative @Priority(1)` (or higher N) | When the module is on classpath; beats all lower tiers | High-performance, specialized, or multi-tenant backend |

A consumer adds the backend as a `compile` or `runtime` dependency. CDI resolution picks the highest-priority bean automatically. The consumer never changes its injection point.

---

## Tier 0 — Zero-Dep Default (`@DefaultBean`)

The `@DefaultBean` must keep the system functional without any external state. Three variants:

- **No-op:** does nothing, returns empty/null. Safe when the capability is optional (`AgentStateStore`, `TrustImportService`, `CapabilityHealth`).
- **In-memory:** uses a `ConcurrentHashMap` or similar. Correct for ephemeral installs and `@QuarkusTest` isolation (`casehub-ledger-memory`, `InMemoryAgentStateStore`).
- **Mock / stub:** fixed return values for testing. Used by `MockPreferenceProvider`, `MockCurrentPrincipal`.

**Decision rule (from PLATFORM.md §SPI defaults):** can the system function correctly with an empty/no-op implementation? If yes → no-op. If no (e.g. a vocabulary registry that returns nothing causes routing to fail immediately) → populated default.

The `@DefaultBean` lives in the same pure-Java module as the SPI — never in a separate module that forces JPA or Quarkus onto consumers.

---

## Tier 1 — Production Default (`@ApplicationScoped`)

Standard JPA/SQL implementation. No qualifier needed — CDI resolves it over `@DefaultBean` automatically when it is visible on the classpath.

Place in a `persistence-jpa` or `runtime` module that declares the datasource dependency. Consumers add this module as a dependency to activate.

```java
// Tier 1 — beats @DefaultBean when this module is on classpath
@ApplicationScoped
public class JpaPreferenceProvider implements PreferenceProvider {
    // datasource-backed implementation
}
```

---

## Tier 2 — Override (`@Alternative @Priority(N)`)

Optional specialised backend that beats both lower tiers. Use for:
- Alternatives that do not fit the default SQL schema (MongoDB, Redis, Elasticsearch)
- Higher-performance in-memory impls for specific deployment profiles

`@Alternative` suppresses the bean unless activated. `@Priority(N)` activates it without a `beans.xml` declaration — classpath presence is sufficient in Quarkus.

```java
// Tier 2 — beats Tier 1 when this module is on classpath
@Alternative @Priority(1)
@ApplicationScoped
public class MongoDbPreferenceProvider implements PreferenceProvider {
    // no Flyway required — startup bean creates index
}
```

Multiple Tier-2 backends can coexist if they target different deployment profiles; whichever is on the classpath wins. If both are on the classpath, the higher `@Priority(N)` value wins.

---

## Reactive Bridge Variant

When a SPI has both a blocking and a reactive interface (`PlanItemStore` + `ReactivePlanItemStore`, `CaseMemoryStore` + `ReactiveCaseMemoryStore`):

| Role | Annotation | Behaviour |
|------|-----------|-----------|
| Blocking-to-reactive bridge | `@DefaultBean @ApplicationScoped` | Wraps any blocking `SPI` impl as `ReactiveSPI` using `Uni.createFrom().item(() -> ...)`. Always active — picks up whichever blocking impl CDI resolves |
| Native async adapter | `@Alternative @Priority(N)` | Beats bridge when present; calls the async API directly without blocking thread pool overhead |

The bridge means the reactive interface is always satisfied without requiring consumers to provide a native reactive impl. Native async adapters are opt-in performance improvements, not correctness requirements.

```java
// Bridge — always active, wraps whatever blocking impl CDI gives it
@DefaultBean @ApplicationScoped
public class BlockingToReactiveBridge implements ReactiveCaseMemoryStore {
    @Inject CaseMemoryStore blocking;
    public Uni<Memory> find(MemoryQuery q) {
        return Uni.createFrom().item(() -> blocking.find(q));
    }
}

// Native async — beats bridge when this module is on classpath
@Alternative @Priority(1)
@ApplicationScoped
public class MemoriCaseMemoryStore implements ReactiveCaseMemoryStore {
    // calls Memori REST API asynchronously
}
```

---

## Scope Rules (Maven)

The `@DefaultBean` mock module (`casehub-platform`, `casehub-eidos-memory`, `casehub-ledger-memory`) must be scoped correctly or augmentation fails:

| Consumer type | Correct scope | Reason |
|---|---|---|
| Library / Quarkus extension (no `<goal>build</goal>`) | `<scope>test</scope>` | Test-only activation is sufficient; `test` scope is invisible to production augmentation |
| Application module (has `<goal>build</goal>`) | `<scope>runtime</scope>` | Production augmentation validates CDI without test classpath — `test` scope makes `@DefaultBean` invisible, causing `UnsatisfiedResolutionException` |

**Symptom of wrong scope:** all `@QuarkusTest` tests pass, then augmentation fails ~20s later with `UnsatisfiedResolutionException` for the SPI type.

---

## Reference Implementations

| SPI | Tier 0 | Tier 1 | Tier 2 |
|-----|--------|--------|--------|
| `PreferenceProvider` | `MockPreferenceProvider @DefaultBean` (casehub-platform) | `JpaPreferenceProvider @ApplicationScoped` (casehub-platform-persistence-jpa) | `MongoDbPreferenceProvider @Alternative @Priority(1)` (casehub-platform-persistence-mongodb) |
| `CaseMemoryStore` | `NoOpCaseMemoryStore @DefaultBean` (casehub-platform) | — | Memori/Mem0/Graphiti adapters `@Alternative @Priority(N)` (casehub-platform submodules) |
| `ReactiveCaseMemoryStore` | `BlockingToReactiveBridge @DefaultBean` (casehub-platform) | — | Native async adapters `@Alternative @Priority(N)` |
| `AgentStateStore` | `NoOpAgentStateStore @DefaultBean` (casehub-eidos) | *(JPA impl deferred, eidos#7)* | `InMemoryAgentStateStore @Alternative @Priority(1)` (casehub-eidos-memory) |
| `TrustImportService` | `NoOpTrustImportService @DefaultBean` (casehub-ledger) | `JpaTrustImportService @Alternative` — **exception**: no `@Priority`; requires explicit `beans.xml` activation, not classpath presence (seed-if-absent semantics) | — |
| `PlanItemStore` | `@DefaultBean` no-op (casehub-engine blackboard) | `JpaPlanItemStore` (casehub-engine-work-adapter) | — |
| `ReactivePlanItemStore` | `@DefaultBean` no-op (casehub-engine blackboard) | `JpaReactivePlanItemStore` (casehub-engine-persistence-hibernate) | — |

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Placing `@DefaultBean` in a module that has JPA deps | Forces every consumer to configure a datasource even without persistence | Move `@DefaultBean` to the pure-Java SPI module or a zero-dep mock module |
| `@Alternative` without `@Priority` | Bean is silenced — `UnsatisfiedResolutionException` | Add `@Priority(N)` to activate without `beans.xml` |
| Two Tier-1 impls on classpath | `AmbiguousResolutionException` at startup | Ensure only one `@ApplicationScoped` impl of each SPI can appear simultaneously; use `@Alternative @Priority` for the second |
| Wrong Maven scope for `@DefaultBean` mock | See Scope Rules table above | Scope to `runtime` in application modules, `test` in library modules |
| Putting bridge in a different module from its SPI | Bridge cannot inject the blocking SPI without creating a circular dep | Bridge lives in the same module as the SPI |
