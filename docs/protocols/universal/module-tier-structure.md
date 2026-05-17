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

**Structure:**

| Artifact | Tier | What it contains |
|----------|------|-----------------|
| `WorkItemStore` interface | Tier 1 (`api/`) | SPI: `put`, `get`, `scan` — no JPA annotations |
| `JpaWorkItemStore` | Tier 3 (`runtime/`) | Default blocking JPA/Panache implementation |
| `InMemoryWorkItemStore` | `testing/` module | `@Alternative @Priority(1)` in-memory test impl |
| `MongoWorkItemStore` | `persistence-mongodb/` | Alternative MongoDB implementation |

**Canonical example:** `casehub-work` — `WorkItemStore` SPI + JPA default + MongoDB alternative + in-memory test impl.

**Rules:**
- The SPI interface is pure Java — no `@Entity`, no Panache, no JPA imports
- The default JPA implementation lives in the Tier 3 runtime module; alternatives in their own modules
- The in-memory implementation lives in a `testing/` module and is activated via `@Alternative @Priority(1)`
- SPI method signatures take domain POJOs, not JPA entity types
- **Dual-variant rule:** Ship both a blocking SPI (`PlanItemStore`) and a reactive mirror (`ReactivePlanItemStore`, returning `Uni<>`) when the store is consumed from both blocking and reactive contexts. Method signatures are identical except for the return type wrapper. See `ledger-sync-async-parity.md` for the canonical example (`LedgerEntryRepository` + `ReactiveLedgerEntryRepository`).

**Checklist when adding a new Store SPI:**

- [ ] SPI interface in the correct tier (Tier 1 `api/` or Tier 2 `common/` — no JPA)
- [ ] Default JPA impl in the runtime module; JPA entities do not leak into the SPI module
- [ ] In-memory test impl in a `testing/` module — activated via `@Alternative @Priority(1)`
- [ ] SPI method signatures use only domain POJOs, not JPA entity types
- [ ] If consumed from both blocking and reactive contexts: ship blocking + reactive (`Uni<>`) variants
- [ ] PLATFORM.md capability ownership table updated if this is a new platform capability

## Checklist when adding a new SPI

- [ ] Does the SPI interface reference any external SDK types? If yes — can it be abstracted? If not — which tier owns that SDK?
- [ ] Is the SPI in the correct tier (`api/` = pure Java; `common/` = no JPA; `runtime/` = full)?
- [ ] Does adding the SPI to its module require a new transitive dependency on consumers that don't need it?
