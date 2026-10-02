# CaseHub Consumer Index

> For app builders. What modules to depend on, what APIs to call, what SPIs to implement.
> Each link goes to a repo's `consumer-guide.md` — aggregated from child repos via git subtree.
>
> For exact type signatures and method contracts, see the [API Reference](api/INDEX.md).

---

## Orchestration & Cases

**Engine** — case lifecycle, YAML DSL, planning strategies, worker dispatch, oversight gates
→ [repos/casehub-engine/consumer-guide.md](repos/casehub-engine/consumer-guide.md)
Key types: `CaseDefinition`, `CasePlanModel`, `PlanItem`, `Worker`, `Binding`, `GoalExpression`, `WorkerResult`

**Work** — human task inbox, WorkItem lifecycle (12 statuses), SLA, delegation, M-of-N quorum, progress tracking, saga compensation
→ [repos/casehub-work/consumer-guide.md](repos/casehub-work/consumer-guide.md)
Key types: `WorkItem`, `WorkerSelectionStrategy`, `SlaBreachPolicy`, `SpawnPort`, `ProgressInstance`

**Worker** — automated task primitives: `Worker`, `Capability`, typed `WorkerFunction<T,R>`, execution policy
→ [repos/casehub-worker/consumer-guide.md](repos/casehub-worker/consumer-guide.md)
Key types: `Worker`, `Capability`, `WorkerFunction<T,R>`, `WorkerResult<R>` (with `reasoning`), `WorkerScope`

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

**Blocks** — agentic orchestration (5 SPIs, 8 topologies, YAML surface), BDI agent intelligence (beliefs, intentions, coalitions, judgment), social cognition framework (90+ types — mood, drives, narrative, goals, emergence), conversation protocol (epistemic common ground, convergence), temporal summarisation, prompt optimisation, agent memory hygiene, trust intake
→ [repos/casehub-blocks/consumer-guide.md](repos/casehub-blocks/consumer-guide.md)
Key types: `ExecutionPlan`, `RoutingStrategy`, `DecompositionStrategy`, `ConversationProtocol`, `EventStreamBus`, `SocialCognitionRenderer`

**Platform** — shared services: identity, preferences, notifications, expressions (MVEL/JQ/JEXL), DataSource alpha network, ACL, credentials, agent infrastructure
→ [repos/casehub-platform/consumer-guide.md](repos/casehub-platform/consumer-guide.md)
Key types: `CurrentPrincipal`, `PreferenceProvider`, `NotificationBridge`, `ExpressionEvaluator`, `AgentProvider`

---

## UI & Frontend

**Pages** — web component framework, data pipelines, push protocol (JDBC + Redis EventStore), design tokens (OKLCH), form components, viz (15 chart types), ARIA scenario automation (hierarchical composition, MCP domain, virtual clock), visual builder (pre-alpha), step orchestration (barrier, signal, quorum, correlation)
→ [repos/casehub-pages/consumer-guide.md](repos/casehub-pages/consumer-guide.md)
Key types: `ConfigurablePanel`, `DataReceiver`, `DataSourceMixin`, `PagesTable`, `FilterModel`, `ScenarioCompiler`

**Blocks UI** — 60 shared domain components across 9 packages (work items, trust, SLA, channel activity, oversight, compliance, document workbench, graph stencils, agent personality UI, evolution conductor, operations infrastructure, deliberation UI)
→ [repos/casehub-blocks-ui/consumer-guide.md](repos/casehub-blocks-ui/consumer-guide.md)
Key components: `split-workbench`, `work-item-inbox`, `channel-feed`, `trust-score-panel`, `kpi-metric-row`, `agent-personality-editor`, `evolution-conductor`

---

## Infrastructure & Integration

**Connectors** — Slack, Discord, Teams, email, Google Calendar; `ChatPlatform` SPI, notification bridge
→ [repos/casehub-connectors/consumer-guide.md](repos/casehub-connectors/consumer-guide.md)
Key types: `Connector`, `InboundConnector`, `ConnectorDiscovery`, `ChatPlatform`, `CalendarPlatform`

**Workers** — 7 transport backends (HTTP, Camel, MCP Streamable HTTP, K8s Job, GitHub Actions, Script, Scenario), unified fault pipeline with transport-specific classification, async completion with callback security, tenant-aware capability resolution, K8s restart recovery
→ [repos/casehub-workers/consumer-guide.md](repos/casehub-workers/consumer-guide.md)
Key types: `WorkerRuntime`, `EndpointResolver`, `ExecutionManager`, `FaultEventHandler`, `AsyncCompletionRegistry`

**OpenClaw** — CaseHub ↔ OpenClaw bridge, @McpDomain (18 operations across 5 domains, tri-channel: REST + GraphQL + MCP), structural completion signaling (ADR-0004), cross-channel context intelligence, crash-safe oversight gates
→ [repos/casehub-openclaw/consumer-guide.md](repos/casehub-openclaw/consumer-guide.md)
Key types: `OpenClawWorkerProvisioner`, `DirectCallBridge`, `OpenClawAgentProvider`, `OversightGateService`, `CommitmentMcpDomain`

**Claudony** — LLM Fleet Manager (declarative pools with auto-scaling, eviction SPI, metrics), remote terminal orchestration (tmux, crash recovery), CaseHub worker runtime (PROV-DM causal links), agent communication mesh (40+ MCP tools), browser workspace (12 Lit components)
→ [repos/claudony/consumer-guide.md](repos/claudony/consumer-guide.md)
Key types: `ClaudonyWorkerProvisioner`, `ClaudonyCaseChannelProvider`, `ClaudonyMcpTools`, `AgentPoolManager`, `FleetDefinition`

**IoT** — device abstraction (Matter-aligned), Home Assistant + OpenHAB providers, SSE streaming, MCP tools
→ [repos/casehub-iot/consumer-guide.md](repos/casehub-iot/consumer-guide.md)
Key types: `DeviceRegistry`, `DeviceProvider`, `DeviceCommand`, `StateChangeEvent`, `DeviceEntity`

**Chat App** — chat workbench application (qhorus UI + H2 backend)
→ [repos/casehub-chat-app/consumer-guide.md](repos/casehub-chat-app/consumer-guide.md)

---

## Operations & Desired State

**Desired State** — reconciliation runtime (domain-agnostic, human-in-the-loop), three-surface graph declaration (annotations, YAML, TypeScript), YAML plugin system (zero-Java resource lifecycle), goal compilation, CBR fault learning loop (retrieve-adapt-apply-revise), eidos org bridge, dual-framework (Quarkus + Spring)
→ [repos/casehub-desiredstate/consumer-guide.md](repos/casehub-desiredstate/consumer-guide.md)
Key types: `DesiredStateGraph`, `GoalCompiler`, `NodeProvisioner`, `FaultPolicy`, `ReconciliationLoop`

**RAS** — situational awareness, 5 ganglion types (incl. SituationWatcher for meta-situations), composable signal architecture (7 sealed ChainMode variants), missed detection API (per-ganglion recall, drift classification), feedback-driven learning loop, situation replay & validation
→ [repos/casehub-ras/consumer-guide.md](repos/casehub-ras/consumer-guide.md)
Key types: `Ganglion`, `SituationDefinitionProvider`, `SituationSource`, `CaseInputContributor`, `MissedDetectionRecorder`

**Ops** — self-managing platform (engine case model against own infrastructure), container lifecycle (Podman SPI quad), 7 fully-implemented case descriptors, adaptive topology with hysteresis, @McpDomain (29 operations), canonical topology test matrix (5×4), K8s lifecycle (fabric8)
→ [repos/casehub-ops/consumer-guide.md](repos/casehub-ops/consumer-guide.md)
Key types: `InfraNodeSpec`, `EvidenceCollector`, `ApplicationGoalCompiler`, `DeploymentGoalCompiler`, `PodmanClient`

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
