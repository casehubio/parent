# Drill-Down: The Shared Foundation

*178 modules of homogeneous primitives — the reason everything else
composes without integration glue.*

---

## Architecture Overview

The platform repo contains 178 modules organised into 14 capability
areas. Every module follows a consistent pattern: a `-core` artifact
with framework-neutral POJOs, a Quarkus wiring module with CDI
producers and `@DefaultBean` displacement, and a Spring
auto-configuration module with `@ConditionalOnMissingBean`
equivalents. Business logic lives in `-core` and is never duplicated
between frameworks.

Cross-cutting concerns — tenancy, identity, events, audit — are not
injected by middleware. They are the primitives every module is built
from. When a new capability is added, it does not integrate with
tenancy — it IS tenant-scoped, because `CurrentPrincipal` is the
identity model it was built on. The result: zero-cost integration
for every new capability.

The connector repo adds 29 modules implementing 7 homogeneous
platform SPIs (Chat, Calendar, Bank, Email, Document, Contacts,
Project), each following the same pattern: SPI interface with
`@SimulationEligible`, routing service with `@All List<T>` CDI
discovery, reference implementation for testing, and one or more
real providers. No vendor SDKs anywhere — all HTTP-based connectors
use `java.net.http.HttpClient` directly.

---

## SPI Contracts

### Identity & Tenancy

| Interface | Module | Purpose |
|-----------|--------|---------|
| `CurrentPrincipal` | `platform-oidc` | Three-level typed identity: Principal → Actor → Participant. Every query is tenant-scoped through this. |
| `ActorType` | `platform-api` | Sealed enum: HUMAN, AGENT, SYSTEM. Determines authorization semantics throughout the platform. |
| `DidResolver` | `platform-identity` | Composite DID resolution (did:key, did:web, SCIM) with Ed25519, P-256, secp256k1. SSRF-protected web resolution. |

### Expression Engines

| Interface | Module | Purpose |
|-----------|--------|---------|
| `ExpressionEvaluator` | `expression-core` | Three engines (JQ, MVEL3, JEXL3) in one CDI-managed registry. Auto-registered. |
| `ExpressionScope` | `expression-core` | Config and secret injection — `$config` and `$secret` scopes reference live PreferenceProvider values. |

### Notification Pipeline

| Interface | Module | Purpose |
|-----------|--------|---------|
| `SubscriptionRegistry` | `notification-api` | Subscription registration with pattern predicates for alpha network matching. |
| `NotificationDispatcher` | `notification-core` | Three-path dispatch: immediate, suppress, digest. Quiet hours with buffer-for-digest. |
| `DeliveryTracker` | `notification-tracking` | Engagement lifecycle: opened, clicked, dismissed, replied, converted. |
| `DigestBatcher` | `notification-digest` | Per-user digest batching with configurable window and template. |

### Agent Infrastructure

| Interface | Module | Purpose |
|-----------|--------|---------|
| `AgentProvider` | `agent-api` | Vendor-agnostic SPI. 7 backends: Claude, OpenAI, Gemini, Gemini CLI, Codex, Ollama, LangChain4j. |
| `ModelRegistry` | `agent-core` | Three-step resolution: alias → tier → registry → key. Consumer requests capability tier; registry resolves to concrete model. |
| `AgentManifest` | `agent-config` | `agent-config.yaml` declaration: providers, models, rate limits, credentials (env/file/Vault). |
| `RateLimiter` | `agent-ratelimit` | CDI decorator: token bucket + concurrency gate. Per-provider and per-model limits. Zero application code changes. |

### Simulation Framework

| Interface | Module | Purpose |
|-----------|--------|---------|
| `@SimulationEligible` | `simulation-api` | Annotation on any SPI interface — APT generates CDI decorators, qualified name constants, parameter metadata. |
| `CorpusStrategy` | `simulation-core` | Response resolution: sequential, key-lookup, random, recorded-replay, nearest-match. Multi-format corpus (YAML, JSON, CSV). |
| `SimulationJournal` | `simulation-core` | Interaction recording for Mockito-quality verification (`verify(spi).method(args)`). |
| `TemporalDriver` | `simulation-temporal` | Tick-based event emitter with lifecycle (start/pause/resume/stop/setSpeed). 3-level speed composition. |

### Connector SPIs

| Interface | Module | Purpose |
|-----------|--------|---------|
| `ChatPlatform` | `connectors-chat-api` | 10 capability interfaces: Messaging, Threading, Discovery, Reactions, Presence, Members, ChannelManagement, MemberManagement, MessageHistory, Commands. |
| `CalendarPlatform` | `connectors-calendar-api` | Full CRUD. Sealed `EventTiming` (Timed/AllDay). Google Calendar provider. |
| `BankPlatform` | `connectors-bank-api` | AISP + PISP sub-interfaces. PSD2 consent lifecycle. TrueLayer provider with JWS-verified webhooks. |
| `EmailPlatform` | `connectors-email-api` | Mailbox listing, paginated messages, attachment download. IMAP provider. |
| `DocumentPlatform` | `connectors-document-api` | FileOperations, FolderOperations, SearchOperations, SharingOperations. Google Drive provider. |
| `UnsupportedCapabilityException` | `connectors-api` | Structured metadata for LLM self-correction. `supports(Class<?>)` for capability introspection. |

### MCP Hierarchical Model

| Interface | Module | Purpose |
|-----------|--------|---------|
| `@McpDomain` | `platform-api` | Annotation on SPI interfaces/classes. APT generates MCP tools, GraphQL operations, REST endpoints — tri-channel from one source. |
| `GraphQLModelScanner` | `mcp-graphql` | Auto-discovers `@McpDomain` domains via CDI. No manual tool registration. |
| `DynamicToolRegistrar` | `mcp-core` | Handles capability exceptions gracefully — missing providers don't crash tool registration. |
| `LandscapeReportService` | `mcp-core` | Parallel report collection across all registered domains. Full platform tool surface queryable at runtime. |

### Access Control

| Interface | Module | Purpose |
|-----------|--------|---------|
| `AclEvaluator` | `acl-core` | Deny-wins-at-specificity resolution. Recursive CTE hierarchy traversal in a single SQL query. Wildcard grants (`type:*`). Parent chain walking to depth 20. |

### Document Signing

| Interface | Module | Purpose |
|-----------|--------|---------|
| `DocumentSigner` | `signing-core` | EU DSS 6.2 PAdES embedded + CAdES detached. Per-tenant PKCS#12 keystores with atomic rotation. EU Trusted List validation. |

---

## Data Model

### Identity Hierarchy

```
Principal         — authentication context (JWT, API key, system)
├── Actor         — execution identity: human, agent, or system
│   └── tenancyId — every query scoped through this
└── Participant   — conversation membership (who is involved)
```

### Notification Lifecycle

```
Event → SubscriptionMatch (alpha network) → Dispatch
    ├── Immediate → Delivery → Engagement tracking
    ├── Suppress  → (discarded)
    └── Digest    → Buffer → Batch → Delivery → Engagement
```

Production backends: JPA with SKIP LOCKED claims, keyset pagination,
retention purge. In-memory alternatives for testing. SSE push
delivery. REST API for presentation.

### Preference Resolution Chain

```
org-default → app-override → case-type-override → case-instance
```

More specific scopes override less specific. Schema validation at
write time. ETag-based versioning. Runtime changes without restart.
Feeds expression engine `$config` scope, SLA thresholds, notification
policies, compliance parameters, and behavioural contract bounds.

---

## Runtime Behaviour

### Alpha Network Event Routing

The DataSource alpha network applies the Rete algorithm to domain
event routing. On event arrival:

1. Event enters the discrimination network at the root node
2. Type nodes filter by event class (constant-time hash lookup)
3. Alpha nodes evaluate tenant-scoped predicates
4. Fan-out dispatches to matching subscribers
5. Self-pruning removes inactive subscriptions automatically
6. Startup reconciliation re-registers durable subscriptions from
   JPA store

This is not a message bus with topic subscriptions. It is a
pattern-matched routing engine that evaluates every event against
every active subscription in a single pass — the same algorithmic
efficiency that made Drools fast.

### Simulation Lifecycle

1. Developer marks SPI interface with `@SimulationEligible`
2. APT code generator produces CDI decorator, qualified name
   constants, and parameter metadata at build time
3. In test: decorator intercepts SPI calls, resolves from corpus
   via configured `CorpusStrategy`, records interaction to
   `SimulationJournal`
4. Verification: `verify(spi).method(args)` asserts expected
   interactions — full Mockito-quality API
5. Temporal simulation: `TemporalDriver` emits tick events at
   configurable speed with pause/resume/speed-change lifecycle
6. Production recording: journal entries from live runs become
   replay corpuses for regression suites

Pre-built adapters: 11 platform SPIs + `CaseMemoryStore` +
`AgentProvider` ready to simulate out of the box.

### Dual-Framework Deployment

Every module follows the extraction pattern:

```
module-core         — framework-neutral POJOs, business logic
module-quarkus      — CDI producers, @DefaultBean, Quarkus config
module-spring       — @Configuration, @ConditionalOnMissingBean, Spring properties
```

Spring generators produce `@Controller`, `@RestController`, Spring
AI `@Tool` equivalents from the same source. Integration tests verify
that Spring auto-configuration produces identical behaviour to
Quarkus CDI wiring. ~30 Spring-specific modules (starters,
generators, auto-configurations). Zero business logic duplication.

---

## Extension Points

| Extension | How to add |
|-----------|-----------|
| New expression engine | Implement `ExpressionEvaluator`, register via CDI. Auto-discovered. |
| New agent backend | Implement `AgentProvider`, add model entries to `agent-config.yaml`. Rate limiting applies automatically via CDI decorator. |
| New connector SPI | Define interface with `@SimulationEligible`, implement routing service with `@All List<T>` discovery, provide reference implementation. |
| New notification channel | Implement delivery adapter in the notification dispatch pipeline. Engagement tracking applies automatically. |
| New event stream connector | Implement stream adapter, construct `CloudEvent` instances. Downstream consumers (ganglia, notifications, reconciliation) receive events transparently. |
| New MCP domain | Annotate SPI with `@McpDomain`. APT generates MCP tools + GraphQL operations + REST endpoints. No manual registration. |
| New simulation corpus | Add YAML/JSON/CSV corpus files to classpath. Corpus strategies resolve from them automatically. |

---

## Module Map — 14 Capability Areas

| Area | Modules | Key types |
|------|---------|-----------|
| Identity & Tenancy | 3 | `CurrentPrincipal`, `ActorType`, `DidResolver` |
| Expression Engine | 3 | `ExpressionEvaluator`, `ExpressionScope` |
| Notification Pipeline | 14 | `SubscriptionRegistry`, `NotificationDispatcher`, `DeliveryTracker` |
| Access Control | 7 | `AclEvaluator`, recursive CTE hierarchy |
| Agent Infrastructure | 24 | `AgentProvider`, `ModelRegistry`, `AgentManifest`, `RateLimiter` |
| Simulation Framework | 14 | `@SimulationEligible`, `CorpusStrategy`, `SimulationJournal`, `TemporalDriver` |
| YAML Primitives | 5 | `VariableResolver`, `ForEachExpander`, `YamlModule`, step runtime |
| DataSource Alpha Network | 3 | `DataSourceRouter`, `CloudEventTypeDispatcher` |
| Document Signing | 3 | `DocumentSigner`, PAdES/CAdES, EU Trusted List |
| Preference Management | 4 | `PreferenceProvider`, schema registry, scope hierarchy |
| Callback System | 10 | Lease-based remote SPI, heartbeat renewal, CBOR serialisation |
| MCP Hierarchical Model | 4 | `@McpDomain`, `GraphQLModelScanner`, `LandscapeReportService` |
| Streams Integration | 5 | Kafka, AMQP, webhook, poll, Camel — all producing CloudEvents |
| Spring Boot Support | ~30 | Starters, generators, auto-configurations — framework parity |
| **Connector SPIs** | **29** | Chat (10 interfaces), Calendar, Bank, Email, Document, Contacts, Project |
