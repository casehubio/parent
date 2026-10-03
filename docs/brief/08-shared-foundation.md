# The Shared Foundation

*500+ modules, one model. Breadth of consistency that doesn't exist elsewhere.*

---

## What It Is

The Shared Foundation is what makes everything else in CaseHub compose
without integration glue. Every module across the platform — case
orchestration, communications, reconciliation, UI — shares one CDI
model, one event system, one tenancy model, one identity hierarchy,
one audit trail, and one simulation framework. Capabilities don't
integrate with each other; they are already integrated by
construction.

This is not a service mesh or an API gateway sitting between separate
systems. It is a single, coherent Java platform where 178 shared
service modules provide the primitives that every capability area
builds on. When a new capability is added, it immediately plugs into
the notification pipeline, the ACL system, the audit trail, the
simulation framework, and the MCP tool surface — because those are
the same primitives it was built from.

The result: adding an agent backend doesn't require a notification
integration. Adding a connector doesn't require an audit integration.
Adding a reconciliation domain doesn't require a tenancy integration.
It's all already there.

---

## Key Capabilities

### Identity & Tenancy

Three-level typed identity hierarchy: Principal (authentication
context), Actor (who did this — human, agent, or system), and
Participant (who is in this conversation). Every SPI call across the
platform is tenant-scoped through `CurrentPrincipal`. This is not a
string user ID — it is a typed model that distinguishes ownership from
execution context from participation.

- **DID resolution** — did:key, did:web, SCIM 2.0 with composite
  resolver supporting Ed25519, P-256, and secp256k1. SSRF-protected
  web DID resolution.
- **OIDC integration** — standard identity provider flow with group
  membership mapping
- **Actor types** — human, agent, system. Each carries different
  authorization semantics throughout the platform.
- 3 identity modules

### Expression Engines

Three expression engines in one CDI-managed registry, each optimised
for its context: JQ for JSON transforms, MVEL3 for business rules,
JEXL3 for template expressions. Auto-registered via CDI — no manual
wiring.

- **Config and secret injection** — expressions reference business
  configuration via `$config` and `$secret` scopes without hard-coding
  values. Config values flow from the Preference Management system.
- **Framework-neutral core** — `expression-core` with Quarkus and
  Spring wiring via PropertySource abstraction
- **Lambda expressions** — compiled expressions for high-frequency
  evaluation paths

### Notification Pipeline

Not "send notifications" — a complete event-driven subscription
engine. 14 modules covering the full lifecycle: subscription
registration, alpha network pattern matching (Rete algorithm),
dispatch routing, delivery with retry, engagement tracking, and
digest batching.

- **Three delivery paths** — immediate, suppress, and digest. Quiet
  hours with buffer-for-digest shift notifications to the next
  delivery window.
- **Engagement events** — opened, clicked, dismissed, replied,
  converted. Full lifecycle tracking per notification.
- **Modular target kinds** — user, agent, and system targets with
  different routing paths per kind
- **Production backends** — JPA with SKIP LOCKED claims, keyset
  pagination, retention purge. In-memory alternatives for testing.
  SSE push delivery. REST API for presentation.
- 14 notification modules

### DataSource Alpha Network

Rete-style event routing with tenant-scoped registries and
self-pruning lifecycle. Applying the Rete algorithm — the same
pattern-matching engine used in production rule systems — to domain
event routing. Data sources register with typed schemas; consumers
subscribe with pattern predicates. The alpha network prunes inactive
subscriptions and optimises matching paths automatically.

This is not a message bus. It is a discrimination network that
evaluates every event against every active subscription in a single
pass — the same algorithmic efficiency that made Drools fast, applied
to domain event distribution.

### Preference Management

Scope-hierarchical business configuration with runtime changes,
schema discovery, and validation. Configuration values resolve
through a tenant → case-type → case-instance ancestor chain, with
more specific scopes overriding less specific ones.

- **Runtime changes** — preferences update without restart. Expression
  engine `$config` scope references resolve live.
- **Schema validation** — each preference key declares its type,
  constraints, and default. Invalid values are rejected at write time.
- **Schema discovery** — REST API exposes available preference keys,
  types, and current values per scope
- Feeds expression engine config injection, SLA thresholds,
  notification policies, compliance parameters, and behavioural
  contract bounds

### Callback System

Remote procedure call over HTTP with lease management, retry, and
heartbeat renewal. 10 callback modules enable distributed SPI
deployment: a service on one node can implement an SPI that another
node calls as if it were local.

- **Lease lifecycle** — register → heartbeat → release with automatic
  expiry detection
- **Retry with backoff** — configurable retry policies for transient
  network failures
- **Multi-format** — JSON and CBOR serialisation
- Enables deployment patterns where specialised SPI implementations
  (e.g. a GPU-accelerated inference provider) run on dedicated nodes
  while the rest of the platform sees a standard CDI bean

### Streams Integration

Five event stream connectors for enterprise event infrastructure:

- **Kafka** — CloudEvent production and consumption with offset
  management
- **AMQP** — RabbitMQ/ActiveMQ integration with durable
  subscriptions
- **Webhook** — inbound HTTP event receivers with signature
  verification
- **Poll** — scheduled HTTP polling with change detection
- **Camel** — Apache Camel routes for integration patterns

All connectors construct standardised CloudEvents — downstream
consumers (ganglia, notification pipeline, reconciliation listeners)
don't know or care which transport delivered the event.

### Agent Infrastructure

Vendor-agnostic `AgentProvider` SPI with 7 pluggable backends:
Claude, OpenAI, Gemini, Gemini CLI, Codex, Ollama, and LangChain4j.
Native SDK integration — not HTTP wrappers — for OpenAI (v4.50),
Gemini (GenAI v1.65), and Claude (claude-code-sdk). Bidirectional
LangChain4j interop for ecosystem compatibility.

- **Three-step model resolution** — alias → tier → registry → key.
  A consumer requests a capability tier ("fast", "reasoning"); the
  registry resolves to a concrete model on a concrete backend.
- **Manifest-driven configuration** — `agent-config.yaml` declares
  providers, models, rate limits, and credentials. Credential
  references resolve from environment, file, or Vault at startup.
- **Rate limiting** — token bucket + concurrency gate via CDI
  decorator. Per-provider and per-model limits. No application code
  changes required.
- 24 agent modules

### LLM Fleet Management

Declarative management of persistent LLM agent pools with
auto-scaling, eviction, and operational metrics. 43 classes in the
fleet package alone. No competing platform offers this.

LangChain and CrewAI create agent sessions on demand and discard them
when done. CaseHub manages persistent pools where sessions survive
across work assignments. Suspend/resume preserves conversation context
— a session paused on one task resumes with full history on the next.

- **Declarative definitions** — three peer representations: fluent
  Java DSL, YAML, and `@PoolDefinition` annotations with APT code
  generation. Runtime registry for dynamic reconfiguration.
- **Auto-scaling** — pluggable `ScalingPolicy` SPI with step
  thresholds and target-tracking policies. Scale up on demand queue
  depth; scale down on idle timeout.
- **Eviction** — pluggable `EvictionPolicy` SPI. Least-recently-used,
  priority-weighted, and custom eviction strategies.
- **Metrics & observability** — Micrometer gauge export, IoTDB
  time-series bridge for historical analysis, real-time SSE event
  push for fleet dashboards
- **Crash recovery** — tmux session options persist case ID and role
  metadata. After restart, the fleet manager reconstructs pool state
  from surviving sessions.
- **Ops integration** — `AgentPoolConfigBridge` connects pool
  definitions to the ops provisioning system for infrastructure-aware
  fleet placement

### Simulation Framework

Complete SPI testing infrastructure — not Mockito, not stubs.
Generated CDI decorators intercept any SPI call at the container
level, resolve responses from a corpus, and record interactions
for verification. 14 modules. Nothing comparable exists in the Java
ecosystem.

- **Generated decorators** — APT code generator produces CDI
  decorators, qualified name constants, and parameter metadata.
  Add `@SimulationEligible` to any SPI interface; the generator
  does the rest.
- **Replay corpuses** — record real interactions, replay them
  deterministically. Corpus strategies: sequential, key-lookup,
  random, recorded-replay, nearest-match. Multi-format corpus
  (YAML, JSON, CSV). LLM-generated corpus population for realistic
  test data. Production recordings become regression suites.
- **Temporal simulation** — tick-based event emitter with temporal
  driver lifecycle (start/pause/resume/stop/setSpeed). Three-level
  speed composition for nested simulation contexts.
- **Verification API** — Mockito-quality assertion API
  (`verify(spi).method(args)`) built on recorded interactions
- **Pre-built adapters** — 11 platform SPIs + CaseMemoryStore +
  AgentProvider ready to simulate out of the box
- 14 simulation modules

### Connector SPIs

Five homogeneous platform SPIs — Chat, Calendar, Bank, Email,
Document — each following the same pattern: SPI interface with
`@SimulationEligible`, routing service, reference implementation,
and one or more real providers. 29 connector modules. No vendor
SDKs anywhere — all HTTP-based connectors use `java.net.http`
directly.

- **Chat Platform** — 10 capability interfaces (Messaging, Threading,
  Discovery, Reactions, Presence, Members, ChannelManagement,
  MemberManagement, MessageHistory, Commands). 5 implementations
  (Reference, IRC, Discord, Slack, Signal). Capability-based
  degradation — consumers write against the full API, unsupported
  features degrade gracefully.
- **Calendar Platform** — full CRUD with sealed `EventTiming` model
  (Timed/AllDay). Google Calendar provider.
- **Bank Platform** — AISP (accounts, balances, transactions) and
  PISP (payment initiation). TrueLayer Open Banking with PSD2
  consent lifecycle and JWS-verified webhooks.
- **Email Platform** — mailbox listing, paginated messages,
  attachment download. Complements outbound EmailConnector and
  inbound push connector.
- **Document Platform** — FileOperations, FolderOperations,
  SearchOperations, SharingOperations. Google Drive provider.
- **LLM self-correction** — `UnsupportedCapabilityException` with
  structured metadata enables agents to detect and recover from
  unsupported operations without crashing. `supports(Class<?>)`
  for capability introspection.
- **Slash Commands** — `CommandHandler` SPI for registering and
  dispatching commands across chat platforms

### IoT Device Management

Typed device abstraction aligned with the Matter Device Type
Library. 11 concrete device types (switch, light, thermostat,
sensor, presence, power, lock, cover, media player, fan, camera)
with a polymorphic hierarchy. Dual-provider architecture with
Home Assistant and OpenHAB.

- **Edge-to-cloud bridge** — sealed wire protocol (7 variants),
  durable store-and-forward for crash resilience, multi-tenant
  device ID namespacing. Protocol-aware and auditable.
- **Auto-discovery** — mDNS/SSDP for provider instances, automatic
  device enumeration on connection
- **AI resolution pipeline** — LLM-driven autonomous resolution
  agent with multi-turn conversation, CBR similarity matching,
  risk classification, and escalation to human work items
- **Simulation** — temporal simulation profiles, corpus seeding,
  scenario runtime. Simulation and production use the same APIs.
- **MCP tools** — 4 tools for LLM agent access to device state and
  commands
- 12 IoT modules

### MCP Hierarchical Model

MCP tools are not hand-written. `@McpDomain`-annotated interfaces
generate tool definitions automatically for three transports: REST,
GraphQL, and MCP — from the same source. `GraphQLModelScanner`
auto-discovers domains. `DynamicToolRegistrar` handles capability
exceptions gracefully. `LandscapeReportService` aggregates all
domain reports in parallel.

- **Tri-channel generation** — one annotated interface produces
  REST endpoints, GraphQL operations, and MCP tools. Consumers pick
  the transport; the API surface is identical.
- **Auto-discovery** — domains register via CDI. No manual tool
  registration. Add a `@McpDomain` class and the tools appear.
- **Landscape aggregation** — parallel report collection across all
  domains. The full platform tool surface is queryable at runtime.
- 4 MCP modules (GraphQL generator APT, REST generator Maven plugin,
  Spring variants)

### Document Signing

EU DSS 6.2 PAdES and CAdES document signing with per-tenant
keystores, certificate lifecycle management, and PDF/A-2b archival
generation. Production-grade compliance — not toy crypto.

- **Signing formats** — PAdES embedded (signed PDF), CAdES detached
  (signed any-format) with signature verification
- **Per-tenant keystores** — PKCS#12 with atomic rotation (no
  restart). Certificate expiry monitoring.
- **EU Trusted List** — validation against the EU Trusted List of
  qualified trust service providers
- **PDF generation** — HTML-to-PDF with bundled fonts for
  reproducible rendering. PDF/A-2b conformance for long-term
  archival.

### Access Control

Hierarchical resource ACL with group-based grants, deny entries, and
parent-child inheritance via recursive CTE in a single SQL query.

- **Deny-wins-at-specificity** — deny entries override grants at the
  same or more specific resource level. Wildcard grants (`type:*`).
  Parent chain walking to depth 20.
- **Tenant-scoped audit** — every grant/deny change is logged with
  retention purge
- **Admin API** — REST endpoints with `@RolesAllowed`, worker
  credential filter for outbound authentication
- 7 ACL modules

### Dual-Framework Deployment

Every module follows a `-core` (framework-neutral POJO) + Quarkus
wiring + Spring auto-configuration pattern. Business logic is never
duplicated between frameworks.

- **Spring generators** — produce `@Controller`, `@RestController`,
  Spring AI `@Tool` equivalents from the same source as Quarkus
  endpoints
- **Integration tested** — Spring starters with full composition
  tests ensuring auto-configuration produces the same behaviour as
  Quarkus CDI wiring
- ~30 Spring-specific modules (starters, generators,
  auto-configurations)

---

## What Makes It Different

### Breadth of Consistency

The single most unusual property of CaseHub is its internal
consistency at scale. 500+ modules — identity, orchestration,
communications, reconciliation, UI — all sharing one CDI model, one
event system, one type hierarchy, one tenancy model, one audit trail.

This is not a claim about code quality. It is a claim about
architecture: every capability was built from the same primitives.
When an agent sends a message through the communications mesh, the
message delivery automatically has tenant context, identity context,
audit context, and event routing context — because those are the same
context. There is no mapping layer between "the auth system" and "the
messaging system" because they share one identity model.

The practical consequence: integration is zero-cost. Adding a new
connector, a new reconciliation domain, or a new agent backend does
not require a separate integration project. The new capability
inherits tenancy, audit, notifications, simulation, and MCP tools
by construction.

### Simulation at the Platform Level

Most platforms simulate at the unit test level — mock this service,
stub that API. CaseHub simulates at the SPI level: any interface
marked `@SimulationEligible` gets a generated CDI decorator that
intercepts calls, resolves from corpus data, and records for
verification. This means you can simulate an entire multi-agent
scenario — with temporal events, agent interactions, and device
state changes — using the same code that runs in production.

No Java ecosystem tool offers this. Mockito mocks objects.
Testcontainers run infrastructure. CaseHub's simulation framework
replaces entire capability surfaces with deterministic,
corpus-driven alternatives.

### No Vendor Lock-In at Any Layer

Agent backends are pluggable (7 providers today). Connectors use
`java.net.http` directly — no Slack SDK, no Twilio SDK, no vendor
dependency conflicts. IoT bridges to Home Assistant and OpenHAB
through typed abstractions. Persistence uses JPA (any database).
The framework itself runs on Quarkus or Spring Boot.

At every integration point, CaseHub owns the abstraction. Providers
are pluggable. Replacing an LLM provider, a chat platform, or a
database is a configuration change — not a code change.

---

## Connections to Other Areas

Every capability area in CaseHub builds on the Shared Foundation:

| Area | What it uses |
|------|-------------|
| [Declaration Surface](01-declaration-surface.md) | Expression engines, YAML primitives, preference management |
| [Agentic Orchestration](02-agentic-orchestration.md) | Agent infrastructure, event routing (alpha network), simulation |
| [AI Knowledge & Learning](03-ai-knowledge-learning.md) | Agent infrastructure (model resolution), identity context |
| [Enterprise Execution](04-enterprise-execution.md) | Identity & tenancy, notification pipeline, ACL, event routing |
| [Accountability & Governance](05-accountability-governance.md) | Document signing, MCP tool surface, identity hierarchy |
| [Convergence & Situational Awareness](06-convergence-situational-awareness.md) | Simulation framework, connector SPIs, IoT device management |
| [Agent Identity & Cognition](07-agent-identity-cognition.md) | Agent infrastructure, identity model, simulation |
| [Application Surface](09-application-surface.md) | SSE push, MCP tools, notification pipeline, design tokens |

The Shared Foundation is also where the **fully automatable** promise
(Theme 6 from the positioning) is delivered. GraphQL and MCP expose
every capability programmatically. The simulation framework enables
deterministic testing of any automation. The playbook infrastructure
(via the Pages playbook runtime and MCP domain) bridges UI
automation with domain operations. The platform is its own best
operator.

---

## Extent

| Component | Modules | Source files | Highlights |
|-----------|---------|-------------|------------|
| Platform services | 178 | 1,821 Java | Identity, expressions, notifications, ACL, agents, simulation, callbacks, MCP, signing, streams, preferences |
| Connector SPIs | 29 | — | 5 platform SPIs, 6 outbound + 8 inbound connectors, 14+ MCP tools |
| IoT devices | 12 | 50+ (webapp) | 11 typed devices, 7 ganglia, 4 case types, 4 CBR schemas |
| LLM Fleet Management | 4 | 164 Java + 12 Lit | 43-class fleet package, 3 scaling policies, ops bridge |

---

*See the [Appendix](appendix/08-shared-foundation-inventory.md) for
the complete capability and module inventory.*
