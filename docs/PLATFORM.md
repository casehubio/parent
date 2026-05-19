# Casehubio Platform Architecture

> **Purpose:** Before implementing *anything* in any casehubio repo, run the Platform Coherence Protocol below.
> Every implementation decision is a platform decision. A feature that seems local may duplicate something elsewhere,
> belong in a different repo, or open an opportunity to consolidate an existing abstraction.
>
> **Per-repo deep dives:** [docs/repos/](https://github.com/casehubio/parent/tree/main/docs/repos/)

> **Platform docs:** Paths are relative to this file's directory (`docs/`). Read them as `<repo-root>/docs/<path>`. If a path does not exist, that repo is not cloned locally — skip it gracefully and continue.

---

## Platform Coherence Protocol

Run this before implementing any feature, API, abstraction, SPI, or data model change in any casehubio repo. This is not a bureaucratic gate — it is the practice that keeps the platform orthogonal, intuitive, and free of duplication.

> **These protocols are living documents — never treat them as dogma.** If implementation reveals a gap or a rule that doesn't fit, update the protocol in the same session. A rule that doesn't adapt to new evidence is just friction.

The protocols index is at [`docs/protocols/INDEX.md`](protocols/INDEX.md). One file per rule, self-contained and retrievable independently. Add new entries there; link from PLATFORM.md when a capability ownership entry needs it.

### Step 1 — Does this already exist?

Check the Capability Ownership table below. Then check the per-repo deep-dive for the repos most likely to already have it.

Ask: *Is there a class, SPI, CDI event, or service in another repo that does this, or 90% of this?*

If yes → use the existing abstraction. If the existing one doesn't quite fit, extend it (in the right repo) rather than creating a parallel one here.

### Step 2 — Is this the right repo?

Check the Boundary Rules below. Then ask:

- Which tier does this belong to? (Foundation / Orchestration / Integration / Application)
- Is this domain-agnostic infrastructure (→ foundation), process coordination logic (→ casehub-engine), integration/deployment-specific (→ claudony), or domain-specific application logic (→ devtown / aml / clinical)?
- Will this be useful to consumers other than just the current one? If yes, it belongs lower in the stack.
- Does this depend on anything that the target repo is not supposed to depend on?

If the right repo is a different one → stop. Implement it there, then consume it from here.

### Step 3 — Does this create a consolidation opportunity?

Ask: *Is there something in another repo that does a similar thing awkwardly, that this new abstraction would make redundant or easier?*

If yes → propose refactoring the other repo to use the new abstraction, even if it's more work. Parallel implementations rot; consolidated abstractions improve everything downstream.

Known consolidation candidates:
- `casehub-work-notifications` Slack/Teams channels → should delegate to `casehub-connectors` (parent#5, open)
- `callerRef` format (`case:{id}/pi:{id}`) defined in casehub-engine but used opaquely by casehub-work → consider a shared constant or typed value in `casehub-work-api`

### Step 4 — Is this consistent with the platform pattern?

Check how the same concern is handled in the two or three most similar places in the platform. Then implement it the same way. Specifically:

- SPIs: follow the SPI placement rule (operational SPIs in `api/spi/`; persistence SPIs in model modules)
- Ledger subclasses: JOINED inheritance, consumer-owned V1004+ migration, domain-agnostic leaf hash. See [`docs/protocols/casehub/ledger-subclass-extension.md`](protocols/casehub/ledger-subclass-extension.md).
- CDI events: async (`@ObservesAsync`) for ledger capture; sync for routing decisions
- Named datasources: Qhorus always on `qhorus`, domain tables never mixed in
- Flyway numbering: V1000–V1003 = ledger; V1–V999 = domain; V1004+ = ledger subclass joins
- Module structure: three-tier rule — pure-Java SPI / core library (no JPA) / full extension. SPI method signatures must not expose heavy external SDK types. See [`docs/protocols/casehub/module-tier-structure.md`](/Users/mdproctor/claude/casehub/parent/docs/protocols/casehub/module-tier-structure.md).
- **Persistence module split:** JPA entities must not co-locate with domain SPIs — forces all consumers to configure a datasource. See [`docs/protocols/casehub/module-tier-structure.md`](protocols/casehub/module-tier-structure.md).
- No-op defaults: every SPI gets a default no-op implementation in the owning repo
- **Application tier rule:** domain logic (git, PRs, clinical protocols, AML investigations) belongs in application repos. Foundation repos must remain domain-agnostic. If it requires knowledge of a specific business domain, it does not belong in foundation.
- **Submodule folder naming:** short descriptive names — no repo prefix. `api` not `casehub-work-api`; `runtime` not `casehub-ledger-runtime`. See [`docs/protocols/universal/maven-submodule-folder-naming.md`](protocols/universal/maven-submodule-folder-naming.md).
- **Auth retrofit readiness:** RBAC is not yet implemented but must not be foreclosed. No auth or principal logic in domain or service layers. REST resources must stay thin enough for `@RolesAllowed`. Queries need a structurally injectable filter. SPI signatures must stay free of auth types. See [`docs/protocols/casehub/auth-retrofit-readiness.md`](protocols/casehub/auth-retrofit-readiness.md).
- **Case definition three-layer architecture:** YAML (classpath resource) → generated schema model (`io.casehub.model.*`) → canonical API model (`CaseDefinition`). Fluent DSL builders target the same canonical model and additionally support `LambdaExpressionEvaluator` (not expressible in YAML). All YAML definitions ⊂ fluent DSL; reverse is not true. Runtime: extend `YamlCaseHub`. Tests: build `CaseDefinition` directly via builders. Never bypass `CaseDefinitionYamlMapper`. Inherited from CNCF Serverless Workflow 1.0 / quarkus-flow. See [`docs/protocols/casehub/case-definition-layers.md`](protocols/casehub/case-definition-layers.md).

### Step 5 — Does this need a platform-level doc update?

If the capability ownership table, boundary rules, or deep-dive docs need updating after this implementation, update `casehub-parent/docs/PLATFORM.md` and/or the relevant `docs/repos/*.md` file.

Also ask: **did this session surface a non-obvious pattern, a corrected rule, or a gotcha?** If yes — add it to `docs/protocols/` now, before the session ends. Patterns worth capturing include:
- A solution that required research or multiple failed attempts to find
- A rule in this document that turned out to be wrong or too coarse (update it)
- A concurrency, boundary, or schema decision that would otherwise be re-discovered independently
- An architectural boundary that was refined through analysis (update the relevant LAYERING or deep-dive doc)

### Step 6 — After implementing: propagate to existing consumers

This step runs **after** the implementation is complete, not before. When you ship a new shared abstraction — a utility, SPI, service, or pattern — immediately search all repos for existing code that does the same thing differently and update it to use the new abstraction.

Do not leave parallel implementations in place. Parallel implementations rot: they diverge over time, create inconsistency in the audit record, produce different behaviour for the same conceptual operation, and make the codebase harder for LLMs to reason about consistently.

**The propagation checklist:**
1. `grep -r` across all repos for the pattern the new abstraction replaces
2. For each hit: replace with the new abstraction or open a tracked issue if the update requires a separate session
3. If a consumer repo needs the new abstraction and it isn't published yet: open the issue, link it to the implementation issue, don't leave it undocumented
4. Update the capability ownership table in this document if a capability has moved or consolidated

---

## Development Session Protocol

Before designing or implementing: brainstorm → TDD → review before committing. IntelliJ first for rename, move, and find-references. Full norms in `~/.claude/design-implementation.md`; IntelliJ tool guide in the `ide-tooling` skill.

---

## Upstream Consistency — Serverless Workflow 1.0 and quarkus-flow

CaseHub is built on top of CNCF Serverless Workflow 1.0 (via quarkus-flow). Before designing any new abstraction in casehub-engine or any harness, check whether Serverless Workflow 1.0 or quarkus-flow already defines it. Consistency with upstream is preferred over reinvention.

This applies to: execution models, case/workflow definition structure, trigger types, expression evaluation, worker/activity contracts, sub-case/sub-workflow composition, and any serialization format decisions.

**The check:** if a concept exists in Serverless Workflow 1.0 or quarkus-flow — use the same name, the same shape, and the same semantics. If CaseHub must diverge (e.g. to add compliance or trust concerns), document the divergence explicitly.

**Known inheritors of this principle:**
- Case definition three-layer architecture (YAML → schema model → canonical API model + fluent DSL) — see [`docs/protocols/casehub/case-definition-layers.md`](protocols/casehub/case-definition-layers.md)

---

## Architectural Patterns

The platform uses a deliberate blend of Clean Architecture, Hexagonal (Ports and Adapters), DDD, Event-Driven, Reactive, CQRS-lite, Strategy, Registry, Interceptor, and Observer patterns. Each tier applies a different subset. The dependency rule — source code dependencies only point inward, domain never depends on infrastructure — governs all of them.

Full pattern map, rationale, and invariants: [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)

---

## What We're Building

A production-grade, compliance-first infrastructure stack for multi-agent AI systems on Quarkus. Targeted at regulated deployments (EU AI Act Art.12, GDPR Art.17/22).

Four tiers, always kept separate:
- **Foundation** — audit ledger, human task primitives, agent communication mesh, outbound connectors. Independently embeddable in any Quarkus app. Domain-agnostic.
- **Orchestration** — `casehub-engine` coordinates agents via hybrid choreography+blackboard. Depends on foundation only.
- **Integration** — `claudony` wires everything together and surfaces it in a browser dashboard. Depends on orchestration.
- **Application** — domain-specific applications built on the foundation. Each is a separate repo with no domain knowledge in the foundation. The pattern: bring your domain logic, use foundation primitives, modify nothing below.

---

## Repository Map

| Repo | GitHub | One-liner | Tier |
|------|--------|-----------|------|
| `casehub-parent` | [casehubio/parent](https://github.com/casehubio/parent) | BOM, CI dashboards, full-stack build tooling | — |
| `casehub-platform` | [casehubio/platform](https://github.com/casehubio/platform) | Zero-dep foundational SPIs — Path, Preferences, Identity. Modules: `platform-api` (SPIs), `platform` (@DefaultBean mocks), `testing` (@Alternative test fixtures) | Foundation |
| `casehub-ledger` | [casehubio/ledger](https://github.com/casehubio/ledger) | Immutable tamper-evident audit ledger + trust scoring | Foundation |
| `casehub-work` | [casehubio/work](https://github.com/casehubio/work) | Human task lifecycle (WorkItem inbox, SLA, delegation, routing) | Foundation |
| `casehub-qhorus` | [casehubio/qhorus](https://github.com/casehubio/qhorus) | Peer-to-peer agent communication mesh | Foundation |
| `casehub-connectors` | [casehubio/connectors](https://github.com/casehubio/connectors) | Outbound message connectors (Slack, Teams, SMS, email) | Foundation |
| `casehub-engine` | [casehubio/engine](https://github.com/casehubio/engine) | Hybrid choreography+blackboard orchestration engine | Orchestration |
| `claudony` | [casehubio/claudony](https://github.com/casehubio/claudony) | Remote Claude CLI sessions + unified ecosystem dashboard | Integration |
| `casehub-poc` | [casehubio/casehub](https://github.com/casehubio/casehub) | **Retiring** — original POC; no new features | — |

Application tier (devtown, aml, clinical): see [APPLICATIONS.md](APPLICATIONS.md).

---

## Build / Dependency Order

```
casehub-parent              (BOM — publish first; all others import it)
  casehub-platform          (no casehubio deps — foundational SPIs, publishes before ledger)
  casehub-ledger            (no casehubio deps)
  casehub-connectors        (no casehubio deps)
  casehub-work              (core: zero casehubio deps; ledger module: depends on casehub-ledger)
  casehub-qhorus            (depends on casehub-ledger)
  casehub-engine            (depends on casehub-work-core + optionally casehub-ledger)
  claudony                  (depends on casehub-qhorus + implements casehub-engine SPIs)

  — Application tier (opt-in, off by default in CI): see APPLICATIONS.md —
```

---

## Cross-Repo Dependency Map

**Purpose:** impact analysis when an artifact changes — rename, removal, SPI break. Look up the artifact here to find every repo that must be updated before the change ships.

**How to maintain:** when adding a cross-repo `<dependency>`, add a row here. When removing one, delete the row. Protocol: [artifact-rename-propagation.md](protocols/artifact-rename-propagation.md).

| Artifact consumed | Consuming repo | Consuming module | Nature |
|-------------------|---------------|-----------------|--------|
| `casehub-ledger-api` | `casehub-qhorus` | `api` | SPI types |
| `casehub-ledger-api` | `casehub-qhorus` | `runtime` | runtime dep |
| `casehub-ledger-api` | `casehub-work` | `ledger` | audit integration |
| `casehub-ledger-api` | `casehub-engine` | `ledger` | case audit |
| `casehub-ledger-api` | `claudony` | `casehub` | worker lineage |
| `casehub-ledger-api` | `devtown` | `review` | trust queries |
| `casehub-ledger` (runtime) | `casehub-qhorus` | `runtime` | runtime dep |
| `casehub-ledger` (runtime) | `casehub-work` | `ledger` | audit writes |
| `casehub-ledger` (runtime) | `casehub-engine` | `ledger` | case audit writes |
| `casehub-ledger` (runtime) | `devtown` | `app` | runtime dep |
| `casehub-connectors-core` | `casehub-work` | `notifications` | delivery SPI impl |
| `casehub-connectors-core` | `devtown` | `app` | notification delivery |
| `casehub-work-api` | `casehub-engine` | `work-adapter` | WorkItem adapter |
| `casehub-work-api` | `devtown` | `review` | WorkItem types |
| `casehub-work-core` | `casehub-engine` | `work-adapter` | WorkBroker |
| `casehub-work` (runtime) | `devtown` | `app` | runtime dep |
| `casehub-work` (runtime) | `casehub-clinical` | `runtime` | runtime dep |
| `casehub-qhorus-api` | `casehub-engine` | `runtime` | channel SPIs |
| `casehub-qhorus-api` | `claudony` | `casehub` | channel provider |
| `casehub-qhorus-api` | `devtown` | `review` | channel routing |
| `casehub-qhorus` (runtime) | `claudony` | `app` | runtime dep |
| `casehub-qhorus` (runtime) | `devtown` | `app` | runtime dep |
| `casehub-engine-api` | `claudony` | `casehub` | SPI implementations |
| `casehub-engine-api` | `devtown` | `review` | engine types |
| `casehub-engine-ledger` | `claudony` | `casehub` | lineage queries |

**Application tier** (aml, clinical) — consume foundation runtime artifacts; see [APPLICATIONS.md](APPLICATIONS.md) for detail.

---

## Capability Ownership — "Where Does X Live?"

| Capability | Owner | Notes |
|---|---|---|
| Hierarchical scope/label path | `casehub-platform-api` | `Path` record — strict segment validation, `isAncestorOf`, `parent`, `depth`. Construct with `Path.of(String...)` (explicit segments) or `Path.parse(String)` (configurable separator via `casehub.platform.path.separator`, default `/`). **Convention for harnesses:** `Path.of("casehubio", "<app>", "<case-type>")` — e.g. `Path.of("casehubio", "devtown", "pr-review")`. Org segment first, app second, case-type third. This makes the inheritance chain work correctly: devtown inherits from casehubio, pr-review inherits from devtown. |
| Typed preference resolution | `casehub-platform-api` | `PreferenceProvider` SPI + `Preferences` interface; `PreferenceKey<T extends Preference>` typed key with `qualifiedName()`; `SettingsScope(Path, Instant)`; `MapPreferences` utility impl. `MockPreferenceProvider` `@DefaultBean`. See [`typed-preference-keys.md`](protocols/casehub/typed-preference-keys.md). |
| Current principal identity | `casehub-platform-api` | `CurrentPrincipal` SPI — `actorId()`, `groups()`, `roles()` (= groups by convention, wires to `@RolesAllowed`), `hasGroup()`, `isSystem()`, `isAuthenticated()`. Real impls must be `@RequestScoped`. `MockCurrentPrincipal` `@DefaultBean`. |
| Group membership lookup | `casehub-platform-api` | `GroupMembershipProvider` SPI — `membersOf(groupName)` returns empty set for unknown groups. `MockGroupMembershipProvider` `@DefaultBean` always returns empty. |
| Immutable entry chain (Merkle Mountain Range) | `casehub-ledger` | Domain-agnostic; consumers extend `LedgerEntry` via JPA JOINED |
| Cryptographic tamper evidence | `casehub-ledger` | `LedgerVerificationService`, inclusion proofs, Ed25519 checkpoints |
| Actor trust scoring (Bayesian Beta + EigenTrust) | `casehub-ledger` | `ActorTrustScore` — four score types: GLOBAL, CAPABILITY, DIMENSION, CAPABILITY_DIMENSION (✅ #76); nightly `TrustScoreJob`, `TrustScoreRoutingPublisher` CDI events |
| Trust score export read-model | `casehub-ledger` | `TrustExportService` (`exportAll`/`exportActor`/`exportDelta`) — consumed by dashboards and upper layers |
| Trust score import SPI | `casehub-ledger` | `TrustImportService` SPI; `JpaTrustImportService` seed-if-absent `@Alternative`; `NoOpTrustImportService` `@DefaultBean` |
| Trust bootstrapping | `casehub-ledger` | `TrustBootstrapSource` SPI + `TrustBootstrapService`; seeds Beta(α,β) from external source on actor first-registration; opt-in via `casehub.ledger.trust-score.bootstrap.enabled` |
| GDPR Art.17 erasure / Art.22 decision records | `casehub-ledger` | `LedgerErasureService`, `ComplianceSupplement` |
| W3C PROV-DM lineage export | `casehub-ledger` | `LedgerProvExportService` |
| OTel trace linkage to audit entries | `casehub-ledger` | `LedgerTraceListener` auto-populates `traceId` from active OTel span |
| Human task inbox (WorkItem lifecycle) | `casehub-work` | 10 statuses, SLA, delegation, escalation, spawn |
| Named outcome classifications for WorkItems | `casehub-work` | `Outcome` record in `casehub-work-api`; `WorkItemTemplate.outcomes` declares valid names; `WorkItem.outcome` stores resolved name at completion; `WorkItemLifecycleEvent.outcome` carries it for engine routing without parsing `resolution` JSON |
| Conflict-of-interest user exclusion | `casehub-work` | `ExclusionPolicy` SPI in `casehub-work-api`; `CommaSeparatedExclusionPolicy` `@DefaultBean`; `excludedUsers` TEXT field on `WorkItemTemplate` + `WorkItem`; enforced at claim, create (assigneeId), delegate, auto-assignment, and `SelectionContext` |
| M-of-N parallel WorkItem completion (group policy primitive) | `casehub-work` | `MultiInstanceCoordinator`; `WorkItemGroupLifecycleEvent`; see LAYERING.md |
| Worker routing / selection strategies | `casehub-work-core` | `WorkBroker`, `WorkerSelectionStrategy` SPI — also used by casehub-engine |
| Label-based queue views | `casehub-work-queues` | Optional module on casehub-work |
| Semantic (embedding) worker matching | `casehub-work-ai` | Optional module; `SemanticWorkerSelectionStrategy` |
| Outbound notifications (Slack, Teams, SMS, email) | `casehub-connectors` | `Connector` SPI; `casehub-work-notifications` must delegate here |
| Agent-to-agent messaging (typed channels + messages) | `casehub-qhorus` | 9 speech-act types, 5 channel semantics, MCP tools |
| Channel message fan-out to external backends | `casehub-qhorus` | `ChannelBackend` SPI in `casehub-qhorus-api`; implementations in consuming repos (Claudony panel, connectors) |
| Cross-cutting message notification | `casehub-qhorus` | `MessageObserver` SPI in `casehub-qhorus-api`; `InProcessMessageBus` CDI default (`Scope.LOCAL`); CLUSTER-scoped impls for distributed topologies |
| Agent commitment/obligation tracking | `casehub-qhorus` | `Commitment` with 7-state lifecycle |
| Normative audit of all agent interactions | `casehub-qhorus` | `MessageLedgerEntry` extends `LedgerEntry`; all 9 speech-act types recorded |
| Case/process orchestration (choreography + WAITING) | `casehub-engine` | `CaseInstance`, `EventLog`, `WorkOrchestrator` |
| Worker provisioner SPIs (provision, lifecycle, context) | `casehub-engine` (defines) / `claudony` (implements) | `WorkerProvisioner`, `CaseChannelProvider`, `WorkerContextProvider`, `WorkerStatusListener` |
| Durable PlanItem status (blackboard persistence) | `casehub-engine` | `PlanItemStore` (blocking) + `ReactivePlanItemStore` (Uni<>) SPIs in `casehub-engine-common`; `@DefaultBean` no-ops in `blackboard`; JPA impl (`JpaReactivePlanItemStore`) in `casehub-engine-persistence-hibernate`; blocking JPA impl (`JpaPlanItemStore`) in `casehub-engine-work-adapter` sharing the casehub-work datasource. Atomicity guarantee: `planItemStore.save(RUNNING)` and WorkItem creation are in the same `@Transactional` boundary. See engine#273. |
| Remote Claude CLI sessions | `claudony` | `TmuxService`, `SessionRegistry`, WebSocket streaming |
| Browser + agent authentication | `claudony` | WebAuthn passkeys + `X-Api-Key` header |
| Ecosystem CI dashboards | `casehub-parent` | `dashboard.yml`, `pr-dashboard.yml`, `full-stack-build.yml` |
| Application domain logic (devtown, aml, clinical) | Application tier | See [APPLICATIONS.md](APPLICATIONS.md) |

---

## Key Boundary Rules

**Do not define parallel path, scope, preference, or principal types.** `casehub-platform-api` owns `Path`, `SettingsScope`, `PreferenceKey`, `Preferences`, `PreferenceProvider`, `CurrentPrincipal`, and `GroupMembershipProvider`. Repos that need these concepts must depend on `casehub-platform-api` and implement its SPIs — they must not define their own equivalent types.

**Do not add orchestration logic to `casehub-work`.** When a WorkItem completes, casehub-work fires a CDI event and stops. Homogeneous M-of-N group completion is casehub-work. Heterogeneous plan-level completion is casehub-engine. "Mark the WorkItem EXPIRED when its deadline passes" is casehub-work.

**Do not add WorkItem inbox management to `casehub-engine`.** casehub-engine depends on `casehub-work-core` (`WorkBroker`) only. WorkItem entities, Flyway migrations, REST endpoints must not flow into the engine.

**Do not add trust scoring to `casehub-work` or `casehub-engine`.** Trust lives in casehub-ledger and is surfaced via CDI routing events (`TrustScoreRoutingPublisher`). Consumers observe those events — they never compute trust themselves.

**Do not duplicate notification infrastructure.** `casehub-connectors` owns Slack/Teams/SMS/email. `casehub-work-notifications` must delegate here.

**Do not implement Qhorus channel semantics in `claudony`.** Claudony embeds Qhorus and adds SPI implementations. It must not re-implement channel, message, or commitment logic. Implementing `ChannelBackend` or `MessageObserver` SPIs from `casehub-qhorus-api` is not re-implementation — it is correct SPI usage.

**Do not call `QhorusMcpTools` or `ReactiveQhorusMcpTools` from consumer service code.** Those classes are the MCP tool dispatch layer for external callers (Claude Code). Consumer service code should inject `ChannelService` / `ReactiveChannelService` or `MessageService` / `ReactiveMessageService` directly, or implement the `ChannelBackend` SPI. Going through the MCP tool class from internal code couples a service to an external protocol layer.

**Choose `ChannelBackend` vs `MessageObserver` based on scope.** `ChannelBackend` is per-channel and knows its context — use it when a consumer needs to act on messages from a specific channel (e.g. Claudony panel display). `MessageObserver` is a global broadcast across all channels — use it for cross-cutting concerns (e.g. clinical PI response monitoring). For topology guidance (LOCAL CDI vs CLUSTER-scoped transport) see [`docs/repos/casehub-qhorus.md`](repos/casehub-qhorus.md) and [qhorus `docs/messaging-architecture.md`](https://github.com/casehubio/qhorus/blob/main/docs/messaging-architecture.md).

**Do not put CaseHub SPI implementations in `casehub-engine`.** casehub-engine defines them; deployment-specific implementations belong in the deploying application.

**Do not use `casehub-work` runtime in `casehub-engine`.** The engine depends on `casehub-work-core` only.

**Do not add domain logic to foundation repos.** If the capability requires knowledge of software development, clinical trials, or financial crime, it belongs in an application repo.

---

## Cross-Cutting Concerns

### Persistence

| Concern | Owner | Mechanism |
|---|---|---|
| Base ledger tables | `casehub-ledger` | Flyway V1000–V1004 |
| WorkItem tables | `casehub-work` runtime | Flyway V1–V999 |
| Qhorus tables | `casehub-qhorus` | Flyway V1–V9, V1003 (named `qhorus` datasource; scoped to `classpath:db/migration/qhorus`) |
| Engine tables | `casehub-engine` | Hibernate `drop-and-create` (no migrations yet) |
| Ledger subclass join tables | Each consumer | Consumer-owned Flyway, V1004+ numbering |

**Flyway numbering rule:** casehub-ledger owns V1000–V1003. Domain: V1–V999. Ledger subclass joins: V1004+.

**Named datasource rule:** Qhorus always runs on named `qhorus` datasource. Claudony uses separate `claudony` and `qhorus` persistence units.

### Observability

- OTel trace → ledger: `LedgerTraceListener` auto-populates `traceId` at `@PrePersist`
- Agent interactions: `MessageLedgerEntry` records all 9 message types
- WorkItem audit: `AuditEntry` (always-on) + optional `WorkItemLedgerEntry` (tamper-evident)
- Case decisions: `EventLog` (engine-internal) + optional `CaseLedgerEntry` (external, tamper-evident)

### Authentication

| Context | Owner | Mechanism |
|---|---|---|
| Extension-level | Consuming app | Extensions provide no auth |
| Browser → Claudony | `claudony` | WebAuthn passkeys |
| Agent → Claudony | `claudony` | `X-Api-Key` header |
| Channel write ACL | `casehub-qhorus` | `allowed_writers` on `Channel` |

### Privacy (GDPR)

All GDPR concerns centralised in `casehub-ledger`:
- Art.17 erasure: `LedgerErasureService` + `ActorIdentityProvider` SPI
- Art.22 decision records: `ComplianceSupplement`
- PII sanitisation: `DecisionContextSanitiser` SPI

### Agent Identity

Format: `{model-family}:{persona}@{major}` — e.g. `"claude:analyst@v1"`. Defined in casehub-ledger ADR 0004. Major version bump resets trust baseline.

### Implementation Protocols

Rules that apply across all casehubio modules:

| Protocol | Rule |
|---|---|
| SQL type portability (GE-20260512-2c2eff) | `DOUBLE PRECISION` not `DOUBLE`; `SMALLINT` not `TINYINT` — garden `jvm/` domain |
| [Flyway migration rules](protocols/flyway-migration-rules.md) | Version namespace ranges; `MODE=PostgreSQL` in all H2 test URLs |
| [Optional module pattern](protocols/optional-module-pattern.md) | Jandex library module; zero cost when absent |
| [Quarkus test database](protocols/quarkus-test-database.md) | H2 `MODE=PostgreSQL`; Testcontainers for dialect validation |
| [Submodule folder naming](protocols/universal/maven-submodule-folder-naming.md) | Short names — no repo prefix. `api` not `casehub-work-api` |

Full index: [`docs/protocols/INDEX.md`](protocols/INDEX.md)

---

## Known Overlap Risks

1. **`EventLog` vs `CaseLedgerEntry`** — `EventLog` is internal (restart recovery). `CaseLedgerEntry` is external (tamper-evident). If a lifecycle transition doesn't fire `CaseLifecycleEvent`, it won't be ledgered.
2. **`AuditEntry` vs `WorkItemLedgerEntry`** — `AuditEntry` is always-on. `WorkItemLedgerEntry` is opt-in tamper-evident. Don't use `AuditEntry` for compliance claims.
3. **Notification duplication** — `casehub-connectors` and `casehub-work-notifications` both provide Slack/Teams. Must converge (parent#5, open).
4. **`callerRef` format is implicit** — carries `case:{caseId}/pi:{planItemId}`. casehub-work treats it as opaque. Consumers must know this format out of band.

---

## Per-Repo Deep Dives

| Repo | Local path |
|------|-----------|
| `casehub-ledger` | `repos/casehub-ledger.md` |
| `casehub-work` | `repos/casehub-work.md` |
| `casehub-qhorus` | `repos/casehub-qhorus.md` |
| `casehub-engine` | `repos/casehub-engine.md` |
| `claudony` | `repos/claudony.md` |
| `casehub-connectors` | `repos/casehub-connectors.md` |
| `casehub-devtown` | `repos/casehub-devtown.md` |
| `casehub-aml` | `repos/casehub-aml.md` |
| `casehub-clinical` | `repos/casehub-clinical.md` |

Application tier: see [APPLICATIONS.md](APPLICATIONS.md)
