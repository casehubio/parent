# CaseHub Architecture Patterns

> **Supplement to PLATFORM.md.** This document names the architectural patterns in use across the platform, states the invariants that flow from each, and explains the rationale. It does not need to be read for every implementation decision — the Platform Coherence Protocol in PLATFORM.md covers that. This document is for understanding *why* the platform is shaped the way it is, and for making principled decisions about new modules, new repos, or structural changes.

---

## The Dependency Rule

The single most important architectural principle in CaseHub. Every structural decision in the platform is an expression of it:

> **Source code dependencies may only point inward. Domain logic never depends on infrastructure.**

In Maven module terms:
```
REST / UI / Deployment (outermost)
        ↓ depends on
Service / Application Logic
        ↓ depends on
SPI Interfaces  (ports)
        ↓ depends on
Domain Model  (innermost — zero infrastructure dependencies)
```

Adapters (JPA, Quarkus, REST) depend on SPIs. SPIs never depend on adapters. This is Clean Architecture's dependency rule expressed as the three-tier module convention.

**Enforced by:** `module-tier-structure.md` protocol — pure-Java SPI tier / core library (no JPA) / full Quarkus extension. SPI signatures must not expose infrastructure types (no `Uni<T>` in blocking SPIs, no JPA annotations in `api/`).

**Verified by:** `ArchitecturalExclusionTest` in `casehub-engine` prevents deprecated casehub-poc types from leaking into the engine.

**Violated by:** referencing a Panache entity from `api/`, putting `@ApplicationScoped` in a module that should be pure Java, or letting a domain event carry a JPA type. All of these invert the dependency direction.

---

## Architecture by Tier

### Foundation — Hexagonal Architecture (Ports and Adapters)

`casehub-ledger`, `casehub-work`, `casehub-connectors`, `casehub-qhorus`

The foundation tier is where Hexagonal Architecture is most explicitly applied. Each repo defines SPI interfaces (ports) in a pure-Java `api/` module, with multiple adapter implementations in separate modules.

**Ports (examples):**
- `EventLogRepository` — storage abstraction for the immutable audit log
- `CaseInstanceRepository` — case persistence port
- `WorkerProvisioner` / `ReactiveWorkerProvisioner` — worker lifecycle management
- `CaseChannelProvider` — external communication channel
- `Connector` — outbound message delivery (Slack, Teams, SMS, email)

**Adapters (examples):**
- `InMemoryEventLogRepository` — in-memory adapter for tests
- `JpaEventLogRepository` — Hibernate/Panache production adapter
- `MongoWorkItemStore` — MongoDB persistence for work items
- `SlackConnector`, `TeamsConnector`, `TwilioSmsConnector` — connector implementations

**Invariant:** The `api/` module compiles with no Quarkus, no JPA, no reactive types. Any class that imports `io.quarkus.*` or `jakarta.persistence.*` belongs in the extension module, not the SPI.

**Dual blocking/reactive SPI pairs:** Where both sync and async callers exist, the SPI is mirrored — `WorkerProvisioner` (blocking) + `ReactiveWorkerProvisioner` (`Uni<T>`). A reflection test (`spi-blocking-reactive-parity.md`) asserts the reactive SPI covers all blocking SPI methods.

---

### Orchestration — DDD + Event-Driven + Reactive

`casehub-engine`

The engine is where the domain model lives and where the most complexity is concentrated. Three patterns work together:

**Domain-Driven Design:**
- A rich domain model in `api/model/` — `CaseDefinition`, `Worker`, `Binding`, `Goal`, `Milestone`, `Capability`, `CaseStatus`
- Domain events as Java records — `PlanItemCompletedEvent`, `StageActivatedEvent`, `CaseLifecycleEvent`
- Aggregates with enforced state machines — `CaseStatus { RUNNING, WAITING, SUSPENDED, COMPLETED, FAULTED, CANCELLED }`
- No anemic domain model: state transitions are enforced by event handlers in `runtime/handler/`, not by setters

**Event-Driven Architecture:**
- Cross-aggregate communication via events only — no direct aggregate-to-aggregate calls
- Two event buses used together: CDI `Event<T>.fireAsync()` for CDI observers, Vert.x EventBus for performance-sensitive routing
- Consumers use `@ObservesAsync` (CDI) or `@ConsumeEvent` (Vert.x) — publishers are unaware of subscribers
- `CaseLedgerEventCapture` observes `CaseLifecycleEvent` asynchronously and writes immutable ledger entries

**Reactive (Smallrye Mutiny):**
- All I/O operations return `Uni<T>` — repository calls, scheduler submissions, SPI invocations
- Composition via `Uni.combine().all().unis()` for parallel calls (e.g., count + page in `CaseDefinitionService`)
- Reactive is the right choice here: cases are long-running, workers execute asynchronously, the scheduler fires independently. Non-blocking composition is a natural fit.

**Blackboard pattern (CMMN):**
- `casehub-engine/blackboard/` implements a CMMN plan model layer on top of the reactive core
- `BlackboardRegistry` maintains active case state in memory
- Stage lifecycle (Activated → Completed → Terminated) driven by blackboard events, not polling

---

### Integration — Adapter + CQRS-lite

`claudony`, `casehub-flow`

The integration tier connects the foundation and orchestration layers to external consumers (browser clients, REST callers, AI agents).

**CQRS-lite:**
- Write operations (commands) go through the engine — `CaseHubRuntime`, `WorkOrchestrator`
- Read operations (queries) can bypass the engine and read directly from persistence
- Command objects: `CreateWorkItemRequest`, `CompleteRequest`, `DelegateRequest`
- Query objects: `CaseLineageQuery`, `DeadLetterQuery`, audit trail queries
- Not full CQRS (no separate read store) — "lite" because the separation is at the service boundary, not at the data store level

**Adapter pattern:**
- `WorkItemLifecycleAdapter` translates work lifecycle events to engine events — bridging two domain models cleanly

---

### Cross-Cutting — Strategy, Registry, Interceptor, Observer, Factory

These patterns appear across all tiers.

**Strategy Pattern** — pluggable algorithms without changing client code:
- `WorkerSelectionStrategy` → `ClaimFirstStrategy`, `LeastLoadedStrategy`
- `InstanceAssignmentStrategy` → `RoundRobinAssignmentStrategy`, `ExplicitListAssignmentStrategy`
- `ContextDiffStrategy` → `JsonPatchContextDiffStrategy`, `NoOpContextDiffStrategy`
- `ActiveParticipationStrategy`, `ReactiveParticipationStrategy` in claudony

**Registry Pattern** — runtime discovery and lookup:
- `CaseDefinitionRegistry` — case definitions from YAML and CDI beans
- `ExpressionEngineRegistry` — pluggable expression engines (JQ, etc.)
- `BlackboardRegistry` — active case plan models
- `FilterEvaluatorRegistry`, `DynamicFilterRegistry` — work item filtering

**Factory Pattern (CDI @Produces)** — conditional construction based on config:
- `HolidayCalendarProducer` — returns `ICalHolidayCalendar` or `ConfigHolidayCalendar` based on config
- `LedgerPrivacyProducer`, `LedgerEntityManagerProducer`

**Interceptor Pattern** — cross-cutting concerns without modifying business logic:
- `@ProvenanceCapture` / `ProvenanceCaptureInterceptor` — wraps method execution to capture audit metadata
- `@Transactional` on event observers for atomic ledger writes

**Observer Pattern (CDI Events):**
- `@ObservesAsync` for ledger capture — non-blocking, does not hold up the publishing transaction
- Sync `@Observes` for routing decisions that need to run before the transaction commits

---

## Event Sourcing — Selective, Not Full

CaseHub uses event sourcing selectively, not as the primary state model.

**What is event-sourced:** the audit ledger — `CaseLedgerEntry` records are immutable, append-only, hash-chained (Merkle tree frontier). This provides tamper-evident history for compliance (EU AI Act Art.12, GDPR Art.17/22).

**What is not event-sourced:** case state. Current state is stored as JPA entities (`CaseInstanceRepository`) and queried directly. Rebuilding state from events on every read would be expensive given the complexity of the case model.

**The hybrid:** the event log gives you full auditability and replay capability. The entity store gives you queryable current state. This is the right tradeoff for a compliance-first platform where reads outnumber writes.

---

## What We Deliberately Did Not Choose

**Full event sourcing:** State reconstruction from events on every read is expensive at scale and adds complexity to queries. The ledger gives audit; entities give query. Both together cover the requirement.

**Separate read stores (full CQRS):** A separate read store (Elasticsearch, read-replica, materialised views) would add operational complexity that isn't justified by current query patterns. CQRS-lite at the service boundary gives the separation of concerns without the infrastructure cost.

---

## On Reactive Complexity

The reactive model (Mutiny `Uni<T>`/`Multi<T>`) is correct for the domain but carries real cognitive overhead. Every new feature requires reasoning about non-blocking composition, transaction boundaries, and CDI context propagation on async threads.

**Why we kept it:** Cases are long-running. Workers execute asynchronously and independently. The scheduler fires outside request threads. Non-blocking composition is natural here — blocking threads would waste resources waiting on async case state transitions.

**The alternative that would have been simpler:** Quarkus virtual threads (Project Loom). Virtual threads allow blocking code without blocking OS threads, which would have eliminated most of the `Uni<T>` composition complexity while preserving concurrency. This was not available at design time. It is worth evaluating for new modules where the reactive model is adding more friction than value.

---

## Blended Approach — What CaseHub Actually Uses

Pure pattern adherence is rare in production systems. CaseHub uses a deliberate blend across its tiers:

| Tier | Blend | Rationale |
|------|-------|-----------|
| Foundation | **Hexagonal + Clean** | Domain protected by SPI ports; dependency rule enforced by module structure |
| Orchestration (engine) | **Hexagonal + DDD + Event-Driven** | Rich domain with separate read/write paths; events as the only cross-aggregate channel |
| Integration | **Hexagonal + CQRS-lite** | Commands through engine (write port); queries bypass engine (read port) |
| Cross-cutting | **Strategy + Registry + Observer** | Pluggable algorithms, runtime discovery, decoupled notification |
| Application tier | **Hexagonal + Vertical Slices** | Domain capability organized by what the system can DO, layered on the horizontal foundation |

The recommended blend for a new AI platform starting today: **Hexagonal + Clean + Vertical Slices** — clean domain core, ports for all external concerns, and slices organised by business capability. CaseHub's foundation arrived at the first two organically; the application tier now uses vertical slices as the primary planning and delivery unit (see `docs/protocols/universal/vertical-slice-planning.md`).

---

## Architecture and AI Agents at Scale

CaseHub is infrastructure for multi-agent AI systems. The architectural choices above were not made in isolation from that context.

**Why the dependency rule matters for AI:** LLMs reasoning about code need stable, predictable structure. When infrastructure (JPA, Quarkus) leaks into the domain layer, an AI agent cannot safely modify business logic without risk of breaking infrastructure wiring. Clean boundaries make AI assistance safer and more accurate.

**Why event-driven matters for agents:** AI agents are inherently asynchronous — they run for unpredictable durations and produce results on their own timeline. An event-driven engine that coordinates agents via `WorkResult` events rather than synchronous calls naturally accommodates this. Polling-based or blocking orchestration would not scale to multi-agent cases.

**Why the SPI pattern matters for agent pluggability:** New agent types are adapters. They implement `WorkerProvisioner` and appear in the registry without touching the engine. The hexagonal architecture makes the platform open to new agent implementations by design.

**The LLM interface is an incoming adapter.** In hexagonal terms, when an LLM calls a tool or function — start a case, signal an event, query case state — that call arrives at an incoming adapter (the REST resource or a function-calling contract). The use case boundary is the port. This means LLM tool schemas are port contracts, not implementation details. Keeping them at the adapter boundary prevents LLM-specific concerns from leaking into the domain. A new LLM provider or a new tool protocol is a new adapter, not a domain change.

**Why immutable audit matters for compliance:** Regulated AI deployments (EU AI Act Art.12) require tamper-evident records of every agent decision and action. The append-only hash-chained ledger is not an afterthought — it is a first-class architectural constraint that shaped the event model throughout the platform.

---

## Vertical Slices in the Application Tier

The foundation tier (qhorus, ledger, work, engine) is organized horizontally by concern — each module owns one infrastructure capability. This was correct: the foundation needed to be fully understood before higher-level slice boundaries could be drawn.

The application tier (devtown, AML, clinical) is organized by vertical slice — each slice is a user-visible capability that cuts through whichever horizontal layers it needs. A slice is planned, built, and documented as a unit before the next slice begins.

**The planning protocol:** `docs/protocols/universal/vertical-slice-planning.md` — how to identify slices, order them, and structure LAYER-LOG.md around them.

**What LAYER-LOG.md documents:** each application maintains a LAYER-LOG.md with a Vertical Slice Index at the top (what the system can DO at each milestone, with architectural pattern cross-references) and detailed layer entries below (how each integration was built, with references to the relevant sections of this document, the applicable protocols, and the garden).

**Architectural pattern cross-referencing:** each vertical slice should identify which patterns from this document it demonstrates — Hexagonal (ports and adapters), Clean (dependency rule), DDD (domain events), Event-Driven (CDI async observers), CQRS-lite (command/query separation), or cross-cutting (Strategy, Registry, Observer). This makes LAYER-LOG.md a navigational hub: a reader can enter from the capability (slice) and find both the implementation record and the architectural rationale in one place.

**The risk to avoid:** wrong slice boundaries scatter a single concept across multiple codebases and are harder to fix than horizontal layers. Identify slices by user-visible capability, not by implementation convenience. The seams the architecture already exposes — SPI ports, event model, ledger subjects — are natural slice boundaries.
