---
id: PP-20260512-module-tiers
title: "Three-tier module structure — pure-Java SPI, core library, full extension"
type: rule
scope: universal
applies_to: "All casehubio multi-module repos"
severity: critical
refs: []
violation_hint: "Adding Quarkus/JPA to an api/ module forces all consumers to configure a datasource or pull in Quarkus — even if they only need the SPI"
created: 2026-05-12
---

# Protocol: Three-Tier Module Structure

**Applies to:** All casehubio multi-module repos  
**Severity:** Required — violations cause cascading datasource failures or force heavy transitive dependencies on lightweight consumers

## The Three Tiers

### Tier 1 — Pure-Java SPI modules (`api/`)

**No Quarkus. No CDI. No JPA. No heavy external SDK types in method signatures.**

Just Java interfaces, records, enums, and POJOs. Any Java application — with or without Quarkus — can consume this tier. The `api/` module is the contract; nothing about the implementation leaks into it.

```
casehub-work-api/      ← Tier 1: WorkItem, WorkItemStore SPI, no Quarkus
casehub-engine-api/    ← Tier 1: CasePlanModel, Binding, WorkerProvisioner SPI
casehub-ledger-api/    ← Tier 1: LedgerEntry type, LedgerEntryType enum
```

**SDK types in SPI signatures:** Do not expose types from heavy external SDKs
(e.g. `io.serverlessworkflow.*`, `io.vertx.*`, `jakarta.persistence.*`) in `api/`
or shared SPI module method signatures. If the SPI must reference an external type,
introduce an abstraction or move the SPI to the tier that already depends on that SDK.

*This session: `WorkflowExecutor` in `casehub-engine-common` referenced
`io.serverlessworkflow.api.types.Workflow` and `WorkflowModel` — causing
compilation failures because engine-common lacked the SDK dependency. Fix:
added the SDK deps to engine-common. Better long-term: abstract the SPI to
avoid leaking the SDK type, or move it to the `engine/` runtime tier.*

### Tier 2 — Core library modules (`common/`, `core/`)

**May have Quarkus and CDI. No JPA.**

Shared utilities, helper beans, and internal types that multiple submodules within the same repo consume. Can use CDI annotations (`@ApplicationScoped`, `@Inject`) but must not pull in JPA — no `@Entity`, no Flyway migrations, no datasource requirement.

```
casehub-engine-common/  ← Tier 2: shared event types, WorkflowExecutor interface
casehub-work-core/      ← Tier 2: WorkBroker, WorkerSelectionStrategy (no JPA)
```

**Why no JPA:** any consumer of a Tier 2 module that doesn't itself use JPA would be
forced to configure a datasource, breaking non-JPA test modules.

### Tier 3 — Full extension runtime modules (`runtime/`, `engine/`, `app/`)

**Quarkus, CDI, JPA, Flyway — everything.**

The working implementation. Flyway migrations, JPA entities, REST resources, CDI producers, Quarkus configuration mappings all live here.

```
casehub-work/           ← Tier 3: WorkItem entity, Flyway V1–V999, REST API
casehub-engine/engine/  ← Tier 3: CaseInstance JPA, WorkOrchestrator CDI bean
```

## Dependency Direction

```
Tier 3 (runtime) → Tier 2 (common) → Tier 1 (api)
```

Never the reverse. Tier 1 must not depend on Tier 2 or 3.

## The Persistence Module Split Rule

**Rule:** JPA entity classes must live in a separate module from the domain model SPI. Any artifact that bundles JPA entities forces every downstream consumer to configure a datasource — including test modules that use in-memory repos.

**Correct split:**
- `<name>-api` — domain POJOs and SPIs, zero JPA (Tier 1)
- `<name>` or `<name>-runtime` — JPA entities and Flyway migrations (Tier 3)

**Canonical example:** `casehub-work-api` is JPA-free. `casehub-engine` consumes it to get `WorkBroker` and `WorkerSelectionStrategy` SPI. If `casehub-work-api` contained JPA entities, every engine test would need a datasource configured — even tests that use only the in-memory WorkBroker.

Violating this rule causes cascading datasource failures across all downstream test suites.

## The Store SPI Pattern — How to Make a Domain Model Persistent

When a domain model needs pluggable persistence (JPA, MongoDB, in-memory, Redis), follow the **Store SPI pattern**. This is the standard mechanism across all casehubio repos.

**Module layout:**

| Module | Contains | When |
|--------|---------|------|
| `api/` | Store SPI interface, domain POJOs — no JPA | Always |
| `runtime/` | Default JPA/Panache impl, Flyway migrations, REST API | Always — the Tier 3 default |
| `persistence-memory/` | `@Alternative @Priority(1)` in-memory impl — no datasource | Required for every module with a Store SPI |
| `persistence-<backend>/` | MongoDB, Redis, JDBC alternatives | When an alternative backend is provided |
| `testing/` | Test utilities, base classes, fixtures — **not persistence implementations** | As needed |

**Canonical example per module:**

| Artifact | Module | Notes |
|----------|--------|-------|
| `WorkItemStore` interface | `api/` | Pure Java, Tier 1 |
| `JpaWorkItemStore` | `runtime/` | Default, included automatically |
| `InMemoryWorkItemStore` | **`persistence-memory/`** | Zero datasource — test AND ephemeral install |
| `MongoWorkItemStore` | `persistence-mongodb/` | Production alternative |

**Why `persistence-memory/` and not `testing/`:**
The in-memory implementation serves two purposes: (1) test isolation without a datasource, and (2) zero-config ephemeral installs for local evaluation. A module named `testing/` is unsuitable for purpose (2) — it signals a test-only dependency and may bundle test-framework artifacts. `persistence-memory/` is a legitimate production deployment target (data is volatile; restart means data loss, which is acceptable for evaluation and demo use cases). The `testing/` module may depend on `persistence-memory/` for convenience, but the implementations themselves belong in the persistence module.

**Rules:**
- The SPI interface is pure Java — no `@Entity`, no Panache, no JPA imports
- The default JPA implementation lives in `runtime/`; alternatives in their own `persistence-<backend>/` modules
- **`persistence-memory/` is mandatory** for every module with a Store SPI — it enables both test isolation and ephemeral installs
- `testing/` contains test utilities only — never persistence implementations
- SPI method signatures take domain POJOs, not JPA entity types
- **Dual-variant rule:** Ship both a blocking SPI and a reactive mirror (`Uni<>`) when the store is consumed from both contexts. See `casehub-qhorus` for the canonical dual-variant example.

**Nuance — when `persistence-memory/` is NOT required:**
For SPIs where a non-DB production alternative already exists (e.g. a file-based or
config-backed provider), the in-memory implementation may be genuinely test-only.

Example: `PreferenceProvider` in `casehub-platform`. The `config/` module provides a
file-based provider for the "no DB" case — so there is no production ephemeral use case
for in-memory preferences. Additionally, `PreferenceKey<T>` carries a `Function<String, T> parser`
that enables `MockPreferenceProvider.get()` to return typed values from config strings directly —
eliminating the need for a separate in-memory fixture entirely.

Contrast with `WorkItemStore`: work items are transactional state with no file-based alternative,
so `persistence-memory/` IS a production deployment target there.

**Decision guide:** ask "could someone reasonably deploy with in-memory persistence in production?"
If no (because a file/config alternative covers that scenario), the in-memory impl is test-only
and belongs in `testing/`. If yes, it belongs in `persistence-memory/`.

**Checklist when adding a new Store SPI:**

- [ ] SPI interface in the correct tier (Tier 1 `api/` or Tier 2 `common/` — no JPA)
- [ ] Default JPA impl in `runtime/`; JPA entities do not leak into the SPI module
- [ ] In-memory impl in **`persistence-memory/`** — not in `testing/` — activated via `@Alternative @Priority(1)`
- [ ] `testing/` module depends on `persistence-memory/` so existing test consumers are unaffected
- [ ] SPI method signatures use only domain POJOs, not JPA entity types
- [ ] If consumed from both blocking and reactive contexts: ship blocking + reactive (`Uni<>`) variants
- [ ] PLATFORM.md capability ownership table updated if this is a new platform capability

**Open issues (tracking adoption across the platform):**
- casehubio/work#191 — split InMemory stores from testing/ → persistence-memory/
- casehubio/ledger#91 — create persistence-memory/ (currently missing entirely)
- casehubio/qhorus#169 — split InMemory stores from testing/ → persistence-memory/
- casehubio/platform — `PreferenceProvider` intentionally has no `persistence-memory/` module:
  file-based `config/` module covers the non-DB scenario; typed parsing via `key.parse()` makes
  in-memory unnecessary for tests

## Checklist when adding a new SPI

- [ ] Does the SPI interface reference any external SDK types? If yes — can it be abstracted? If not — which tier owns that SDK?
- [ ] Is the SPI in the correct tier (`api/` = pure Java; `common/` = no JPA; `runtime/` = full)?
- [ ] Does adding the SPI to its module require a new transitive dependency on consumers that don't need it?
