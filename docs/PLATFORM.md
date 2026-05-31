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

- SPIs: consumer-facing SPI interfaces go in `api/spi/` — see [`docs/protocols/casehub/consumer-spi-placement.md`](protocols/casehub/consumer-spi-placement.md). `@DefaultBean` implementations go in `runtime/` when they have JPA or config deps; in `api/spi/` itself when they are trivially pure-Java. Persistence SPIs with JPA deps belong in model modules. The test: could a consumer implement this interface without depending on `runtime/`? If yes, the interface belongs in `api/spi/`.
- Ledger subclasses: JOINED inheritance, consumer-owned V2000+ migration (V1000–V1007 reserved for ledger base; V2000+ provides safe buffer), domain-agnostic leaf hash. See [`docs/protocols/casehub/ledger-subclass-extension.md`](protocols/casehub/ledger-subclass-extension.md).
- CDI events: async (`@ObservesAsync`) for ledger capture; sync for routing decisions
- Named datasources: Qhorus always on `qhorus`, domain tables never mixed in
- Flyway numbering: V1000–V1007 = ledger base (`classpath:db/ledger/migration`); V1–V999 = domain; V2000+ = ledger subclass joins (qhorus reference: `V2000__agent_message_ledger_entry`). Extensions with a named datasource must scope migrations to `db/<module>/migration/` — **never** inside `db/migration/<module>/` (Flyway scans recursively; subdirectories of `db/migration/` are visible to any datasource scanning the parent path). See [`docs/protocols/casehub/flyway-version-range-allocation.md`](protocols/casehub/flyway-version-range-allocation.md) Rule 4.
- Module structure: three-tier rule — pure-Java SPI / core library (no JPA) / full extension. SPI method signatures must not expose heavy external SDK types. See [`docs/protocols/universal/module-tier-structure.md`](/Users/mdproctor/claude/casehub/parent/docs/protocols/universal/module-tier-structure.md).
- **Persistence module split:** JPA entities must not co-locate with domain SPIs — forces all consumers to configure a datasource. See [`docs/protocols/universal/module-tier-structure.md`](protocols/universal/module-tier-structure.md).
- **SPI defaults — two patterns:** *Operational SPIs* (`WorkerProvisioner`, `CaseChannelProvider`, `WorkerStatusListener`) get a no-op default — skipping the operation leaves the system functional. *Vocabulary/registry SPIs* (`CapabilityRegistry` and equivalents) get a *populated* default expressing domain vocabulary — an empty implementation breaks routing and selection immediately. Decision rule: can the system function correctly with an empty/do-nothing implementation? Yes → no-op. No → populated default. Both live in the same pure-Java module as the SPI; the app module provides the `@ApplicationScoped` wrapper.
- **`casehub-platform-api` is not a shared types bucket.** It exists to avoid duplication of shared concepts across repos that should not depend on each other. A type belongs there only if multiple peer repos need it AND cannot share it by depending on a single domain `*-api` module. `ActorType`, `ActorTypeResolver`, `CurrentPrincipal`, `Path`, `PreferenceKey` qualify (`ActorType`/`ActorTypeResolver` moved here from `casehub-ledger` in ledger#88 — import from `io.casehub.platform.api.identity`, not `io.casehub.ledger.api.model`). Domain types like `AgentDescriptor`, `WorkItem`, or `LedgerEntry` do not — repos that need them depend on the domain's own `api/` module (`casehub-eidos-api`, `casehub-work-api`, `casehub-ledger-api`). See [`docs/protocols/casehub/platform-api-scope.md`](protocols/casehub/platform-api-scope.md).
- **`casehub-platform` (mock module) scope rule:** use `<scope>test</scope>` in library and Quarkus extension modules (no `quarkus:build` goal — test-only activation is sufficient and `test` scope is invisible to production augmentation, which is the goal); use `<scope>runtime</scope>` in application modules that declare `<goal>build</goal>` in the quarkus-maven-plugin (production augmentation validates CDI without the test classpath, so `test` scope makes `MockPreferenceProvider @DefaultBean` invisible at augmentation time, causing `UnsatisfiedResolutionException` for `PreferenceProvider`). Wrong-scope symptom: all `@QuarkusTest` tests pass, then augmentation fails ~20s later.
- **Application tier rule:** domain logic (git, PRs, clinical protocols, AML investigations) belongs in application repos. Foundation repos must remain domain-agnostic. If it requires knowledge of a specific business domain, it does not belong in foundation.
- **Submodule folder naming:** short descriptive names — no repo prefix. `api` not `casehub-work-api`; `runtime` not `casehub-ledger-runtime`. See [`docs/protocols/universal/maven-submodule-folder-naming.md`](protocols/universal/maven-submodule-folder-naming.md).
- **Agent mesh alignment:** when implementing a new MCP tool or channel interaction, verify it aligns with the normative 3-channel layout (work/observe/oversight) and 4-layer accountability framework. See [`docs/repos/claudony.md`](repos/claudony.md) §Agent Mesh Framework and the [Claudony mesh spec](https://github.com/casehubio/claudony/blob/main/docs/superpowers/specs/2026-04-27-claudony-agent-mesh-framework.md).
- **Trust routing cold-start:** any application using trust-based routing must implement the four-phase maturity model — Phase 0 is availability routing (Gastown parity), phases advance automatically as `minimumObservations` thresholds are crossed, every capability must declare a `fallbackType`. Never block on missing trust data. See [`docs/protocols/casehub/trust-maturity-model.md`](protocols/casehub/trust-maturity-model.md).
- **Auth retrofit readiness:** RBAC is not yet implemented but must not be foreclosed. No auth or principal logic in domain or service layers. REST resources must stay thin enough for `@RolesAllowed`. Queries need a structurally injectable filter. SPI signatures must stay free of auth types. See [`docs/protocols/casehub/auth-retrofit-readiness.md`](protocols/casehub/auth-retrofit-readiness.md).
- **Case definition three-layer architecture:** YAML (classpath resource) → generated schema model (`io.casehub.model.*`) → canonical API model (`CaseDefinition`). Fluent DSL builders target the same canonical model and additionally support `LambdaExpressionEvaluator` (not expressible in YAML). All YAML definitions ⊂ fluent DSL; reverse is not true. Runtime: extend `YamlCaseHub`. Tests: build `CaseDefinition` directly via builders. Never bypass `CaseDefinitionYamlMapper`. Inherited from CNCF Serverless Workflow 1.0 / quarkus-flow. See [`casehub/garden: docs/protocols/casehub/case-definition-layers.md`](../garden/docs/protocols/casehub/case-definition-layers.md).

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
| `casehub-platform` | [casehubio/platform](https://github.com/casehubio/platform) | Zero-dep foundational SPIs — Path, Preferences, Identity, Memory. Modules: `platform-api` (SPIs), `platform` (@DefaultBean mocks + ReactiveCaseMemoryStore SPI + BlockingToReactiveBridge), `testing` (@Alternative identity fixtures), `config/` (YAML preference provider), `oidc/` (OIDC CurrentPrincipal), `expression/` (JQEvaluator), `persistence-jpa/` (JPA PreferenceProvider — Flyway, @ApplicationScoped), `persistence-mongodb/` (MongoDB PreferenceProvider — @Alternative @Priority(1), no Flyway), `memory-inmem/` (@Alternative @Priority(1) volatile CaseMemoryStore — ConcurrentHashMap, no quarkus:build goal. Add test-scope for @QuarkusTest isolation; compile for ephemeral installs. Do NOT combine with memory-jpa in production scope), `memory-jpa/` (@ApplicationScoped JPA CaseMemoryStore — PostgreSQL, Flyway V1000 at `classpath:db/memory/migration`, FTS via websearch_to_tsquery when question provided. No quarkus:build goal), `scim/` (SCIM 2.0 GroupMembershipProvider — @ApplicationScoped, displaces mock by classpath presence, platform#45). Adapters are submodules — extracted to a standalone repo only when a confirmed non-CaseHub consumer warrants it (see `PP-20260529-spi-adapter-placement`). | Foundation |
| `casehub-ledger` | [casehubio/ledger](https://github.com/casehubio/ledger) | Immutable tamper-evident audit ledger + trust scoring. Modules: `api`, `runtime`, `deployment`, `persistence-memory` (`casehub-ledger-memory` — zero-datasource in-memory SPIs) | Foundation |
| `casehub-work` | [casehubio/work](https://github.com/casehubio/work) | Human task lifecycle (WorkItem inbox, SLA, delegation, routing) | Foundation |
| `casehub-qhorus` | [casehubio/qhorus](https://github.com/casehubio/qhorus) | Peer-to-peer agent communication mesh | Foundation |
| `casehub-connectors` | [casehubio/connectors](https://github.com/casehubio/connectors) | Outbound and inbound message connectors (Slack, Teams, SMS, email outbound; webhook + IMAP email inbound) | Foundation |
| `casehub-engine` | [casehubio/engine](https://github.com/casehubio/engine) | Hybrid choreography+blackboard orchestration engine | Orchestration |
| `claudony` | [casehubio/claudony](https://github.com/casehubio/claudony) | Remote Claude CLI sessions + unified ecosystem dashboard | Integration |
| `casehub-openclaw` | [casehubio/openclaw](https://github.com/casehubio/openclaw) | CaseHub × OpenClaw integration — ChannelContextWindow, WorkerProvisioner, ChannelBackend SPI, Python SDK context hook | Integration |
| `casehub-eidos` | [casehubio/eidos](https://github.com/casehubio/eidos) | Agent identity — descriptor, discovery registry, vocabulary system, system prompt generation | Foundation |
| `casehub-poc` | [casehubio/casehub](https://github.com/casehubio/casehub) | **Retiring** — original POC; no new features | — |
| `quarkmind` | [mdproctor/quarkmind](https://github.com/mdproctor/quarkmind) | StarCraft II game AI — living lab proving the CaseHub harness pattern at millisecond game-loop granularity outside regulated domains | Application |
| `flow` | [mdproctor/flow](https://github.com/mdproctor/flow) | Standalone Quarkus engine app with REST endpoints — tier and platform coherence pending analysis (external contributor) | TBD |

Application tier (devtown, aml, clinical, life, drafthouse, quarkmind): see [APPLICATIONS.md](APPLICATIONS.md).

---

## Build / Dependency Order

```
casehub-parent              (BOM — publish first; all others import it)
  casehub-platform          (no casehubio deps — foundational SPIs + CaseMemoryStore adapters as submodules, publishes before ledger)
  casehub-ledger            (no casehubio deps)
  casehub-connectors        (no casehubio deps)
  casehub-work              (api: depends on casehub-platform-api; core: zero other casehubio deps; ledger module: depends on casehub-ledger)
  casehub-qhorus            (depends on casehub-ledger)
  casehub-eidos             (depends on casehub-ledger; casehub-eidos-api depends on nothing)
  casehub-engine            (depends on casehub-work-core + optionally casehub-ledger + optionally casehub-eidos-api)
  casehub-engine-ai         (optional — depends on casehub-engine-api; adds AgentEmbeddingProvider SPI + SemanticAgentRoutingStrategy)
  claudony                  (depends on casehub-qhorus + implements casehub-engine SPIs)
  casehub-openclaw          (depends on casehub-qhorus + casehub-engine SPIs; opt-in — off by default in CI)

  — Application tier (opt-in, off by default in CI): see APPLICATIONS.md —
  casehub-life              (depends on full foundation stack + casehub-openclaw as WorkerProvisioner)
  casehub-drafthouse        (depends on casehub-qhorus; engine + ledger + work added later)
  quarkmind                 (depends on casehub-engine; standalone Quarkus harness app — mdproctor/quarkmind)
```

---

## Cross-Repo Dependency Map

**Purpose:** impact analysis when an artifact changes — rename, removal, SPI break. Look up the artifact here to find every repo that must be updated before the change ships.

**How to maintain:** when adding a cross-repo `<dependency>`, add a row here. When removing one, delete the row. Protocol: [artifact-rename-propagation.md](protocols/artifact-rename-propagation.md).

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
| `casehub-engine-api` | `devtown` | `review` | engine types |
| `casehub-engine` (runtime) | `devtown` | `app` | YamlCaseHub, CaseHubRuntime |
| `casehub-engine-work-adapter` | `devtown` | `app` | HITL bridge — HumanTaskScheduleHandler + WorkItemLifecycleAdapter |
| `casehub-engine-blackboard` | `devtown` | `app` | BlackboardRegistry — transitive via work-adapter; required for plan item tracking |
| `casehub-engine-ledger` | `claudony` | `casehub` | lineage queries |
| `casehub-eidos-api` | `casehub-engine` | `engine-api` | optional capability probe — `AgentDescriptor` on `Worker`; `CapabilityHealth.probe()` in `WorkOrchestrator` |
| `casehub-engine-api` | `casehub-engine-ai` | `ai` | `AgentRoutingStrategy` SPI consumer; `AgentEmbeddingProvider` SPI definition |

| `casehub-platform` | `casehub-aml` | `app` | `@DefaultBean` mocks for casehub-engine CDI wiring (runtime scope — required when engine is present) |
| `casehub-engine` (runtime) | `casehub-aml` | `app` | YamlCaseHub, CaseHubRuntime, engine worker execution |
| `casehub-engine-scheduler-quartz` | `casehub-aml` | `app` | Quartz worker execution for in-process worker functions |
| `casehub-platform-expression` | `casehub-aml` | `app` | JQEvaluator required by engine CDI beans (GE-20260523-86ed13) |
| `casehub-engine-persistence-memory` | `casehub-aml` | `app` | In-memory persistence SPIs for test and tutorial deployment |
| `casehub-engine-ledger` | `casehub-aml` | `app` | Layer 6: trust-weighted routing — activates `TrustWeightedAgentStrategy @ApplicationScoped` and `WorkerDecisionEventCapture`; local V2002/V2003 migrations for `case_ledger_entry` and `worker_decision_entry` join tables (pending engine#395 scoping fix) |

| `casehub-platform` | `casehub-clinical` | `runtime` | `@DefaultBean` mocks for casehub-engine CDI wiring |
| `casehub-platform-expression` | `casehub-clinical` | `runtime` | `JQEvaluator` for engine expression evaluation |
| `casehub-engine` | `casehub-clinical` | `runtime` | case orchestration (`CasePlanModel`, IRB gate, AE escalation) |
| `casehub-engine-work-adapter` | `casehub-clinical` | `runtime` | `HumanTaskScheduleHandler` + `WorkItemLifecycleAdapter` |
| `casehub-engine-scheduler-quartz` | `casehub-clinical` | `runtime` | Quartz worker execution (Layer 5) |

| `casehub-qhorus-api` | `casehub-openclaw` | `core` | `ChannelBackend`, `MessageObserver` SPIs |
| `casehub-qhorus` (runtime) | `casehub-openclaw` | `casehub` | Qhorus runtime for SPI registration |
| `casehub-qhorus-api` | `drafthouse` | `app` | channel routing |
| `casehub-qhorus` (runtime) | `drafthouse` | `app` | runtime dep |
| `casehub-engine-api` | `casehub-openclaw` | `casehub` | `WorkerProvisioner`, `CaseChannelProvider`, `WorkerStatusListener` SPI implementations; uses api (not runtime) to avoid engine CDI beans with unsatisfied persistence SPIs |
| `casehub-platform-api` | `casehub-openclaw` | `core` | `CurrentPrincipal`, `GroupMembershipProvider` (permission-aware context) |
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

**Application tier** (aml, clinical, life) — consume foundation runtime artifacts; see [APPLICATIONS.md](APPLICATIONS.md) for detail.

---

## Capability Ownership — "Where Does X Live?"

| Capability | Owner | Notes |
|---|---|---|
| Hierarchical scope/label path | `casehub-platform-api` | `Path` record — strict segment validation, `isAncestorOf`, `parent`, `depth`. Construct with `Path.of(String...)` (explicit segments) or `Path.parse(String)` (configurable separator via `casehub.platform.path.separator`, default `/`). **Convention for harnesses:** `Path.of("casehubio", "<app>", "<case-type>")` — e.g. `Path.of("casehubio", "devtown", "pr-review")`. Org segment first, app second, case-type third. This makes the inheritance chain work correctly: devtown inherits from casehubio, pr-review inherits from devtown. |
| Typed preference resolution | `casehub-platform-api` | `PreferenceProvider` SPI + `Preferences` interface; `PreferenceKey<T extends Preference>` typed key with `qualifiedName()`; `SettingsScope(Path, Instant)`; `MapPreferences` utility impl. `MockPreferenceProvider` `@DefaultBean`. See [`typed-preference-keys.md`](protocols/casehub/typed-preference-keys.md). **Backends (add as compile dep to activate):** `casehub-platform-config` — YAML file-based, `@ApplicationScoped`, no DB; `casehub-platform-persistence-jpa` — JPA/SQL, `@ApplicationScoped`, requires Flyway at `classpath:db/platform/migration`; `casehub-platform-persistence-mongodb` — MongoDB, `@Alternative @Priority(1)`, beats JPA when co-deployed, startup bean creates scope index. CDI priority ladder: see [`persistence-backend-cdi-priority.md`](protocols/universal/persistence-backend-cdi-priority.md). |
| Current principal identity | `casehub-platform-api` | `CurrentPrincipal` SPI — `actorId()`, `groups()`, `roles()` (= groups by convention, wires to `@RolesAllowed`), `hasGroup()`, `isSystem()`, `isAuthenticated()`, `tenancyId()`, `isCrossTenantAdmin()`. Real impls must be `@RequestScoped`. `MockCurrentPrincipal` `@DefaultBean`. `TenancyConstants` holds `DEFAULT_TENANT_ID` and `PLATFORM_TENANT_ID` sentinels. **OIDC impl:** `casehub-platform-oidc` ships `OidcCurrentPrincipal @RequestScoped` — reads actorId/groups from `SecurityIdentity`, `tenancyId` and `crossTenantAdmin` from fixed JWT claims. Add as compile dep to activate; displaces mock automatically. |
| Group membership lookup | `casehub-platform-api` | `GroupMembershipProvider` SPI — `membersOf(groupName)` returns `Set<GroupMember>` (actorId = OIDC sub = SCIM value UUID, displayName = human label). Empty set = group unknown or has no members. `MockGroupMembershipProvider @DefaultBean` returns empty. **Real implementation:** `casehub-platform-scim` (`@ApplicationScoped`, displaces mock by classpath presence) — SCIM 2.0 two-step fetch, `@CacheResult`, static bearer token or OIDC client-credentials auth. |
| Agent memory (queryable, permission-aware, persistent) | `casehub-platform-api` (SPI + types) / `casehub-platform` (adapters) | `CaseMemoryStore` SPI + value types (`MemoryInput`, `Memory`, `MemoryQuery`, `EraseRequest`, `MemoryDomain`) + `MemoryPermissions` static utility. `NoOpCaseMemoryStore @DefaultBean` in `casehub-platform`; adapters as submodules: `memory-inmem/` (@Alternative @Priority(1) volatile ConcurrentHashMap — add test-scope for @QuarkusTest isolation; compile for ephemeral installs), `memory-jpa/` (@ApplicationScoped PostgreSQL + Flyway V1000 + FTS via websearch_to_tsquery when question provided — add compile-scope for persistence). `BlockingToReactiveBridge @DefaultBean` wraps blocking adapters as `ReactiveCaseMemoryStore`; native async adapters override as `@Alternative @Priority(N)`. |
| Immutable entry chain (Merkle Mountain Range) | `casehub-ledger` | Domain-agnostic; consumers extend `LedgerEntry` via JPA JOINED |
| In-memory persistence (zero datasource / ephemeral install) | `casehub-ledger` | `casehub-ledger-memory` — `@Alternative @Priority(1)` impls of all persistence SPIs; add as compile dep for `@QuarkusTest` isolation |
| Cryptographic tamper evidence | `casehub-ledger` | `LedgerVerificationService` (Merkle: treeRoot/inclusionProof/verify), `AgentSignatureVerificationService` (blocking Ed25519), `ReactiveAgentSignatureVerificationService` (reactive Ed25519), `AgentCryptographicVerifier` (shared static utility) |
| Actor trust scoring (Bayesian Beta + EigenTrust) | `casehub-ledger` | `ActorTrustScore` — four score types: GLOBAL, CAPABILITY, DIMENSION, CAPABILITY_DIMENSION (✅ #76); nightly `TrustScoreJob`, `TrustScoreRoutingPublisher` CDI events |
| Trust score export read-model | `casehub-ledger` | `TrustExportService` (`exportAll`/`exportActor`/`exportDelta`) — consumed by dashboards and upper layers |
| Trust score import SPI | `casehub-ledger` | `TrustImportService` SPI; `JpaTrustImportService` seed-if-absent `@Alternative`; `NoOpTrustImportService` `@DefaultBean` |
| Trust bootstrapping | `casehub-ledger` | `TrustBootstrapSource` SPI + `TrustBootstrapService`; seeds Beta(α,β) from external source on actor first-registration; opt-in via `casehub.ledger.trust-score.bootstrap.enabled` |
| GDPR Art.17 erasure / Art.22 decision records | `casehub-ledger` | `LedgerErasureService`, `ComplianceSupplement` |
| W3C PROV-DM lineage export | `casehub-ledger` | `LedgerProvExportService` |
| OTel trace linkage to audit entries | `casehub-ledger` | `LedgerTraceListener` auto-populates `traceId` from active OTel span |
| Human task inbox (WorkItem lifecycle) | `casehub-work` | 10 statuses, SLA, delegation, escalation, spawn |
| SLA breach policy | `casehub-work-api` | `SlaBreachPolicy` SPI — replaces `EscalationPolicy`; returns `BreachDecision` (Fail / EscalateTo / Extend) with `thenOnBreach` fallback chaining; `SlaBreachContext(BreachType, BreachedTask, Path, Preferences)`; casehub-work executes the decision, fires `SlaBreachEvent` CDI event for side-effect observers. See casehubio/work#213 |
| Named outcome classifications for WorkItems | `casehub-work` | `Outcome` record in `casehub-work-api`; `WorkItemTemplate.outcomes` declares valid names; `WorkItem.outcome` stores resolved name at completion; `WorkItemLifecycleEvent.outcome` carries it for engine routing without parsing `resolution` JSON |
| Conflict-of-interest user exclusion | `casehub-work` | `ExclusionPolicy` SPI in `casehub-work-api` (`check() : PolicyDecision`); `CommaSeparatedExclusionPolicy` `@DefaultBean`; `excludedUsers` TEXT field on `WorkItemTemplate` + `WorkItem`; enforced at claim, create (assigneeId), delegate, auto-assignment, and `SelectionContext`; `BlockedAttemptAuditService` writes `CLAIM_DENIED`/`DELEGATE_DENIED` audit entries via `REQUIRES_NEW` |
| M-of-N parallel WorkItem completion (group policy primitive) | `casehub-work` | `MultiInstanceCoordinator`; `WorkItemGroupLifecycleEvent`; see LAYERING.md |
| Human task routing / selection | `casehub-work-core` | `WorkBroker`, `WorkerSelectionStrategy` SPI; `SemanticWorkerSelectionStrategy` in `casehub-work-ai` (`@Alternative @Priority(1)`) |
| Label-based queue views | `casehub-work-queues` | Optional module on casehub-work |
| Agent routing / selection | `casehub-engine-api` | `AgentRoutingStrategy` SPI; CDI priority resolution in `WorkOrchestrator` (`@Any Instance<AgentRoutingStrategy>`). Implementations: `LeastLoadedAgentStrategy` (engine runtime, `@Priority(0)` default), `TrustWeightedAgentStrategy` (casehub-engine-ledger, `@Priority(1)`), `SemanticAgentRoutingStrategy` (casehub-engine-ai, `@Priority(2)`, optional) |
| Agent embedding vector provider | `casehub-engine-ai` | `AgentEmbeddingProvider` SPI — required by `SemanticAgentRoutingStrategy`; activates semantic agent routing when on classpath (see [`optional-module-pattern.md`](protocols/optional-module-pattern.md)). SPI lives in `casehub-engine-ai` (not `casehub-engine-api`) so the entire feature is opt-in — no embedding provider contract imposed on deployments that don't use semantic routing. |
| Outbound notifications (Slack, Teams, SMS, email) | `casehub-connectors` | `Connector` SPI; `casehub-work-notifications` must delegate here |
| Inbound message reception (webhook push + IMAP pull) | `casehub-connectors` | `WebhookInboundConnector` SPI (push); `InboundConnector` SPI + `InboundConnectorService` polling (pull); fires `Event<InboundMessage>` CDI event; `casehub-connectors-email-inbound` for IMAP via `EmailInboundAccountProvider` SPI |
| Agent-to-agent messaging (typed channels + messages) | `casehub-qhorus` | 9 speech-act types, 5 channel semantics, MCP tools. All writes flow through `MessageService.dispatch(MessageDispatch)` — single gate for ACL, rate limit, LAST_WRITE, ledger, and fan-out. `MessageDispatch` builder carries sender, type, content, correlationId, inReplyTo, artefactRefs, target, actorType, deadline; builder validates protocol invariants at `build()` (DONE/DECLINE/FAILURE/HANDOFF/RESPONSE require inReplyTo + correlationId; HANDOFF requires target). `DispatchResult` carries ledgerEntryId, subjectId, causedByEntryId, parentReplyCount. |
| Dashboard read/write API (composed views: channel with message count, instance with capability tags, timeline mapping, human message send) | `casehub-qhorus` | `QhorusDashboardService` in `io.casehub.qhorus.runtime.dashboard` — inject this for dashboard/UI consumers needing composed views. Do NOT inject raw entity services for this use case. |
| Channel message fan-out to external backends | `casehub-qhorus` | `ChannelBackend` SPI in `casehub-qhorus-api`; implementations in consuming repos (Claudony panel, connectors) |
| Real-time channel feed to Claudony browser panel | `claudony` | `ClaudonyChannelBackend` implements `ChannelBackend` SPI — per-channel scope; ticks `ChannelEventBus` on `post()`, driving SSE delivery via `MeshResource.channelEvents()`. WebSocket is for terminal streaming only. |
| Cross-cutting message notification | `casehub-qhorus` | `MessageObserver` SPI in `casehub-qhorus-api`; `InProcessMessageBus` CDI default (`Scope.LOCAL`); `FleetMessageRelayObserver` in claudony (`Scope.CLUSTER`) — relays a channel-name tick to all healthy fleet peers on every Qhorus message dispatch, enabling real-time SSE delivery across fleet nodes (claudony#118) |
| Agent commitment/obligation tracking | `casehub-qhorus` | `Commitment` with 7-state lifecycle |
| Normative audit of all agent interactions | `casehub-qhorus` | `MessageLedgerEntry` extends `LedgerEntry`; all 9 speech-act types recorded |
| Case/process orchestration (choreography + WAITING) | `casehub-engine` | `CaseInstance`, `EventLog`, `WorkOrchestrator` |
| Worker provisioner SPIs (provision, lifecycle, channels, context) | `casehub-engine` (defines) / `claudony` (implements) | `WorkerProvisioner`, `CaseChannelProvider`, `WorkerContextProvider`, `WorkerStatusListener`. **`postToChannel` is 6-param** (engine#343): `(channel, from, content, MessageType, correlationId, deadline)` — `correlationId` and `deadline` are first-class SPI params, not parsed from content JSON. 3-param convenience default delegates with three nulls. |
| Durable PlanItem status (blackboard persistence) | `casehub-engine` | `PlanItemStore` (blocking) + `ReactivePlanItemStore` (Uni<>) SPIs in `casehub-engine-common`; `@DefaultBean` no-ops in `blackboard`; JPA impl (`JpaReactivePlanItemStore`) in `casehub-engine-persistence-hibernate`; blocking JPA impl (`JpaPlanItemStore`) in `casehub-engine-work-adapter` sharing the casehub-work datasource. Atomicity guarantee: `planItemStore.save(RUNNING)` and WorkItem creation are in the same `@Transactional` boundary. See engine#273. |
| External signal delivery to running cases | `casehub-work-api` (SPI) / `casehub-engine` (impl) | `CaseSignalSink` SPI in `casehub-work-api` — called by casehub-work when SLA escalation fires; implemented in `casehub-engine-work-adapter` calling `CaseHubRuntime.signal()`; Qhorus-driven signals via `QhorusMessageSignalBridge` in engine runtime (`@ObservesAsync MessageReceivedEvent`). Three entry points: SLA escalation → CaseSignalSink, Qhorus message → QhorusMessageSignalBridge, direct REST → CaseHubRuntime. |
| Remote Claude CLI sessions | `claudony` | `TmuxService`, `SessionRegistry`, WebSocket streaming |
| Browser + agent authentication | `claudony` | WebAuthn passkeys + `X-Api-Key` header |
| OpenClaw worker provisioner | `casehub-openclaw` | `WorkerProvisioner` SPI implementation — provisions OpenClaw instances via `POST /hooks/agent`; no heartbeat required for in-case steps. Two modes: heartbeat (OpenClaw autonomous monitoring → creates CaseHub case) vs direct call (CaseHub case step → on-demand skill execution). See [`docs/repos/casehub-openclaw.md`](repos/casehub-openclaw.md). |
| Qhorus ↔ OpenClaw channel bridge | `casehub-openclaw` | `ChannelBackend` SPI — bidirectional: Qhorus dispatches → `ChannelBackend.post()` → `/hooks/agent`; OpenClaw output → `deliver:webhook` → Qhorus endpoint → `MessageService.dispatch()` |
| ChannelContextWindow (short-term channel context for LLM injection) | `casehub-openclaw` | `MessageObserver` SPI → per-channel ring buffer (configurable size + TTL) → REST `GET /channel-context/{agentId}?since={sequenceNumber}`. Python SDK `before_prompt_build` hook injects result as `appendSystemContext` (compaction-safe). Best-effort — correctness guaranteed by Qhorus; intelligence layer only. |
| Ecosystem CI dashboards | `casehub-parent` | `dashboard.yml`, `pr-dashboard.yml`, `full-stack-build.yml` |
| Application domain logic (devtown, aml, clinical, life, drafthouse, quarkmind) | Application tier | See [APPLICATIONS.md](APPLICATIONS.md) |
| Agent descriptor (structured 4-layer identity) | `casehub-eidos` | `AgentDescriptor` record — identity, slot, capabilities, disposition; `tenancyId` always required; `AgentQuery` for criteria-based discovery |
| Agent registry (store + discover by slot/capability) | `casehub-eidos` | `AgentRegistry` (blocking) + `ReactiveAgentRegistry` (reactive, build-gated `casehub.eidos.reactive.enabled`); `InMemoryAgentRegistry` + `InMemoryAgentStateStore` for ephemeral installs via `casehub-eidos-memory` |
| Vocabulary registry (term resolution + cross-vocab equivalence) | `casehub-eidos` | `VocabularyRegistry` SPI + `CdiVocabularyRegistry` @DefaultBean; discovers `@Produces Vocabulary` CDI beans at startup |
| Well-known vocabularies (SVO, Conscientiousness, CasehubSlot) | `casehub-eidos-vocab` | Optional module — add as dependency to activate; Jandex-indexed for CDI bean discovery |
| Agent capability health (declared vs operable) | `casehub-eidos` | `CapabilityHealth` SPI — `probe(AgentDescriptor, capabilityTag, ProbeContext)` returns `CapabilityStatus` (`Ready`, `Degraded`, `Unavailable`, `EpistemicallyWeak`). `DegradationReason` is a top-level type in `casehub-eidos-api` — not nested inside `CapabilityHealth`. `DefaultCapabilityHealth` checks `AgentStateStore` first (degraded state takes precedence), then declared capabilities + epistemic domain confidence; configurable `casehub.eidos.epistemic.weak-threshold` (default 0.3); `ReactiveCapabilityHealth` for reactive parity (build-gated). **Engine integration (engine#341):** `WorkOrchestrator` calls `probe()` at dispatch time for workers that carry an `AgentDescriptor` (via `Worker.agentDescriptor()`, guarded by `Worker.hasDescriptor()`); workers without a descriptor skip the probe and are assumed capable (non-agent workers). Engine provides `NoOpCapabilityHealth @DefaultBean` — deployments without eidos get no filtering. **ProbeContext semantics:** `taskDomain` is the *subject domain* of the task (e.g. `"rust"` within a `"code-review"` capability) — distinct from `capabilityTag`. Pass actual task subject context in `taskDomain`; use `taskMetadata` for additional attributes. Conflating `taskDomain` with `capabilityTag` prevents `EpistemicallyWeak` from triggering correctly. |
| Agent operational state (degradation tracking) | `casehub-eidos` | `AgentStateStore` SPI — `record(agentId, DegradationReason, expiresAt)`, `query(agentId)`. `NoOpAgentStateStore @DefaultBean` (no tracking). `InMemoryAgentStateStore @Alternative @Priority(1)` in `casehub-eidos-memory` (TTL-based ConcurrentHashMap). `DefaultCapabilityHealth` checks store first at probe time — degraded state takes precedence over Ready/EpistemicallyWeak. JPA persistence deferred (eidos#7). |
| System prompt generation | `casehub-eidos` | `SystemPromptRenderer` SPI — `render(AgentDescriptor, AgentPromptContext)` → `RenderedPrompt`; `ClaudeMarkdownRenderer @DefaultBean` implements a two-step pipeline: structural YAML serialization → optional LangChain4j `ChatModel` semantic pass → markdown assembly. `AgentPromptContext` carries `Optional<GoalContext>`, `List<Resource>`, `situationalContext`, `RenderFormat` — re-renderable as agent context evolves. Works without LLM (structural-only). Hashes enable cache invalidation. `DegradationReason`, `AgentPromptContext`, `GoalContext`, `Resource`, `AgentStateStore` are top-level types in `casehub-eidos-api`. |

---

## Key Boundary Rules

**Any casehub repo may depend on `casehub-platform-api`.** It is a zero-external-dependency pure-Java module — taking a compile dependency on it does not force Quarkus, JPA, or any framework onto consumers. Foundation repos (`casehub-work-api`, `casehub-ledger-api`, etc.) may use `Path`, `Preferences`, `CurrentPrincipal` and other platform types in their own SPI signatures.

**Do not define parallel path, scope, preference, or principal types.** `casehub-platform-api` owns `Path`, `SettingsScope`, `PreferenceKey`, `Preferences`, `PreferenceProvider`, `CurrentPrincipal`, and `GroupMembershipProvider`. Repos that need these concepts must depend on `casehub-platform-api` and implement its SPIs — they must not define their own equivalent types.

**Do not add orchestration logic to `casehub-work`.** When a WorkItem completes, casehub-work fires a CDI event and stops. Homogeneous M-of-N group completion is casehub-work. Heterogeneous plan-level completion is casehub-engine. "Mark the WorkItem EXPIRED when its deadline passes" is casehub-work.

**Do not add WorkItem inbox management to `casehub-engine`.** casehub-engine depends on `casehub-work-core` (`WorkBroker`) only. WorkItem entities, Flyway migrations, REST endpoints must not flow into the engine.

**Do not add trust scoring to `casehub-work` or `casehub-engine`.** Trust lives in casehub-ledger and is surfaced via CDI routing events (`TrustScoreRoutingPublisher`). Consumers observe those events — they never compute trust themselves.

**Do not duplicate notification infrastructure.** `casehub-connectors` owns Slack/Teams/SMS/email. `casehub-work-notifications` must delegate here.

**Do not implement Qhorus channel semantics in `claudony`.** Claudony embeds Qhorus and adds SPI implementations. It must not re-implement channel, message, or commitment logic. Implementing `ChannelBackend` or `MessageObserver` SPIs from `casehub-qhorus-api` is not re-implementation — it is correct SPI usage.

**Do not call `QhorusMcpTools` or `ReactiveQhorusMcpTools` from consumer service code.** Those classes are the MCP tool dispatch layer for external callers (Claude Code); they carry `@WrapBusinessError` exception semantics that internal consumers must not be exposed to. Consumer service code has three correct integration points: (1) **Dashboard/UI consumers** needing composed views (channel with message count, instance with capability tags, timeline entries) — inject `QhorusDashboardService`. (2) **Service-layer integrations** that need to send messages — call `MessageService.dispatch(MessageDispatch)` (blocking) or `ReactiveMessageService.dispatch(MessageDispatch) → Uni<DispatchResult>` (reactive). These are the enforcement gates: paused check, ACL, rate limiting, LAST_WRITE semantics, ledger write, and fan-out all happen inside `dispatch()`. Do not bypass to entity stores for write operations. (3) **Reactive event-driven integrations** — implement `ChannelBackend` or `MessageObserver` SPI. Note: injecting entity services directly is also wrong for dashboard consumers — `ReactiveChannelService.listAll()` returns entities without message counts, requiring store-layer injection and creating worse coupling. See `docs/protocols/casehub/qhorus-consumer-integration-pattern.md`.

**Choose `ChannelBackend` vs `MessageObserver` based on scope.** `ChannelBackend` is per-channel and knows its context — use it when a consumer needs to act on messages from a specific channel (e.g. Claudony panel display). `MessageObserver` is a global broadcast across all channels — use it for cross-cutting concerns (e.g. clinical PI response monitoring). For topology guidance (LOCAL CDI vs CLUSTER-scoped transport) see [`docs/repos/casehub-qhorus.md`](repos/casehub-qhorus.md) and [qhorus `docs/messaging-architecture.md`](https://github.com/casehubio/qhorus/blob/main/docs/messaging-architecture.md).

**Do not put CaseHub SPI implementations in `casehub-engine`.** casehub-engine defines them; deployment-specific implementations belong in the deploying application.

**Do not use `casehub-work` runtime in `casehub-engine`.** The engine depends on `casehub-work-core` only.

**Use `CaseSignalSink` (in `casehub-work-api`) as the only path for external events that must unblock a waiting case.** casehub-work injects and calls `CaseSignalSink` at SLA escalation time; the implementation in `casehub-engine-work-adapter` translates to `CaseHubRuntime.signal()`. Qhorus message signals route via `QhorusMessageSignalBridge` in engine runtime. Do not add case-signaling logic to any other module.

**Do not add domain logic to foundation repos.** If the capability requires knowledge of software development, clinical trials, or financial crime, it belongs in an application repo.

**Do not re-implement CapabilityHealth probe semantics in casehub-engine.** Engine calls `CapabilityHealth.probe()` via the `casehub-eidos-api` SPI contract from `WorkOrchestrator`. Engine provides a `NoOpCapabilityHealth @DefaultBean` for deployments without eidos — that is the full extent of engine's responsibility. Do not add `AgentDescriptor`, vocabulary, or epistemic domain logic to engine types. `Worker` carries an optional `AgentDescriptor` field for probe dispatch only — not for identity, registry, or vocabulary operations.

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

**Flyway path scoping rule:** Every module must ship migrations under a repo-scoped path (`db/<reponame>/migration/`) — never the generic `db/migration/`. See [`PP-20260525-607b33`](../garden/docs/protocols/universal/flyway-repo-scoped-migration-path.md). Consumers must configure `quarkus.flyway.locations=classpath:db/<repo>/migration` explicitly — Quarkus has no runtime auto-registration mechanism. See [`PP-20260528-flyway-ext-reg`](protocols/universal/flyway-extension-migration-registration.md).

**Named datasource rule:** Qhorus always runs on named `qhorus` datasource. Claudony uses separate `claudony` and `qhorus` persistence units.

### Observability

- OTel trace → ledger: `LedgerTraceListener` auto-populates `traceId` at `@PrePersist`
- Agent interactions: `MessageLedgerEntry` records all 9 message types
- WorkItem audit: `AuditEntry` (always-on) + optional `WorkItemLedgerEntry` (tamper-evident)
- Case decisions: `EventLog` (engine-internal) + optional `CaseLedgerEntry` (external, tamper-evident)

### Authentication

**Gateway topology:** Claudony is the single authenticated entry point for all human operators and Claude agent sessions. Internal foundation services (Qhorus, casehub-engine, casehub-work) carry no auth annotations on their REST resources — they trust callers implicitly, relying on network policy or mTLS for isolation. This contract is only valid when Claudony sits in front. A standalone deployment of Qhorus, engine, or work without Claudony requires an auth proxy or Quarkus OIDC/JWT before any external traffic is admitted. The A2A endpoint on Qhorus (`POST /a2a/message:send`) extends this posture to the agent surface — no token auth is applied at the Qhorus layer; the caller is trusted. See [`docs/protocols/casehub/auth-retrofit-readiness.md`](protocols/casehub/auth-retrofit-readiness.md) for rules on keeping services auth-retrofit-ready while this remains implicit.

| Context | Owner | Mechanism |
|---|---|---|
| Extension-level | Consuming app | Extensions provide no auth |
| Browser → Claudony | `claudony` | WebAuthn passkeys |
| Agent → Claudony | `claudony` | `X-Api-Key` header |
| Channel write ACL | `casehub-qhorus` | `allowed_writers` on `Channel` |
| Internal service-to-service | Network boundary | Trust implicit — no token auth on Qhorus, engine, or work REST resources |

### Privacy (GDPR)

All GDPR concerns centralised in `casehub-ledger`:
- Art.17 erasure: `LedgerErasureService` + `ActorIdentityProvider` SPI
- Art.22 decision records: `ComplianceSupplement`
- PII sanitisation: `DecisionContextSanitiser` SPI

### Agent Identity

Format: `{model-family}:{persona}@{major}` — e.g. `"claude:analyst@v1"`. Defined in casehub-ledger ADR 0004. Major version bump resets trust baseline.

### Agent Communication Mesh

The platform uses a normative 3-channel layout for agent-to-agent and agent-to-human interactions:

| Channel | Purpose | Primary speech acts |
|---------|---------|---------------------|
| `work` | Task assignment and completion (prescriptive) | COMMAND, RESPONSE, DONE, DECLINE, EXPIRED |
| `observe` | Passive monitoring and state sharing (descriptive) | EVENT, QUERY, STATUS |
| `oversight` | Human governance gates (commitment-based) | COMMAND → human, RESPONSE from human |

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
| SQL type portability (GE-20260512-2c2eff) | `DOUBLE PRECISION` not `DOUBLE`; `SMALLINT` not `TINYINT` — garden `jvm/` domain |
| [Flyway migration rules](protocols/flyway-migration-rules.md) | Version namespace ranges; `MODE=PostgreSQL` in all H2 test URLs |
| [Flyway extension migration registration](protocols/universal/flyway-extension-migration-registration.md) | Extensions use repo-scoped `db/<repo>/migration/` paths + `NativeImageResourcePatternsBuildItem`; Quarkus consumers must configure `quarkus.flyway.locations` explicitly — no runtime auto-registration exists |
| [Optional module pattern](protocols/optional-module-pattern.md) | Jandex library module; zero cost when absent |
| [Quarkus test database](protocols/quarkus-test-database.md) | H2 `MODE=PostgreSQL`; Testcontainers for dialect validation |
| [Submodule folder naming](protocols/universal/maven-submodule-folder-naming.md) | Short names — no repo prefix. `api` not `casehub-work-api` |
| [Reactive-service build gating](protocols/casehub/reactive-service-build-gating.md) | Extensions gate the reactive tier via `@IfBuildProperty(name="casehub.<module>.reactive.enabled", stringValue="true")` backed by a `@ConfigRoot(phase=BUILD_TIME)` config in deployment/. Default false — blocking-only consumers pay no Hibernate Reactive cost. Write methods use `@WithTransaction`; no `withSafeContext` wrapper needed with Panache repos. Every `Reactive*Service` must mirror its blocking counterpart (ArchUnit 1.4.1, casehub-ledger). |
| [Persistence-backend CDI priority](protocols/universal/persistence-backend-cdi-priority.md) | `@DefaultBean` → `@ApplicationScoped` → `@Alternative @Priority(1)` — backend activates by classpath presence, no consumer changes |

Full index: [`docs/protocols/INDEX.md`](protocols/INDEX.md)

---

## Known Overlap Risks

1. **`EventLog` vs `CaseLedgerEntry`** (engine) — `EventLog` is operational (restart recovery, observability). `CaseLedgerEntry` is the compliance record (tamper-evident). If a lifecycle transition doesn't fire `CaseLifecycleEvent`, it won't be ledgered — and the async observer can fail silently. See [`docs/protocols/casehub/dual-trail-audit-pattern.md`](protocols/casehub/dual-trail-audit-pattern.md) for the write rule, failure modes, and detection queries.
2. **`AuditEntry` vs `WorkItemLedgerEntry`** (work) — `AuditEntry` is always-on operational. `WorkItemLedgerEntry` is opt-in tamper-evident and is what trust score computation reads. A state transition that calls `audit()` but omits the CDI event produces an operational record but no compliance record, and silently corrupts trust scores. See [`docs/protocols/casehub/dual-trail-audit-pattern.md`](protocols/casehub/dual-trail-audit-pattern.md).
3. **`CommitmentState.DELEGATED` (Qhorus) ≠ `WorkItemStatus.DELEGATED` (work)** — same word, opposite terminal semantics. Qhorus DELEGATED is **terminal** for the original obligor (obligation transferred, closed, child Commitment created for the named target). Work DELEGATED is **non-terminal** (`isTerminal()` returns false — work reassigned to a named actor, item stays active). Integration code bridging a Qhorus HANDOFF to WorkItem delegation will misapply terminal semantics. A developer reasoning about a HANDOFF-then-DELEGATED path expects the obligation to end — it does not. See javadoc on `CommitmentState.DELEGATED` and `WorkItemStatus.DELEGATED`.
4. **Notification duplication** — `casehub-connectors` and `casehub-work-notifications` both provide Slack/Teams. Must converge (parent#5, open).
5. **`callerRef` format is implicit** — carries `case:{caseId}/pi:{planItemId}`. casehub-work treats it as opaque. Consumers must know this format out of band.

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
| `claudony` | `repos/claudony.md` |
| `casehub-connectors` | `repos/casehub-connectors.md` |
| `casehub-devtown` | `repos/casehub-devtown.md` |
| `casehub-aml` | `repos/casehub-aml.md` |
| `casehub-clinical` | `repos/casehub-clinical.md` |
| `quarkmind` | `repos/quarkmind.md` |

Application tier: see [APPLICATIONS.md](APPLICATIONS.md)
