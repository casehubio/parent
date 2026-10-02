# CaseHub Capability Index

> What can I do with CaseHub? Find the capability, follow the link.
> Each chunk is self-contained with YAML frontmatter for RAG retrieval.
>
> For repo-level overviews, see [consumer-index.md](consumer-index.md).
> For exact type signatures, see [API Reference](api/INDEX.md).

---

## Identity & Access

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Identity & tenancy | CurrentPrincipal, groups, actor types, OIDC | [identity.md](repos/casehub-platform/capabilities/identity.md) | platform |
| Access control | Resource ACL with hierarchy, deny entries, bulk ops | repos/casehub-platform/capabilities/acl.md | platform |
| Credentials | Outbound endpoint credential resolution | repos/casehub-platform/capabilities/credentials.md | platform |

## Orchestration

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Case lifecycle | Define and execute multi-step case plans | repos/casehub-engine/capabilities/case-lifecycle.md | engine |
| Work items | Human task inbox with SLA and delegation | repos/casehub-work/capabilities/work-items.md | work |
| Worker dispatch | Automated task execution and routing | repos/casehub-worker/capabilities/worker-api.md | worker |
| Desired state | Domain-agnostic reconciliation with human-in-the-loop | repos/casehub-desiredstate/capabilities/reconciliation.md | desiredstate |
| Three-surface graph declaration | Annotations, YAML, TypeScript with cross-surface rules | — | desiredstate |
| YAML plugins | Complete resource lifecycle in YAML, zero Java knowledge required | — | desiredstate |
| CBR fault learning | Retrieve-adapt-apply-revise on reconciliation outcomes (CloudEvents) | — | desiredstate |

## Communication

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Notifications | Delivery pipeline (digest/suppress/immediate), subscriptions, SSE | [notifications.md](repos/casehub-platform/capabilities/notifications.md) | platform |
| Speech acts | Commitments, channels, message dispatch, topic projections | repos/casehub-qhorus/capabilities/speech-acts.md | qhorus |
| EU AI Act compliance | Compliance evidence generation with digital signing (Art.12) | — | qhorus |
| A2A protocol bridge | Google A2A protocol with governance layer | — | qhorus |
| Communication watchdogs | 11 watchdog types detecting coordination pathologies | — | qhorus |

## AI & Knowledge

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Expressions | JQ + MVEL3 + JEXL3 engines, config/secret injection | [expressions.md](repos/casehub-platform/capabilities/expressions.md) | platform |
| RAG retrieval | Hybrid search (dense + sparse + reranking), corpus ingestion | repos/casehub-neocortex/capabilities/rag.md | neocortex |
| CBR | Case-based reasoning with typed features, trend detection | repos/casehub-neocortex/capabilities/cbr.md | neocortex |
| Agent identity | Structured agent descriptors, capability health, system prompts | repos/casehub-eidos/capabilities/agent-identity.md | eidos |
| Agent infrastructure | AgentProvider SPI, Claude + LangChain4j, MCP activate/subscribe | repos/casehub-platform/capabilities/agents.md | platform |
| PDF generation | HTML-to-PDF with PDF/A-2b conformance | repos/casehub-platform/capabilities/pdf.md | platform |
| YAML processing | Truthiness, VariableResolver, CsvParser, ForEachExpander | repos/casehub-platform/capabilities/yaml-core.md | platform |
| TypeScript execution | TsExecutor SPI, JVM-hosted TS evaluation | repos/casehub-platform/capabilities/ts-core.md | platform |
| Signing | Cryptographic signing and verification | repos/casehub-platform/capabilities/signing.md | platform |
| Simulation framework | Generated CDI decorators, corpus strategies, temporal events, verification | — | platform |
| Callback system | Generated remote SPI callbacks (10 modules) | — | platform |
| MCP hierarchical model | Auto-discovered tool registration, landscape aggregation | — | platform |
| Cognitive architecture | Goal cognition (5 phases), OCC emotions, progressive attention, personality calibration | — | neocortex |
| Agent memory | 7 backends, salience ordering, GDPR erasure | — | neocortex |
| Knowledge graph | Thing model, dynamic types, confidence, PAD | — | neocortex |

## Audit & Trust

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Tamper-evident audit | Merkle MMR ledger, peer attestation, EigenTrust, Bayesian trust scoring | repos/casehub-ledger/capabilities/audit.md | ledger |
| Document signing | EU DSS 6.2, per-tenant keystores, 4 cloud KMS providers | — | platform |
| Situational awareness | 5 ganglion types (incl. meta-situations), composable signal architecture | repos/casehub-ras/capabilities/situational-awareness.md | ras |
| Meta-situation detection | Situations watching situations with cycle detection and deadlines | — | ras |
| Missed detection | Per-ganglion recall measurement, drift classification | — | ras |
| Situation replay | Deterministic replay using production pipeline for validation | — | ras |

## Data & Preferences

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Preferences | Scope-hierarchical business config, schema validation | repos/casehub-platform/capabilities/preferences.md | platform |
| DataSource alpha network | Rete-style event routing, tenant-scoped registries | repos/casehub-platform/capabilities/datasource.md | platform |
| Subject views & labels | Label-path view evaluation, pattern matching, caching | repos/casehub-platform/capabilities/views.md | platform |

## Shared Patterns

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Agentic orchestration | 5 SPIs, 8 topologies (supervisor, sequence, loop, parallel, voting, debate, HTN), YAML surface | repos/casehub-blocks/capabilities/orchestration.md | blocks |
| Conversation protocol | Epistemic common ground, convergence detection, structured deliberation | repos/casehub-blocks/capabilities/conversation.md | blocks |
| Social cognition | 90+ types — mood, drives, narrative identity, goals, emergence, all rendering as PromptSections | — | blocks |
| BDI agent intelligence | Beliefs, intentions, coalitions, judgment framework | — | blocks |
| Prompt optimisation | Variant generation, few-shot injection, runtime customisation | — | blocks |
| Agent memory hygiene | Confidence scoring, integrity checks, retention policies | — | blocks |
| Decision narratives | Raw platform signals → human-readable accountability explanations | — | blocks |

## Integration & Connectors

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Chat platforms | Slack, Discord, Teams, email | repos/casehub-connectors/capabilities/chat-platforms.md | connectors |
| Worker runtimes | 7 transport backends (HTTP, Camel, MCP Streamable HTTP, K8s Job, GitHub Actions, Script, Scenario) | repos/casehub-workers/capabilities/runtimes.md | workers |
| Multi-transport fault pipeline | Transport-specific fault classification converging into unified retry pipeline | — | workers |
| Async completion | Callback security, tenant-aware capability resolution | — | workers |
| K8s restart recovery | Reconstruct dispatch state from Job labels after application restart | — | workers |
| IoT devices | Device abstraction (Matter-aligned), HA + OpenHAB | repos/casehub-iot/capabilities/devices.md | iot |
| Event streams | Kafka, AMQP, Webhook, Poll, Camel connectors | repos/casehub-platform/capabilities/streams.md | platform |
| LLM Fleet Management | Declarative pools with auto-scaling, eviction SPI, Micrometer metrics, real-time SSE | — | claudony |
| Remote terminal orchestration | tmux-based fleet federation, circuit breaker, crash recovery | — | claudony |
| @McpDomain tri-channel | Single-source API generation for REST + GraphQL + MCP | — | openclaw |
| Structural completion signaling | Tool-call-first agent completion (ADR-0004), no text classification | — | openclaw |
| Container lifecycle | Podman SPI quad — provisioner, adapter, fault policy, event source | — | ops |
| Self-managing platform | Engine case model operating against own infrastructure | — | ops |
| Adaptive topology | RAS situation-driven recompilation of deployment topology with hysteresis | — | ops |

## UI & Frontend

| Capability | What it does | Consumer chunk | Repo |
|------------|-------------|----------------|------|
| Web components | Data pipelines, push protocol (JDBC + Redis), OKLCH design tokens | repos/casehub-pages/capabilities/web-components.md | pages |
| Scenario automation | ARIA-based UI + domain automation with hierarchical composition, MCP domain, virtual clock | — | pages |
| Visual builder | Dashboard authoring workbench with document model and component catalog (pre-alpha) | — | pages |
| Step orchestration | Barrier, signal, quorum, correlation primitives; 13-layer DecoratorChain pipeline | — | pages |
| Data visualisation | 15 chart types (heatmap, density, treemap, etc.), timeline, statistic components | — | pages |
| Domain components | 60 shared components across 9 packages (work items, trust, SLA, channel, agent personality, evolution) | repos/casehub-blocks-ui/capabilities/domain-components.md | blocks-ui |
| Agent personality UI | Visual agent identity configuration: catalog → avatar → manifest → profile | — | blocks-ui |
| Evolution conductor | Operational dashboard for gated agent improvement streams | — | blocks-ui |

---

*Chunks without links are not yet decomposed — they will be created during the per-repo doc audit (#434-#461).*
