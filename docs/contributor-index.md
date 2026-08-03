# CaseHub Contributor Index

> For platform builders. Architecture, internal SPIs, module structure, extension points.
> Each link goes to a repo's `contributor-guide.md` — aggregated from child repos via git subtree.

---

## Foundation Tier — shared primitives, zero domain knowledge

### Engine (case orchestration)
Module structure, handler pipeline, routing architecture, DAG execution, CaseDefinitionRegistry, tenancy enforcement, SPI placement rules, virtual thread migration
→ [repos/casehub-engine/contributor-guide.md](repos/casehub-engine/contributor-guide.md)
17 modules · depends on: platform-api, worker-api · depended on by: all application repos

### Work (human tasks)
Module architecture (20+ modules), core/runtime split, engine adapter, progress model (6 modules), filter engine, template versioning, flow bridge
→ [repos/casehub-work/contributor-guide.md](repos/casehub-work/contributor-guide.md)
20+ modules · depends on: platform-api · depended on by: engine, clinical, aml, life, devtown

### Worker (automated task primitives)
Execution model (12-step DefaultWorkerExecutor pipeline), SchemaValidator, Guard caching, typed function builders, persistent worker variant
→ [repos/casehub-worker/contributor-guide.md](repos/casehub-worker/contributor-guide.md)
3 modules · depends on: platform-api · depended on by: engine, desiredstate

### Qhorus (agent communication)
Dispatch gate pipeline, channel gateway, protocol enforcement, delivery service, 13 store interfaces, evidential checker, reactive tier (retired)
→ [repos/casehub-qhorus/contributor-guide.md](repos/casehub-qhorus/contributor-guide.md)
14 modules · depends on: ledger, platform-api · depended on by: claudony, engine, all app repos

### Eidos (agent identity)
8 modules, BehavioralSignalStore (signal-parameterized API), disposition health/evolution, Jungian personality framework, render pipeline, template system, eval harness (10 judges, 18 profiles)
→ [repos/casehub-eidos/contributor-guide.md](repos/casehub-eidos/contributor-guide.md)
8 modules · depends on: ledger, langchain4j · depended on by: engine (optional)

### Ledger (audit & trust)
Module structure (api, runtime, rest, testing, memory, signing), save pipeline, CDI bean graph, repository architecture (tenant/cross-tenant/unscoped), trust routing events, privacy architecture, enricher pipeline
→ [repos/casehub-ledger/contributor-guide.md](repos/casehub-ledger/contributor-guide.md)
14 modules · depends on: nothing (Quarkus + Hibernate only) · depended on by: work, qhorus, engine

### Neocortex (AI & knowledge)
36 modules: inference (ONNX, task adapters), RAG (3-leg hybrid, cross-encoder, query expansion, tracking), CBR (typed features, similarity specs, plan adaptation, temporal decay, reconciliation), memory (5 backends), corpus, fusion
→ [repos/casehub-neocortex/contributor-guide.md](repos/casehub-neocortex/contributor-guide.md)
36 modules · depends on: platform-api, LangChain4j, Qdrant · depended on by: eidos, engine, all app repos

### Platform (shared services)
~50 modules: identity, preferences, notifications (subscriptions, dispatch, digest, delivery), DataSource alpha network, expression engines (MVEL/JQ/JEXL), DID infrastructure, ACL, credentials, agent infrastructure, CloudEvent dispatcher
→ [repos/casehub-platform/contributor-guide.md](repos/casehub-platform/contributor-guide.md)
~50 modules · depends on: nothing · depended on by: everything

---

## Integration Tier — bridges, UI, shared patterns

### Blocks (agentic patterns)
Single-module library: 6 packages (channel, conversation, agentic with 9 sub-packages, routing, routing.agent, summarisation), execution driver architecture, pattern builders, decomposition strategies, epistemic common ground
→ [repos/casehub-blocks/contributor-guide.md](repos/casehub-blocks/contributor-guide.md)
1 module · depends on: qhorus-api, work-api, engine-api, worker-api · depended on by: drafthouse, engine, aml, devtown, clinical, quarkmind

### Connectors (external integrations)
16 modules: core SPI, Slack/Discord/Teams/email/Google Calendar implementations, chat SPI, notification bridge, MCP tools, webhook infrastructure
→ [repos/casehub-connectors/contributor-guide.md](repos/casehub-connectors/contributor-guide.md)
16 modules · depends on: platform-api · depended on by: devtown, openclaw, chat-app

### Workers (execution runtimes)
8 modules: HTTP, Camel, MCP, K8s, GitHub Actions, Script backends. Four-class pattern (Runtime, Resolver, ExecutionManager, FaultEventHandler)
→ [repos/casehub-workers/contributor-guide.md](repos/casehub-workers/contributor-guide.md)
8 modules · depends on: worker-api, engine-api · depended on by: engine

### Desired State (reconciliation)
API, runtime, testing, engine-adapter, work-adapter, ras-adapter, persistence-jpa, 4 examples. ReconciliationLoop (per-tenant event-driven), TransitionPlanner (Kahn's algorithm), LifecycleManager (dual CAS), CBR pipeline
→ [repos/casehub-desiredstate/contributor-guide.md](repos/casehub-desiredstate/contributor-guide.md)
11 modules · depends on: platform-api, engine-api, work-api, ras-api · depended on by: ops

### RAS (situational awareness)
RasEngine, SituationEvaluator (two-phase), 4 built-in ganglion types, clustered conflict handling, compaction, dynamic registration, 30+ Micrometer metrics
→ [repos/casehub-ras/contributor-guide.md](repos/casehub-ras/contributor-guide.md)
8 modules · depends on: platform-api · depended on by: desiredstate, iot, ops

### Pages (web framework)
TypeScript packages: data pipeline, event system, table, form, primitives, tokens, viz, graph-core, graph-renderer. Java backend: auth, runtime, push wire protocol, Quinoa integration
→ [repos/casehub-pages/contributor-guide.md](repos/casehub-pages/contributor-guide.md)
15+ packages · depends on: nothing · depended on by: blocks-ui, all app UIs

### Blocks UI (shared components)
31 Lit web components: data patterns (DataSourceMixin, EventStreamController, TrendSourceMixin), Shadow DOM conventions, portal resolution, document workbench (9 panels), graph stencils
→ [repos/casehub-blocks-ui/contributor-guide.md](repos/casehub-blocks-ui/contributor-guide.md)
31 components · depends on: pages · depended on by: life, devtown, clinical, aml, chat-app, claudony, drafthouse

### OpenClaw (OpenClaw bridge)
4 modules: core, casehub, app, plugin. DirectCallBridge, OversightGateService, 1:N agent registry, parallel COMMAND routing, MCP endpoint (8 tools), PluginTokenBridgeMechanism
→ [repos/casehub-openclaw/contributor-guide.md](repos/casehub-openclaw/contributor-guide.md)
4 modules · depends on: qhorus, engine-api, platform-agent-api · depended on by: life

### Claudony (Claude CLI bridge)
3 modules: core, casehub, app. System prompt three-layer model, terminal streaming, agent mesh framework, channel architecture, persistence
→ [repos/claudony/contributor-guide.md](repos/claudony/contributor-guide.md)
3 modules · depends on: qhorus, engine-api, platform · depended on by: none (standalone)

### IoT (device management)
13 modules: api, runtime, Home Assistant provider, OpenHAB provider (Equipment + Thing paths), bridge (wire protocol, 7 sealed variants), webapp (REST, case engine, ganglia, CBR, AI resolution), testing
→ [repos/casehub-iot/contributor-guide.md](repos/casehub-iot/contributor-guide.md)
13 modules · depends on: platform-api, ras-api · depended on by: ops, life

---

## Application Tier — domain showcases

| App | Modules | Key internals | Guide |
|-----|---------|---------------|-------|
| **DevTown** | domain, review, queue, merge, github, app | PR review CasePlanModel, merge queue (adaptive batching, bisection), CBR reviewer matching, 22 MCP tools, governance workbench | [repos/casehub-devtown/contributor-guide.md](repos/casehub-devtown/contributor-guide.md) |
| **AML** | api, app (hexagonal) | Investigation CasePlanModel, CBR triage pipeline, compliance evidence, 9 layers complete | [repos/casehub-aml/contributor-guide.md](repos/casehub-aml/contributor-guide.md) |
| **Clinical** | api, app | Multi-site sub-case architecture, two-datasource, 16 LedgerEntry subclasses, 6 CBR domains, AE grade regrading | [repos/casehub-clinical/contributor-guide.md](repos/casehub-clinical/contributor-guide.md) |
| **Life** | api, app | 8 CaseHub implementations, 12 action risk types, sentinel heartbeat (7 types), dual-path CBR, household RBAC | [repos/casehub-life/contributor-guide.md](repos/casehub-life/contributor-guide.md) |
| **Drafthouse** | api, runtime, claude-agent, frontend | Debate protocol, 6 sub-agent handlers, 30 MCP tools, document workbench panels | [repos/casehub-drafthouse/contributor-guide.md](repos/casehub-drafthouse/contributor-guide.md) |
| **SOC** | api, app | Alert ingestion pipeline (CloudEvent → Ganglion → Case), 6 workers, dual rule/LLM architecture | [repos/casehub-soc/contributor-guide.md](repos/casehub-soc/contributor-guide.md) |
| **FSI Trading** | api, app | Strategy evaluation, order lifecycle, P&L attestation, human approval gates | [repos/casehub-fsitrading/contributor-guide.md](repos/casehub-fsitrading/contributor-guide.md) |
| **QuarkMind** | single module | 58 strategy archetypes, 12 LLM agents, Drools CEP enemy classifier, coaching pipeline | [repos/quarkmind/contributor-guide.md](repos/quarkmind/contributor-guide.md) |
| **Ops** | api, infra, deployment, compliance, iot, app, testing | K8s lifecycle (fabric8), adaptive topology, case model (drift remediation + scaling), 3-layer approval | [repos/casehub-ops/contributor-guide.md](repos/casehub-ops/contributor-guide.md) |
| **Chat App** | single module | Qhorus-backed persistence, WebSocket protocol (7 datasets), frontend app shell | [repos/casehub-chat-app/contributor-guide.md](repos/casehub-chat-app/contributor-guide.md) |
