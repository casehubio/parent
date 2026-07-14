# Cross-Repo Dependency Map

> **Scope:** Repo topology, build order, and dependency impact analysis
> **Audience:** Platform builders (app builders rarely need this)
> **Key repos:** all foundation repos

## Repository Map

| Repo | GitHub | One-liner | Tier |
|------|--------|-----------|------|
| `casehub-parent` | [casehubio/parent](https://github.com/casehubio/parent) | BOM, CI dashboards, full-stack build tooling | — |
| `casehub-platform` | [casehubio/platform](https://github.com/casehubio/platform) | Zero-dep foundational SPIs — Path, Preferences, Identity. **Memory SPI types and backends migrated to `casehub-neocortex` (neocortex#56)** — see neocortex entry. Platform `memory-*` modules are legacy stubs pending removal. Modules: `platform-api` (SPIs — Path, Preferences, CurrentPrincipal, ActorStateContributor), `platform` (@DefaultBean mocks), `testing` (@Alternative identity fixtures), `config/` (YAML preference provider), `oidc/` (OIDC CurrentPrincipal), `expression/` (JQEvaluator), `persistence-jpa/` (JPA PreferenceProvider — Flyway, @ApplicationScoped), `persistence-mongodb/` (MongoDB PreferenceProvider — @Alternative @Priority(1), no Flyway), `scim/` (SCIM 2.0 GroupMembershipProvider — @ApplicationScoped, displaces mock by classpath presence, platform#45), `agent-api/` (AgentProvider SPI — Mutiny only, no Quarkus. Package: `io.casehub.platform.agent`), `agent-claude/` (@ApplicationScoped ClaudeAgentProvider + ClaudeAgentClient @Startup — activates by classpath presence, requires Claude CLI, concurrent-session semaphore. Two subprocess paths: `invoke()` → `ClaudeOneShotProcess` (direct ProcessBuilder, immediate destroyForcibly — eidos#52); `openSession()` → ClaudeAgentSession (SDK session mode, multi-turn). `ClaudeAgentClient` CDI constructor requires `ObjectMapper`. Package: `io.casehub.platform.agent.claude`), `agent-langchain4j/` (bidirectional LangChain4j interop — ChatModelAgentProvider (any ChatModel → AgentProvider) + AgentProviderChatModel (any AgentProvider → ChatModel); no longer Claude-specific. @Alternative @Priority(10). Not for use with engine.Agent which forces JSON mode), `streams-kafka/` (SmallRye reactive messaging, static topics, raw byte[], builds CloudEvent from STREAM_EVENT_TYPE), `streams-amqp/` (AMQP reactive messaging, single address, same CloudEvent pattern), `streams-webhook/` (@Startup JAX-RS, structured CloudEvents HTTP binding, CloudEventBuilder.from() preserve+enrich), `streams-poll/` (@Scheduled HTTP GET, HttpClient field, explicit status code check, polling EndpointRegistry HTTP endpoints), `streams-camel/` (dynamic Camel route builder, @ObservesAsync EndpointRegistered for EndpointProtocol.CAMEL, idempotent routedUris set). Adapters are submodules — extracted to a standalone repo only when a confirmed non-CaseHub consumer warrants it (see `PP-20260529-spi-adapter-placement`). | Foundation |
| `casehub-worker` | [casehubio/casehub-worker](https://github.com/casehubio/casehub-worker) | Worker primitive foundation — `Worker`, `Capability`, `WorkerFunction`, `WorkerResult`, `WorkerOutcome` (sealed interface: `Success(PlannedAction)`, `Declined(reason)`, `Failed(reason)`, `Expired(reason)`), `PlannedAction`. `Worker` record carries `Set<String> capabilityNames` (not `List<Capability>` — engine#591); workers declare support by name, engine resolves authoritative `Capability` instances from `CaseDefinition.getCapabilities()`. Builder: `capabilityName(String)` or `capabilityNames(String...)`. `YamlCaseHub.getDefinition()` is `final` with `protected void augment(CaseDefinition)` hook for subclasses. Consumed by `casehub-engine` and `casehub-desiredstate`. Modules: `casehub-worker-api` (pure-Java value types + `WorkerFunction` interface — no Quarkus, no JPA), `casehub-worker` (`DefaultWorkerExecutor` — capability-aware `execute(Worker, Capability, Map)` with validation guards and OTel `worker.capability` span attribute), `casehub-worker-testing` (`MockWorkerExecutor` `@DefaultBean @ApplicationScoped`, `TestWorkerBuilder` with `syncWithCapability()` convenience and `WorkerWithCapability` record). | Foundation |
| `casehub-ledger` | [casehubio/ledger](https://github.com/casehubio/ledger) | Immutable tamper-evident audit ledger + trust scoring. Modules: `api`, `runtime`, `deployment`, `persistence-memory` (`casehub-ledger-memory` — zero-datasource in-memory SPIs). SCIM2 agent DID resolution via `ScimActorDIDProvider @Alternative`. | Foundation |
| `casehub-work` | [casehubio/work](https://github.com/casehubio/work) | Human task lifecycle (WorkItem inbox, SLA, delegation, routing) | Foundation |
| `casehub-qhorus` | [casehubio/qhorus](https://github.com/casehubio/qhorus) | Peer-to-peer agent communication mesh | Foundation |
| `casehub-connectors` | [casehubio/connectors](https://github.com/casehubio/connectors) | Outbound and inbound message connectors (Slack, Teams, SMS, email outbound; webhook + IMAP email inbound) | Foundation |
| `casehub-iot` | [casehubio/iot](https://github.com/casehubio/iot) | Typed IoT device abstraction layer — `DeviceEntity` hierarchy (Matter-aligned), `DeviceProvider` SPI (reactive `Uni<>` returns), `StateChangeEvent` CDI bus, `DeviceCommand` dispatch. Modules: `api` (public API — semver), `homeassistant` (HA REST + WebSocket provider + HA supplement types), `openhab` (OpenHAB REST + SSE provider + OH supplement types), `testing` (MockDeviceProvider, Java `Fixtures` + YAML `DeviceFixtureLoader`, `DeviceTypeHandler` SPI with 16 handlers, `StateChangeEventPublisher`), `bridge` (local bridge agent — event relay, CDI filter chain, WebSocket client), `bridge-server` (cloud-side `BridgeDeviceProvider implements DeviceProvider` — remote devices look local to cloud consumers; `DeviceTypeIdResolver` for compound type ID serialization; 6 deployment topologies), `bridge-persistence-jpa` (JPA BridgeAuditStore with configurable data retention — `casehub.iot.bridge.audit-store.jpa.retention-days` optional, `casehub.iot.bridge.audit-store.jpa.purge-interval` default 24h; `@Scheduled` purge job, bulk JPQL DELETE; iot#40), `webapp` (standalone Quarkus operational console — 8 REST resource groups: devices, situations, cases, workitems, bridge, providers, SSE events, health; three-datasource Flyway layout: default for bridge audit + webapp tables, `iot-work` for work + ledger migrations, `iot-ras` for RAS migrations), `webapp-api` (reusable by casehub-life for IoT ganglia and case descriptors — 5 JavaSwitch ganglia: MotionAtTime, TemperatureThreshold, DeviceUnavailable, LockState, PowerAnomaly; 4 case descriptors: SecurityAlert, SafetyAlert, HvacAnomaly, GenericResponse; `IoTActionRiskClassifier`; 3 worker functions: DeviceCommand, HouseholdNotification, HumanDecision), `webapp-drools` (2 DroolsCEP ganglia: SustainedTemperatureRise, MultiRoomMotion). **Note:** `api` module now includes Jackson annotations for `DeviceTypeIdResolver`. Triggers `casehub-life` downstream on publish. Refs iot#44. | Foundation |
| `casehub-ras` | [casehubio/casehub-ras](https://github.com/casehubio/casehub-ras) | Reticular Activating System — situational awareness and reactive case creation. Observes `@ObservesAsync CloudEvent` from `casehub-platform-api`; routes to pluggable `Ganglion` detection strategies (`JavaSwitch`, `DroolsCEP`, `Bayesian`, `LLM`); correlates composite events; triggers `startCase()` when situation threshold crossed. Stream infrastructure (Quarkus/Camel) lives in casehub-platform stream submodules. `ras-llm` module remains Integration tier (LLM infrastructure dep); all other modules are Foundation. | Foundation |
| `casehub-desiredstate` | [casehubio/casehub-desiredstate](https://github.com/casehubio/casehub-desiredstate) | Generic desired-state management runtime — `DesiredStateGraph`, `TransitionPlanner` (pruning-first), `ReconciliationLoop`, `FaultPolicyEngine`; SPIs: `GoalCompiler`, `ActualStateAdapter`, `NodeProvisioner`, `FaultPolicy`, `EventSource`, `TransitionExecutor`, `HumanNodeHandler`, `PendingApprovalHandler`. `NodeSpec` marker interface has `default boolean requiresHuman()` method — domain specs override to declare non-automatable nodes; `DesiredNode` overrides its accessor with OR composition (`requiresHuman || spec.requiresHuman()`). Domain-agnostic; delegates to `casehub-engine-flow`; human nodes and approval workflows via casehub-work WorkItems. 6 modules: api, runtime, testing, engine-adapter, examples/dungeon, examples/pipeline. Runtime module: OTel tracing instrumentation (`opentelemetry-api`) on `ReconciliationLoop` and `SimpleTransitionExecutor`. **Examples:** Nefarious Dungeons (entity hierarchy), Data Pipeline (medallion architecture — Bronze/Silver/Gold, schema validation, three-tier fault escalation: auto-retry → AI_REVIEW via real `AgentProvider` SPI for LLM diagnosis → HUMAN_REVIEW via casehub-work `WorkItem`; pluggable `ExecutionBackend` strategy per processing stage for per-node execution dispatch). Research project. | Foundation |
| `casehub-blocks` | [casehubio/blocks](https://github.com/casehubio/blocks) | Reusable building blocks composed from qhorus, engine, work primitives | Foundation-adjacent |
| `casehub-blocks-ui` | [casehubio/blocks-ui](https://github.com/casehubio/blocks-ui) | Shared UI components for CaseHub applications — composed from casehub-pages primitives. TypeScript/Yarn monorepo. Components: `case-timeline` (case lifecycle), `trust-score-panel` (Bayesian Beta visualisation), `channel-activity` (qhorus message feed). `blocks-ui-core` thinning to domain types only after a11y mixins, SchemaForm, and event helpers migrated to casehub-pages (pages#116). UI parallel to casehub-blocks (shared Java patterns). | Foundation-adjacent |
| `casehub-engine` | [casehubio/engine](https://github.com/casehubio/engine) | Hybrid choreography+blackboard orchestration engine | Orchestration |
| `claudony` | [casehubio/claudony](https://github.com/casehubio/claudony) | Remote Claude CLI sessions + unified ecosystem dashboard | Integration |
| `casehub-openclaw` | [casehubio/openclaw](https://github.com/casehubio/openclaw) | CaseHub × OpenClaw integration — ChannelContextWindow, WorkerProvisioner, ChannelBackend SPI, Python SDK context hook | Integration |
| `casehub-workers` | [casehubio/workers](https://github.com/casehubio/workers) | HTTP, Camel, and GitHub Actions worker dispatch adapters — `workers-common` (shared dispatch SPI; `PermanentFaultException`, `RetryAfterException`), `workers-camel` (Apache Camel route-based dispatch), `workers-http` (HTTP POST worker dispatch), `workers-github-actions` (`workflow_dispatch` + `repository_dispatch` REST APIs) | Integration |
| `casehub-ops` | [casehubio/casehub-ops](https://github.com/casehubio/casehub-ops) | Domain implementations of `casehub-desiredstate` SPIs for CasehHub-specific deployment concerns. Modules: `deployment` (`DeploymentGoalCompiler` — processes `casehub-deployment.yaml` goal declaration into a `DesiredStateGraph`; 5 node types: agents, channels, case types, trust policies, endpoints. Endpoint provisioning registers `EndpointDescriptor` in `EndpointRegistry` — stream modules discover and react to registered endpoints. `DeploymentProviderConfigStore` maintains reverse index (`providerName → Set<agentId>`) for O(1) `agentIdsForProvider()` lookups), `infra` (Terraform/Ansible augmentation), `compliance` (SOC2/GDPR/EU-AI-Act/DORA posture), `iot` (IoT desired state). `casehub-desiredstate` stays domain-agnostic; casehub-ops is the CasehHub domain layer above it. Research project and reference architecture. | Integration |
| `casehub-eidos` | [casehubio/eidos](https://github.com/casehubio/eidos) | Agent identity — descriptor, discovery registry, vocabulary system, system prompt generation | Foundation |
| `casehub-neocortex` | [casehubio/neocortex](https://github.com/casehubio/neocortex) | ONNX neural text inference (NLI, classification, SPLADE, reranking) + LangChain4j RAG integration with hybrid search + agent memory SPI and backends. `rag-api`, `rag`, `rag-testing` consumed by Hortora/engine (neocortex#35). Memory SPI types (`CaseMemoryStore`, `ReactiveCaseMemoryStore`, `GraphCaseMemoryStore`, value types) migrated from `casehub-platform-api` to `casehub-neocortex-memory-api` (package `io.casehub.neocortex.memory`); `NoOpCaseMemoryStore` + `BlockingToReactiveBridge` in `casehub-neocortex-memory`; backends: `memory-inmem`, `memory-jpa`, `memory-sqlite`, `memory-mem0`, `memory-graphiti`, `memory-qdrant`, `memory-cbr-inmem`, `memory-testing`. Refs neocortex#56. | Foundation |
| `casehub-poc` | [casehubio/casehub](https://github.com/casehubio/casehub) | **Retiring** — original POC; no new features | — |
| `casehub-devtown` | [casehubio/devtown](https://github.com/casehubio/devtown) | PR review automation, merge queue management, GitHub integration | Application |
| `casehub-aml` | [casehubio/aml](https://github.com/casehubio/aml) | Anti-money laundering case management | Application |
| `casehub-clinical` | [casehubio/clinical](https://github.com/casehubio/clinical) | Clinical adverse event investigation | Application |
| `casehub-life` | [casehubio/life](https://github.com/casehubio/life) | Personal life automation | Application |
| `casehub-drafthouse` | [casehubio/drafthouse](https://github.com/casehubio/drafthouse) | Document review and multi-participant LLM debate | Application |
| `casehub-soc` | [casehubio/soc](https://github.com/casehubio/soc) | Security operations center | Application |
| `casehub-fsitrading` | [casehubio/fsitrading](https://github.com/casehubio/fsitrading) | Financial services trading compliance | Application |
| `quarkmind` | [casehubio/quarkmind](https://github.com/casehubio/quarkmind) | StarCraft II game AI — living lab proving the CaseHub harness pattern at millisecond game-loop granularity outside regulated domains | Application |
| `flow` (scaffold) | [mdproctor/flow](https://github.com/mdproctor/flow) | Reference deployment — composes engine + work + ledger + persistence into a runnable Quarkus app. REST endpoints being extracted to per-library `-rest` modules (engine#657); scaffold will become a thin composition of those modules. | Application |

Application tier (devtown, aml, clinical, life, drafthouse, quarkmind, soc, fsitrading): see [APPLICATIONS.md](../APPLICATIONS.md).

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
  casehub-neocortex       (inference-*: zero casehubio deps; rag-*: depends on casehub-platform-api + LangChain4j; memory-api: zero casehubio deps; memory backends: various. Publishes before engine, aml, devtown, clinical, life, soc, fsitrading — all memory consumers)
  casehub-engine            (depends on casehub-work-core + optionally casehub-ledger + optionally casehub-eidos-api)
  casehub-ras               (depends on casehub-platform-api + casehub-engine-api; ras-llm module is Integration tier, all others Foundation)
  casehub-desiredstate      (depends on casehub-platform-api; engine-adapter depends on casehub-engine-common)
  casehub-blocks            (depends on casehub-qhorus-api, casehub-work-api, casehub-engine-api — foundation-adjacent library)
  casehub-blocks-ui         (depends on casehub-pages + engine + work + qhorus + ledger + blocks — TypeScript/Yarn; foundation-adjacent UI components rendering data from the full foundation stack)
  casehub-engine-ai         (optional — depends on casehub-engine-api; adds AgentEmbeddingProvider SPI + SemanticAgentRoutingStrategy)
  casehub-engine-flow       (optional — depends on casehub-engine-common only; enables Worker(Workflow) to dispatch casehub workers from Serverless Workflow steps)
  claudony                  (depends on casehub-qhorus + implements casehub-engine SPIs)
  casehub-openclaw          (depends on casehub-qhorus + casehub-engine SPIs; opt-in — off by default in CI)
  casehub-workers           (depends on casehub-engine-api + casehub-engine-common; opt-in — off by default in CI)
  casehub-ops               (depends on casehub-desiredstate + casehub-platform-api; Integration tier)

  — Application tier (opt-in, off by default in CI): see APPLICATIONS.md —
  casehub-life              (depends on full foundation stack + casehub-openclaw as WorkerProvisioner)
  casehub-drafthouse        (depends on casehub-qhorus; engine + ledger + work added later)
  quarkmind                 (depends on casehub-poc + casehub-engine-api + casehub-engine-blackboard; migrating from poc to engine — casehubio/quarkmind#193)
  casehub-soc               (depends on full foundation stack — engine, ledger, work, qhorus, worker, platform)
  casehub-fsitrading        (depends on full foundation stack — engine, ledger, work, qhorus, worker, platform)
```

## Cross-Repo Dependencies

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
| `casehub-platform-api` | `casehub-neocortex` | `rag` | `CurrentPrincipal`, `TenancyConstants` — tenant-scoped corpus isolation |
| `casehub-neocortex-inference-api` | `casehub-eidos` | `runtime` | `ScalarRegressor` — dynamic epistemic domain confidence estimation (future) |
| `casehub-neocortex-inference-api` | `casehub-engine` | `runtime` | `NliClassifier` — hallucination detection hook (future, #154) |
| `casehub-engine-api` | `quarkmind` | `quarkmind-agent` | `CaseContext` interface — Phase 1 plugin API migration (quarkmind#193) |
| `casehub-engine-blackboard` | `quarkmind` | `quarkmind-agent` | `CaseContextImpl` — test scope only, for synthetic `CaseContext` construction |
| `casehub-neocortex-rag-api` | `casehub-engine` | `runtime` | `CaseRetriever`, `ReactiveCaseRetriever` — fact space prompt compiler context injection (future) |
| `casehub-neocortex-rag-api` | `Hortora/engine` | garden retrieval engine | `CaseRetriever`, `EmbeddingIngestor` SPIs — replaces duplicated Qdrant/ingestion code; tenancy via `TenantGuard` (neocortex#35, #36) |
| `casehub-neocortex-rag` | `Hortora/engine` | garden retrieval engine | RAG pipeline implementation (Qdrant, hybrid RRF, ingestion bridge) |
| `casehub-neocortex-rag-testing` | `Hortora/engine` | test | In-memory `EmbeddingIngestor` + `CaseRetriever` stubs for `@QuarkusTest` isolation |
| `casehub-engine-api` | `casehub-engine-ai` | `ai` | `AgentRoutingStrategy` SPI consumer; `AgentEmbeddingProvider` SPI definition |
| `casehub-desiredstate-api` | `casehub-ops` | `api` | `GoalCompiler`, `NodeProvisioner`, `ActualStateAdapter`, `FaultPolicy`, `EventSource`, `TransitionExecutor`, `HumanNodeHandler`, `PendingApprovalHandler` SPIs |
| `casehub-desiredstate-api` | `casehub-ops` | `infra` | SPI implementations |
| `casehub-desiredstate` (runtime) | `casehub-ops` | `infra` | `DefaultDesiredStateGraphFactory` (test scope) |
| `casehub-platform-agent-api` | `casehub-desiredstate` | `examples/pipeline` | `AgentProvider` SPI for AI_REVIEW fault node LLM diagnosis (desiredstate#37) |
| `casehub-eidos-api` | `casehub-ledger` | CBR subsystem | `BehavioralSignalStore` SPI — accumulates learned signals (DECLINE, SUCCESS, COMPLIANT, VIOLATED) per capability with per-signal TTL for routing exclusion and compliance checking (eidos#55, eidos#85) |
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
| `casehub-neocortex-memory-api` | `casehub-aml` | `app` | Memory SPI types (`CaseMemoryStore`, value types) — migrated from `casehub-platform-api` (neocortex#56) |
| `casehub-neocortex-memory-jpa` | `casehub-aml` | `app` | JPA-backed `CaseMemoryStore` for production — Layer 8 prior entity context and SAR outcome memory (aml#32) |
| `casehub-neocortex-memory-inmem` | `casehub-aml` | `app` | In-memory `CaseMemoryStore` for test isolation — Layer 8 (aml#32) |
| `casehub-neocortex-memory-inmem` | `casehub-devtown` | `app` | In-memory `CaseMemoryStore` for `@QuarkusTest` isolation (devtown#43) |
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
| `casehub-blocks` | `quarkmind` | `quarkmind-agent` | Summarisation framework — `EventStreamBus`, `SummarisationRunner`, etc. (blocks#27) |
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

**Application tier** (aml, clinical, life) — consume foundation runtime artifacts; see [APPLICATIONS.md](../APPLICATIONS.md) for detail.
