# Implementation Protocols

> **Scope:** Cross-cutting conventions — audience-mapped summary with garden links
> **Audience:** All
> **Full index:** [garden protocols INDEX.md](https://github.com/casehubio/garden/blob/main/docs/protocols/INDEX.md)

## Overview

Implementation protocols are living documents capturing cross-project conventions. Each protocol is self-contained and retrievable independently.

Protocols live in `casehubio/garden` — cloned locally at `../garden/docs/protocols/`.

**Three namespaces:**
- `casehub/` — Platform-specific conventions (API taxonomy, routing strategies, ledger extension)
- `universal/` — Technology-agnostic conventions (module structure, REST adapters)
- `web/` — Web Component and browser-side conventions (Lit reactivity, shadow DOM)

## For App Builders

These protocols apply when building domain-specific applications on the CaseHub platform.

### CaseHub-Specific Conventions

| Protocol | Rule |
|----------|------|
| [Case definition layers](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/case-definition-layers.md) | YAML → schema model → canonical API model. Fluent DSL targets canonical model. Runtime: extend `YamlCaseHub`. |
| [Descriptor+Handler pattern](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/descriptor-handler-pattern.md) | Enum-driven domain logic belongs in `*CaseDescriptor` POJOs + CDI handlers — never switch statements in service classes. |
| [Trust maturity model](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/trust-maturity-model.md) | Four-phase cold-start: Phase 0 is availability routing, phases advance as `minimumObservations` thresholds are crossed. Never block on missing trust data. |
| [Auth retrofit readiness](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/auth-retrofit-readiness.md) | Keep services auth-retrofit-ready: no auth/principal logic in domain layers, thin REST resources, injectable query filters, auth-free SPI signatures. |
| [Dual-trail audit pattern](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/dual-trail-audit-pattern.md) | Every state transition writes operational + compliance trails. Operational: always-on, SQL-queryable. Compliance: opt-in, tamper-evident. |
| [Platform-api scope](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/platform-api-scope.md) | Types belong in `casehub-platform-api` when multiple peer repos need them AND no single domain `-api` owns them. Domain types stay in their own `-api` modules. |
| [Typed preference keys](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/typed-preference-keys.md) | Preferences use `PreferenceKey<T extends Preference>` with `qualifiedName()`. Backends: YAML (file-based), JPA (SQL), MongoDB. |
| [SCIM2 agent identity](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/scim2-agent-identity.md) *(link placeholder)* | Agent identity attributes (DID, public key, capabilities) resolved via SCIM2 `Agent` endpoint using `actorId` as `externalId`. |
| [Ledger subclass extension](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/ledger-subclass-extension.md) *(link placeholder)* | JOINED inheritance, consumer-owned V2000+ migration, domain-agnostic leaf hash. |
| [Routing strategy convention](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/routing-strategy-convention.md) | Per-case selectable strategies extend `NamedStrategy`, declare `id()`, ship `@DefaultBean` default, resolve via `StrategyResolver`. |
| [API interface taxonomy](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/api-interface-taxonomy.md) | Four categories: stores (`api/store/`), SPIs (`api/spi/`), gateways (`api/gateway/`), service facades (`api/<domain>/`). |
| [Types and labels convention](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/types-labels-convention.md) *(link placeholder)* | Every definable entity carries `types: Set<Path>` (behavioral contracts — routing, dispatch, evaluation) and `labels: Set<Path>` (operational classification — queues, dashboards, analytics). Ancestor matching via `Path.isAncestorOf()`. Adopters: `CaseDefinition` (engine#652), `WorkItem`/`WorkItemTemplate` (work#291). |
| [Normative channel layout single source](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/normative-channel-layout-single-source.md) | `CaseChannelLayout` SPI defines 3-channel layout (work/observe/oversight). Use `named("normative"\|"simple")` for config-driven selection. |
| [Qhorus consumer integration pattern](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/qhorus-consumer-integration-pattern.md) *(link placeholder)* | Service integrations: inject `MessageService` / `ChannelService`. Dashboard/UI: inject `QhorusDashboardService`. Event-driven: implement `ChannelBackend` or `MessageObserver`. |
| [Per-binding credential reference](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/per-binding-credential-reference.md) | Tier 1.5: logical credential name in DB, resolved via `Config.getValue()`. Tier 2 secrets resolver deferred. |
| [Reactive service build gating](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/reactive-service-build-gating.md) | Extensions gate reactive tier via `@IfBuildProperty(name="casehub.<module>.reactive.enabled")`. Default false. |
| [Casehub dependency tier order](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/casehub-dependency-tier-order.md) *(link placeholder)* | Foundation repos depend on `casehub-platform-api` only. Orchestration depends on foundation. Integration depends on orchestration. |

### Universal Conventions

| Protocol | Rule |
|----------|------|
| [Module tier structure](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/module-tier-structure.md) | Three-tier: pure-Java SPI / core library (no JPA) / full extension. SPI method signatures must not expose heavy external SDK types. |
| [REST adapter module](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/rest-adapter-module.md) | REST layer in separate opt-in module (`-rest`) — never in core library runtime. Consumers include by dependency. |
| [Persistence backend CDI priority](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/persistence-backend-cdi-priority.md) | `@DefaultBean` → `@ApplicationScoped` → `@Alternative @Priority(1)`. Backend activates by classpath presence. |
| [Maven submodule folder naming](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/maven-submodule-folder-naming.md) | Short names — no repo prefix. `api` not `casehub-work-api`. |
| [Flyway repo-scoped migration path](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/flyway-repo-scoped-migration-path.md) | Migrations under `db/<reponame>/migration/`, never `db/migration/<reponame>/`. Prevents recursive scan visibility. |
| [Flyway extension migration registration](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/flyway-extension-migration-registration.md) | Extensions use repo-scoped paths + `NativeImageResourcePatternsBuildItem`. Consumers configure `quarkus.flyway.locations` explicitly. |
| [Quarkus test database](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/quarkus-test-database.md) *(link placeholder)* | H2 `MODE=PostgreSQL`. Testcontainers for dialect validation (FTS, LISTEN/NOTIFY, JSON ops). |
| [Optional module pattern](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/optional-module-pattern.md) | Jandex library module; zero cost when absent. Features activate by classpath presence. |

## For Platform Builders

These protocols apply when extending or modifying the CaseHub platform itself.

### Platform Evolution

| Protocol | Rule |
|----------|------|
| [Flyway version range allocation](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/flyway-version-range-allocation.md) *(link placeholder)* | V1000–V1007 = ledger base. V1–V999 = domain. V2000+ = ledger subclass joins. |
| [Flyway migration rules](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/flyway-migration-rules.md) | Version namespace ranges, `MODE=PostgreSQL` in all H2 test URLs. |
| [Artifact rename propagation](https://github.com/casehubio/garden/blob/main/docs/protocols/casehub/artifact-rename-propagation.md) *(link placeholder)* | When renaming/removing an artifact, update Cross-Repo Dependency Map in PLATFORM.md. Grep all repos before shipping. |
| [SPI default patterns](https://github.com/casehubio/garden/blob/main/docs/protocols/universal/module-tier-structure.md) | Operational SPIs: no-op default. Vocabulary SPIs: populated default. Store SPIs: no-op `@DefaultBean`, in-memory `@Alternative @Priority(N)` in separate module. |

### Garden Maintenance

**Adding a new protocol:**

1. Determine scope: `casehub/` (platform), `universal/` (tech-agnostic), or `web/` (browser)
2. Write protocol file with YAML frontmatter (see existing protocols for format)
3. Add row to namespace's INDEX.md
4. Commit to garden main

**Protocol update trigger:** After implementing a capability that required research, multiple failed approaches, or corrected a rule in PLATFORM.md — use the `protocol` skill to capture it before the session ends.

## Web Component Conventions

| Protocol | Rule |
|----------|------|
| [Lit reactive property semantics](https://github.com/casehubio/garden/blob/main/docs/protocols/web/lit-reactive-property-semantics.md) *(link placeholder)* | Lit `@property()` triggers re-render. Avoid deep mutations; use immutable updates for arrays/objects. |
| [Shadow DOM event bubbling](https://github.com/casehubio/garden/blob/main/docs/protocols/web/shadow-dom-event-bubbling.md) *(link placeholder)* | Custom events must set `composed: true` to cross shadow boundaries. Use `CustomEvent` with `{bubbles: true, composed: true}`. |

Full index: [garden protocols INDEX.md](https://github.com/casehubio/garden/blob/main/docs/protocols/INDEX.md)
