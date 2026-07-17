# CaseHub Platform Index

> Load this first. Find your topic, follow the link.
> For audience-specific guidance: [Building Apps](guides/building-apps.md)
> | [Building Platform](guides/building-platform.md)

## Orchestration & Cases
- **Engine** — case lifecycle, YAML DSL, blackboard, planning strategies
  → [repos/casehub-engine.md](repos/casehub-engine.md)
- **Work** — human task lifecycle, WorkItem inbox, SLA, delegation
  → [repos/casehub-work.md](repos/casehub-work.md)
- **Routing** — trust-weighted, semantic, CBR-evidence agent selection
  → [platform/routing.md](platform/routing.md)
- **CBR** — case-based reasoning: retrieve, reuse, revise, retain
  → [platform/cbr.md](platform/cbr.md)

## Agent Communication
- **Qhorus** — speech acts, commitments, channels, spaces (recursive hierarchy), presence, topic-aware projections, message delivery, OTel tracing
  → [repos/casehub-qhorus.md](repos/casehub-qhorus.md)
- **Agent Mesh** — 3-channel normative layout, mesh participation
  → [platform/agent-mesh.md](platform/agent-mesh.md)
- **Channels taxonomy** — purpose categories, discriminator dimensions
  → [CHANNELS.md](CHANNELS.md)

## Agent Identity & Behavior
- **Eidos** — structured identity, capability health/specialization, vocabulary, behavioral contracts, eval framework
  → [repos/casehub-eidos.md](repos/casehub-eidos.md)
- **Identity** — platform identity submodule (OIDC, SCIM, groups)
  → [repos/casehub-identity.md](repos/casehub-identity.md)
- **Agent Identity** — DID format, SCIM2, versioning
  → [platform/agent-identity.md](platform/agent-identity.md)

## AI & Knowledge
- **Neocortex** — embeddings, vector stores, RAG pipelines (hybrid search, CRAG, query expansion), CBR (typed features, trend detection, plan adaptation), agent memory SPI
  → [repos/casehub-neocortex.md](repos/casehub-neocortex.md)
- **Quarkmind** — agentic orchestration strategies, trust routing
  → [repos/quarkmind.md](repos/quarkmind.md)

## UI & Frontend
- **Pages** — web component framework, data pipelines, push protocol SDK, a11y primitives, design tokens
  → [repos/casehub-pages.md](repos/casehub-pages.md)
- **Blocks UI** — 21 shared domain components (work items, trust, SLA, channel activity, oversight, compliance, GDPR, KPI)
  → [repos/casehub-blocks-ui.md](repos/casehub-blocks-ui.md)
- **UI Architecture** — pages → blocks-ui → app UI layering
  → [platform/ui-architecture.md](platform/ui-architecture.md)
  → protocols: [custom-event-shadow-dom], [lit-immutable-collections]

## Shared Java Patterns
- **Blocks** — agentic orchestration patterns (supervisor, sequence, loop, parallel, voting, debate, HTN), trust routing, oversight gates, conversation management, channel summarisation
  → [repos/casehub-blocks.md](repos/casehub-blocks.md)
  → scope criteria, consolidation epic, placement decisions
- **Platform** — shared services, notification pipeline (subscriptions, dispatch, digest, delivery), DataSource alpha network, expression engines, DID infrastructure
  → [repos/casehub-platform.md](repos/casehub-platform.md)

## Persistence & Data
- **Persistence** — Flyway conventions, datasource naming
  → [platform/persistence.md](platform/persistence.md)
  → protocols: [flyway-repo-scoped-migration-path],
    [flyway-extension-migration-registration], [flyway-migration-rules]
- **Ledger** — tamper-evident audit, Merkle, trust scoring
  → [repos/casehub-ledger.md](repos/casehub-ledger.md)

## Infrastructure & Integration
- **Connectors** — Slack, Discord, Teams, email; ChatPlatform SPI, RichCard cross-platform messaging
  → [repos/casehub-connectors.md](repos/casehub-connectors.md)
- **Workers** — HTTP, Camel, MCP, K8s, GitHub Actions, Script dispatch + testing
  → [repos/casehub-workers.md](repos/casehub-workers.md)
- **Worker API** — Worker, Capability, WorkerFunction primitives (capabilityNames convention)
  → [repos/casehub-worker.md](repos/casehub-worker.md)
- **IoT** — device abstraction, Matter-aligned, HA/OpenHAB providers
  → [repos/casehub-iot.md](repos/casehub-iot.md)
- **OpenClaw** — CaseHub ↔ OpenClaw bridge, worker provisioning
  → [repos/casehub-openclaw.md](repos/casehub-openclaw.md)
- **Chat App** — chat workbench application (qhorus UI + SQLite backend)
  → [repos/casehub-chat-app.md](repos/casehub-chat-app.md)
- **Flow** — Serverless Workflow 1.0 orchestration runtime
  → [repos/casehub-flow.md](repos/casehub-flow.md) (when created)

## Operations & Desired State
- **Desired State** — reconciliation runtime, goal compilation
  → [repos/casehub-desiredstate.md](repos/casehub-desiredstate.md)
- **RAS** — situational awareness, event correlation, case triggers
  → [repos/casehub-ras.md](repos/casehub-ras.md)
- **Ops** — CaseHub deployment, infrastructure, compliance posture
  → [repos/casehub-ops.md](repos/casehub-ops.md)

## Cross-Cutting
- **Auth** — gateway topology, roles, outbound credentials
  → [platform/auth.md](platform/auth.md)
- **Notifications** — subscription engine, delivery, digest batching
  → [platform/notifications.md](platform/notifications.md)
- **Privacy** — GDPR erasure, PII sanitisation
  → [platform/privacy.md](platform/privacy.md)
- **Observability** — OTel tracing, audit entries, ledger correlation
  → [platform/observability.md](platform/observability.md)

## Platform Operations
- **Coherence Protocol** — 6-step pre-implementation protocol (run before any change)
  → [platform/coherence-protocol.md](platform/coherence-protocol.md)
- **Capability Ownership** — "where does X live?" lookup table
  → [platform/capability-ownership.md](platform/capability-ownership.md)
- **Dependency Map** — cross-repo impact analysis for renames, removals, SPI breaks
  → [platform/dependency-map.md](platform/dependency-map.md)
- **Overview** — tier structure, repo map, build order
  → [platform/overview.md](platform/overview.md)

## Architecture & Conventions
- **Boundary Rules** — all "do not" rules across the platform
  → [platform/boundary-rules.md](platform/boundary-rules.md)
- **Overlap Risks** — known semantic collisions
  → [platform/overlap-risks.md](platform/overlap-risks.md)
- **Architecture** — tier patterns, dependency rule, selective event sourcing
  → [ARCHITECTURE.md](ARCHITECTURE.md)
- **DSL Style** — fluent API conventions
  → [DSL-STYLE-GUIDE.md](DSL-STYLE-GUIDE.md)
- **Lifecycle** — state machines, terminal semantics
  → [LIFECYCLE.md](LIFECYCLE.md)
- **Protocols** — implementation conventions (audience-mapped)
  → [platform/protocols.md](platform/protocols.md)
  → full index: [garden protocols INDEX.md](../../garden/docs/protocols/INDEX.md)

## Applications
- **App inventory** — all domain applications with status
  → [APPLICATIONS.md](APPLICATIONS.md)
- **AML** — anti-money laundering case investigations
  → [repos/casehub-aml.md](repos/casehub-aml.md)
- **Clinical** — clinical decision support, CBR-driven case management
  → [repos/casehub-clinical.md](repos/casehub-clinical.md)
- **DevTown** — developer governance and compliance workbench
  → [repos/casehub-devtown.md](repos/casehub-devtown.md)
- **Drafthouse** — contract drafting and review workspace
  → [repos/casehub-drafthouse.md](repos/casehub-drafthouse.md)
- **FSI Trading** — financial services trading scenarios
  → [repos/casehub-fsitrading.md](repos/casehub-fsitrading.md)
- **Life** — IoT-driven personal risk and wellness
  → [repos/casehub-life.md](repos/casehub-life.md)
- **SOC** — security operations center case management
  → [repos/casehub-soc.md](repos/casehub-soc.md)
- **Claudony** — CaseHub ↔ Colony bridge, multi-tenancy provisioning
  → [repos/claudony.md](repos/claudony.md)

## Guides & Tools
- **Building Apps** — capability matrix, pattern catalogue, placement criteria
  → [guides/building-apps.md](guides/building-apps.md)
- **Building Platform** — adding capabilities, SPI design, boundary enforcement
  → [guides/building-platform.md](guides/building-platform.md)
- **Agentic Harness** — session conventions for LLM work in app repos
  → [AGENTIC-HARNESS-GUIDE.md](AGENTIC-HARNESS-GUIDE.md)
- **arc42stories** — standard architecture documentation format
  → [arc42stories-spec.md](arc42stories-spec.md) | [profile](arc42stories-casehub-profile.md) | [README](arc42stories-readme.md)
- **Config Architecture** — topic ownership, what's authoritative where
  → [config-architecture.md](config-architecture.md)
- **New Repo Checklist** — setup steps for adding a new repository
  → [new-repo-checklist.md](new-repo-checklist.md)
- **Prompt Snippets** — work-item opening sequences, doc-sync reminders
  → [prompt-snippets.md](prompt-snippets.md)
