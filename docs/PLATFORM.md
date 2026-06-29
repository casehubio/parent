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

Protocols live in `casehubio/garden` — read the index at `docs/protocols/INDEX.md` in that repo (cloned locally at `../garden/docs/protocols/`). One file per rule, self-contained and retrievable independently. Add new entries there; link from PLATFORM.md when a capability ownership entry needs it.

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

- SPIs: consumer-facing SPI interfaces go in `api/spi/` — see `casehub/garden: docs/protocols/casehub/consumer-spi-placement.md`. `@DefaultBean` implementations go in `runtime/` when they have JPA or config deps; in `api/spi/` itself when they are trivially pure-Java. Persistence SPIs with JPA deps belong in model modules. The test: could a consumer implement this interface without depending on `runtime/`? If yes, the interface belongs in `api/spi/`.
- Ledger subclasses: JOINED inheritance, consumer-owned V2000+ migration (V1000–V1007 reserved for ledger base; V2000+ provides safe buffer), domain-agnostic leaf hash. See `casehub/garden: docs/protocols/casehub/ledger-subclass-extension.md`.
- CDI events: async (`@ObservesAsync`) for ledger capture; sync for routing decisions
- Named datasources: Qhorus always on `qhorus`, domain tables never mixed in
- Flyway numbering: V1000–V1007 = ledger base (`classpath:db/ledger/migration`); V1–V999 = domain; V2000+ = ledger subclass joins (qhorus reference: `V2000__agent_message_ledger_entry`). Extensions with a named datasource must scope migrations to `db/<module>/migration/` — **never** inside `db/migration/<module>/` (Flyway scans recursively; subdirectories of `db/migration/` are visible to any datasource scanning the parent path). See `casehub/garden: docs/protocols/casehub/flyway-version-range-allocation.md` Rule 4.
- Module structure: three-tier rule — pure-Java SPI / core library (no JPA) / full extension. SPI method signatures must not expose heavy external SDK types. CDI annotation JARs (`jakarta.inject-api`, `jakarta.enterprise.cdi-api`) and Mutiny (`io.smallrye.reactive:mutiny` as `provided`) are acceptable in Tier 1 — both are inert without a container/runtime and every Quarkus consumer already has them. JPA and Quarkus runtime types remain excluded from Tier 1. See `casehub/garden: docs/protocols/universal/module-tier-structure.md`.
- **Persistence module split:** JPA entities must not co-locate with domain SPIs — forces all consumers to configure a datasource. See `casehub/garden: docs/protocols/universal/module-tier-structure.md`.
- **SPI defaults — three patterns:** *Operational SPIs* (`WorkerProvisioner`, `CaseChannelProvider`, `WorkerStatusListener`) get a no-op default — skipping the operation leaves the system functional. *Vocabulary/registry SPIs* (`CapabilityRegistry` and equivalents) get a *populated* default expressing domain vocabulary — an empty implementation breaks routing and selection immediately. Decision rule: can the system function correctly with an empty/do-nothing implementation? Yes → no-op. No → populated default. Both live in the same pure-Java module as the SPI; the app module provides the `@ApplicationScoped` wrapper. *Store SPIs* (SPIs that maintain persistent state — `CaseMemoryStore`, `WorkItemStore`, `LedgerEntryRepository`, `EndpointRegistry`) always get a **no-op `@DefaultBean`** in the mock module — never an in-memory working implementation as the default. The in-memory working implementation is `@Alternative @Priority(N)` in a separate `persistence-memory/` module (or `*-memory/` by platform naming convention), activated by classpath presence. Anti-pattern: labelling an `InMemoryXxx` as `@DefaultBean` — `@DefaultBean` means no-op, not in-memory. See `casehub/garden: docs/protocols/universal/persistence-backend-cdi-priority.md` and `module-tier-structure.md`.
- **`casehub-platform-api` is not a shared types bucket.** It exists to avoid duplication of shared concepts across repos that should not depend on each other. A type or SPI belongs there only if multiple peer repos need it AND cannot share it by depending on a single domain `*-api` module. `ActorType`, `ActorTypeResolver`, `CurrentPrincipal`, `Path`, `PreferenceKey` qualify (`ActorType`/`ActorTypeResolver` moved here from `casehub-ledger` in ledger#88 — import from `io.casehub.platform.api.identity`, not `io.casehub.ledger.api.model`). Behaviour SPIs with zero domain types also qualify: `ActorStateContributor`/`ActorStateAccumulator` (parent#56) — needed by ledger, work, qhorus, and engine; uses only `java.util.UUID`, `java.time.Instant`, primitives. Domain types like `AgentDescriptor`, `WorkItem`, or `LedgerEntry` do not — repos that need them depend on the domain's own `api/` module (`casehub-eidos-api`, `casehub-work-api`, `casehub-ledger-api`). See `casehub/garden: docs/protocols/casehub/platform-api-scope.md`.
- **`casehub-platform` (mock module) scope rule:** use `<scope>test</scope>` in library and Quarkus extension modules (no `quarkus:build` goal — test-only activation is sufficient and `test` scope is invisible to production augmentation, which is the goal); use `<scope>runtime</scope>` in application modules that declare `<goal>build</goal>` in the quarkus-maven-plugin (production augmentation validates CDI without the test classpath, so `test` scope makes `MockPreferenceProvider @DefaultBean` invisible at augmentation time, causing `UnsatisfiedResolutionException` for `PreferenceProvider`). Wrong-scope symptom: all `@QuarkusTest` tests pass, then augmentation fails ~20s later.
- **Application tier rule:** domain logic (git, PRs, clinical protocols, AML investigations) belongs in application repos. Foundation repos must remain domain-agnostic. If it requires knowledge of a specific business domain, it does not belong in foundation.
- **Submodule folder naming:** short descriptive names — no repo prefix. `api` not `casehub-work-api`; `runtime` not `casehub-ledger-runtime`. See `casehub/garden: docs/protocols/universal/maven-submodule-folder-naming.md`.
- **Agent mesh alignment:** when implementing a new MCP tool or channel interaction, verify it aligns with the normative 3-channel layout (work/observe/oversight) and 4-layer accountability framework. See [`docs/repos/claudony.md`](repos/claudony.md) §Agent Mesh Framework and the [Claudony mesh spec](https://github.com/casehubio/claudony/blob/main/docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md).
- **Trust routing cold-start:** any application using trust-based routing must implement the four-phase maturity model — Phase 0 is availability routing (Gastown parity), phases advance automatically as `minimumObservations` thresholds are crossed, every capability must declare a `fallbackType`. Never block on missing trust data. See `casehub/garden: docs/protocols/casehub/trust-maturity-model.md`.
- **Auth retrofit readiness:** RBAC infrastructure is implemented — `CurrentPrincipal.roles()` delegates to `groups()` (groups-as-roles contract); `casehub-platform-oidc` ships `OidcCurrentPrincipal @RequestScoped` which reads roles from `SecurityIdentity.getRoles()`. `@RolesAllowed` annotations work with CaseHub group names without additional bridge code. **Activation:** add `casehub-platform-oidc` as compile dep. **Status:** casehub-life wired (life#40, 2026-06-22) — `@RolesAllowed` on all 5 REST resources, RBAC-differentiated risk thresholds in `LifeActionRiskClassifier`. Other harnesses pending (parent#251 tracks adoption). Annotations remain inert in harnesses without the OIDC module on classpath. Structural constraints remain: no auth/principal logic in domain or service layers; thin REST resources; injectable query filters; auth-free SPI signatures. See `casehub/garden: docs/protocols/casehub/auth-retrofit-readiness.md`.
- **Case definition three-layer architecture:** YAML (classpath resource) → generated schema model (`io.casehub.model.*`) → canonical API model (`CaseDefinition`). Fluent DSL builders target the same canonical model and additionally support `LambdaExpressionEvaluator` (not expressible in YAML). All YAML definitions ⊂ fluent DSL; reverse is not true. Runtime: extend `YamlCaseHub`. Tests: build `CaseDefinition` directly via builders. Never bypass `CaseDefinitionYamlMapper`. Inherited from CNCF Serverless Workflow 1.0 / quarkus-flow. YAML carries structure; `*CaseDescriptor` POJO carries business logic (worker lambdas, capability routing, SLA policies). `*CaseDefinitions` FuncDSL companions are superseded for new harnesses — use the descriptor pattern instead. See [`casehub/garden: docs/protocols/casehub/case-definition-layers.md`](../garden/docs/protocols/casehub/case-definition-layers.md).
- **Descriptor+Handler pattern (application repos):** when implementing domain logic for an enum type (routing policy, SLA, capabilities, templates, worker lambdas), does it belong in a `*CaseDescriptor` POJO rather than a switch statement in a service class? Ask: "am I adding a switch on an enum value in a service class?" If yes — it belongs in the descriptor. See `casehub/garden: docs/protocols/casehub/descriptor-handler-pattern.md`.
- **Application-tier notification SPIs:** define the SPI interface in `api/spi/` (no Quarkus, no framework deps); provide a `@DefaultBean` no-op in `runtime/service/`. This allows test deployments to run without a notification backend and lets production deployments activate implementations by classpath presence. Do not hard-code notification delivery in service code. See casehub-clinical (`SponsorNotifier`, `SafetyOfficerNotifier`) and casehub-aml for reference implementations.
- **Worker primitives (`Worker`, `Capability`, `WorkerFunction`, `WorkerResult`, `WorkerOutcome`, `PlannedAction`):** the canonical worker identity and capability vocabulary lives in `casehub-worker-api`. Do not define parallel worker identity types in `casehub-engine` or `casehub-desiredstate` — add `casehub-worker-api` as a compile dep and use the platform types. `casehub-worker-testing` provides `MockWorkerExecutor` and `TestWorkerBuilder` for `@QuarkusTest` isolation.
- **Worker(Workflow) for durable multi-step workers:** when a case worker needs durable execution with retry, branching, or sub-task composition, use `Worker(Workflow)` backed by `casehub-engine-flow` rather than implementing ad-hoc state management. Add `casehub-engine-flow` as a compile dep — `FlowWorkerExecutor` activates by classpath presence. The worker step is then a Serverless Workflow definition; dispatch to casehub workers from within it via `call: casehub:dispatch` (YAML) or `CasehubFlow` (FuncDSL). This is the **preferred pattern for any worker with internal state or multi-step logic** — it makes the structure explicit and durable rather than embedded in Java. See Capability Ownership table.

### Step 5 — Does this need a platform-level doc update?

If the capability ownership table, boundary rules, or deep-dive docs need updating after this implementation, update `casehub-parent/docs/PLATFORM.md` and/or the relevant `docs/repos/*.md` file.

Also ask: **did this session surface a non-obvious pattern, a corrected rule, or a gotcha?** If yes — use the `protocol` skill to capture it in `casehubio/garden`, before the session ends. Patterns worth capturing include:
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
- Case definition three-layer architecture (YAML → schema model → canonical API model + fluent DSL) — see [`casehub/garden: docs/protocols/casehub/case-definition-layers.md`](../garden/docs/protocols/casehub/case-definition-layers.md)

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
| `casehub-platform` | [casehubio/platform](https://github.com/casehubio/platform) | Zero-dep foundational SPIs — Path, Preferences, Identity, Memory. Modules: `platform-api` (SPIs + `ReactiveCaseMemoryStore` Mutiny SPI), `platform` (@DefaultBean mocks + BlockingToReactiveBridge), `testing` (@Alternative identity fixtures), `config/` (YAML preference provider), `oidc/` (OIDC CurrentPrincipal), `expression/` (JQEvaluator), `persistence-jpa/` (JPA PreferenceProvider — Flyway, @ApplicationScoped), `persistence-mongodb/` (MongoDB PreferenceProvider — @Alternative @Priority(1), no Flyway), `memory-inmem/` (@Alternative @Priority(1) volatile CaseMemoryStore — ConcurrentHashMap, no quarkus:build goal. Add test-scope for @QuarkusTest isolation; compile for ephemeral installs. Do NOT combine with memory-jpa or memory-sqlite in the same scope), `memory-jpa/` (@ApplicationScoped JPA CaseMemoryStore — PostgreSQL, Flyway V1000 at `classpath:db/memory/migration`, FTS via websearch_to_tsquery when question provided. No quarkus:build goal), `memory-sqlite/` (@Alternative @Priority(1) SQLite CaseMemoryStore — xerial JDBC + HikariCP WAL + FTS5 + Flyway programmatic at `classpath:db/memory-sqlite/migration`. Configure `casehub.memory.sqlite.path`. No quarkus:build goal. Do NOT combine with memory-inmem or memory-jpa in the same scope), `memory-mem0/` (@Alternative @Priority(1) Mem0 REST CaseMemoryStore — vector embeddings via Mem0 OSS (Docker + pgvector), infer:false (verbatim storage). Tenant isolation via compound user_id={tenantId}::{entityId} (Mem0 OSS has no app_id). RELEVANCE uses POST /search with top_k + threshold. Do NOT combine with memory-inmem or memory-sqlite), `memory-graphiti/` (@Alternative @Priority(2) Graphiti REST GraphCaseMemoryStore — temporal knowledge graph (Neo4j/FalkorDB/Kuzu); LLM entity extraction (async); graphQuery(GraphMemoryQuery) for temporal queries. Configure: quarkus.rest-client.graphiti.url, casehub.memory.graphiti.api-key), `scim/` (SCIM 2.0 GroupMembershipProvider — @ApplicationScoped, displaces mock by classpath presence, platform#45), `agent-api/` (AgentProvider SPI — Mutiny only, no Quarkus. Package: `io.casehub.platform.agent`), `agent-claude/` (@ApplicationScoped ClaudeAgentProvider + ClaudeAgentClient @Startup — activates by classpath presence, requires Claude CLI, concurrent-session semaphore. Two subprocess paths: `invoke()` → `ClaudeOneShotProcess` (direct ProcessBuilder, immediate destroyForcibly — eidos#52); `openSession()` → ClaudeAgentSession (SDK session mode, multi-turn). `ClaudeAgentClient` CDI constructor requires `ObjectMapper`. Package: `io.casehub.platform.agent.claude`), `agent-langchain4j/` (bidirectional LangChain4j interop — ChatModelAgentProvider (any ChatModel → AgentProvider) + AgentProviderChatModel (any AgentProvider → ChatModel); no longer Claude-specific. @Alternative @Priority(10). Not for use with engine.Agent which forces JSON mode), `streams-kafka/` (SmallRye reactive messaging, static topics, raw byte[], builds CloudEvent from STREAM_EVENT_TYPE), `streams-amqp/` (AMQP reactive messaging, single address, same CloudEvent pattern), `streams-webhook/` (@Startup JAX-RS, structured CloudEvents HTTP binding, CloudEventBuilder.from() preserve+enrich), `streams-poll/` (@Scheduled HTTP GET, HttpClient field, explicit status code check, polling EndpointRegistry HTTP endpoints), `streams-camel/` (dynamic Camel route builder, @ObservesAsync EndpointRegistered for EndpointProtocol.CAMEL, idempotent routedUris set). Adapters are submodules — extracted to a standalone repo only when a confirmed non-CaseHub consumer warrants it (see `PP-20260529-spi-adapter-placement`). | Foundation |
| `casehub-worker` | [casehubio/casehub-worker](https://github.com/casehubio/casehub-worker) | Worker primitive foundation — `Worker`, `Capability`, `WorkerFunction`, `WorkerResult`, `WorkerOutcome`, `PlannedAction`. Consumed by `casehub-engine` and `casehub-desiredstate`. Modules: `casehub-worker-api` (pure-Java value types + `WorkerFunction` interface — no Quarkus, no JPA), `casehub-worker` (`DefaultWorkerExecutor` runtime), `casehub-worker-testing` (`MockWorkerExecutor`, `TestWorkerBuilder`). | Foundation |
| `casehub-ledger` | [casehubio/ledger](https://github.com/casehubio/ledger) | Immutable tamper-evident audit ledger + trust scoring. Modules: `api`, `runtime`, `deployment`, `persistence-memory` (`casehub-ledger-memory` — zero-datasource in-memory SPIs). SCIM2 agent DID resolution via `ScimActorDIDProvider @Alternative`. | Foundation |
| `casehub-work` | [casehubio/work](https://github.com/casehubio/work) | Human task lifecycle (WorkItem inbox, SLA, delegation, routing) | Foundation |
| `casehub-qhorus` | [casehubio/qhorus](https://github.com/casehubio/qhorus) | Peer-to-peer agent communication mesh | Foundation |
| `casehub-connectors` | [casehubio/connectors](https://github.com/casehubio/connectors) | Outbound and inbound message connectors (Slack, Teams, SMS, email outbound; webhook + IMAP email inbound) | Foundation |
| `casehub-iot` | [casehubio/iot](https://github.com/casehubio/iot) | Typed IoT device abstraction layer — `DeviceEntity` hierarchy (Matter-aligned), `DeviceProvider` SPI (reactive `Uni<>` returns), `StateChangeEvent` CDI bus, `DeviceCommand` dispatch. Modules: `api` (public API — semver), `homeassistant` (HA REST + WebSocket provider + HA supplement types), `openhab` (OpenHAB REST + SSE provider + OH supplement types), `testing` (MockDeviceProvider, Java `Fixtures` + YAML `DeviceFixtureLoader`, `DeviceTypeHandler` SPI with 16 handlers, `StateChangeEventPublisher`), `bridge` (local bridge agent — event relay, CDI filter chain, WebSocket client), `bridge-server` (cloud-side `BridgeDeviceProvider implements DeviceProvider` — remote devices look local to cloud consumers; `DeviceTypeIdResolver` for compound type ID serialization; 6 deployment topologies). **Note:** `api` module now includes Jackson annotations for `DeviceTypeIdResolver`. Triggers `casehub-life` downstream on publish. | Foundation |
| `casehub-desiredstate` | [casehubio/casehub-desiredstate](https://github.com/casehubio/casehub-desiredstate) | Generic desired-state management runtime — `DesiredStateGraph`, `TransitionPlanner` (pruning-first), `ReconciliationLoop`, `FaultPolicyEngine`; SPIs: `GoalCompiler`, `ActualStateAdapter`, `NodeProvisioner`, `FaultPolicy`, `EventSource`, `TransitionExecutor`. Domain-agnostic; delegates to `casehub-engine-flow`; human nodes via casehub-work WorkItems. 6 modules: api, runtime, testing, engine-adapter, examples/dungeon, examples/pipeline. Runtime module: OTel tracing instrumentation (`opentelemetry-api`) on `ReconciliationLoop` and `SimpleTransitionExecutor`. **Examples:** Nefarious Dungeons (entity hierarchy), Data Pipeline (medallion architecture — Bronze/Silver/Gold, schema validation, three-tier fault escalation: auto-retry → AI_REVIEW via real `AgentProvider` SPI for LLM diagnosis → HUMAN_REVIEW via casehub-work `WorkItem`; pluggable `ExecutionBackend` strategy per processing stage for per-node execution dispatch). Research project. | Foundation |
| `casehub-blocks` | [casehubio/blocks](https://github.com/casehubio/blocks) | Reusable building blocks composed from qhorus, engine, work primitives | Foundation-adjacent |
| `casehub-engine` | [casehubio/engine](https://github.com/casehubio/engine) | Hybrid choreography+blackboard orchestration engine | Orchestration |
| `claudony` | [casehubio/claudony](https://github.com/casehubio/claudony) | Remote Claude CLI sessions + unified ecosystem dashboard | Integration |
| `casehub-openclaw` | [casehubio/openclaw](https://github.com/casehubio/openclaw) | CaseHub × OpenClaw integration — ChannelContextWindow, WorkerProvisioner, ChannelBackend SPI, Python SDK context hook | Integration |
| `casehub-workers` | [casehubio/workers](https://github.com/casehubio/workers) | HTTP, Camel, and GitHub Actions worker dispatch adapters — `workers-common` (shared dispatch SPI; `PermanentFaultException`, `RetryAfterException`), `workers-camel` (Apache Camel route-based dispatch), `workers-http` (HTTP POST worker dispatch), `workers-github-actions` (`workflow_dispatch` + `repository_dispatch` REST APIs) | Integration |
| `casehub-ras` | [casehubio/casehub-ras](https://github.com/casehubio/casehub-ras) | Reticular Activating System — situational awareness and reactive case creation. Observes `@ObservesAsync CloudEvent` from `casehub-platform-api`; routes to pluggable `Ganglion` detection strategies (`JavaSwitch`, `DroolsCEP`, `Bayesian`, `LLM`); correlates composite events; triggers `startCase()` when situation threshold crossed. Stream infrastructure (Quarkus/Camel) lives in casehub-platform stream submodules. | Integration |
| `casehub-ops` | [casehubio/casehub-ops](https://github.com/casehubio/casehub-ops) | Domain implementations of `casehub-desiredstate` SPIs for CasehHub-specific deployment concerns. Modules: `deployment` (`DeploymentGoalCompiler` — processes `casehub-deployment.yaml` goal declaration into a `DesiredStateGraph`; 5 node types: agents, channels, case types, trust policies, endpoints. Endpoint provisioning registers `EndpointDescriptor` in `EndpointRegistry` — stream modules discover and react to registered endpoints), `infra` (Terraform/Ansible augmentation), `compliance` (SOC2/GDPR/EU-AI-Act/DORA posture), `iot` (IoT desired state). `casehub-desiredstate` stays domain-agnostic; casehub-ops is the CasehHub domain layer above it. Research project and reference architecture. | Integration |
| `casehub-eidos` | [casehubio/eidos](https://github.com/casehubio/eidos) | Agent identity — descriptor, discovery registry, vocabulary system, system prompt generation | Foundation |
| `casehub-neural-text` | [casehubio/neural-text](https://github.com/casehubio/neural-text) | ONNX neural text inference (NLI, classification, SPLADE, reranking) + LangChain4j RAG integration with hybrid search. `rag-api`, `rag`, `rag-testing` now also consumed by Hortora/engine (neural-text#35). | Foundation |
| `casehub-poc` | [casehubio/casehub](https://github.com/casehubio/casehub) | **Retiring** — original POC; no new features | — |
| `casehub-devtown` | [casehubio/devtown](https://github.com/casehubio/devtown) | PR review automation, merge queue management, GitHub integration | Application |
| `casehub-aml` | [casehubio/aml](https://github.com/casehubio/aml) | Anti-money laundering case management | Application |
| `casehub-clinical` | [casehubio/clinical](https://github.com/casehubio/clinical) | Clinical adverse event investigation | Application |
| `casehub-life` | [casehubio/life](https://github.com/casehubio/life) | Personal life automation | Application |
| `casehub-drafthouse` | [casehubio/drafthouse](https://github.com/casehubio/drafthouse) | Document review and multi-participant LLM debate | Application |
| `casehub-soc` | [casehubio/soc](https://github.com/casehubio/soc) | Security operations center | Application |
| `casehub-fsitrading` | [casehubio/fsitrading](https://github.com/casehubio/fsitrading) | Financial services trading compliance | Application |
| `quarkmind` | [casehubio/quarkmind](https://github.com/casehubio/quarkmind) | StarCraft II game AI — living lab proving the CaseHub harness pattern at millisecond game-loop granularity outside regulated domains | Application |
| `flow` | [mdproctor/flow](https://github.com/mdproctor/flow) | Standalone Quarkus engine app with REST endpoints — tier and platform coherence pending analysis (external contributor) | TBD |

Application tier (devtown, aml, clinical, life, drafthouse, quarkmind, soc, fsitrading): see [APPLICATIONS.md](APPLICATIONS.md).

---

## Build / Dependency Order

```
casehub-parent              (BOM — publish first; all others import it)
  casehub-platform          (no casehubio deps — foundational SPIs + CaseMemoryStore adapters as submodules, publishes before ledger)
  casehub-worker            (no casehubio deps — Worker, Capability, WorkerFunction primitives; consumed by engine + desiredstate)
  casehub-ledger            (no casehubio deps)
  casehub-connectors        (no casehubio deps)
  casehub-iot               (iot-api: depends on casehub-platform-api for CloudEvent vocabulary — iot#19; providers: platform-specific REST/WebSocket clients)
  casehub-work              (api: depends on casehub-platform-api; core: zero other casehubio deps; ledger module: depends on casehub-ledger)
  casehub-qhorus            (depends on casehub-ledger)
  casehub-eidos             (depends on casehub-ledger; casehub-eidos-api depends on nothing)
  casehub-neural-text       (inference-*: zero casehubio deps; rag-*: depends on casehub-platform-api + LangChain4j)
  casehub-engine            (depends on casehub-work-core + optionally casehub-ledger + optionally casehub-eidos-api)
  casehub-blocks            (depends on casehub-qhorus-api, casehub-work-api, casehub-engine-api — foundation-adjacent library)
  casehub-engine-ai         (optional — depends on casehub-engine-api; adds AgentEmbeddingProvider SPI + SemanticAgentRoutingStrategy)
  casehub-engine-flow       (optional — depends on casehub-engine-common only; enables Worker(Workflow) to dispatch casehub workers from Serverless Workflow steps)
  claudony                  (depends on casehub-qhorus + implements casehub-engine SPIs)
  casehub-openclaw          (depends on casehub-qhorus + casehub-engine SPIs; opt-in — off by default in CI)
  casehub-workers           (depends on casehub-engine-api + casehub-engine-common; opt-in — off by default in CI)

  — Application tier (opt-in, off by default in CI): see APPLICATIONS.md —
  casehub-life              (depends on full foundation stack + casehub-openclaw as WorkerProvisioner)
  casehub-drafthouse        (depends on casehub-qhorus; engine + ledger + work added later)
  quarkmind                 (depends on casehub-poc + casehub-engine-api + casehub-engine-blackboard; migrating from poc to engine — casehubio/quarkmind#193)
  casehub-soc               (depends on full foundation stack — engine, ledger, work, qhorus, worker, platform)
  casehub-fsitrading        (depends on full foundation stack — engine, ledger, work, qhorus, worker, platform)
```

---

## Cross-Repo Dependency Map

**Purpose:** impact analysis when an artifact changes — rename, removal, SPI break. Look up the artifact here to find every repo that must be updated before the change ships.

**How to maintain:** when adding a cross-repo `<dependency>`, add a row here. When removing one, delete the row. Protocol: `casehub/garden: docs/protocols/artifact-rename-propagation.md`.

| Artifact consumed | Consuming repo | Consuming module | Nature |
|-------------------|---------------|-----------------|--------|
| `casehub-platform-api` | `casehub-work` | `api` | `Path`, `Preferences`, `ActorType`, `ActorTypeResolver` in SPI signatures |
| `casehub-platform-api` | `casehub-ledger` | `api` | `ActorType`, `ActorTypeResolver` (moved from ledger in ledger#88) |
| `casehub-platform-api` | `casehub-qhorus` | `api` | `ActorType`, `ActorTypeResolver` (identity primitives from `io.casehub.platform.api.identity`) |
| `casehub-platform-api` | `casehub-qhorus` | `runtime` | transitive via api |
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
| `casehub-platform-expression` | `casehub-work` | `queues` | JQ expression evaluation (JQEvaluator) |
| `casehub-connectors-core` | `casehub-work` | `notifications` | delivery SPI impl |
| `casehub-connectors-core` | `devtown` | `app` | notification delivery |
| `casehub-connectors-core` | `casehub-clinical` | `runtime` | sponsor + safety officer notification delivery |
| `casehub-connectors-core` | `casehub-qhorus` | `connectors` | optional — `WatchdogAlertEvent → ConnectorService.send()` bridge; activates by classpath presence |
| `casehub-connectors-core` | `casehub-qhorus` | `connector-backend` | optional — `InboundMessage → ConnectorChannelBackend` bridge; activates by classpath presence |
| `casehub-connectors-slack-bot` | `casehub-qhorus` | `slack-channel` | optional — `SlackBotClient` used by `SlackChannelBackend`; activates by classpath presence; Refs qhorus#261 |
| `casehub-platform-api` | `casehub-engine` | `actor-state` | `ActorStateContributor`, `ActorStateAccumulator` SPI interfaces |
| `casehub-platform-api` | `casehub-iot` | `api` | `io.cloudevents.CloudEvent` vocabulary — `IoTCloudEventAdapter` fires `StateChangeEvent → CloudEvent`; `cloudevents-core` transitive (iot#19) |
| `casehub-ledger` (runtime) | `casehub-engine` | `actor-state` | `TrustGateService` for global + capability scores |
| `casehub-work` | `casehub-engine` | `actor-state` | `WorkItemStore` for active WorkItems |
| `casehub-qhorus` | `casehub-engine` | `actor-state` | `CommitmentStore`, `ChannelStore` for open Commitments |
| `casehub-work-api` | `casehub-engine` | `work-adapter` | WorkItem adapter |
| `casehub-work-api` | `casehub-engine` | `work-adapter` | `CaseSignalSink` implementation — signals running cases on SLA escalation (compile scope, not a runtime routing dep) |
| `casehub-work-api` | `devtown` | `review` | WorkItem types |
| `casehub-work-core` | `casehub-engine` | `work-adapter` | WorkBroker |
| `casehub-work` (runtime) | `devtown` | `app` | runtime dep |
| `casehub-work` (runtime) | `casehub-clinical` | `runtime` | runtime dep |
| `casehub-qhorus-api` | `casehub-engine` | `runtime` | channel SPIs |
| `casehub-qhorus-api` | `claudony` | `casehub` | channel provider |
| `casehub-qhorus-api` | `devtown` | `review` | channel routing |
| `casehub-qhorus` (runtime) | `claudony` | `app` | runtime dep |
| `casehub-qhorus` (runtime) | `devtown` | `app` | runtime dep |
| `casehub-qhorus-api` | `casehub-clinical` | `api` | SPI types / MessageReceivedEvent |
| `casehub-qhorus` (runtime) | `casehub-clinical` | `runtime` | runtime dep |
| `casehub-engine-api` | `claudony` | `casehub` | SPI implementations |
| `casehub-engine-common` | `claudony` | `casehub` | `WorkerExecutionManager`, `WorkflowExecutionCompleted`, `CaseInstance`, `CrossTenantCaseInstanceRepository` — exit watcher for tmux session lifecycle (claudony#146) |
| `casehub-engine-api` | `devtown` | `review` | engine types |
| `casehub-engine` (runtime) | `devtown` | `app` | YamlCaseHub, CaseHubRuntime |
| `casehub-engine-work-adapter` | `devtown` | `app` | HITL bridge — HumanTaskScheduleHandler + WorkItemLifecycleAdapter |
| `casehub-engine-blackboard` | `devtown` | `app` | BlackboardRegistry — transitive via work-adapter; required for plan item tracking |
| `casehub-engine-ledger` | `claudony` | `casehub` | lineage queries |
| `casehub-engine-ledger` | `devtown` | `app` | trust-weighted agent routing — activates `TrustWeightedAgentStrategy` + `WorkerDecisionEventCapture` |
| `casehub-platform-config` | `devtown` | `app` | YAML-backed preference provider for trust routing policies (`trust-routing.yaml`) |
| `casehub-eidos-api` | `casehub-engine` | `engine-api` | optional capability probe — `AgentDescriptor` on `Worker`; `CapabilityHealth.probe()` in `WorkOrchestrator` |
| `casehub-eidos-api` | `casehub-engine` | `engine-api` / `runtime` | write-path SPI calls: `AgentGraphStore.recordTask()`, `recordOutcome()` from `WorkOrchestrator` (eidos#32) |
| `casehub-platform-api` | `casehub-neural-text` | `rag` | `CurrentPrincipal`, `TenancyConstants` — tenant-scoped corpus isolation |
| `casehub-inference-api` | `casehub-eidos` | `runtime` | `ScalarRegressor` — dynamic epistemic domain confidence estimation (future) |
| `casehub-inference-api` | `casehub-engine` | `runtime` | `NliClassifier` — hallucination detection hook (future, #154) |
| `casehub-engine-api` | `quarkmind` | `quarkmind-agent` | `CaseContext` interface — Phase 1 plugin API migration (quarkmind#193) |
| `casehub-engine-blackboard` | `quarkmind` | `quarkmind-agent` | `CaseContextImpl` — test scope only, for synthetic `CaseContext` construction |
| `casehub-rag-api` | `casehub-engine` | `runtime` | `CaseRetriever`, `ReactiveCaseRetriever` — fact space prompt compiler context injection (future) |
| `casehub-rag-api` | `Hortora/engine` | garden retrieval engine | `CaseRetriever`, `CorpusStore` SPIs — replaces duplicated Qdrant/ingestion code; tenancy via `TenantGuard` (neural-text#35, #36) |
| `casehub-rag` | `Hortora/engine` | garden retrieval engine | RAG pipeline implementation (Qdrant, hybrid RRF, ingestion bridge) |
| `casehub-rag-testing` | `Hortora/engine` | test | In-memory `CorpusStore` + `CaseRetriever` stubs for `@QuarkusTest` isolation |
| `casehub-engine-api` | `casehub-engine-ai` | `ai` | `AgentRoutingStrategy` SPI consumer; `AgentEmbeddingProvider` SPI definition |
| `casehub-desiredstate-api` | `casehub-ops` | `api` | `GoalCompiler`, `NodeProvisioner`, `ActualStateAdapter`, `FaultPolicy`, `EventSource` SPIs |
| `casehub-desiredstate-api` | `casehub-ops` | `infra` | SPI implementations |
| `casehub-desiredstate` (runtime) | `casehub-ops` | `infra` | `DefaultDesiredStateGraphFactory` (test scope) |
| `casehub-platform-agent-api` | `casehub-desiredstate` | `examples/pipeline` | `AgentProvider` SPI for AI_REVIEW fault node LLM diagnosis (desiredstate#37) |
| `casehub-eidos-api` | `casehub-ledger` | CBR subsystem | `CapabilitySpecializationStore` SPI — records DECLINE/FAIL patterns per capability for learned routing exclusion (eidos#55) |
| `casehub-iot-api` | `casehub-ops` | `iot` | `DeviceProvider`, `DeviceRegistry`, `StateChangeEvent`, `DeviceCommand`, `DeviceEntity` hierarchy — IoT desired-state bridge |
| `casehub-platform-api` | `casehub-ops` | `api` | `Path`, `Preferences`, `CurrentPrincipal` |
| `casehub-ops-api` | `casehub-ops` | `deployment` | `NodeDriftChecker` SPI, `ProviderConfig`, deployment node spec types |
| `casehub-eidos-api` | `casehub-ops` | `deployment` | `AgentDescriptor`, `AgentCapability`, `AgentDisposition`, `AgentRegistry` |
| `casehub-qhorus` (runtime) | `casehub-ops` | `deployment` | `ChannelService`, `Channel` JPA entity (provided scope) |
| `casehub-engine-api` | `casehub-ops` | `deployment` | `CaseDefinition`, `TrustRoutingPolicy`, `TrustRoutingPolicyProvider` |
| `casehub-work-api` | `casehub-ops` | `infra` | `WorkItem` generation for human nodes |
| `casehub-ledger-api` | `casehub-ops` | `compliance` | `LedgerEntry` base class for `ComplianceLedgerEntry` |
| `casehub-ledger` (runtime) | `casehub-ops` | `compliance` | JPA entity registration, `LedgerEntryRepository` for evidence persistence and queries |
| `casehub-qhorus-api` | `casehub-engine` | `casehub-engine-inbound` | `MessageObserver`, `MessageReceivedEvent` SPI and event type |
| `casehub-work` (runtime) | `casehub-engine` | `casehub-engine-inbound` | `WorkItemService`, `TenantContextRunner`, `WorkItemCreateRequest` |

| `casehub-platform` | `casehub-aml` | `app` | `@DefaultBean` mocks for casehub-engine CDI wiring (runtime scope — required when engine is present) |
| `casehub-engine` (runtime) | `casehub-aml` | `app` | YamlCaseHub, CaseHubRuntime, engine worker execution |
| `casehub-engine-scheduler-quartz` | `casehub-aml` | `app` | Quartz worker execution for in-process worker functions |
| `casehub-platform-expression` | `casehub-aml` | `app` | JQEvaluator required by engine CDI beans (GE-20260523-86ed13) |
| `casehub-engine-persistence-memory` | `casehub-aml` | `app` | In-memory persistence SPIs for test and tutorial deployment — requires `MemorySubCaseGroupRepository` and `MemoryPlanItemStore` activated via `quarkus.arc.selected-alternatives` in application-tier test properties |
| `casehub-platform-memory-jpa` | `casehub-aml` | `app` | JPA-backed `CaseMemoryStore` for production — Layer 8 prior entity context and SAR outcome memory (aml#32) |
| `casehub-platform-memory-inmem` | `casehub-aml` | `app` | In-memory `CaseMemoryStore` for test isolation — Layer 8 (aml#32) |
| `casehub-platform-memory-inmem` | `casehub-devtown` | `app` | In-memory `CaseMemoryStore` for `@QuarkusTest` isolation (devtown#43) |
| `casehub-platform` | `casehub-drafthouse` | `runtime` | `MockCurrentPrincipal @DefaultBean` — satisfies `CurrentPrincipal` injection in Qhorus JPA stores at Quarkus augmentation time (drafthouse#44) |
| `casehub-engine-ledger` | `casehub-aml` | `app` | Layer 6: trust-weighted routing — activates `TrustWeightedAgentStrategy @ApplicationScoped` and `WorkerDecisionEventCapture`; local V2002/V2003 migrations for `case_ledger_entry` and `worker_decision_entry` join tables (pending engine#395 scoping fix) |
| `casehub-engine-work-adapter` | `casehub-aml` | `app` | Layer 9: `ActionGateWorkItemHandler` + `WorkItemLifecycleAdapter` — oversight gate WorkItem creation and gate approval routing |
| `casehub-engine-blackboard` | `casehub-aml` | `app` | Layer 9: `BlackboardRegistry` — required for gate signal routing; transitive via work-adapter |

| `casehub-platform` | `casehub-clinical` | `runtime` | `@DefaultBean` mocks for casehub-engine CDI wiring |
| `casehub-platform-expression` | `casehub-clinical` | `runtime` | `JQEvaluator` for engine expression evaluation |
| `casehub-engine` | `casehub-clinical` | `runtime` | case orchestration (`CasePlanModel`, IRB gate, AE escalation) |
| `casehub-engine-work-adapter` | `casehub-clinical` | `runtime` | `HumanTaskScheduleHandler` + `WorkItemLifecycleAdapter` |
| `casehub-engine-scheduler-quartz` | `casehub-clinical` | `runtime` | Quartz worker execution (Layer 5) |

| `casehub-qhorus-api` | `casehub-openclaw` | `core` | `ChannelBackend`, `MessageObserver` SPIs |
| `casehub-qhorus` (runtime) | `casehub-openclaw` | `casehub` | Qhorus runtime for SPI registration |
| `casehub-qhorus-api` | `casehub-drafthouse` | `runtime` | `ChannelService`, `MessageService`, `ChannelGateway`, `DataService`, `InstanceService` — channel mesh SPIs |
| `casehub-qhorus` (runtime) | `casehub-drafthouse` | `runtime` | Channel mesh runtime — commitment lifecycle, typed messages |
| `casehub-qhorus-api` | `casehub-drafthouse` | `api` | `ChannelProjection<S>`, `RenderableProjection<S>`, `ProjectionResult<S>`, `MessageView`, `MessageType` — debate projection SPI |
| `casehub-qhorus` (runtime) | `casehub-drafthouse` | `runtime` | `ProjectionService` — channel history fold for LLM context |
| `casehub-engine-api` | `casehub-openclaw` | `casehub` | `WorkerProvisioner`, `CaseChannelProvider`, `WorkerStatusListener` SPI implementations; uses api (not runtime) to avoid engine CDI beans with unsatisfied persistence SPIs |
| `casehub-platform-agent-api` | `casehub-openclaw` | `casehub` | `AgentProvider` SPI, `AgentSessionConfig`, `AgentEvent` — DirectCallBridge agent provider (openclaw#49) |
| `langchain4j-core` | `casehub-openclaw` | `casehub` | `ChatModel` interface — `OpenClawChatModel` bridges langchain4j to `AgentProvider` (openclaw#49) |
| `casehub-worker-api` | `casehub-engine` | `runtime` | `Worker`, `Capability`, `WorkerFunction` — worker identity on the execution path (engine#543) |
| `casehub-worker-api` | `casehub-desiredstate` | `runtime` | `Worker`, `Capability` — node provisioning in desiredstate graph (desiredstate#41) |
| `casehub-engine-api` | `casehub-workers` | `common`, `camel`, `http`, `github-actions` | Worker dispatch SPI types |
| `casehub-engine-common` | `casehub-workers` | `common`, `camel`, `http`, `github-actions` | `WorkerExecutionManager`, `CaseInstance`, shared execution types |
| `casehub-platform-api` | `casehub-workers` | `http` | `CurrentPrincipal` — HTTP request context |
| `casehub-platform-api` | `casehub-openclaw` | `core` | `CurrentPrincipal`, `GroupMembershipProvider` (permission-aware context) |
| `casehub-qhorus-api` | `casehub-blocks` | (root) | Channel and message SPIs for structured conversation and channel dispatch |
| `casehub-work-api` | `casehub-blocks` | (root) | WorkItem types for oversight gate coordination |
| `casehub-engine-api` | `casehub-blocks` | (root) | Case orchestration SPIs for context tracking and gate signal routing |
| `casehub-blocks` | `casehub-drafthouse` | `runtime` | (planned) Structured conversation, channel dispatch |
| `casehub-blocks` | `claudony` | `casehub` | (planned) Oversight gate, context tracking |
| `casehub-blocks` | `casehub-openclaw` | `casehub` | (planned) Oversight gate, channel dispatch |
| `casehub-blocks` | `casehub-aml` | `app` | (planned) Oversight gate, context tracking |
| `casehub-blocks` | `casehub-clinical` | `runtime` | (planned) Oversight gate, structured conversation |
| `casehub-blocks` | `casehub-life` | `app` | (planned) Context tracking, channel dispatch |
| `casehub-ledger` (runtime) | `casehub-life` | `app` | Merkle audit, GDPR erasure, trust scoring |
| `casehub-work` (runtime) | `casehub-life` | `app` | WorkItems with SLA and escalation |
| `casehub-qhorus` (runtime) | `casehub-life` | `app` | commitment lifecycle, oversight channel |
| `casehub-engine` (runtime) | `casehub-life` | `app` | CasePlanModel orchestration |
| `casehub-engine-work-adapter` | `casehub-life` | `app` | HumanTaskScheduleHandler + WorkItemLifecycleAdapter |
| `casehub-engine-scheduler-quartz` | `casehub-life` | `app` | Quartz worker execution |
| `casehub-connectors-core` | `casehub-life` | `app` | household notifications (contractor, carer alerts) |
| `casehub-platform` | `casehub-life` | `app` | `@DefaultBean` mocks (runtime scope) |
| `casehub-platform-expression` | `casehub-life` | `app` | `JQEvaluator` for engine |
| `casehub-openclaw-casehub` | `casehub-life` | `app` | OpenClaw WorkerProvisioner (Layer 7) |
| `casehub-engine-ledger` | `casehub-life` | `app` | Trust-weighted agent routing — activates `TrustWeightedAgentStrategy` + `WorkerDecisionEventCapture` (Layer 6) |
| `casehub-platform-config` | `casehub-life` | `app` | YAML-backed preference provider for trust routing policies (`trust-routing.yaml`) (Layer 6) |

**Application tier** (aml, clinical, life) — consume foundation runtime artifacts; see [APPLICATIONS.md](APPLICATIONS.md) for detail.

---

## Capability Ownership — "Where Does X Live?"

| Capability | Owner | Notes |
|---|---|---|
| Hierarchical scope/label path | `casehub-platform-api` | `Path` record — strict segment validation, `isAncestorOf`, `parent`, `depth`. Construct with `Path.of(String...)` (explicit segments) or `Path.parse(String)` (configurable separator via `casehub.platform.path.separator`, default `/`). **Convention for harnesses:** `Path.of("casehubio", "<app>", "<case-type>")` — e.g. `Path.of("casehubio", "devtown", "pr-review")`. Org segment first, app second, case-type third. This makes the inheritance chain work correctly: devtown inherits from casehubio, pr-review inherits from devtown. |
| Typed preference resolution | `casehub-platform-api` | `PreferenceProvider` SPI + `Preferences` interface; `PreferenceKey<T extends Preference>` typed key with `qualifiedName()`; `SettingsScope(Path, Instant)`; `MapPreferences` utility impl. `MockPreferenceProvider` `@DefaultBean`. See `casehub/garden: docs/protocols/casehub/typed-preference-keys.md`. **Backends (add as compile dep to activate):** `casehub-platform-config` — YAML file-based, `@ApplicationScoped`, no DB; `casehub-platform-persistence-jpa` — JPA/SQL, `@ApplicationScoped`, requires Flyway at `classpath:db/platform/migration`; `casehub-platform-persistence-mongodb` — MongoDB, `@Alternative @Priority(1)`, beats JPA when co-deployed, startup bean creates scope index. CDI priority ladder: see `casehub/garden: docs/protocols/universal/persistence-backend-cdi-priority.md`. |
| IoT → CloudEvent adapter | `casehub-iot-api` | `IoTCloudEventAdapter` — `@ObservesAsync StateChangeEvent`, produces `CloudEvent` via `Event<CloudEvent>.fireAsync()`. Event type: `io.casehub.iot.state_change.<deviceClass>` (reverse-DNS). First casehub-iot-api dependency on casehub-platform-api (iot#19). |
| WorkItem → CloudEvent adapter | `casehub-work` runtime | `WorkCloudEventAdapter` — `@ObservesAsync WorkItemLifecycleEvent` + `WorkItemGroupLifecycleEvent`, produces `CloudEvent` via `Event<CloudEvent>.fireAsync()`. Event types: `io.casehub.work.workitem.*` (24 types), `io.casehub.work.group.*` (3 types). Dual-channel emitter (`WorkItemLifecycleEmitter`, `WorkItemGroupLifecycleEmitter`) enforces `fire()` + `fireAsync()` at all sites. Ships work#273. |
| Typed async event envelope (CloudEvents) | `casehub-platform-api` | `io.cloudevents.CloudEvent` (CNCF CloudEvents Java SDK, `cloudevents-core` compile dep) as the platform CDI event type. Producers fire `Event<CloudEvent>.fireAsync()`; consumers observe `@ObservesAsync CloudEvent`. Standard fields: `type` (reverse-DNS, e.g. `io.casehub.iot.temperature`), `source` (logical producer URI), `subject` (entity the event concerns — `device/id`, `channel/id`), `id`, `time`, `data`. `tenancyid` extension attribute carries tenant ID. Produced by: `platform-streams-*` modules (external transports), `casehub-iot` (StateChangeEvent adapter), `casehub-qhorus` (MessageReceivedEvent adapter), `casehub-connectors` (InboundMessage adapter), `casehub-work` (WorkItemLifecycleEvent + WorkItemGroupLifecycleEvent adapter, work#273). Consumed by: `casehub-ras` (situational awareness), any future observer. Ships platform#98. |
| Async tenancy context (stream processing) | `casehub-platform-api` | `StreamContext` SPI — `tenancyId()`. The async equivalent of `CurrentPrincipal` for stream processing chains where CDI request scope is inactive. Stream modules extract `tenancyid` from CloudEvent extension attribute at ingestion boundary and propagate via `StreamContext`. `NoOpStreamContext @DefaultBean @ApplicationScoped` in `casehub-platform`. **Design deferred to P1.8** — `@DefaultBean` returning `DEFAULT_TENANT_ID` silently corrupts multi-tenant stream deployments; propagation mechanism requires Mutiny context or CDI scope solution. |
| External event stream ingestion | `casehub-platform` (submodules) | Five classpath-activated stream modules — each fires `Event<CloudEvent>.fireAsync()` and discovers targets from `EndpointRegistry`. `platform-streams-kafka` (SmallRye reactive messaging, static topics); `platform-streams-amqp` (AMQP reactive messaging); `platform-streams-webhook` (REST POST, CloudEvents HTTP binding); `platform-streams-poll` (@Scheduled + REST client, polls EndpointRegistry HTTP endpoints); `platform-streams-camel` (observes `@ObservesAsync EndpointRegistered` for `EndpointProtocol.CAMEL` only — adds Camel routes via `CamelContext.addRoutes()` when new CAMEL endpoints are registered; the dynamic topology path). Ships platform#98. |
| Named endpoint registry | `casehub-platform-api` | `EndpointRegistry` SPI — register/resolve/discover/deregister named endpoints by `(Path, tenancyId)`. `EndpointProtocol` enum (HTTP, GRPC, KAFKA, AMQP, MCP, CAMEL, QHORUS). Protocol-specific properties in `Map<String,String>`; shared keys in `EndpointPropertyKeys` (`URL`, `TOPIC`, `STREAM_EVENT_TYPE`). `credentialRef` for secrets backend integration (resolution deferred). Platform-global endpoints use `TenancyConstants.PLATFORM_TENANT_ID`. `NoOpEndpointRegistry @DefaultBean` in `casehub-platform`; `InMemoryEndpointRegistry @Alternative @Priority(100)` in `casehub-platform-endpoints-memory`. JPA backend deferred. `EndpointPermissions.assertTenant(tenancyId, principal)` — write-auth utility for runtime endpoint registration; 2-arg form only (platform#89). YAML-backed endpoint populator: `casehub-platform-endpoints-config` — `@Startup @ApplicationScoped`, reads `casehub.platform.endpoints.files`, `${VAR}` interpolation, multi-file support (platform#88). Shipped platform#73; extended platform#88+#89. |
| HTTP inbound tenant routing | `casehub-qhorus` | `QhorusInboundCurrentPrincipal @DefaultBean @ApplicationScoped` reads `X-Tenancy-ID` header via `TenancyContextFilter @PreMatching` and populates `CurrentPrincipal.tenancyId()` for all HTTP requests. `@ApplicationScoped` (not `@RequestScoped`) so the `ContextNotActiveException` catch is reachable for background threads. `X-Tenancy-ID` is NOT a security boundary — trust from network policy only. Displaced by any `@Alternative` (test fixtures, `OidcCurrentPrincipal`). Test deployments with both qhorus runtime and casehub-platform must add `quarkus.arc.exclude-types=io.casehub.platform.mock.MockCurrentPrincipal` to prevent CDI ambiguity. Refs qhorus#269. |
| Current principal identity | `casehub-platform-api` | `CurrentPrincipal` SPI — `actorId()`, `groups()`, `roles()` (= groups by convention, wires to `@RolesAllowed`), `hasGroup()`, `isSystem()`, `isAuthenticated()`, `tenancyId()`, `isCrossTenantAdmin()`. Real impls must be `@RequestScoped`. `MockCurrentPrincipal` `@DefaultBean`. `TenancyConstants` holds `DEFAULT_TENANT_ID` and `PLATFORM_TENANT_ID` sentinels. **OIDC impl:** `casehub-platform-oidc` ships `OidcCurrentPrincipal @RequestScoped` — reads actorId/groups from `SecurityIdentity`, `tenancyId` and `crossTenantAdmin` from fixed JWT claims. Add as compile dep to activate; displaces mock automatically. |
| RBAC enforcement (`@RolesAllowed`) | `casehub-platform-oidc` | Infrastructure implemented. `roles()` delegates to `groups()` — CaseHub group names map directly to `@RolesAllowed` without a bridge. Activate by adding `casehub-platform-oidc` as compile dep; `SecurityIdentityAugmentor` bridges `GroupMembershipProvider` to `SecurityIdentity.getRoles()`. **Adoption pending** — no harness has wired this yet; annotations are inert without the OIDC module on classpath (devtown#71 tracks first adoption). |
| Group membership lookup | `casehub-platform-api` | `GroupMembershipProvider` SPI — `membersOf(groupName)` returns `Set<GroupMember>` (actorId = OIDC sub = SCIM value UUID, displayName = human label). Empty set = group unknown or has no members. `MockGroupMembershipProvider @DefaultBean` returns empty. **Real implementation:** `casehub-platform-scim` (`@ApplicationScoped`, displaces mock by classpath presence) — SCIM 2.0 two-step fetch, `@CacheResult`, static bearer token or OIDC client-credentials auth. |
| Agent memory (queryable, permission-aware, persistent) | `casehub-platform-api` (SPI + types) / `casehub-platform` (adapters) | `CaseMemoryStore` SPI + value types (`MemoryInput`, `Memory`, `MemoryQuery`, `EraseRequest`, `MemoryDomain`) + `MemoryPermissions` static utility. `eraseById(memoryId, entityId, tenantId)` — 3-arg; entity mismatch is a silent no-op (platform#64). `eraseEntity(entityId, tenantId)` returns `int` count for GDPR Art.5(2) audit (platform#72). `eraseEntityAcrossTenants(entityId, Set<String> tenantIds)` — GDPR Art.17 cross-tenant entity wipe; requires `isCrossTenantAdmin()`; `CROSS_TENANT_ERASE` `MemoryCapability`; `MemoryPermissions.assertCrossTenantAdmin(principal)` (1-arg, no async bypass); `NoOpCaseMemoryStore` returns 0 and does not declare `CROSS_TENANT_ERASE`; JDBC adapters (JPA, SQLite) use single optimized `DELETE IN` query (SQLite chunked at 500 for `SQLITE_LIMIT_VARIABLE_NUMBER`); REST adapters (Mem0, Graphiti) use sequential loop — idempotent/retry-safe (platform#99). `MemoryPermissions.assertTenant(tenantId, principal, requestContextActive)` — 3-arg async-aware form; skip principal check when CDI request scope inactive (platform#79). `GraphCaseMemoryStore` — graph-native SPI extension in `platform-api`, extends `CaseMemoryStore`, adds `graphQuery(GraphMemoryQuery)` for temporal graph queries. `MemoryCapability` enum — self-description mechanism: adapters declare `capabilities()`, callers use `requireCapability()` for typed exceptions. `NoOpCaseMemoryStore @DefaultBean` in `casehub-platform`; adapters as submodules: `memory-inmem/` (@Alternative @Priority(1) volatile ConcurrentHashMap — add test-scope for @QuarkusTest isolation; compile for ephemeral installs), `memory-jpa/` (@ApplicationScoped PostgreSQL + Flyway V1000 + FTS via websearch_to_tsquery when question provided — add compile-scope for persistence), `memory-sqlite/` (@Alternative @Priority(1) SQLite + HikariCP WAL + FTS5 via MATCH + rank — add compile-scope for durable single-process deployments. Configure `casehub.memory.sqlite.path`), `memory-mem0/` (@Alternative @Priority(1) Mem0 REST adapter — vector embeddings + semantic search via POST /search; infer:false preserves 1:1 store()/memoryId contract; compound user_id for tenant isolation; see platform#33), `memory-graphiti/` (@Alternative @Priority(2) Graphiti REST `GraphCaseMemoryStore` — temporal knowledge graph (Neo4j/FalkorDB/Kuzu), LLM entity extraction (async); configure `quarkus.rest-client.graphiti.url`, `casehub.memory.graphiti.api-key`). `ReactiveCaseMemoryStore` (Mutiny SPI) lives in `casehub-platform-api`. `BlockingToReactiveBridge @DefaultBean` in `casehub-platform` wraps blocking adapters as `ReactiveCaseMemoryStore`; native async adapters override as `@Alternative @Priority(N)`. Emission: direct injection is canonical — inject `CaseMemoryStore` and call `store()` from the domain event handler. See SPI Javadoc for thread-context and transaction atomicity guidance. **Application-tier consumers:** `casehub-aml` — prior entity context + SAR outcomes (aml#32); `casehub-devtown` — contributor history, reviewer agent context, and code-area history on PR review cases (devtown#43). |
| Task-scoped and multi-turn agent invocation (Claude CLI) | `casehub-platform-agent-api` (SPI) / `casehub-platform-agent-claude` (impl) | `AgentProvider` SPI — `run(AgentSessionConfig) → Multi<AgentEvent>`. Streams token-level `TextDelta` events from a Claude CLI subprocess. Concurrent-session semaphore (configurable). Wall-clock timeout. `NoOpAgentProvider @DefaultBean` in `casehub-platform`. Claude impl: `ClaudeAgentProvider @ApplicationScoped` + `ClaudeAgentClient @Startup` in `agent-claude/` — activates by classpath presence, requires Claude CLI. Package: `io.casehub.platform.agent`. **Multi-turn sessions (platform#58):** `AgentSession` interface in `agent-api/` — serial `query()`/`interrupt()`/`close(Duration)`; `AgentProvider.openSession(AgentSessionInit)` factory. `AgentSessionInit` carries systemPrompt, mcpServers, timeout, correlationId (no userPrompt — passed per-turn). `ClaudeAgentSession` in `agent-claude/` — IDLE/ACTIVE/CLOSED state machine; per-turn wall-clock timeout; true-drain `close(Duration)`; `interrupt()` fire-and-forget (TOCTOU-guarded); semaphore held for session lifetime. `NoOpAgentSession` in `platform/` returned by `NoOpAgentProvider.openSession()`. Note: SPI lives in `casehub-platform-agent-api` (not `platform-api`) — implementation-specific to the Claude agent SDK; does not qualify for `platform-api` (requires multiple peer-repo consumers — see protocol `platform-api-scope.md`). **Two subprocess paths in `agent-claude/`:** `invoke()` (single-turn) uses `ClaudeOneShotProcess` — direct `ProcessBuilder` one-shot subprocess; starts eagerly in constructor; `destroyForcibly()` is immediate (no grace period); fixes zombie subprocess accumulation when parallel `invoke()` calls all timeout simultaneously (eidos#52). `openSession()` (multi-turn) uses `ClaudeAgentSession` backed by `org.springaicommunity:claude-code-sdk` — SDK session mode. **SDK choice note applies to `openSession()` only:** `claude-code-sdk` runs Claude's tool loop autonomously (tool calls opaque, hence `AgentEvent` only has `TextDelta`), provides native prompt caching (70–80% cost reduction). `ClaudeAgentClient` CDI constructor requires `ObjectMapper` alongside `ClaudeAgentProperties` — direct wiring without `ObjectMapper` fails CDI augmentation. **`agent-langchain4j/` shipped (platform#100, renamed platform#105):** bidirectional LangChain4j interop — `ChatModelAgentProvider` (any ChatModel → AgentProvider) + `AgentProviderChatModel` (any AgentProvider → ChatModel). No longer Claude-specific. `@Alternative @Priority(10) @ApplicationScoped`. **Incompatible with `engine.Agent`** which always forces `ResponseFormatType.JSON`. `casehub.platform.agent.langchain4j.closeTimeout` (default PT30S). No quarkus:build goal — library module. See `docs/repos/casehub-platform.md §Agent Infrastructure`. |
| Actor workload state view | `casehub-engine-actor-state` | `GET /actors/{actorId}/state` — assembles trust scores (ledger), active WorkItems (work), open Commitments (qhorus), and active Quartz cases (engine) via `ActorStateContributor` SPI. New contributors activate by CDI discovery. Add `casehub-engine-actor-state` as a compile dep to activate. |
| Actor state aggregation SPI | `casehub-platform-api` | `ActorStateContributor` + `ActorStateAccumulator` — stdlib types only (UUID, Instant, primitives). First use-case-specific SPI in platform-api; placed here because it is needed by ≥4 peer repos and no single domain api can host it. See ADR. |
| Immutable entry chain (Merkle Mountain Range) | `casehub-ledger` | Domain-agnostic; consumers extend `LedgerEntry` via JPA JOINED |
| In-memory persistence (zero datasource / ephemeral install) | `casehub-ledger` | `casehub-ledger-memory` — `@Alternative @Priority(1)` impls of all persistence SPIs; add as compile dep for `@QuarkusTest` isolation |
| Cryptographic tamper evidence | `casehub-ledger` | `LedgerVerificationService` (Merkle: treeRoot/inclusionProof/verify), `AgentSignatureVerificationService` (blocking Ed25519), `ReactiveAgentSignatureVerificationService` (reactive Ed25519), `AgentCryptographicVerifier` (shared static utility) |
| Actor trust scoring (Bayesian Beta + EigenTrust) | `casehub-ledger` | `ActorTrustScore` — four score types: GLOBAL, CAPABILITY, DIMENSION, CAPABILITY_DIMENSION (✅ #76); nightly `TrustScoreJob` + optional per-attestation `IncrementalTrustUpdateObserver` (ledger#115, opt-in via `casehub.ledger.trust-score.incremental.enabled`); `TrustScoreRoutingPublisher` CDI events + `TrustScoreActorUpdatedEvent` (incremental path) |
| Trust score export read-model | `casehub-ledger` | `TrustExportService` (`exportAll`/`exportActor`/`exportDelta`) — consumed by dashboards and upper layers |
| Trust score import SPI | `casehub-ledger` | `TrustImportService` SPI; `JpaTrustImportService` seed-if-absent `@Alternative`; `NoOpTrustImportService` `@DefaultBean` |
| Trust bootstrapping | `casehub-ledger` | `TrustBootstrapSource` SPI + `TrustBootstrapService`; seeds Beta(α,β) from external source on actor first-registration; opt-in via `casehub.ledger.trust-score.bootstrap.enabled` |
| GDPR Art.17 erasure / Art.22 decision records | `casehub-ledger` | `LedgerErasureService`, `ComplianceSupplement`, `ErasureReceiptLedgerEntry` (opt-in: `casehub.ledger.erasure-receipt.enabled=true`; `ErasureReason` enum: `GDPR_ART_17_REQUEST \| RETENTION_EXPIRED \| ACCOUNT_DELETION`; `ErasureResult` carries `Optional<UUID> receiptEntryId`; activate `JpaErasureReceiptRepository @Alternative` via `quarkus.arc.selected-alternatives`) |
| W3C PROV-DM lineage export | `casehub-ledger` | `LedgerProvExportService` |
| OTel trace linkage to audit entries | `casehub-ledger` | `LedgerTraceListener` auto-populates `traceId` from active OTel span |
| Ledger entry enrichment pipeline | `casehub-ledger` | `LedgerEnricherPipeline` — CDI-discovered `LedgerEntryEnricher` implementations run at persist time; enrichers add domain-specific metadata to entries without coupling ledger to domain types |
| Actor DID/VC resolution | `casehub-ledger` | `ActorDIDProvider` SPI — resolves a DID and public key from an `actorId`. `ScimActorDIDProvider @Alternative` is the SCIM 2.0 implementation (activate with `quarkus.arc.selected-alternatives`). `ReactiveAgentIdentityVerificationService` for async Ed25519 DID verification. |
| Human task inbox (WorkItem lifecycle) | `casehub-work` | 10 statuses, SLA, delegation, escalation, spawn. `DELEGATED`: pre-acceptance — forwarded to named actor who must accept (`PUT /workitems/{id}/accept-delegation`) or decline (`PUT /workitems/{id}/decline-delegation`); non-terminal. `DELEGATION_DECLINED` fires `AssignmentTrigger` for re-routing; `DeclineTarget` scope preference (`casehub.work.delegation.decline-target`: POOL/DELEGATOR, default POOL) controls where declined item returns. `EXPIRED` and `ESCALATED` are both terminal. `BreachDecision.Exhausted(String reason)`: returned when all `Chained` SLA policy branches fail — sets status to `ESCALATED`. |
| SLA breach policy | `casehub-work-api` | `SlaBreachPolicy` SPI — replaces `EscalationPolicy`; returns `BreachDecision` (Fail / EscalateTo / Extend) with `thenOnBreach` fallback chaining; `SlaBreachContext(BreachType, BreachedTask, Path, Preferences)`; casehub-work executes the decision, fires `SlaBreachEvent` CDI event for side-effect observers. See casehubio/work#213 |
| Named outcome classifications for WorkItems | `casehub-work` | `Outcome` record in `casehub-work-api`; `WorkItemTemplate.outcomes` declares valid names; `WorkItem.outcome` stores resolved name at completion; `WorkItemLifecycleEvent.outcome` carries it for engine routing without parsing `resolution` JSON |
| Conflict-of-interest user exclusion | `casehub-work` | `ExclusionPolicy` SPI in `casehub-work-api` (`check() : PolicyDecision`); `CommaSeparatedExclusionPolicy` `@DefaultBean`; `excludedUsers` TEXT field on `WorkItemTemplate` + `WorkItem`; enforced at claim, create (assigneeId), delegate, auto-assignment, and `SelectionContext`; `BlockedAttemptAuditService` writes `CLAIM_DENIED`/`DELEGATE_DENIED` audit entries via `REQUIRES_NEW` |
| M-of-N parallel WorkItem completion (group policy primitive) | `casehub-work` | `MultiInstanceCoordinator`; `WorkItemGroupLifecycleEvent`; see LAYERING.md |
| Human task routing / selection | `casehub-work-core` | `WorkBroker`, `WorkerSelectionStrategy` SPI; `SemanticWorkerSelectionStrategy` in `casehub-work-ai` (`@Alternative @Priority(1)`) |
| Label-based queue views | `casehub-work-queues` | Optional module on casehub-work |
| Agent routing / selection | `casehub-engine-api` | `AgentRoutingStrategy` SPI; CDI priority resolution in `WorkOrchestrator` (`@Any Instance<AgentRoutingStrategy>`). Implementations: `LeastLoadedAgentStrategy` (engine runtime, `@Priority(0)` default), `TrustWeightedAgentStrategy` (casehub-engine-ledger, `@Priority(1)`), `SemanticAgentRoutingStrategy` (casehub-engine-ai, `@Priority(2)`, optional) |
| Implementation routing / selection (competing `TaskDefinition` implementations for the same capability) | `casehub-engine` — **gap, not yet implemented** | When multiple `TaskDefinition` beans implement the same capability interface (e.g. three `StrategyTask` implementations), the engine must select among them using the same trust-maturity four-phase model as `TrustWeightedAgentStrategy`. This is symmetric to agent routing but operates over implementations, not workers. Application-layer workarounds (see QuarkMind `StrategyTrustRouter`) must migrate here once the SPI exists. Track as `casehub-engine` issue. See [`docs/CBR-CAPABILITY.md`](CBR-CAPABILITY.md) §Reuse. |
| Case-Based Reasoning (CBR) — Retrieve / Reuse / Revise / Retain | Cross-cutting — see [`docs/CBR-CAPABILITY.md`](CBR-CAPABILITY.md) | Four-step AI pattern: **Retain** (`casehub-ledger` + `CaseMemoryStore`), **Retrieve** (`casehub-neural-text` `CaseRetriever` SPI), **Reuse** (`casehub-engine` routing — agent: ✅; implementation: gap), **Revise** (adaptive plan templates — gap). Every harness application is a natural CBR system. QuarkMind is the reference implementation at game-loop granularity. Full capability map and per-repo responsibilities in `docs/CBR-CAPABILITY.md`. |
| Agent embedding vector provider | `casehub-engine-ai` | `AgentEmbeddingProvider` SPI — required by `SemanticAgentRoutingStrategy`; activates semantic agent routing when on classpath (see `casehub/garden: docs/protocols/optional-module-pattern.md`). SPI lives in `casehub-engine-ai` (not `casehub-engine-api`) so the entire feature is opt-in — no embedding provider contract imposed on deployments that don't use semantic routing. |
| IoT device abstraction (typed device hierarchy, state events, command dispatch) | `casehub-iot` | `DeviceProvider` SPI — reactive `Uni<>` returns: `discover()`, `dispatch(DeviceCommand)`, `status()`. `DeviceRegistry` SPI (`findById`, `findByClass`, `findAll`, `refresh()`). `StateChangeEvent` (CDI `fireAsync`) carries before/after `DeviceEntity` + `changedCapabilities` set. Common device classes aligned with Matter vocabulary: `SwitchDevice`, `LightDevice`, `ThermostatDevice`, `SensorDevice`, `PresenceSensor`, `PowerSensor`, `LockDevice`, `CoverDevice`, `MediaPlayerDevice`, `FanDevice`. Vendor supplements in `homeassistant` and `openhab` extend common types for unmappable fields only. Bridge: `iot-bridge` (local agent — event relay with CDI filter chain) + `iot-bridge-server` (`BridgeDeviceProvider implements DeviceProvider` — remote devices look local to cloud consumers via DeviceProvider SPI). `DeviceTypeIdResolver` for compound type ID serialization. 6 deployment topologies (SaaS, hybrid, multi-site, constrained edge, dev, multiple consumers). **`api` is a public API — semver from first release. Note:** `api` now includes Jackson annotations for `DeviceTypeIdResolver` (no longer zero-framework-dependency). |
| Worker primitives (`Worker`, `Capability`, `WorkerFunction`, `WorkerResult`, `WorkerOutcome`, `PlannedAction`) | `casehub-worker` | `casehub-worker-api` — pure-Java value types + `WorkerFunction` interface (no Quarkus, no JPA). Add `casehub-worker-api` as a compile dep; add `casehub-worker-testing` in test scope for `MockWorkerExecutor` and `TestWorkerBuilder`. Consumed by `casehub-engine` (worker execution path) and `casehub-desiredstate` (node provisioning). |
| Worker runtime lifecycle (init, shutdown, status, capability discovery) | `casehub-workers` | `WorkerRuntime` SPI + `WorkerRuntimeStatus` enum in `workers-common`. `WorkerLifecycleOrchestrator` drives CDI discovery and lifecycle. All four worker types implement `WorkerRuntime`. |
| Worker dispatch (HTTP, Camel, GitHub Actions, MCP) | `casehub-workers` | `workers-common`: `WorkerDispatcher` SPI, `PermanentFaultException`, `RetryAfterException` (shared across all worker types). `workers-camel`: `WorkerCamelDispatcher` — dispatches via Apache Camel routes. `workers-http`: `WorkerHttpDispatcher` — dispatches via HTTP POST; depends on `casehub-platform-api`. `workers-github-actions`: `WorkerGitHubActionsDispatcher` — dispatches to GitHub Actions via `workflow_dispatch` + `repository_dispatch` REST APIs; PAT-based auth (Tier 1 static config). `workers-mcp`: MCP tool dispatch + dynamic tool discovery via `tools/list` at startup (`discovery=auto` default, `discovery=manual` for config-only). |
| Outbound notifications (Slack, Teams, SMS, email) | `casehub-connectors` | `Connector` SPI; `casehub-work-notifications` must delegate here |
| MCP notification tools (LLM agent surface) | `casehub-connectors-mcp` | `send_slack`, `send_teams`, `send_sms`, `send_whatsapp`, `send_email`, `send_slack_bot` (bot-token Slack posting, returns `ts` for thread replies), `list_channels` (aggregates all `ConnectorDiscovery` beans) MCP tools for Quarkus MCP server. `ConnectorMeshBridge` SPI bridges successful delivery to a configured Qhorus delivery channel as a STATUS message (no-op default; Qhorus impl activates by classpath presence via qhorus#249; configure `casehub.qhorus.connector-backend.delivery-channel`). |
| Connector target discovery | `casehub-connectors-core` | `ConnectorDiscovery` SPI — optional interface CDI beans implement when their targets are discoverable (`connectorId()`, `discover() → List<DiscoveredTarget>`). `SlackBotClient` is the reference implementation (discovers Slack channels via `conversations.list`). `list_channels` MCP tool aggregates all registered `ConnectorDiscovery` beans. |
| Inbound message reception (webhook push + IMAP pull) | `casehub-connectors` | `WebhookInboundConnector` SPI (push); `InboundConnector` SPI + `InboundConnectorService` polling (pull); fires `Event<InboundMessage>` CDI event; `casehub-connectors-email-inbound` for IMAP via `EmailInboundAccountProvider` SPI |
| Agent-to-agent messaging (typed channels + messages) | `casehub-qhorus` | 9 speech-act types, 5 channel semantics, MCP tools. All writes flow through `MessageService.dispatch(MessageDispatch)` — single gate for ACL, rate limit, LAST_WRITE, ledger, and fan-out. `MessageDispatch` builder carries sender, type, content, correlationId, inReplyTo, artefactRefs, target, actorType, deadline; builder validates protocol invariants at `build()` (DONE/DECLINE/FAILURE/HANDOFF/RESPONSE require inReplyTo + correlationId; HANDOFF requires target). `DispatchResult` carries ledgerEntryId, subjectId, causedByEntryId, parentReplyCount. |
| Dashboard read/write API (composed views: channel with message count, instance with capability tags, timeline mapping, human message send) | `casehub-qhorus` | `QhorusDashboardService` in `io.casehub.qhorus.runtime.dashboard` — inject this for dashboard/UI consumers needing composed views. Do NOT inject raw entity services for this use case. |
| Channel message fan-out to external backends | `casehub-qhorus` | `ChannelBackend` SPI in `casehub-qhorus-api`; implementations in consuming repos (Claudony panel, connectors) |
| Real-time channel feed to Claudony browser panel | `claudony` | `ClaudonyChannelBackend` implements `ChannelBackend` SPI — per-channel scope; ticks `ChannelEventBus` on `post()`, driving SSE delivery via `MeshResource.channelEvents()`. WebSocket is for terminal streaming only. |
| Cross-cutting message notification | `casehub-qhorus` | `MessageObserver` SPI in `casehub-qhorus-api`; `InProcessMessageBus` CDI default (`Scope.LOCAL`); `FleetMessageRelayObserver` in claudony (`Scope.CLUSTER`) — relays a channel-name tick to all healthy fleet peers on every Qhorus message dispatch, enabling real-time SSE delivery across fleet nodes (claudony#118) |
| Inbound message → WorkItem bridge | `casehub-engine-inbound` | Optional module — `InboundWorkItemBridge implements MessageObserver`; delegates to consumer-provided `InboundWorkItemPolicy @FunctionalInterface` SPI. Inert without a policy bean. Activated by classpath presence. At-most-once delivery. |
| Human-participating channel backend | `casehub-qhorus` | `HumanParticipatingChannelBackend` SPI — extended `ChannelBackend` for channels where humans receive and respond to messages. Implementations route to messaging apps via `casehub-connectors` or directly via vendor clients. `SlackChannelBackend` (`casehub-qhorus-slack-channel`) uses `SlackBotClient` directly for thread-aware Slack delivery without the generic connector path (qhorus#261). |
| Qhorus MCP tool surface | `casehub-qhorus` | Six capability groups exposed as MCP tools for LLM agents: channel management, message dispatch, commitment tracking, instance queries, oversight gates, projection queries. `QhorusMcpTools` and `ReactiveQhorusMcpTools` — do NOT call from internal service code (see Boundary Rules). Uses `@McpServer("qhorus")` named server scoping (see convention below). |
| Agent commitment/obligation tracking | `casehub-qhorus` | `Commitment` with 7-state lifecycle |
| Normative audit of all agent interactions | `casehub-qhorus` | `MessageLedgerEntry` extends `LedgerEntry`; all 9 speech-act types recorded |
| Channel read-model projection (left-fold over message history) | `casehub-qhorus` | `ChannelProjection<S>` SPI + `ProjectionService` in runtime; incremental re-projection via `ProjectionResult<S>` cursor (`lastMessageId`); reactive parity via `ReactiveProjectionService` (build-gated) |
| YAML dashboard rendering (pages framework) | `casehub-pages` | TypeScript/Yarn foundation module. Embedded via iframe in runtime consumers (claudony, drafthouse, devtown, life, aml). Exports dataset schema (`casehub-pages-dataset` wire contract), component API (`ComponentController`, `ComponentApi`), form system (input bindings, save handlers), and tree navigation. No casehub upstream dependencies — independent foundation tier. Zero build-time coupling; runtime-only consumption via iframe embedding. See casehubio/casehub-pages#24. |
| Case/process orchestration (choreography + WAITING) | `casehub-engine` | `CaseInstance`, `EventLog`, `WorkOrchestrator` |
| Workflow-based worker execution (Serverless Workflow steps dispatching casehub workers) | `casehub-engine-flow` | Optional module — add as compile dep to activate. `FlowWorkerExecutor @ApplicationScoped` displaces `NoOpWorkflowExecutor @DefaultBean` by classpath presence. Use `Worker(Workflow)` in case definitions when a worker step should be executed as a Serverless Workflow (quarkus-flow). Non-blocking: Quartz fires `workflowExecutor.execute()` and returns immediately; success/failure arrives via event bus. FuncDSL: `CasehubFlow` helper. YAML: `call: casehub:dispatch` steps via `CasehubCallableTaskBuilder`. **Depends on `casehub-engine-common` only** — does not pull in the full engine runtime. See `docs/repos/casehub-engine.md`. |
| Agent mesh channel topology (normative layout) | `casehub-engine-api` (`io.casehub.api.spi.mesh`) | `CaseChannelLayout` SPI + `ChannelSpec` record + `named()` factory. Standard implementations: `NormativeChannelLayout` (3-channel: work/observe/oversight) and `SimpleLayout` (2-channel: work/observe, no governance gate). Extracted from claudony in parent#93. Use `CaseChannelLayout.named("normative"\|"simple")` for config-driven selection. `CaseDefinition definition` param is intentionally null at all current call sites — forward-looking extensibility for per-definition topology (claudony#87). Protocol: `casehub/garden: docs/protocols/casehub/normative-channel-layout-single-source.md`. |
| Agent mesh participation strategy | `casehub-engine-api` (`io.casehub.api.spi.mesh`) | `MeshParticipationStrategy` SPI — `strategyFor(String workerId, UUID caseId)` returns `MeshParticipation` (ACTIVE/REACTIVE/SILENT). Standard implementations: `ActiveParticipationStrategy`, `ReactiveParticipationStrategy`, `SilentParticipationStrategy`. Use `MeshParticipationStrategy.named("active"\|"reactive"\|"silent")` for config-driven selection. Null caseId is valid (strategy consulted before case exists). Extracted from claudony in parent#93. |
| Worker provisioner SPIs (provision, lifecycle, channels, context) | `casehub-engine` (defines) / `claudony` (implements) | `WorkerProvisioner`, `CaseChannelProvider`, `WorkerContextProvider`, `WorkerStatusListener`. **`postToChannel` is 6-param** (engine#343): `(channel, from, content, MessageType, correlationId, deadline)` — `correlationId` and `deadline` are first-class SPI params, not parsed from content JSON. 3-param convenience default delegates with three nulls. **`ProvisionContext` carries `tenancyId`** — implementations resolve tenant-specific endpoints/credentials without injecting `CurrentPrincipal` (engine#530). |
| Durable PlanItem status (blackboard persistence) | `casehub-engine` | `PlanItemStore` (blocking) + `ReactivePlanItemStore` (Uni<>) SPIs in `casehub-engine-common`; `@DefaultBean` no-ops in `blackboard`; JPA impl (`JpaReactivePlanItemStore`) in `casehub-engine-persistence-hibernate`; blocking JPA impl (`JpaPlanItemStore`) in `casehub-engine-work-adapter` sharing the casehub-work datasource. Atomicity guarantee: `planItemStore.save(RUNNING)` and WorkItem creation are in the same `@Transactional` boundary. **`PlanItemStatus` — 8 states:** `PENDING`, `ENABLED`, `ACTIVE`, `RUNNING`, `COMPLETED`, `TERMINATED`, `FAILED`, `OBSOLETE` (added engine#539). Terminal check: always use `isTerminal()` / `isActive()` — never enumerate statuses in consumer code. See engine#273, engine#539 and `docs/LIFECYCLE.md`. |
| External signal delivery to running cases | `casehub-work-api` (SPI) / `casehub-engine` (impl) | `CaseSignalSink` SPI in `casehub-work-api` — called by casehub-work when SLA escalation fires; implemented in `casehub-engine-work-adapter` calling `CaseHubRuntime.signal()`; Qhorus-driven signals via `QhorusMessageSignalBridge` in engine runtime (`@ObservesAsync MessageReceivedEvent`). Three entry points: SLA escalation → CaseSignalSink, Qhorus message → QhorusMessageSignalBridge, direct REST → CaseHubRuntime. |
| Remote Claude CLI sessions | `claudony` | `TmuxService`, `SessionRegistry`, WebSocket streaming. `ClaudonyWorkerExecutionManager` — `WorkerExecutionManager` SPI; virtual thread watcher publishes `WorkflowExecutionCompleted` when tmux session exits; supports recovery after server restart via tmux session options (claudony#146) |
| Fleet management + peer discovery | `claudony` | Fleet health monitoring, peer registry, cluster-scoped event relay. `FleetMessageRelayObserver` broadcasts channel ticks to all healthy peers. Enables SSE delivery across distributed deployments. |
| MCP server for controller Claude | `claudony` | Claudony exposes an MCP server that Claude Code (and other LLM clients) use to manage sessions, inspect cases, and post to channels. Distinct from Qhorus MCP tools — claudony's MCP surface is operator-facing; Qhorus MCP tools are agent-facing. |
| Browser + agent authentication | `claudony` | WebAuthn passkeys + `X-Api-Key` header |
| Oversight gate lifecycle | `casehub-openclaw` | `OversightGateService.evaluate()` archives deliver:webhook text output as non-resolving STATUS; `fulfill()` processes human oversight gate responses. Gate entry re-wired from `evaluate()` to `CommitmentTools.done()` in openclaw#30. **Intended home: `casehub-engine-api`** (openclaw#31) — currently in casehub-openclaw pending extraction. |
| Provisioner config registry | `casehub-engine-api` | `ProvisionerConfigRegistry` SPI — shared provisioner config lookup. `NoOp @DefaultBean`. ops implements `@Alternative @Priority(1)` from deployment YAML. Refs engine#584, claudony#164. |
| Bridge audit store (query/retrieval) | `casehub-iot` | `BridgeAuditStore` SPI in `casehub-iot-api` + `InMemoryBridgeAuditStore @DefaultBean` in `casehub-iot-bridge-server`. Structured audit query for bridge interactions. Consuming apps may implement JPA/MongoDB backends. Shipped iot#35. |
| Action risk classification | `casehub-engine` | `ActionRiskClassifier` SPI — workers return `WorkerResult` containing a `PlannedAction`; engine gates via WorkItem before case advances. `@RiskClassifier @ApplicationScoped` for consumer implementations. Gate resolved via casehub-work-adapter (requires classpath presence). `pendingActionGate` in-memory only in v1 (engine#433). Gate approval re-fires `WorkflowExecutionCompleted(plannedAction=null)`. Consumers: aml, clinical, devtown, life, openclaw. `TextClassifier` from `casehub-neural-text` is the recommended implementation. Shipped engine#402. |
| OpenClaw worker provisioner | `casehub-openclaw` | `WorkerProvisioner` SPI implementation — provisions OpenClaw instances via `POST /hooks/agent`; no heartbeat required for in-case steps. Two modes: heartbeat (OpenClaw autonomous monitoring → creates CaseHub case) vs direct call (CaseHub case step → on-demand skill execution). See [`docs/repos/casehub-openclaw.md`](repos/casehub-openclaw.md). |
| Qhorus ↔ OpenClaw channel bridge | `casehub-openclaw` | `ChannelBackend` SPI — bidirectional: Qhorus dispatches → `ChannelBackend.post()` → `/hooks/agent`; OpenClaw output → `deliver:webhook` → Qhorus endpoint → `MessageService.dispatch()` |
| ChannelContextWindow (short-term channel context for LLM injection) | `casehub-openclaw` | `MessageObserver` SPI → per-channel ring buffer (configurable size + TTL) → REST `GET /channel-context/{agentId}?since={sequenceNumber}`. Python SDK `before_prompt_build` hook injects result as `appendSystemContext` (compaction-safe). Best-effort — correctness guaranteed by Qhorus; intelligence layer only. |
| AgentProvider (OpenClaw DirectCallBridge) | `casehub-openclaw` (`casehub` module) | `OpenClawAgentProvider` implements `AgentProvider` SPI — synchronous request-reply over async webhooks. `DirectCallBridge` maps correlationId to `CompletableFuture`; `OpenClawHookClient.invokeDirect()` calls `/hooks/agent` sessionlessly with a per-correlationId delivery URL; `DirectCallDeliveryResource` (`POST /openclaw/direct-call/{correlationId}`) receives the response and completes the future. `OpenClawChatModel` bridges langchain4j `ChatModel` to `AgentProvider` (JSON schema support via text preamble). Three modules: `core` (HookClient), `casehub` (Bridge + Provider + ChatModel), `app` (DeliveryResource). openclaw#49. |
| CaseHub accountability tools for OpenClaw (MCP) | `casehub-openclaw` | Four-layer architecture: Quarkus MCP endpoint (`casehub_commit`, `casehub_done`, `casehub_reject`, `casehub_checkpoint`, `casehub_escalate`, `casehub_create_workitem`, `casehub_queue`, `casehub_status`), MCP resources (`casehub://agent/{id}/commitments`, `casehub://channel/{id}/recent`), TypeScript plugin hooks (`before_tool_call`, `agent_end`, `session_start`), global skill + stateless SKILL.md files. Direction 2 of OpenClaw ↔ CaseHub integration: OpenClaw agents calling CaseHub. See [`docs/repos/casehub-openclaw.md`](repos/casehub-openclaw.md) §Layer 0. |
| Infrastructure desired-state provisioning (Terraform/Ansible/standalone) | `casehub-ops` (infra module) | PoC — `InfraBackend` SPI, `InfraGoalCompiler`, `StandaloneBackend` + `InMemoryResourceProvisioner`. Three operating modes: standalone, Terraform augmentation, Ansible augmentation. 96 tests green. |
| CaseHub deployment topology provisioning | `casehub-ops` (deployment module) | `DeploymentGoalCompiler` — processes `casehub-deployment.yaml` into a `DesiredStateGraph`; 5 node types: agents, channels, case types, trust policies, endpoints. Endpoint provisioning via `EndpointProvisionHandler` → `EndpointRegistry.register(spec.toDescriptor(tenancyId))`; drift detection via `EndpointDriftChecker` using `toDescriptor()` + record `equals()` comparison. Provider-specific agent config via `ProviderConfig(providerName, Map<String, Object>)` stored in `DeploymentProviderConfigStore`. Case definition file loading via `DefinitionPayloadLoader` (classpath-first, filesystem-fallback). Layered drift detection: `NodeDriftChecker` SPI (in ops-api, 5 default implementations) → `SpecHashStore` spec hash comparison. `DeploymentGoalLoader` for single-file and multi-directory YAML. Foundation bridge modules (eidos#60) override drift checkers via `@Alternative @Priority(1)`. Self-healing requires desiredstate#38 (TransitionPlanner DRIFTED fix). Research project. |
| Continuous compliance posture management | `casehub-ops` (compliance module) | Six frameworks (SOC2, GDPR, EU AI Act, DORA, NIS2, ISO27001), six control types (`LOG_RETENTION`, `ENCRYPTION_AT_REST`, `ACCESS_REVIEW`, `INCIDENT_RESPONSE`, `DATA_PROCESSING`, `AI_RISK_ASSESSMENT`). Generic `ComplianceControlSpec` with `controlType` discriminator — controls map to multiple frameworks via `FrameworkMapping`. Evidence-based drift detection: `EvidenceCollector` SPI collects evidence → `ComplianceLedgerEntry extends LedgerEntry` (tamper-evident, V2000 migration at `db/compliance/migration/`) → evidence staleness triggers DRIFTED → reconciliation re-collects. `ComplianceFrameworkRegistry` maintains control → framework mapping. `CompliancePostureService` aggregates per-framework compliance scores with five-category model (passing, failing, unavailable, stale, missing). Self-healing requires desiredstate#38 (TransitionPlanner DRIFTED fix). Research project. |
| Ecosystem CI dashboards | `casehub-parent` | `dashboard.yml`, `pr-dashboard.yml`, `full-stack-build.yml` |
| Document diff review MCP tools (start_review, update_selection, query_review, end_review) | `casehub-drafthouse` | `DraftHouseMcpTools @ApplicationScoped` — Qhorus APPEND channel per session; `DocumentReviewer @AiService` handles QUERY messages; session state in `ReviewSessionRegistry`; session handle is channel.id.toString(). |
| Multi-participant LLM debate MCP tools | `casehub-drafthouse` | `DebateMcpTools @ApplicationScoped` — 10 tools: `start_debate`, `raise_point`, `respond_to`, `flag_human`, `get_debate_summary`, `end_debate`, `post_memo`, `request_subagent`, `get_debate_summary_at_round`, `restart_from_round`; `DebateChannelProjection` + `DebateChannelProjection.RoundBoundedProjection` for bounded round views; `DebateChannelBackend`; session branching via `restart_from_round` with RESTART_CONTEXT provenance (drafthouse#40). Participant roles: REV, IMP, SUPERVISOR, MODERATOR, SELECTOR — any role may post; REV and IMP registered eagerly, others lazy-register on first use. `DebateSession` stores participants in `ConcurrentHashMap<AgentType,String>`; `DebateChannelProjection.agentType()` uses `AgentType.valueOf()` for fold-safe role resolution (drafthouse#41). |
| Oversight gate orchestration (reusable approval lifecycle) | `casehub-blocks` | Composes casehub-work (WorkItem) with casehub-engine (case signal) for human-review gates. Scaffold — not yet extracted. |
| Structured conversation management (turn-taking, topic scoping) | `casehub-blocks` | Higher-level API over casehub-qhorus channel dispatch for structured multi-turn agent interactions. Scaffold — not yet extracted. |
| Channel agent dispatch coordination | `casehub-blocks` | Manages agent participation across qhorus channels — provisioning lifecycle and context-based routing. Scaffold — not yet extracted. |
| Cross-lifecycle context tracking | `casehub-blocks` | Composes casehub-engine case state with casehub-qhorus channel history for unified context view. Scaffold — not yet extracted. |
| Application domain logic (devtown, aml, clinical, life, drafthouse, quarkmind) | Application tier | See [APPLICATIONS.md](APPLICATIONS.md) |
| ONNX neural text inference (NLI, classification, regression, reranking) | `casehub-neural-text` | `inference-tasks` — typed adapters over `InferenceModel` SPI; `inference-inmem` for testing |
| SPLADE sparse embeddings | `casehub-neural-text` | `inference-splade` — log-saturation SPLADE output; sparse leg of hybrid RAG search |
| Learned capability exclusion (DECLINE-pattern aggregation) | `casehub-eidos` | `CapabilitySpecializationStore` SPI in `casehub-eidos-api`; called by casehub-ledger CBR subsystem to push learned DECLINE/FAIL patterns into eidos; enables proactive routing exclusion based on pattern history. `EidosPreferenceKeys.EXCLUDE_THRESHOLD` controls sensitivity. Activates `#258` (adaptive routing epic) (eidos#55). |
| Corrective RAG (CRAG) — retrieval quality evaluation and self-correction | `casehub-neural-text` | `rag-crag` module — `@Decorator` on `CaseRetriever`; `RelevanceEvaluator` SPI in `rag-api`; evaluates retrieved chunks and corrects low-relevance results before returning; classpath-activated (neural-text#33). |
| Knowledge corpus retrieval (RAG) | `casehub-neural-text` | `rag` — LangChain4j pipeline, Qdrant, hybrid RRF fusion; `CorpusStore` + `CaseRetriever` SPIs (blocking); `ReactiveCorpusStore` + `ReactiveCaseRetriever` (`Uni<T>` variants, Mutiny `provided` in `rag-api`); `BlockingToReactiveRagBridge @DefaultBean` in `rag`. `rag-api` SPIs: `MetadataExtractor` (document body + metadata extraction), `CursorStore` (pluggable cursor persistence). Corpus ingestion bridge: `CorpusIngestionService` — config-driven `@Scheduled` polling bridge (`ChangeSource` → `CorpusReader` → `MetadataExtractor` → chunk → `EmbeddingIngestor`); `YamlFrontmatterExtractor @DefaultBean`; `FileCursorStore @DefaultBean`; `InMemoryCursorStore @Alternative @Priority(1)` test stub in `rag-testing` (neural-text#19). |
| Agent task history (write) | `casehub-eidos` | `AgentGraphStore` SPI — called by casehub-engine at dispatch/completion via `AgentGraphStore.recordTask()` / `recordOutcome()` from `WorkOrchestrator` |
| Agent task history (read) | `casehub-eidos` | `AgentGraphQuery` SPI — history, outcome stats, attestation chain |
| Agent graph backfill | `casehub-eidos` | `AgentGraphBackfill` SPI — ingests historical casehub-ledger attestations |
| Semantic task enrichment | `casehub-eidos` | `TaskSemanticEnricher` SPI — application-tier implementations; eidos pulls at query time |
| Agent descriptor (structured 4-layer identity) | `casehub-eidos` | `AgentDescriptor` record — identity, slot, capabilities, disposition; `tenancyId` always required; `AgentQuery` for criteria-based discovery |
| Agent registry (store + discover by slot/capability) | `casehub-eidos` | `AgentRegistry` (blocking) + `ReactiveAgentRegistry` (reactive, build-gated `casehub.eidos.reactive.enabled`); `InMemoryAgentRegistry` + `InMemoryAgentStateStore` for ephemeral installs via `casehub-eidos-memory` |
| Vocabulary registry (term resolution + cross-vocab equivalence) | `casehub-eidos` | `VocabularyRegistry` SPI + `CdiVocabularyRegistry` @DefaultBean; vocabularies are enums implementing `VocabularyTerm`; discovers `@ApplicationScoped VocabularyRegistrar` beans; axis-aware `equivalentValues(S, Class<T>, DispositionAxis)` — typed bypass registration (eidos#40) |
| Well-known vocabularies (SVO, Conscientiousness, CasehubSlot, Belbin, DISC, Thomas-Kilmann) | `casehub-eidos-vocab` | Optional module — `SvoTerm`, `ConscientiousnessTerm`, `CasehubSlotTerm`, `BelbinTerm` (9 Belbin team roles, slot vocab), `DiscTerm` (4 DISC types, disposition vocab, `axisExactMatch` → Conscientiousness + TK), `ThomasKilmannTerm` (5 conflict modes, disposition vocab for `CONFLICT_MODE` axis); each accompanied by a `VocabularyRegistrar` bean; Jandex-indexed for CDI discovery |
| Agent capability health (declared vs operable) | `casehub-eidos` | `CapabilityHealth` SPI — `probe(AgentDescriptor, capabilityTag, ProbeContext)` returns `CapabilityStatus` (`Ready`, `Degraded`, `Unavailable`, `EpistemicallyWeak`). `DegradationReason` is a top-level type in `casehub-eidos-api` — not nested inside `CapabilityHealth`. `DefaultCapabilityHealth` checks `AgentStateStore` first (degraded state takes precedence), then declared capabilities + epistemic domain confidence; configurable `casehub.eidos.epistemic.weak-threshold` (default 0.3); `ReactiveCapabilityHealth` for reactive parity (build-gated). **Engine integration (engine#341):** `WorkOrchestrator` calls `probe()` at dispatch time for workers that carry an `AgentDescriptor` (via `Worker.agentDescriptor()`, guarded by `Worker.hasDescriptor()`); workers without a descriptor skip the probe and are assumed capable (non-agent workers). Engine provides `NoOpCapabilityHealth @DefaultBean` — deployments without eidos get no filtering. **ProbeContext semantics:** `taskDomain` is the *subject domain* of the task (e.g. `"rust"` within a `"code-review"` capability) — distinct from `capabilityTag`. Pass actual task subject context in `taskDomain`; use `taskMetadata` for additional attributes. Conflating `taskDomain` with `capabilityTag` prevents `EpistemicallyWeak` from triggering correctly. |
| Agent operational state (degradation tracking) | `casehub-eidos` | `AgentStateStore` SPI — `record(agentId, DegradationReason, expiresAt)`, `query(agentId)`. `NoOpAgentStateStore @DefaultBean` (no tracking). `InMemoryAgentStateStore @Alternative @Priority(1)` in `casehub-eidos-memory` (TTL-based ConcurrentHashMap). `DefaultCapabilityHealth` checks store first at probe time — degraded state takes precedence over Ready/EpistemicallyWeak. JPA persistence deferred (eidos#7). |
| System prompt generation | `casehub-eidos` | `SystemPromptRenderer` SPI — `render(AgentDescriptor, AgentPromptContext)` → `RenderedPrompt`; `EidosSystemPromptRenderer @DefaultBean` — two-step pipeline: structural assembly → optional LangChain4j `ChatModel` semantic pass; three output formats: `MARKDOWN`, `PROSE`, `A2A_CARD`. `A2A_CARD` exposes `slot`, per-axis `disposition` objects with vocabulary context, and `frameworks` array (deduplicated vocabulary index for machine-to-machine capability negotiation); `A2ASemanticEnrichmentStep` handles per-capability descriptions (eidos#45). Capability rendering is format-discriminated (PP-20260611-228599, eidos#49): PROSE and MARKDOWN surface capability names and `inputTypes`/`outputTypes` only; `A2A_CARD` carries full routing signals — `qualityHint`, `latencyHintP50Ms`, `costHint`, `epistemicDomains`, `inputTypes`, `outputTypes` — for casehub-engine dispatch. `AgentDescriptor.vocabUriForSlot()` — `slotVocabulary → domainVocabulary` two-step fallback alongside `vocabUriForAxis()`. Falls back to structural output when no `ChatModel` is available. `AgentPromptContext` carries `Optional<GoalContext>`, `List<Resource>`, `situationalContext`, `RenderFormat`. `DegradationReason`, `AgentPromptContext`, `GoalContext`, `Resource`, `AgentStateStore` are top-level types in `casehub-eidos-api`. |

---

## Key Boundary Rules

**Any casehub repo may depend on `casehub-platform-api`.** It is a zero-external-dependency pure-Java module — taking a compile dependency on it does not force Quarkus, JPA, or any framework onto consumers. Foundation repos (`casehub-work-api`, `casehub-ledger-api`, etc.) may use `Path`, `Preferences`, `CurrentPrincipal` and other platform types in their own SPI signatures.

**Do not define parallel path, scope, preference, or principal types.** `casehub-platform-api` owns `Path`, `SettingsScope`, `PreferenceKey`, `Preferences`, `PreferenceProvider`, `CurrentPrincipal`, and `GroupMembershipProvider`. Repos that need these concepts must depend on `casehub-platform-api` and implement its SPIs — they must not define their own equivalent types.

**Do not add orchestration logic to `casehub-work`.** When a WorkItem completes, casehub-work fires a CDI event and stops. Homogeneous M-of-N group completion is casehub-work. Heterogeneous plan-level completion is casehub-engine. "Mark the WorkItem EXPIRED when its deadline passes" is casehub-work.

**Do not add WorkItem inbox management to `casehub-engine`.** casehub-engine depends on `casehub-work-core` (`WorkBroker`) only. WorkItem entities, Flyway migrations, REST endpoints must not flow into the engine.

**Do not add trust scoring to `casehub-work` or `casehub-engine`.** Trust lives in casehub-ledger and is surfaced via CDI routing events (`TrustScoreRoutingPublisher`). Consumers observe those events — they never compute trust themselves.

**Do not duplicate notification infrastructure.** `casehub-connectors` owns Slack/Teams/SMS/email. `casehub-work-notifications` must delegate here.

**Do not implement Qhorus channel semantics in `claudony`.** Claudony embeds Qhorus and adds SPI implementations. It must not re-implement channel, message, or commitment logic. Implementing `ChannelBackend` or `MessageObserver` SPIs from `casehub-qhorus-api` is not re-implementation — it is correct SPI usage.

**Do not call `QhorusMcpTools` or `ReactiveQhorusMcpTools` from consumer service code.** Those classes are the MCP tool dispatch layer for external callers (Claude Code); they carry `@WrapBusinessError` exception semantics that internal consumers must not be exposed to. Consumer service code has three correct integration points: (1) **Dashboard/UI consumers** needing composed views (channel with message count, instance with capability tags, timeline entries) — inject `QhorusDashboardService`. (2) **Service-layer integrations** that need to send messages — call `MessageService.dispatch(MessageDispatch)` (blocking) or `ReactiveMessageService.dispatch(MessageDispatch) → Uni<DispatchResult>` (reactive). These are the enforcement gates: paused check, ACL, rate limiting, LAST_WRITE semantics, ledger write, and fan-out all happen inside `dispatch()`. Do not bypass to entity stores for write operations. (3) **Reactive event-driven integrations** — implement `ChannelBackend` or `MessageObserver` SPI. Note: injecting entity services directly is also wrong for dashboard consumers — `ReactiveChannelService.listAll()` returns entities without message counts, requiring store-layer injection and creating worse coupling. See `../garden/docs/protocols/casehub/qhorus-consumer-integration-pattern.md`.

**Choose `ChannelBackend` vs `MessageObserver` based on scope.** `ChannelBackend` is per-channel and knows its context — use it when a consumer needs to act on messages from a specific channel (e.g. Claudony panel display). `MessageObserver` is a global broadcast across all channels — use it for cross-cutting concerns (e.g. clinical PI response monitoring). For topology guidance (LOCAL CDI vs CLUSTER-scoped transport) see [`docs/repos/casehub-qhorus.md`](repos/casehub-qhorus.md) and [qhorus `docs/messaging-architecture.md`](https://github.com/casehubio/qhorus/blob/main/docs/messaging-architecture.md).

**Do not put CaseHub SPI implementations in `casehub-engine`.** casehub-engine defines them; deployment-specific implementations belong in the deploying application.

**Do not use `casehub-work` runtime in `casehub-engine`.** The engine depends on `casehub-work-core` only.

**Use `CaseSignalSink` (in `casehub-work-api`) as the only path for external events that must unblock a waiting case.** casehub-work injects and calls `CaseSignalSink` at SLA escalation time; the implementation in `casehub-engine-work-adapter` translates to `CaseHubRuntime.signal()`. Qhorus message signals route via `QhorusMessageSignalBridge` in engine runtime. Do not add case-signaling logic to any other module.

**Do not add domain logic to foundation repos.** If the capability requires knowledge of software development, clinical trials, or financial crime, it belongs in an application repo.

**Do not implement CBR retrieval logic in application repos.** Case similarity matching belongs in `casehub-neural-text` via the `CaseRetriever` SPI. Application repos provide domain-specific feature vectors (what fields describe a case) and similarity thresholds; the retrieval mechanism itself must not be re-implemented per domain. See [`docs/CBR-CAPABILITY.md`](CBR-CAPABILITY.md).

**Do not implement implementation-selection trust routing in application repos.** When multiple `TaskDefinition` implementations compete for the same capability, routing between them is a `casehub-engine` concern (`ImplementationRoutingStrategy` — gap, to be filed). Application-layer workarounds (`canActivate()` gating via a selector bean) are temporary and must migrate to the engine SPI once it exists. See [`docs/CBR-CAPABILITY.md`](CBR-CAPABILITY.md) §Reuse.

**Do not re-implement CapabilityHealth probe semantics in casehub-engine.** Engine calls `CapabilityHealth.probe()` via the `casehub-eidos-api` SPI contract from `WorkOrchestrator`. Engine provides a `NoOpCapabilityHealth @DefaultBean` for deployments without eidos — that is the full extent of engine's responsibility. Do not add `AgentDescriptor`, vocabulary, or epistemic domain logic to engine types. `Worker` carries an optional `AgentDescriptor` field for probe dispatch only — not for identity, registry, or vocabulary operations.

**Named MCP server convention.** Library modules that expose MCP tools must use `@McpServer("<library-name>")` to scope their tools to a named server. The default (unnamed) MCP server belongs to the application. This prevents library tools from colliding with application tools and lets applications compose multiple library MCP surfaces. Established by claudony#105 and qhorus#306.

---

## Cross-Cutting Concerns

### Persistence

| Concern | Owner | Mechanism |
|---|---|---|
| Base ledger tables | `casehub-ledger` | Flyway V1000–V1007 at `classpath:db/ledger/migration` |
| WorkItem tables | `casehub-work` runtime | Flyway V1–V999 at `classpath:db/work/migration`; consumers must declare `quarkus.flyway.locations=classpath:db/work/migration` |
| Qhorus tables | `casehub-qhorus` | Flyway V1–V14, V2000 (named `qhorus` datasource; `classpath:db/qhorus/migration,classpath:db/ledger/migration`; next domain migration: V15) |
| Engine tables | `casehub-engine` | Hibernate `drop-and-create` (no migrations yet) |
| Ledger subclass join tables | Each consumer | Consumer-owned Flyway, V2000+ numbering |

**Flyway numbering rule:** casehub-ledger owns V1000–V1007 at `classpath:db/ledger/migration`. Domain: V1–V999. Ledger subclass joins: V2000+ (provides safe buffer above the ledger base range). Qhorus reference: V1–V10 domain migrations, V2000 subclass join; next domain migration V11. Consumers must add `classpath:db/ledger/migration` to their Flyway locations alongside their own path.

**Flyway path scoping rule:** Every module must ship migrations under a repo-scoped path (`db/<reponame>/migration/`) — never the generic `db/migration/`. See `PP-20260525-607b33` (`casehub/garden: docs/protocols/universal/flyway-repo-scoped-migration-path.md`). Consumers must configure `quarkus.flyway.locations=classpath:db/<repo>/migration` explicitly — Quarkus has no runtime auto-registration mechanism. See `PP-20260528-flyway-ext-reg` (`casehub/garden: docs/protocols/universal/flyway-extension-migration-registration.md`).

**Named datasource rule:** Qhorus always runs on named `qhorus` datasource. Claudony uses separate `claudony` and `qhorus` persistence units.

### Observability

- OTel trace → ledger: `LedgerTraceListener` auto-populates `traceId` at `@PrePersist`
- Agent interactions: `MessageLedgerEntry` records all 9 message types
- WorkItem audit: `AuditEntry` (always-on) + optional `WorkItemLedgerEntry` (tamper-evident)
- Case decisions: `EventLog` (engine-internal) + optional `CaseLedgerEntry` (external, tamper-evident)

### Authentication

**Gateway topology:** Claudony is the single authenticated entry point for all human operators and Claude agent sessions. Internal foundation services (Qhorus, casehub-engine, casehub-work) carry no auth annotations on their REST resources — they trust callers implicitly, relying on network policy or mTLS for isolation. This contract is only valid when Claudony sits in front. A standalone deployment of Qhorus, engine, or work without Claudony requires an auth proxy or Quarkus OIDC/JWT before any external traffic is admitted. The A2A endpoint on Qhorus (`POST /a2a/message:send`) extends this posture to the agent surface — no token auth is applied at the Qhorus layer; the caller is trusted. See `casehub/garden: docs/protocols/casehub/auth-retrofit-readiness.md` for rules on keeping services auth-retrofit-ready while this remains implicit.

| Context | Owner | Mechanism |
|---|---|---|
| Extension-level | Consuming app | Extensions provide no auth |
| Browser → Claudony | `claudony` | WebAuthn passkeys |
| Agent → Claudony | `claudony` | `X-Api-Key` header |
| Channel write ACL | `casehub-qhorus` | `allowed_writers` on `Channel` |
| Internal service-to-service | Network boundary | Trust implicit — no token auth on Qhorus, engine, or work REST resources |
| Qhorus multi-tenant HTTP (no OIDC) | `casehub-qhorus` | `QhorusInboundCurrentPrincipal @Priority(1)` reads `X-Tenancy-ID` header — routing mechanism only, not an auth boundary; appropriate only when network policy provides trust isolation |

### Outbound Authentication (external service calls)

Three systems make outbound HTTP calls to external services: **workers** (`casehub-workers`), **connectors** (`casehub-connectors`), and **quarkus-flow `call: http` workflow steps**. All three must use a consistent authentication vocabulary.

**The canonical model is Serverless Workflow 1.0's `AuthenticationPolicy`.** quarkus-flow already implements it. The five auth types — **Basic**, **Bearer**, **Digest**, **OAuth2** (client credentials), **OpenID Connect** — plus **named policy references** (`use("my-policy")`) cover every outbound auth pattern the platform needs.

| Auth type | Use case | Mechanism |
|---|---|---|
| None | Internal services behind a gateway | No auth headers |
| Bearer | Static API tokens (Slack, Twilio, external REST APIs) | `Authorization: Bearer <token>` |
| Basic | Legacy services, SMTP relay | Base64 username:password |
| OAuth2 | Machine-to-machine, cloud APIs (GCP, Azure, AWS) | Client credentials flow, Quarkus OIDC Client handles token lifecycle |
| OIDC | Identity-propagating calls | Token exchange or forward |
| Digest | HTTP digest auth | Challenge-response |
| Named reference | Shared policy reuse | `use("salesforce-prod")` — resolves to a named policy definition |

**Three tiers of outbound credentials:**

| Tier | Scope | Config mechanism | Example |
|---|---|---|---|
| **1 — Static deploy-time** | Fixed per deployment, single-vendor | `@ConfigProperty` (MicroProfile Config) | Twilio account SID, global Slack bot token |
| **1.5 — Per-binding config reference** | One credential per DB binding record, deploy-time config | Logical name stored in DB; resolved via `Config.getValue("casehub.<module>.credentials." + ref, String.class)` | Different Slack bot token per Qhorus channel / Slack workspace |
| **2 — Named endpoint** | Multi-endpoint, per-capability, runtime-registered | `EndpointRegistry` SPI (platform#73) with `credentialRef` — **resolution not yet implemented** | Worker dispatching to customer APIs with different auth per tenant |

Connectors currently use Tier 1 (static `@ConfigProperty`), which is correct for their use case — they connect to a single vendor per connector type. Optional modules that bind one external account per channel or entity (e.g. one Slack workspace per Qhorus channel) use Tier 1.5. Workers and quarkus-flow target Tier 2 when the secrets resolver is implemented.

**Secrets management:** Auth policies reference credentials by name, never inline in DB or endpoint descriptors. The actual token lives in the runtime environment (env var or `application.properties`), not the DB. Actual secret storage (Vault, k8s Secret, environment variable) at Tier 2 is resolved by a secrets backend — not yet implemented; `EndpointRegistry.credentialRef` is a forward-compatibility field only.

**"credentialRef is deferred"** means the `EndpointRegistry` SPI's `EndpointDescriptor.credentialRef` field (shipped platform#73) exists but no runtime resolver reads it. Adding `credentialRef` to an endpoint descriptor has no effect today. Use Tier 1.5 for per-binding credentials until a secrets backend resolver is implemented. See `casehub/garden: docs/protocols/casehub/per-binding-credential-reference.md`.

### Role Name Convention (`@RolesAllowed`)

Role names used in `@RolesAllowed` annotations are CaseHub group names — `CurrentPrincipal.roles()` delegates to `groups()`, so group membership IS role membership. Role names must be documented when first introduced in any harness.

**Known roles:**

| Role name | Harness | What it gates |
|---|---|---|
| `admin` | `casehub-devtown` | `MemoryAdminResource` — internal memory store admin operations (devtown#71) |

**Convention:** role names are lowercase, domain-prefixed when ambiguous (e.g. `devtown-admin` if `admin` becomes overloaded). `@RolesAllowed` is inert until `casehub-platform-oidc` is on classpath and OIDC is configured — add the module and configure the OIDC provider to issue the group claims.

### Privacy (GDPR)

All GDPR concerns centralised in `casehub-ledger`:
- Art.17 erasure: `LedgerErasureService` + `ActorIdentityProvider` SPI
- Art.22 decision records: `ComplianceSupplement`
- PII sanitisation: `DecisionContextSanitiser` SPI

### Agent Identity

Format: `{model-family}:{persona}@{major}` — e.g. `"claude:analyst@v1"`. Defined in casehub-ledger ADR 0004. Major version bump resets trust baseline. SCIM2 resolution via `ScimActorDIDProvider @Alternative` — activate with `quarkus.arc.selected-alternatives`.

### Agent Communication Mesh

The platform uses a normative 3-channel layout for agent-to-agent and agent-to-human interactions:

| Channel | Purpose | Primary speech acts |
|---------|---------|---------------------|
| `work` | Task assignment and completion (prescriptive) | COMMAND, RESPONSE, DONE, DECLINE |
| `observe` | Passive monitoring and state sharing (descriptive) | EVENT |
| `oversight` | Human governance gates (commitment-based) | All obligation-carrying types (COMMAND, QUERY, RESPONSE, DONE, DECLINE, FAILURE, STATUS, HANDOFF); EVENT excluded — no telemetry on the governance channel (`deniedTypes = EVENT`) |

These map to the 4-layer normative accountability framework implemented by casehub-qhorus:
1. **Illocutionary** — what was said (speech act type, channel)
2. **Commitment** — what was obligated (Commitment record, OPEN → FULFILLED/FAILED/EXPIRED)
3. **Temporal** — when obligations become stale (Watchdog, deadline enforcement)
4. **Enforcement** — casehub-engine orchestration reacts to commitment outcomes via CDI events

When implementing a new MCP tool or channel interaction: **does this align with the normative mesh patterns?** See the full framework spec: [`casehubio/claudony docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md`](https://github.com/casehubio/claudony/blob/main/docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md).

### Implementation Protocols

Rules that apply across all casehubio modules:

| Protocol | Rule |
|---|---|
| [SCIM2 agent identity lookup](integration/scim2-agent-identity.md) | Agent identity attributes (DID, public key, capabilities) resolved via SCIM2 `Agent` endpoint using `actorId` as `externalId`. Schema extension: `urn:ietf:params:scim:schemas:extension:casehub:2.0:Agent`. `ScimActorDIDProvider @Alternative` is the ledger-side implementation. |
| SQL type portability (GE-20260512-2c2eff) | `DOUBLE PRECISION` not `DOUBLE`; `SMALLINT` not `TINYINT` — garden `jvm/` domain |
| Flyway migration rules (`casehub/garden: docs/protocols/flyway-migration-rules.md`) | Version namespace ranges; `MODE=PostgreSQL` in all H2 test URLs |
| Flyway extension migration registration (`casehub/garden: docs/protocols/universal/flyway-extension-migration-registration.md`) | Extensions use repo-scoped `db/<repo>/migration/` paths + `NativeImageResourcePatternsBuildItem`; Quarkus consumers must configure `quarkus.flyway.locations` explicitly — no runtime auto-registration exists |
| Optional module pattern (`casehub/garden: docs/protocols/optional-module-pattern.md`) | Jandex library module; zero cost when absent |
| Quarkus test database (`casehub/garden: docs/protocols/quarkus-test-database.md`) | H2 `MODE=PostgreSQL`; Testcontainers for dialect validation |
| Submodule folder naming (`casehub/garden: docs/protocols/universal/maven-submodule-folder-naming.md`) | Short names — no repo prefix. `api` not `casehub-work-api` |
| Reactive-service build gating (`casehub/garden: docs/protocols/casehub/reactive-service-build-gating.md`) | Extensions gate the reactive tier via `@IfBuildProperty(name="casehub.<module>.reactive.enabled", stringValue="true")` backed by a `@ConfigRoot(phase=BUILD_TIME)` config in deployment/. Default false — blocking-only consumers pay no Hibernate Reactive cost. Write methods use `@WithTransaction`; no `withSafeContext` wrapper needed with Panache repos. Every `Reactive*Service` must mirror its blocking counterpart (ArchUnit 1.4.1, casehub-ledger). |
| Persistence-backend CDI priority (`casehub/garden: docs/protocols/universal/persistence-backend-cdi-priority.md`) | `@DefaultBean` → `@ApplicationScoped` → `@Alternative @Priority(1)` — backend activates by classpath presence, no consumer changes |
| Descriptor+Handler pattern (`casehub/garden: docs/protocols/casehub/descriptor-handler-pattern.md`) | Application repos: every enum whose values have distinct behaviour belongs in a `*CaseDescriptor` POJO + optional CDI handler — never in switch statements across service classes. Reference implementation: casehub-life#27 |

Full index: `casehubio/garden/docs/protocols/INDEX.md` (cloned locally at `../garden/docs/protocols/`)

---

## Known Overlap Risks

1. **`EventLog` vs `CaseLedgerEntry`** (engine) — `EventLog` is operational (restart recovery, observability). `CaseLedgerEntry` is the compliance record (tamper-evident). If a lifecycle transition doesn't fire `CaseLifecycleEvent`, it won't be ledgered — and the async observer can fail silently. See `casehub/garden: docs/protocols/casehub/dual-trail-audit-pattern.md` for the write rule, failure modes, and detection queries.
2. **`AuditEntry` vs `WorkItemLedgerEntry`** (work) — `AuditEntry` is always-on operational. `WorkItemLedgerEntry` is opt-in tamper-evident and is what trust score computation reads. A state transition that calls `audit()` but omits the CDI event produces an operational record but no compliance record, and silently corrupts trust scores. See `casehub/garden: docs/protocols/casehub/dual-trail-audit-pattern.md`.
3. **`CommitmentState.DELEGATED` (Qhorus) ≠ `WorkItemStatus.DELEGATED` (work)** — same word, opposite terminal semantics. Qhorus DELEGATED is **terminal** for the original obligor (obligation transferred, closed, child Commitment created for the named target). Work DELEGATED is **non-terminal** (`isTerminal()` returns false — work reassigned to a named actor, item stays active). Integration code bridging a Qhorus HANDOFF to WorkItem delegation will misapply terminal semantics. A developer reasoning about a HANDOFF-then-DELEGATED path expects the obligation to end — it does not. See javadoc on `CommitmentState.DELEGATED` and `WorkItemStatus.DELEGATED`.
4. **Notification duplication** — `casehub-connectors` and `casehub-work-notifications` both provide Slack/Teams. Must converge (parent#5, open).
5. **`callerRef` format is implicit** — carries `case:{caseId}/pi:{planItemId}`. casehub-work treats it as opaque. Consumers must know this format out of band.

## Known Placement Violations

SPIs and capabilities that exist in the wrong module pending extraction. Do not add new consumers — use the intended home once extracted.

| Capability | Current home | Intended home | Tracking |
|---|---|---|---|
| `OversightGateService` | `casehub-openclaw` | `casehub-engine-api` | *(untracked — file issue before implementing)* |

---

## Per-Repo Deep Dives

| Repo | Local path |
|------|-----------|
| `casehub-platform` | `repos/casehub-platform.md` |
| `casehub-eidos` | `repos/casehub-eidos.md` |
| `casehub-ledger` | `repos/casehub-ledger.md` |
| `casehub-work` | `repos/casehub-work.md` |
| `casehub-qhorus` | `repos/casehub-qhorus.md` |
| `casehub-engine` | `repos/casehub-engine.md` |
| `casehub-neural-text` | `repos/casehub-neural-text.md` |
| `claudony` | `repos/claudony.md` |
| `casehub-connectors` | `repos/casehub-connectors.md` |
| `casehub-iot` | `repos/casehub-iot.md` |
| `casehub-blocks` | `repos/casehub-blocks.md` |
| `casehub-ops` | `repos/casehub-ops.md` |
| `casehub-devtown` | `repos/casehub-devtown.md` |
| `casehub-aml` | `repos/casehub-aml.md` |
| `casehub-clinical` | `repos/casehub-clinical.md` |
| `quarkmind` | `repos/quarkmind.md` |

Application tier: see [APPLICATIONS.md](APPLICATIONS.md)
