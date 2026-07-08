# Platform Coherence Protocol

> **Scope:** The 6-step pre-implementation protocol — run before any platform change
> **Audience:** All (platform + app builders)
> **Key repos:** all casehubio repos

Run this before implementing any feature, API, abstraction, SPI, or data model change in any casehubio repo. This is not a bureaucratic gate — it is the practice that keeps the platform orthogonal, intuitive, and free of duplication.

> **These protocols are living documents — never treat them as dogma.** If implementation reveals a gap or a rule that doesn't fit, update the protocol in the same session. A rule that doesn't adapt to new evidence is just friction.

Protocols live in `casehubio/garden` — read the index at `docs/protocols/INDEX.md` in that repo (cloned locally at `../garden/docs/protocols/`). One file per rule, self-contained and retrievable independently. Add new entries there; link from capability-ownership.md when a capability entry needs it.

## Step 1 — Does this already exist?

Check the Capability Ownership table below. Then check the per-repo deep-dive for the repos most likely to already have it.

Ask: *Is there a class, SPI, CDI event, or service in another repo that does this, or 90% of this?*

If yes → use the existing abstraction. If the existing one doesn't quite fit, extend it (in the right repo) rather than creating a parallel one here.

## Step 2 — Is this the right repo?

Check the Boundary Rules below. Then ask:

- Which tier does this belong to? (Foundation / Orchestration / Integration / Application)
- Is this domain-agnostic infrastructure (→ foundation), process coordination logic (→ casehub-engine), integration/deployment-specific (→ claudony), or domain-specific application logic (→ devtown / aml / clinical)?
- Will this be useful to consumers other than just the current one? If yes, it belongs lower in the stack.
- Does this depend on anything that the target repo is not supposed to depend on?

If the right repo is a different one → stop. Implement it there, then consume it from here.

## Step 3 — Does this create a consolidation opportunity?

Ask: *Is there something in another repo that does a similar thing awkwardly, that this new abstraction would make redundant or easier?*

If yes → propose refactoring the other repo to use the new abstraction, even if it's more work. Parallel implementations rot; consolidated abstractions improve everything downstream.

Known consolidation candidates:
- `casehub-work-notifications` Slack/Teams channels → should delegate to `casehub-connectors` (parent#5, open)
- `callerRef` format (`case:{id}/pi:{id}`) defined in casehub-engine but used opaquely by casehub-work → consider a shared constant or typed value in `casehub-work-api`

## Step 4 — Is this consistent with the platform pattern?

Check how the same concern is handled in the two or three most similar places in the platform. Then implement it the same way.

### Implementation Conventions

See `casehub/garden: docs/protocols/` for the full protocol library. Key patterns:

**API interface taxonomy**
> Four categories of interface: stores, SPIs, gateways, service facades. Service facades are consumer-called (not implemented); stores/SPIs/gateways are consumer-provided. `@DefaultBean` SPI implementations go in `runtime/` when they have JPA/config deps; in `api/spi/` when pure-Java.

See [`casehub/garden: docs/protocols/casehub/api-interface-taxonomy.md`](../../../garden/docs/protocols/casehub/api-interface-taxonomy.md)

**Ledger subclass extension**
> JOINED inheritance, consumer-owned V2000+ migration (V1000–V1007 reserved for ledger base), domain-agnostic leaf hash.

See [`casehub/garden: docs/protocols/casehub/ledger-subclass-extension.md`](../../../garden/docs/protocols/casehub/ledger-subclass-extension.md)

**CDI events**
> async (`@ObservesAsync`) for ledger capture; sync for routing decisions

**Named datasources**
> Qhorus always on `qhorus`, domain tables never mixed in

**Flyway versioning**
> V1000–V1007 = ledger base (`classpath:db/ledger/migration`); V1–V999 = domain; V2000+ = ledger subclass joins (qhorus reference: `V2000__agent_message_ledger_entry`). Extensions with a named datasource must scope migrations to `db/<module>/migration/` — **never** inside `db/migration/<module>/` (Flyway scans recursively; subdirectories of `db/migration/` are visible to any datasource scanning the parent path).

See [`casehub/garden: docs/protocols/casehub/flyway-version-range-allocation.md`](../../../garden/docs/protocols/casehub/flyway-version-range-allocation.md) Rule 4

**Module structure**
> Three-tier rule — pure-Java SPI / core library (no JPA) / full extension. SPI method signatures must not expose heavy external SDK types. CDI annotation JARs (`jakarta.inject-api`, `jakarta.enterprise.cdi-api`) and Mutiny (`io.smallrye.reactive:mutiny` as `provided`) are acceptable in Tier 1 — both are inert without a container/runtime and every Quarkus consumer already has them. JPA and Quarkus runtime types remain excluded from Tier 1.

See [`casehub/garden: docs/protocols/universal/module-tier-structure.md`](../../../garden/docs/protocols/universal/module-tier-structure.md)

**Persistence module split**
> JPA entities must not co-locate with domain SPIs — forces all consumers to configure a datasource.

See [`casehub/garden: docs/protocols/universal/module-tier-structure.md`](../../../garden/docs/protocols/universal/module-tier-structure.md)

**SPI defaults — three patterns**
> *Operational SPIs* (`WorkerProvisioner`, `CaseChannelProvider`, `WorkerStatusListener`) get a no-op default — skipping the operation leaves the system functional. *Vocabulary/registry SPIs* (`CapabilityRegistry` and equivalents) get a *populated* default expressing domain vocabulary — an empty implementation breaks routing and selection immediately. Decision rule: can the system function correctly with an empty/do-nothing implementation? Yes → no-op. No → populated default. Both live in the same pure-Java module as the SPI; the app module provides the `@ApplicationScoped` wrapper. *Store SPIs* (SPIs that maintain persistent state — `CaseMemoryStore`, `WorkItemStore`, `LedgerEntryRepository`, `EndpointRegistry`) always get a **no-op `@DefaultBean`** in the mock module — never an in-memory working implementation as the default. The in-memory working implementation is `@Alternative @Priority(N)` in a separate `persistence-memory/` module (or `*-memory/` by platform naming convention), activated by classpath presence. Anti-pattern: labelling an `InMemoryXxx` as `@DefaultBean` — `@DefaultBean` means no-op, not in-memory.

See [`casehub/garden: docs/protocols/universal/persistence-backend-cdi-priority.md`](../../../garden/docs/protocols/universal/persistence-backend-cdi-priority.md) and [`module-tier-structure.md`](../../../garden/docs/protocols/universal/module-tier-structure.md)

**casehub-platform-api scope**
> The universal shared dependency — every repo already depends on it, and adding a type here creates no new dependency for anyone. It exists so peer repos can share concepts without depending on each other. A type belongs here when multiple peer repos need it AND no single domain `-api` module owns it: `ActorType`, `ActorTypeResolver`, `CurrentPrincipal`, `Path`, `PreferenceKey` qualify (`ActorType`/`ActorTypeResolver` moved here from `casehub-ledger` in ledger#88 — import from `io.casehub.platform.api.identity`, not `io.casehub.ledger.api.model`). Cross-cutting SPIs and conventions also qualify: `ActorStateContributor`/`ActorStateAccumulator` (parent#56) — needed by ledger, work, qhorus, and engine; uses only stdlib types. Domain types like `AgentDescriptor`, `WorkItem`, or `LedgerEntry` do NOT belong — repos that need them depend on the domain's own `api/` module (`casehub-eidos-api`, `casehub-work-api`, `casehub-ledger-api`).

See [`casehub/garden: docs/protocols/casehub/platform-api-scope.md`](../../../garden/docs/protocols/casehub/platform-api-scope.md) and [`casehub/garden: docs/protocols/casehub/casehub-dependency-tier-order.md`](../../../garden/docs/protocols/casehub/casehub-dependency-tier-order.md)

**casehub-platform (mock module) scope rule**
> Use `<scope>test</scope>` in library and Quarkus extension modules (no `quarkus:build` goal — test-only activation is sufficient and `test` scope is invisible to production augmentation, which is the goal); use `<scope>runtime</scope>` in application modules that declare `<goal>build</goal>` in the quarkus-maven-plugin (production augmentation validates CDI without the test classpath, so `test` scope makes `MockPreferenceProvider @DefaultBean` invisible at augmentation time, causing `UnsatisfiedResolutionException` for `PreferenceProvider`). Wrong-scope symptom: all `@QuarkusTest` tests pass, then augmentation fails ~20s later.

**Application tier rule**
> Domain logic (git, PRs, clinical protocols, AML investigations) belongs in application repos. Foundation repos must remain domain-agnostic. If it requires knowledge of a specific business domain, it does not belong in foundation.

**Submodule folder naming**
> Short descriptive names — no repo prefix. `api` not `casehub-work-api`; `runtime` not `casehub-ledger-runtime`.

See [`casehub/garden: docs/protocols/universal/maven-submodule-folder-naming.md`](../../../garden/docs/protocols/universal/maven-submodule-folder-naming.md)

**Routing strategies**
> Any SPI where a harness author selects among alternative implementations per case or per binding must extend `NamedStrategy` (platform-api), declare a stable `id()`, and ship a `@DefaultBean` no-op or sensible-default implementation. Resolve via `StrategyResolver`, never via direct `Instance<>` iteration or CDI `@Priority` override.

**REST adapter module**
> When a library exposes HTTP endpoints, the REST layer lives in a separate opt-in module (`-rest`) — never in the core runtime. The REST module is a plain JAR (JAX-RS resources + DTOs + exception mappers); Quarkus auto-discovers via Jandex. Consumers include it by dependency; consumers who only need the Java SPI pay no JAX-RS coupling cost. Composition apps (scaffold) compose libraries + their REST modules into a deployable. This is Ports & Adapters applied to HTTP.

See [`casehub/garden: docs/protocols/universal/rest-adapter-module.md`](../../../garden/docs/protocols/universal/rest-adapter-module.md)

**Migration status:** `casehub-ledger-rest` (greenfield, ledger#162), `casehub-engine-rest` (extract from scaffold, engine#657), `casehub-work-rest` (extract from runtime, work#292 — breaking change, lower priority).

**Agent mesh alignment**
> When implementing a new MCP tool or channel interaction, verify it aligns with the normative 3-channel layout (work/observe/oversight) and 4-layer accountability framework.

See [`docs/repos/claudony.md`](../repos/claudony.md) §Agent Mesh Framework and the [Claudony mesh spec](https://github.com/casehubio/claudony/blob/main/docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md)

**Trust routing cold-start**
> Any application using trust-based routing must implement the four-phase maturity model — Phase 0 is availability routing (Gastown parity), phases advance automatically as `minimumObservations` thresholds are crossed, every capability must declare a `fallbackType`. Never block on missing trust data.

See [`casehub/garden: docs/protocols/casehub/trust-maturity-model.md`](../../../garden/docs/protocols/casehub/trust-maturity-model.md)

**Auth retrofit readiness**
> RBAC infrastructure is implemented — `CurrentPrincipal.roles()` delegates to `groups()` (groups-as-roles contract); `casehub-platform-oidc` ships `OidcCurrentPrincipal @RequestScoped` which reads roles from `SecurityIdentity.getRoles()`. `@RolesAllowed` annotations work with CaseHub group names without additional bridge code. **Activation:** add `casehub-platform-oidc` as compile dep. **Status:** casehub-life wired (life#40, 2026-06-22) — `@RolesAllowed` on all 5 REST resources, RBAC-differentiated risk thresholds in `LifeActionRiskClassifier`. Other harnesses pending (parent#251 tracks adoption). Annotations remain inert in harnesses without the OIDC module on classpath. Structural constraints remain: no auth/principal logic in domain or service layers; thin REST resources; injectable query filters; auth-free SPI signatures.

See [`casehub/garden: docs/protocols/casehub/auth-retrofit-readiness.md`](../../../garden/docs/protocols/casehub/auth-retrofit-readiness.md)

**Case definition three-layer architecture**
> YAML (classpath resource) → generated schema model (`io.casehub.model.*`) → canonical API model (`CaseDefinition`). Fluent DSL builders target the same canonical model and additionally support `LambdaExpressionEvaluator` (not expressible in YAML). All YAML definitions ⊂ fluent DSL; reverse is not true. Runtime: extend `YamlCaseHub`. Tests: build `CaseDefinition` directly via builders. Never bypass `CaseDefinitionYamlMapper`. Inherited from CNCF Serverless Workflow 1.0 / quarkus-flow. YAML carries structure; `*CaseDescriptor` POJO carries business logic (worker lambdas, capability routing, SLA policies). `*CaseDefinitions` FuncDSL companions are superseded for new harnesses — use the descriptor pattern instead.

See [`casehub/garden: docs/protocols/casehub/case-definition-layers.md`](../../../garden/docs/protocols/casehub/case-definition-layers.md)

**Descriptor+Handler pattern (application repos)**
> When implementing domain logic for an enum type (routing policy, SLA, capabilities, templates, worker lambdas), does it belong in a `*CaseDescriptor` POJO rather than a switch statement in a service class? Ask: "am I adding a switch on an enum value in a service class?" If yes — it belongs in the descriptor.

See [`casehub/garden: docs/protocols/casehub/descriptor-handler-pattern.md`](../../../garden/docs/protocols/casehub/descriptor-handler-pattern.md)

**Application-tier notification SPIs**
> Define the SPI interface in `api/spi/` (no Quarkus, no framework deps); provide a `@DefaultBean` no-op in `runtime/service/`. This allows test deployments to run without a notification backend and lets production deployments activate implementations by classpath presence. Do not hard-code notification delivery in service code. See casehub-clinical (`SponsorNotifier`, `SafetyOfficerNotifier`) and casehub-aml for reference implementations.

**Worker primitives**
> The canonical worker identity and capability vocabulary lives in `casehub-worker-api`. `WorkerFunction` variants: `Sync` (in-process lambda) and `None` (external worker with no in-process function — `WorkerFunction.NONE` singleton). External worker backends (HTTP, MCP, Camel, Script, GitHub Actions) handle `None`-function workers via external dispatch. `WorkerExecutionManager.canExecute(WorkerFunction)` is a `default true` method; `QuartzWorkerExecutionManager` overrides with positive handler delegation — iterates `WorkerFunctionHandler` instances, returns `true` only when a handler supports the function. `FirstSupportedRoutingStrategy` checks both `supports()` and `canExecute()` to determine backend eligibility. Do not define parallel worker identity types in `casehub-engine` or `casehub-desiredstate` — add `casehub-worker-api` as a compile dep and use the platform types. `casehub-worker-testing` provides `MockWorkerExecutor` and `TestWorkerBuilder` for `@QuarkusTest` isolation.

**Worker(Workflow) for durable multi-step workers**
> When a case worker needs durable execution with retry, branching, or sub-task composition, use `Worker(Workflow)` backed by `casehub-engine-flow` rather than implementing ad-hoc state management. Add `casehub-engine-flow` as a compile dep — `FlowWorkerExecutor` activates by classpath presence. The worker step is then a Serverless Workflow definition; dispatch to casehub workers from within it via `call: casehub:dispatch` (YAML) or `CasehubFlow` (FuncDSL). This is the **preferred pattern for any worker with internal state or multi-step logic** — it makes the structure explicit and durable rather than embedded in Java.

## Step 5 — Does this need a platform-level doc update?

If the capability ownership table, boundary rules, or deep-dive docs need updating after this implementation, update the relevant topic chunks (`platform/capability-ownership.md`, `platform/boundary-rules.md`) and/or the relevant `docs/repos/*.md` file.

Also ask: **did this session surface a non-obvious pattern, a corrected rule, or a gotcha?** If yes — use the `protocol` skill to capture it in `casehubio/garden`, before the session ends. Patterns worth capturing include:
- A solution that required research or multiple failed attempts to find
- A rule in this document that turned out to be wrong or too coarse (update it)
- A concurrency, boundary, or schema decision that would otherwise be re-discovered independently
- An architectural boundary that was refined through analysis (update the relevant LAYERING or deep-dive doc)

## Step 6 — After implementing: propagate to existing consumers

This step runs **after** the implementation is complete, not before. When you ship a new shared abstraction — a utility, SPI, service, or pattern — immediately search all repos for existing code that does the same thing differently and update it to use the new abstraction.

Do not leave parallel implementations in place. Parallel implementations rot: they diverge over time, create inconsistency in the audit record, produce different behaviour for the same conceptual operation, and make the codebase harder for LLMs to reason about consistently.

**The propagation checklist:**
1. `grep -r` across all repos for the pattern the new abstraction replaces
2. For each hit: replace with the new abstraction or open a tracked issue if the update requires a separate session
3. If a consumer repo needs the new abstraction and it isn't published yet: open the issue, link it to the implementation issue, don't leave it undocumented
4. Update the capability ownership table in this document if a capability has moved or consolidated
