# CaseHub Consumer Index

> For app builders. What modules to depend on, what APIs to call, what SPIs to implement.
> Each link goes to a repo's `consumer-guide.md` — aggregated from child repos via git subtree.

---

## Orchestration & Cases

**Engine** — case lifecycle, YAML DSL, planning strategies, worker dispatch, oversight gates
→ [repos/casehub-engine/consumer-guide.md](repos/casehub-engine/consumer-guide.md)
Key types: `CaseDefinition`, `CasePlanModel`, `PlanItem`, `Worker`, `Binding`, `GoalExpression`, `WorkerResult`

**Work** — human task inbox, WorkItem lifecycle (11 statuses), SLA, delegation, M-of-N quorum, progress tracking
→ [repos/casehub-work/consumer-guide.md](repos/casehub-work/consumer-guide.md)
Key types: `WorkItem`, `WorkerSelectionStrategy`, `SlaBreachPolicy`, `SpawnPort`, `ProgressInstance`

**Worker** — automated task primitives: `Worker`, `Capability`, typed `WorkerFunction<T,R>`, execution policy
→ [repos/casehub-worker/consumer-guide.md](repos/casehub-worker/consumer-guide.md)
Key types: `Worker`, `Capability`, `WorkerFunction<T,R>`, `WorkerResult<R>`, `WorkerScope`

---

## Agent Communication

**Qhorus** — speech acts, commitments, channels, message delivery, dispatch gates, topic-aware projections, OTel tracing
→ [repos/casehub-qhorus/consumer-guide.md](repos/casehub-qhorus/consumer-guide.md)
Key types: `ChannelManager`, `MessageDispatcher`, `Commitment`, `ChannelProjection`, `MessageObserver`

---

## Agent Identity & Behaviour

**Eidos** — structured agent identity (4-layer descriptors), capability health probing, system prompt rendering, vocabulary, behavioural contracts
→ [repos/casehub-eidos/consumer-guide.md](repos/casehub-eidos/consumer-guide.md)
Key types: `AgentDescriptor`, `AgentCapability`, `AgentRegistry`, `CapabilityHealth`, `SystemPromptRenderer`

---

## Audit & Trust

**Ledger** — tamper-evident audit (Merkle MMR), peer attestation, EigenTrust reputation, GDPR erasure, cloud KMS signing
→ [repos/casehub-ledger/consumer-guide.md](repos/casehub-ledger/consumer-guide.md)
Key types: `LedgerEntry`, `LedgerAttestation`, `TrustGateService`, `LedgerAppender`, `ActorIdentityProvider`

---

## AI & Knowledge

**Neocortex** — ONNX inference (NLI, classification, reranking, SPLADE), RAG pipelines (3-leg hybrid search), CBR (typed features, trend detection, plan adaptation), agent memory SPI
→ [repos/casehub-neocortex/consumer-guide.md](repos/casehub-neocortex/consumer-guide.md)
Key types: `InferenceModel`, `CaseRetriever`, `EmbeddingIngestor`, `CaseMemoryStore`, `CbrCaseMemoryStore`

---

## Shared Patterns

**Blocks** — agentic orchestration framework (supervisor, sequence, loop, parallel, voting, debate, HTN), conversation protocol, channel summarisation, trust routing strategies
→ [repos/casehub-blocks/consumer-guide.md](repos/casehub-blocks/consumer-guide.md)
Key types: `ExecutionPlan`, `RoutingStrategy`, `DecompositionStrategy`, `ConversationProtocol`, `EventStreamBus`

**Platform** — shared services: identity, preferences, notifications, expressions (MVEL/JQ/JEXL), DataSource alpha network, ACL, credentials, agent infrastructure
→ [repos/casehub-platform/consumer-guide.md](repos/casehub-platform/consumer-guide.md)
Key types: `CurrentPrincipal`, `PreferenceProvider`, `NotificationBridge`, `ExpressionEvaluator`, `AgentProvider`

---

## UI & Frontend

**Pages** — web component framework, data pipelines, push protocol, design tokens, form components
→ [repos/casehub-pages/consumer-guide.md](repos/casehub-pages/consumer-guide.md)
Key types: `ConfigurablePanel`, `DataReceiver`, `DataSourceMixin`, `PagesTable`, `FilterModel`

**Blocks UI** — 31 shared domain components (work items, trust, SLA, channel activity, oversight, compliance, document workbench, graph stencils)
→ [repos/casehub-blocks-ui/consumer-guide.md](repos/casehub-blocks-ui/consumer-guide.md)
Key components: `split-workbench`, `work-item-inbox`, `channel-feed`, `trust-score-panel`, `kpi-metric-row`

---

## Infrastructure & Integration

**Connectors** — Slack, Discord, Teams, email, Google Calendar; `ChatPlatform` SPI, notification bridge
→ [repos/casehub-connectors/consumer-guide.md](repos/casehub-connectors/consumer-guide.md)
Key types: `Connector`, `InboundConnector`, `ConnectorDiscovery`, `ChatPlatform`, `CalendarPlatform`

**Workers** — HTTP, Camel, MCP, K8s, GitHub Actions, Script worker runtimes + dispatch
→ [repos/casehub-workers/consumer-guide.md](repos/casehub-workers/consumer-guide.md)
Key types: `WorkerRuntime`, `EndpointResolver`, `ExecutionManager`, `FaultEventHandler`

**OpenClaw** — CaseHub ↔ OpenClaw bridge, worker provisioning, MCP tools, ChannelContextWindow
→ [repos/casehub-openclaw/consumer-guide.md](repos/casehub-openclaw/consumer-guide.md)
Key types: `OpenClawWorkerProvisioner`, `DirectCallBridge`, `OpenClawAgentProvider`, `OversightGateService`

**Claudony** — CaseHub ↔ Claude CLI bridge, worker provisioning, system prompt layers, agent mesh
→ [repos/claudony/consumer-guide.md](repos/claudony/consumer-guide.md)
Key types: `ClaudonyWorkerProvisioner`, `ClaudonyCaseChannelProvider`, `ClaudonyMcpTools`

**IoT** — device abstraction (Matter-aligned), Home Assistant + OpenHAB providers, SSE streaming, MCP tools
→ [repos/casehub-iot/consumer-guide.md](repos/casehub-iot/consumer-guide.md)
Key types: `DeviceRegistry`, `DeviceProvider`, `DeviceCommand`, `StateChangeEvent`, `DeviceEntity`

**Chat App** — chat workbench application (qhorus UI + H2 backend)
→ [repos/casehub-chat-app/consumer-guide.md](repos/casehub-chat-app/consumer-guide.md)

---

## Operations & Desired State

**Desired State** — reconciliation runtime (Kubernetes controller pattern), goal compilation, fault policies, CBR
→ [repos/casehub-desiredstate/consumer-guide.md](repos/casehub-desiredstate/consumer-guide.md)
Key types: `DesiredStateGraph`, `GoalCompiler`, `NodeProvisioner`, `FaultPolicy`, `ReconciliationLoop`

**RAS** — situational awareness, event correlation (ganglions), case triggers, situation detection
→ [repos/casehub-ras/consumer-guide.md](repos/casehub-ras/consumer-guide.md)
Key types: `Ganglion`, `SituationDefinitionProvider`, `SituationSource`, `CaseInputContributor`

**Ops** — CaseHub deployment, K8s integration, compliance posture, infrastructure provisioning
→ [repos/casehub-ops/consumer-guide.md](repos/casehub-ops/consumer-guide.md)
Key types: `InfraNodeSpec`, `EvidenceCollector`, `ApplicationGoalCompiler`, `DeploymentGoalCompiler`

---

## Applications

Each application is a domain showcase built on the CaseHub harness.

| App | Domain | Guide |
|-----|--------|-------|
| **DevTown** | Software engineering coordination, PR review, merge queue | [repos/casehub-devtown/consumer-guide.md](repos/casehub-devtown/consumer-guide.md) |
| **AML** | Anti-money laundering investigations, compliance | [repos/casehub-aml/consumer-guide.md](repos/casehub-aml/consumer-guide.md) |
| **Clinical** | Clinical decision support, adverse event management | [repos/casehub-clinical/consumer-guide.md](repos/casehub-clinical/consumer-guide.md) |
| **Life** | Personal life automation, household management | [repos/casehub-life/consumer-guide.md](repos/casehub-life/consumer-guide.md) |
| **Drafthouse** | Contract drafting, multi-agent deliberation | [repos/casehub-drafthouse/consumer-guide.md](repos/casehub-drafthouse/consumer-guide.md) |
| **SOC** | Security operations center, alert triage | [repos/casehub-soc/consumer-guide.md](repos/casehub-soc/consumer-guide.md) |
| **FSI Trading** | Financial services trading automation | [repos/casehub-fsitrading/consumer-guide.md](repos/casehub-fsitrading/consumer-guide.md) |
| **QuarkMind** | Agentic StarCraft II orchestration | [repos/quarkmind/consumer-guide.md](repos/quarkmind/consumer-guide.md) |
