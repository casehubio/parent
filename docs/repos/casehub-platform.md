# casehub-platform — SPI Layer Rationale and Quarkus Integration

**Repo:** `casehubio/platform`
**Tier:** Foundation (first in build order, zero casehubio dependencies)
**Purpose:** Zero-dependency SPIs and types shared across all casehub modules.

This document answers the question developers will always ask: *"Why does casehub define its own identity, preferences, and path types when Quarkus already has those things?"* The short answer is that casehub-platform is not a parallel system — it is a thin, zero-dependency domain layer that Quarkus-specific code implements. The long answer is below.

---

## The Three-Layer Model

```
platform-api/               ← Tier 1: zero dependencies — pure Java interfaces and records
platform/                   ← Tier 3: Quarkus @DefaultBean mocks, @ConfigProperty
testing/                    ← companion: @Alternative @Priority(1) test fixtures (CDI API only)
config/                     ← optional: scope-aware YAML + SmallRye Config preference provider
oidc/                       ← optional: @RequestScoped CurrentPrincipal backed by SecurityIdentity + JWT
expression/                 ← optional: JQ + MVEL3 expression evaluation
persistence-jpa/            ← optional: JPA-backed scoped preference overrides
persistence-mongodb/        ← optional: MongoDB preference backend
agent-api/                  ← optional: AgentProvider SPI (Mutiny only, no Quarkus)
agent-claude/               ← optional: ClaudeAgentProvider — Claude CLI subprocess integration
agent-langchain4j/          ← optional: bidirectional LangChain4j interop
endpoints-memory/           ← optional: @Alternative @Priority(100) InMemoryEndpointRegistry
endpoints-config/           ← optional: YAML-backed endpoint populator
datasource-alpha/           ← Rete-style alpha network for event routing (AlphaDataSource)
datasource-inmem/           ← @Alternative @Priority(100) in-memory DataSourceRegistry
datasource-jpa/             ← @ApplicationScoped JPA DataSourceRegistry with startup reconciliation
identity/                   ← DID infrastructure: did:key (secp256k1), did:web, SCIM resolver, composite ActorDIDProvider
acl-inmem/                  ← @Alternative @Priority(100) in-memory ACL store
acl-jpa/                    ← @ApplicationScoped JPA ACL store
governance/                 ← platform governance module
credentials-quarkus/        ← Quarkus CredentialsProvider-based CredentialResolver bridge
scim/                       ← SCIM 2.0 GroupMembershipProvider
notifications/              ← REST + SSE endpoints for notification presentation
notifications-inmem/        ← @Alternative @Priority(100) in-memory NotificationStore
notifications-jpa/          ← @ApplicationScoped JPA NotificationStore (Hibernate Reactive Panache)
notification-dispatch/      ← three-path delivery: digest buffer, suppress, or deliver immediately
notification-settings-inmem/ ← @Alternative @Priority(100) in-memory preference/suppression store
notification-settings-jpa/  ← @ApplicationScoped JPA preference/suppression store
delivery-channel-inmem/     ← @ApplicationScoped channel-to-deliverer registry (production implementation)
delivery-tracking-inmem/    ← @Alternative @Priority(100) in-memory delivery attempt store
delivery-tracking-jpa/      ← @ApplicationScoped JPA delivery attempt store (SKIP LOCKED claims)
digest-inmem/               ← @Alternative @Priority(100) in-memory digest buffer
digest-jpa/                 ← @ApplicationScoped JPA digest buffer
subscriptions/              ← subscription matching engine + REST — wires DataSource alpha network
subscriptions-inmem/        ← @Alternative @Priority(100) in-memory subscription store
subscriptions-jpa/          ← @ApplicationScoped JPA subscription store (Hibernate Reactive Panache)
streams-kafka/              ← Kafka event stream connector
streams-amqp/               ← AMQP event stream connector
streams-webhook/            ← Webhook event stream connector
streams-poll/               ← Polling event stream connector
streams-camel/              ← Apache Camel event stream connector
```

**Removed from build:** `memory-inmem/`, `memory-jpa/`, `memory-sqlite/`, `memory-mem0/`, `memory-graphiti/` — memory backends migrated to casehub-neocortex (neocortex#56). Directories remain on disk but are no longer listed in `<modules>` in the parent POM.

`platform-api/` must never import Quarkus, CDI, JPA, or any casehubio artifact. This constraint is what makes the SPIs useful to every module in the stack — including modules that have no Quarkus dependency of their own.

**Package structure in `platform-api/`:** `identity` (`CurrentPrincipal`, `GroupMembershipProvider`, `GroupMember`, `ActorType`, `ActorTypeResolver`, `SecurityIdentityAttributes`, `TenancyConstants`, `MissingTenancyException`, `DIDResolver`, `DIDMethod` (CDI qualifier), `DIDDocument`, `VerificationMethod`, `VerificationMethodType`, `ActorDIDProvider`, `ActorDIDSource` (CDI qualifier), `AgentCredentialValidator`, `CredentialValidationResult`, `IdentityVerificationResult`, `IdentityBindingStatus`, `AgentIdentityValidatedEvent`, `AgentIdentityViolationEvent`), `preferences` (`PreferenceProvider`, `PreferenceKey`, `Preferences`, `SettingsScope`), `path` (`Path`), `endpoints` (`EndpointRegistry`, `EndpointDescriptor`, `EndpointPermissions` (static: `assertTenant(tenancyId, principal)` — write-auth for runtime registration), `EndpointType`, `EndpointProtocol`, `EndpointCapability`, `EndpointQuery`, `EndpointPropertyKeys`), `datasource` (`DataSource<T>`, `DataProcessor<T>`, `DataSourceRegistry`, `DataSourceDescriptor`, `DataSourceQuery`, `ObjectType<T>`, `ClassObjectType<T>`, `SubscriptionHandle`, `Marshaller<I,O>`, `MarshallerRegistry`, `MarshalException`, `FilterExpression<T>`, `DataSourceRegistered`, `DataSourceDeregistered`, `DataSourceUpdated`), `delivery` (`DeliveryAttemptStore`, `DeliveryChannelRegistry`, `NotificationDeliverer`, `DigestBuffer`, `DeliveryAttempt`, `DeliveryAttemptPage`, `DeliveryAttemptQuery`, `DeliveryChannelDescriptor`, `DeliveryResult`, `DigestBufferKey`, `DigestSchedule`, `DigestSummary`, `DeliveryExhausted`, `DeliveryChannels`, `DeliveryStatus`, `DeliveryType`, `DigestGroupBy`), `notification.settings` (`NotificationPreferenceStore`, `SuppressionStore`, `NotificationPreferences`, `NotificationPreferenceUpdate`, `ChannelPreference`, `QuietHours`, `MuteRule`, `MuteRuleInput`, `Snooze`, `SnoozeInput`, `SuppressionResult`, `MuteScope`, `QuietHoursAction`), `subscription` (`SubscriptionStore`, `ReactiveSubscriptionStore`, `EventTypeRegistry`, `SubscribableEvent`, `EntityWatcherProvider`, `Subscription`, `SubscriptionInput`, `SubscriptionUpdate`, `SubscriptionQuery`, `SubscriptionPage`, `NotificationTarget`, `NotificationTemplate`, `EventTypeDescriptor`, `EventFieldDescriptor`, `SubscriptionMatched`, `SubscriptionCreated`, `SubscriptionUpdated`, `SubscriptionDeleted`, `SubscriptionScope`, `TargetType`), `notification` (`Notification`, `NotificationStore`, `ReactiveNotificationStore`, `NotificationInput`, `NotificationQuery`, `NotificationPage`, `NotificationSeverity`, `NotificationSource`, `NotificationStatus`), `routing` (`NamedStrategy` — marker interface for CDI-discoverable routing strategies with `String id()`, `StrategyResolver` — resolves `NamedStrategy` beans by `(type, id)` with `resolve`, `find`, `defaultStrategy`, `available`), `actor` (`ActorStateAccumulator` — visitor for assembling actor state (trustScore, capabilityScore, workItem, commitment, engineActiveCaseId), `ActorStateContributor` — SPI for contributing to unified actor state with `sourceName()` and `contribute(actorId, accumulator)`), `governance` (`ExecutionPolicy`, `RetryPolicy`, `BackoffStrategy`), `credentials` (`CredentialResolver`, `CredentialPropertyKeys`), `util` (`UUIDv7` — UUID v7 generator per RFC 9562 with thread-local monotonic counter, `Vectors` — stateless float[] vector operations: `dotProduct`, `magnitude`, `cosineSimilarity`), `memory` (`CaseMemoryStore`, `GraphCaseMemoryStore` (graph-native SPI extension — adds `graphQuery(GraphMemoryQuery)` for temporal queries), `MemoryCapability` (self-description enum — adapters declare `capabilities()`; callers use `requireCapability()` for typed exceptions), `MemoryInput`, `Memory`, `MemoryQuery`, `GraphMemoryQuery`, `EraseRequest`, `MemoryDomain`, `MemoryPermissions`). `ReactiveCaseMemoryStore` lives in `platform/`, not `platform-api/` — Mutiny is a Quarkus dep and would violate the zero-dep constraint.

`config/` and `oidc/` are optional — consumers add them as compile-scope dependencies to activate the capability. Each displaces its corresponding `@DefaultBean` mock automatically via CDI without exclusion config.

---

## Path

**Problem:** casehub needs a hierarchical, scope-labelling type — for case types
(`casehubio/devtown/pr-review`), preference scopes, label paths, and work-item types. It must be
a domain record with strict validation, not a filesystem path.

**Why not `java.nio.file.Path`?** Filesystem semantics (`/`, `..`, absolute vs relative) do not apply. `java.nio.file.Path` also carries heavy I/O semantics and platform-specific behaviour. A dedicated record gives strict validation (no empty segments, no leading/trailing slashes) and domain methods (`isAncestorOf`, `parent`, `depth`).

**Quarkus integration:** `PathParserConfigurator` (@Startup) registers the separator from `casehub.platform.path.separator` via `Path.setDefaultParser()`. `Path.parse(String)` uses the configured parser; `Path.of(String...)` is always explicit and does no parsing.

**Harness convention:** Build scope paths as `Path.of("casehubio", "<app>", "<case-type>")` — org segment, app segment, case-type segment. This convention makes scope inheritance work correctly: `casehubio/devtown` inherits from `casehubio`, `casehubio/devtown/pr-review` inherits from both.

**JAX-RS integration:** `PathParamConverter` and `PathParamConverterProvider` are shipped in `platform/` (`io.casehub.platform.converter`). REST endpoints can declare `@PathParam` and `@QueryParam` of type `Path` directly — no manual string conversion needed.

---

## Preferences

**Problem:** case-type business rules that vary at runtime — *how many approvers does a PR review require?*, *is a security review mandatory for this commit?* These are not deployment-time settings; they change per case type and per installation without restarting the application.

**Why not SmallRye Config / `@ConfigMapping`?**

| | SmallRye Config | casehub `PreferenceProvider` |
|--|--|--|
| When resolved | Startup | Per-request, per scope |
| Can change without restart | No | Yes |
| Varies per case type | No | Yes |
| Scope hierarchy | No | `casehubio → devtown → pr-review` |
| Where stored | `application.properties`, env vars | File, DB, both |

SmallRye Config is for *deployment configuration* — database URLs, connection pool sizes, feature flags that are the same for every case. `PreferenceProvider` is for *business configuration* — rules that vary between case types and between installations. They solve different problems and belong together, not in competition.

**`MockPreferenceProvider` uses `@ConfigProperty` deliberately.** In dev/test with no database, SmallRye Config *is* the backend — you set preferences via `application.properties`. This is correct layering, not a workaround.

**`PreferenceKey<T>` carries a parser.** Each key definition includes a `Function<String, T> parser`:

```java
public static final PreferenceKey<HumanApprovalThreshold> KEY =
    new PreferenceKey<>("devtown", "humanApprovalThreshold",
        new HumanApprovalThreshold(500),            // null guard only — real defaults in YAML
        s -> new HumanApprovalThreshold(Integer.parseInt(s)));
```

The parser follows the Drools `OptionKey<T>` / `ClockTypeOption.get(String)` precedent: colocated with the key, no type registry, no reflection. `key.parse(raw)` is called by any string-source provider (mock, YAML reader). `key.defaultValue()` is a type-safe null guard — real business defaults live in the harness preferences YAML file, not in Java code.

**`Function` equality trap.** `PreferenceKey` is a record with a `Function` component. Records include all components in `equals()`/`hashCode()`, but `Function` instances only have identity equality. Two separately-created keys with the same namespace/name are NOT `equals()`. Always use `key.qualifiedName()` as map keys, never the `PreferenceKey` object.

**`config/` module design (recommended for next epic):** Implement as a SmallRye `ConfigSource` so the scope-aware YAML reader participates in the standard Quarkus config chain with proper ordinal/priority. This lets it be overridden by environment variables (higher ordinal) without custom code, and lets `@ConfigProperty` injection pick up preference values during tests without any mock. See `casehubio/platform#5`.

---

## Identity

### CurrentPrincipal

**Problem:** casehub modules need to know who is acting — `actorId` (a casehub-specific agent identity string like `"claude:analyst@v1"` or `"alice"`) and group membership. They must not depend on `quarkus-security` to express this.

**Why not inject `SecurityIdentity` directly?** `io.quarkus.security.identity.SecurityIdentity` lives in `quarkus-security`, which cannot be a dependency of `platform-api/` (Tier 1, zero deps). More importantly, `SecurityIdentity` represents an *authenticated HTTP request principal* — casehub actors include AI agents operating outside HTTP request context, system actors, and internal services. The semantics are different enough to warrant a dedicated SPI.

**How it integrates:** Real implementations are `@RequestScoped` and delegate to `SecurityIdentity`:

```java
@RequestScoped
public class SecurityCurrentPrincipal implements CurrentPrincipal {
    @Inject SecurityIdentity identity;
    @Override public String actorId() { return identity.getPrincipal().getName(); }
    @Override public Set<String> groups() { return identity.getRoles(); }
}
```

`@DefaultBean` yields to this automatically — no exclusion config needed.

**`MockCurrentPrincipal` is `@ApplicationScoped` by design.** No request context exists in dev/test mode. This is not a design flaw; it is the correct behaviour for a mock. `@ActivateRequestContext` is required before accessing `CurrentPrincipal` in reactive pipelines.

**`roles()` defaults to `groups()`.** This wires directly to `@RolesAllowed` without an interface change when RBAC is implemented. Override `roles()` in the real implementation if RBAC roles and group memberships need to diverge.

**Auth retrofit path:** `casehub-platform-oidc` ships the OIDC-backed `CurrentPrincipal`:

1. `OidcCurrentPrincipal` → `@RequestScoped`, reads `actorId`/`groups` from `SecurityIdentity`, reads `tenancyId` (required) and `crossTenantAdmin` (optional, defaults `false`) from fixed JWT claims. Anonymous identity returns sentinels without touching the JWT. Add `casehub-platform-oidc` as a compile dependency to activate — displaces the mock automatically.
2. `GroupMembershipProvider` real implementation shipped as `casehub-platform-scim` — SCIM 2.0 client, `@ApplicationScoped`, displaces mock by classpath presence, `@CacheResult` on group fetches. Returns `Set<GroupMember>` (actorId = OIDC sub = SCIM value UUID, displayName = human label). The `SecurityIdentityAugmentor` integration (populating `@RolesAllowed` from SCIM groups) remains deferred; see Out of Scope in platform#45.
3. Multi-tenant scope derivation via quarkiverse `TenantContext` is deferred (closed casehubio/platform#14 as won't-do-until-needed).

**`tenancyId()` and `isCrossTenantAdmin()` are abstract.** Every implementor must provide them — compile error if missing. Single-tenant deployments return `TenancyConstants.DEFAULT_TENANT_ID` (configurable via `casehub.tenancy.default-id`); real OIDC-backed implementations read from the JWT `tenancyId` claim. `TenancyConstants` is a utility class in `platform-api` exposing `DEFAULT_TENANT_ID` and `PLATFORM_TENANT_ID` as importable constants. See protocols `PP-20260520-439daf` (no conditional tenancy filtering) and `PP-20260520-e6a5f0` (bind tenancy in data access layer only).

**`isSystem()` checks `actorId == "system"`.** The `"anonymous"` sentinel marks unauthenticated; `"system"` marks the platform acting on its own behalf. These are casehub conventions, not Quarkus conventions.

**Missing: `actorType()`.** A TODO comment in `CurrentPrincipal` tracks this. `ActorType` (HUMAN / AGENT / SYSTEM) is currently in `casehub-ledger-api` and needs to migrate to `casehub-platform-api` before the method can be added. See `casehubio/ledger#88`. Prioritise this migration before the auth retrofit to avoid two-pass refactoring.

### GroupMembershipProvider

**Problem:** "Who is in the 'legal-reviewer' group?" — an inverse membership query. casehub needs this to route work items to eligible workers. Quarkus security answers the forward query ("what roles does this user have?") but not the inverse.

**Quarkus relationship:** Complementary, not duplicating. The real implementation should:

1. Implement `GroupMembershipProvider` (answers "who can do this task?")
2. Also register as `SecurityIdentityAugmentor` (populates `SecurityIdentity.getRoles()` so `@RolesAllowed` reflects casehub group memberships)

These are two different query directions over the same data source. Example:

```java
@ApplicationScoped
public class LdapGroupMembershipProvider
        implements GroupMembershipProvider, SecurityIdentityAugmentor {

    @Override
    public Set<GroupMember> membersOf(String groupName) {
        return ldapClient.membersOf(groupName);  // returns GroupMember(actorId, displayName)
    }

    @Override
    public Uni<SecurityIdentity> augment(SecurityIdentity identity,
                                         AuthenticationRequestContext context) {
        Set<String> groups = ldapClient.groupsOf(identity.getPrincipal().getName());
        return Uni.createFrom().item(() ->
            QuarkusSecurityIdentity.builder(identity).addRoles(groups).build()
        );
    }
}
```

See `platform-spi-contract.md` for the full pattern.

---

## CaseMemoryStore

**Problem:** every CaseHub case starts cold. Facts established in one case — about an entity, an agent's behaviour, a recurring pattern — are invisible to the next case unless explicitly passed as parameters. This produces repeated research, missed context, and weaker routing decisions across all consumer repos.

**Why a platform SPI, not a per-repo solution:** devtown, clinical, aml, and life all need semantic recall across cases. A per-repo memory implementation would duplicate the permission model, domain isolation logic, and backend adapter overhead in every consumer. `CaseMemoryStore` follows the same SPI placement logic as `PreferenceProvider` and `CurrentPrincipal` — shared concept, zero external dependency, displaces via CDI.

**SPI contract (`casehub-platform-api`):**
- `CaseMemoryStore` (blocking) — `store`, `storeAll` (bulk convenience default), `query`, `erase`, `eraseById`
- `MemoryInput`, `Memory`, `MemoryQuery`, `EraseRequest`, `MemoryDomain` — value types (zero deps)
- `MemoryPermissions` — static utility enforcing `CurrentPrincipal` + `GroupMembershipProvider` boundary; **enforced at the SPI layer**, never delegated to backends
- Domain isolation: `MemoryDomain` scopes facts — health, finance, household facts do not cross domain boundaries regardless of backend

**`platform/` contains:** `NoOpCaseMemoryStore @DefaultBean`, `ReactiveCaseMemoryStore` interface (Mutiny dep — cannot live in zero-dep `platform-api/`), `BlockingToReactiveBridge @DefaultBean`.

**`@DefaultBean` pattern — silent no-op (contrast with configurable mock):**

This is an explicit design choice, not a missing feature. The two patterns serve different purposes:

| Pattern | Used by | Behaviour | Rationale |
|---------|---------|-----------|-----------|
| **Configurable mock** | `PreferenceProvider`, `CurrentPrincipal` | Returns SmallRye Config values or fixed test values | System makes routing/auth decisions based on these values — wrong values produce wrong behaviour, so the mock must be explicit |
| **Silent no-op** | `CaseMemoryStore` | Returns empty results, accepts writes silently | System functions correctly without memory — just without recall; zero overhead is the valid production default when no adapter is installed |

`NoOpCaseMemoryStore @DefaultBean` in `platform/` is correct for the vast majority of deployments at startup. Adapters activate by classpath presence — no configuration needed.

**`eraseById` signature:** `eraseById(memoryId, entityId, tenantId)` — 3-arg form (platform#64). Entity mismatch is a silent no-op (no information leak). The SPI default throws `UnsupportedOperationException` — a GDPR guard forcing adapters to implement erasure explicitly. `NoOpCaseMemoryStore` overrides this to a true no-op. Adapter implementors must not rely on the SPI default — override it unconditionally.

**`eraseEntity` return type:** `eraseEntity(entityId, tenantId)` returns `int` (count of records deleted) for GDPR Art.5(2) audit trail (platform#72). REST-backed adapters (Mem0: count-then-delete, Graphiti: episode count capped at 10k) are best-effort.

**`MemoryPermissions` async overload (platform#79):** `assertTenant(tenantId, principal, boolean requestContextActive)` — 3-arg form skips the principal check when no CDI request scope is active (e.g. in `@ObservesAsync` handlers). All adapters use this form. `@QuarkusTest` adapter tests must be annotated `@ActivateRequestContext`.

**Reactive bridge:**
`BlockingToReactiveBridge @DefaultBean` in `platform/` wraps any blocking `CaseMemoryStore` implementation as a `ReactiveCaseMemoryStore`. Native async adapters override with `@Alternative @Priority(N)` — the same CDI priority ladder used throughout the platform. See `casehub/garden: docs/protocols/universal/persistence-backend-cdi-priority.md`.

**Adapter implementations — migrated to casehub-neocortex (neocortex#56):**

The memory backend modules (`memory-inmem/`, `memory-jpa/`, `memory-sqlite/`, `memory-mem0/`, `memory-graphiti/`) have been removed from the platform build. Their directories remain on disk but are no longer listed in `<modules>`. Memory SPIs (`CaseMemoryStore`, `GraphCaseMemoryStore`, `MemoryCapability`, etc.) remain in `platform-api/` — the SPI contract is unchanged. Backend implementations now live in casehub-neocortex.

---

## Agent Infrastructure

### AgentProvider SPI

**Problem:** casehub modules need to invoke an AI agent — submit a prompt and stream back token-level text — without coupling to a specific model or runtime. `AgentProvider` in `agent-api/` is the abstraction. `NoOpAgentProvider @DefaultBean` in `platform/` emits a WARN per invocation so unconfigured deployments fail loudly.

**Why only `TextDelta` in `AgentEvent`?**

`AgentEvent` is a sealed interface with a single permit: `TextDelta`. Tool calls are intentionally absent. This is not an omission — it is a consequence of the execution model. The `claude-code-sdk` runs the full Claude Code CLI as a subprocess. Claude executes its tool loop internally (bash, file I/O, web fetch, MCP servers). By the time a token reaches the caller it is already post-reasoning, post-tool-use output. There is nothing to surface. If a future implementation backed by the Anthropic API directly (or LangChain4j) needed to expose tool calls to the caller, `AgentEvent` would need `ToolCall` and `ToolResult` variants — the sealed interface would have to be extended.

### Why `claude-code-sdk`, not the official Anthropic Java SDK

These two SDKs operate at entirely different levels of the stack and are not interchangeable:

| | Anthropic official Java SDK (`anthropics/anthropic-sdk-java`) | Spring AI Community SDK (`org.springaicommunity:claude-code-sdk`) |
|---|---|---|
| What it provides | Raw API client — HTTP messages endpoint | Java wrapper around the Claude Code CLI |
| Tool loop | **You** implement it (receive tool call → execute → feed back → repeat) | **Claude** runs it autonomously (bash, file I/O, glob, web fetch built-in) |
| Tool calls visible to caller | Yes — you must handle them | No — opaque inside the subprocess |
| MCP servers | Manual wiring | Native (`AgentMcpServer` sealed: Stdio / Sse / Http) |
| Prompt caching | Requires explicit `cache_control` placement in your code | Handled natively by the Claude Code runtime |
| Multi-step agents | You write the orchestration loop | Claude orchestrates; optional human-in-the-loop checkpoints built in |
| What the SPI models | A chat completion API | A full autonomous agent subprocess |

The official SDK is the right choice for simple API calls, content generation, and chat where you own the orchestration. The `claude-code-sdk` is the right choice for agents that need to reason, use tools autonomously, and run multi-step tasks — it exposes the same harness that powers Claude Code itself.

### Why not LangChain4j as the default or alternative

LangChain4j was in the original spec as a `@DefaultBean` implementation, but the design moved to `NoOpAgentProvider @DefaultBean` for two reasons:

**1. Different execution model.** LangChain4j's `ChatModel` is a chat completion abstraction — the host app manages the tool loop. An `AgentProvider` backed by LangChain4j would expose tool calls to the caller and would need `AgentEvent` variants that don't exist yet (`ToolCall`, `ToolResult`). The current SPI assumes the execution model of `claude-code-sdk` (opaque autonomous agent). Grafting LangChain4j onto it without extending the SPI would produce a degraded implementation.

**2. Prompt caching.** LangChain4j's Anthropic integration does not support Claude's prompt caching (`cache_control` breakpoints) — it is an open feature request ([langchain4j#1591](https://github.com/langchain4j/langchain4j/issues/1591)). Claude's native caching reduces token costs by 70–80% for repeated contexts (system prompts, large tool definitions, conversation history). Calling Claude via LangChain4j silently foregoes this. The `claude-code-sdk` subprocess handles caching natively.

### Future evolution path

The SPI is designed to support multiple implementations on the CDI priority ladder:

- **`agent-claude/` (current):** wraps `claude-code-sdk` → full autonomous agent, native prompt caching, MCP, extended thinking. Best for Claude-native deployments.
- **`agent-claude-api/` (future option):** wraps Anthropic Java SDK directly → chat completion with explicit `cache_control` management, tool loop in the implementation. Would require `AgentEvent` extension for `ToolCall`/`ToolResult` if tool transparency is needed.
- **`agent-langchain4j/` (shipped — platform#100, renamed platform#105):** bidirectional LangChain4j interop — `ChatModelAgentProvider` (any ChatModel → AgentProvider) + `AgentProviderChatModel` (any AgentProvider → ChatModel). No longer Claude-specific. `@Alternative @Priority(10) @ApplicationScoped`. **Incompatible with `engine.Agent`** — `engine.Agent.buildResponseFormat()` always forces `ResponseFormatType.JSON`; throws `UnsupportedFeatureException` for JSON format. Use a JSON-capable `ChatModel` with `engine.Agent`. `casehub.platform.agent.langchain4j.closeTimeout` (default PT30S). No quarkus:build goal — library module.

For Claude-native work, keep `agent-claude/` for direct CLI integration or `agent-langchain4j/` when the `ChatModel` interface is needed. For non-Claude LLMs, `agent-langchain4j/` now provides the bidirectional bridge directly.

### `AgentSessionConfig` and MCP

`AgentMcpServer` is a sealed interface with three variants: `Stdio` (subprocess MCP server), `Sse` (legacy HTTP SSE), and `Http` (streamable HTTP, current standard). `Sse` and `Http` are protocol-neutral. `Stdio` assumes a subprocess execution model (currently only Claude Code). All three map cleanly to the MCP spec, which is now a cross-provider standard — OpenAI, Google, and others adopted it in 2025. Including MCP in `AgentSessionConfig` is not Claude-specific.

---

## DataSource SPI and Alpha Network

**Problem:** casehub modules need to route domain events to subscribers based on type and predicate filters — without coupling producers to consumers. The DataSource SPI in `platform-api` provides a Rete-style alpha network for event ingestion, type discrimination, and predicate evaluation, with a self-pruning deregistration lifecycle.

### Core SPI (`platform-api/`)

| Type | Kind | Purpose |
|------|------|---------|
| `DataProcessor<T>` | interface | Single-method `add(T)` — the fundamental processing unit. Must be non-blocking. |
| `DataSource<T>` | interface (extends `DataProcessor<T>`) | Ingestion entry point and subscription hub — four `subscribe()` overloads with increasing specificity |
| `DataSourceRegistry` | interface | Tenant-scoped registry — `register`, `resolve`, `resolveSource`, `discover`, `deregister`, `update` |
| `DataSourceDescriptor` | record | Immutable description: `path`, `tenancyId`, `objectType`, `endpointPath`, `acceptedEventTypes`, `properties`, `marshallerKeys` |
| `DataSourceQuery` | record | Discovery criteria: `tenancyId` + optional `objectType` wildcard |
| `ObjectType<T>` | interface | Type discriminator — `matches(Object)` + `getTypeKey()` for hash-based routing |
| `ClassObjectType<T>` | class | Standard Java class-based `ObjectType` — uses `Class.isInstance()` for subtype matching |
| `SubscriptionHandle` | interface | Returned by every subscribe — `unsubscribe()` (idempotent) + `isActive()` |
| `Marshaller<I,O>` | interface | `@FunctionalInterface` for transforming objects — pre-processing decorator on `DataSource.add()` |
| `MarshallerRegistry` | interface | Named marshaller lookup — populate in `@PostConstruct`, not `@Observes StartupEvent` |
| `FilterExpression<T>` | record (implements `Predicate<T>`) | Compiled filter with metadata (`type`, `expression`, `predicate`) — enables filter node sharing in the alpha network |

**CDI events:** `DataSourceRegistered`, `DataSourceDeregistered` (carries both descriptor and DataSource instance for identity-based comparison), `DataSourceUpdated` (carries old + new descriptor).

**Subscription overloads on `DataSource<T>`:**
1. `subscribe(DataProcessor<? super T>)` — all objects, no filter
2. `subscribe(ObjectType<U>, DataProcessor<? super U>)` — type-filtered
3. `subscribe(ObjectType<U>, Predicate<U>, DataProcessor<? super U>)` — type + predicate
4. `subscribe(Class<U>, Predicate<U>, DataProcessor<? super U>)` — convenience wrapping `ClassObjectType`

**Priority lookup:** `resolve(Path, tenancyId)` returns tenant-specific before platform-global. `discover(DataSourceQuery)` returns all matching descriptors without override semantics.

### Alpha Network (`datasource-alpha/`)

`AlphaDataSource<T>` implements `DataSource<T>` using the Rete algorithm's alpha network pattern:

```
add(object)
  ├─→ directSubscribers (FanOutProcessor) — all objects, no filter
  └─→ typeNodes (ConcurrentHashMap<Object, TypeNode>)
        └─→ TypeNode: checks objectType.matches()
              ├─→ noFilterSubscribers (FanOutProcessor) — type match only
              └─→ filterNodes (List<FilterNode>)
                    └─→ FilterNode: checks predicate.test()
                          └─→ fanOut (FanOutProcessor) — type + filter match
```

**Node sharing:** TypeNodes are shared by `getTypeKey()`. FilterNodes are shared when wrapping `FilterExpression` instances with matching `type()` and `expression()`. Plain predicates use identity comparison only.

**Self-pruning:** Empty TypeNodes are removed from the map when the last subscriber unsubscribes (both no-filter and filter subscribers gone).

**Error isolation:** `FanOutProcessor` uses `CopyOnWriteArrayList` — exceptions are WARN-logged but never propagate to other subscribers.

### Self-Pruning Deregistration Lifecycle

1. `registry.deregister(path, tenancyId)` calls `source.markForRemoval(cleanupCallback)`
2. If `shareCount == 0`, cleanup fires immediately
3. Otherwise the DataSource enters "pending removal" — continues accepting `add()` and even new subscriptions
4. Registry fires `DataSourceDeregistered` via `fireAsync()` — observers react by calling `handle.unsubscribe()`
5. Each `unsubscribe()` decrements `shareCount` — when the last subscriber leaves, cleanup fires
6. Cleanup uses `sources.remove(key, source)` (identity-based) — prevents corruption if a replacement was registered during the drain period
7. Re-registration during drain creates a **new** `AlphaDataSource` — `compute()` treats a draining DataSource as absent

### Modules

| Module | Artifact | CDI | Purpose |
|--------|----------|-----|---------|
| `datasource-alpha/` | `casehub-platform-datasource-alpha` | (library) | Rete-style `AlphaDataSource` implementation — type nodes, filter nodes, fan-out, self-pruning |
| `datasource-inmem/` | `casehub-platform-datasource-inmem` | `@Alternative @Priority(100) @ApplicationScoped` | In-memory `DataSourceRegistry` — dual ConcurrentHashMap stores; Tier 4; test or ephemeral installs |
| `datasource-jpa/` | `casehub-platform-datasource-jpa` | `@ApplicationScoped` | JPA `DataSourceRegistry` — startup reconciliation from `datasource_descriptor` table; `@Transactional` register/deregister/update; same dual-map cache + JPA persistence |

---

## DID and Identity Infrastructure

The `identity/` module implements Decentralized Identifier (DID) resolution, actor-to-DID mapping, and verifiable credential validation. The SPI types live in `platform-api/` (`io.casehub.platform.api.identity`); the implementations live in `identity/`.

### DID Resolution — Composite Pattern

Consumers inject the unqualified `DIDResolver` and get `CompositeDIDResolver`, which iterates all `@DIDMethod`-qualified resolvers by `@Priority` (ascending), returning the first non-empty result.

| Resolver | `@Priority` | DID Method | How it works |
|----------|-------------|------------|--------------|
| `KeyDIDResolver` | 100 | `did:key:` | Decodes multibase key material, parses multicodec varint prefix, dispatches to `MulticodecKeyType` for SPKI conversion |
| `WebDIDResolver` | 100 | `did:web:` | HTTPS GET to `/.well-known/did.json` or `/{path}/did.json`; SSRF protection (rejects RFC 1918, loopback, link-local); configurable max response size (default 1 MiB) and timeout (default 5000ms) |
| `ScimDIDResolver` | 1000 | (any) | Constructs synthetic DID documents from SCIM2 `x509Certificates`; validates requested DID matches SCIM-stored DID; extracts SPKI from X.509 DER certificates |

### secp256k1 did:key Support

`MulticodecKeyType` handles three key types with full SPKI DER construction:

| Variant | Multicodec | Raw Key | Verification Method Type |
|---------|-----------|---------|--------------------------|
| `ED25519` | `0xed` | 32 bytes | `Ed25519VerificationKey2020` |
| `P256` | `0x1200` | 33 bytes (SEC1 compressed) | `EcdsaSecp256r1VerificationKey2019` |
| `SECP256K1` | `0xe7` | 33 bytes (SEC1 compressed) | `EcdsaSecp256k1VerificationKey2019` |

**Why manual ASN.1 for secp256k1:** JDK 15+ removed secp256k1 from SunEC (JDK-8235710). The implementation manually decompresses the SEC1 point using secp256k1 curve parameters and constructs an 88-byte SPKI by concatenating a pre-built ASN.1 header with the 64-byte uncompressed X/Y coordinates.

### ActorDIDProvider — Composite Pattern

Maps actorIds to DID URIs. Same composite pattern as DID resolution — inject unqualified `ActorDIDProvider`, get `CompositeActorDIDProvider`.

| Provider | `@Priority` | Source |
|----------|-------------|--------|
| `ConfiguredActorDIDProvider` | 100 | Static config: `casehub.identity.dids."claude:reviewer@v1"=did:web:...` |
| `ScimActorDIDProvider` | 200 | SCIM2 Agent endpoint via `ScimAgentLookup`; supports `invalidate(actorId)` for cache clearing |

### Credential Validation

`AgentCredentialValidator` — optional VC (Verifiable Credential) validation. `NoOpCredentialValidator @DefaultBean` returns `Optional.empty()` (VC validation is opt-in).

`JwtVCValidator @ApplicationScoped` — reads VC JWT files from paths configured via `casehub.identity.credentials."actorId"`. Validates JWT structure, expiration, subject-DID match, issuer DID resolution, verification method lookup, and signature (EdDSA/ES256). EXPIRED results are never cached. Displaces the no-op when present.

### Identity Verification Services

`AgentIdentityVerificationService @ApplicationScoped` — read-path: checks stored agent public key against DID document verification methods and `alsoKnownAs` binding. Does NOT re-run VC validation.

`ReactiveAgentIdentityVerificationService @DefaultBean` — Mutiny `Uni<>` bridge over the blocking service, offloads to Vert.x worker pool.

**CDI events fired:** `AgentIdentityValidatedEvent` (success — carries actorId, tenancyId, actorDid, status, key/AKA verification details, credential result, DID method) and `AgentIdentityViolationEvent` (failure — carries actorId, tenancyId, actorDid, status).

### Caching

`AbstractCachingIdentityProvider<C>` — TTL cache used by `ScimAgentLookup` and `JwtVCValidator`. Atomic conditional remove on expired entries. Transient failures are NOT cached. Empty results ARE cached for full TTL.

---

## ACL, Governance, and Credentials

### Access Control

The ACL SPI in `platform-api/` (`io.casehub.platform.api.acl`) provides async access control with resource hierarchy inheritance. All `AccessControlProvider` methods return `CompletionStage` and default to permit-all (no-ops).

| Type | Kind | Purpose |
|------|------|---------|
| `AccessControlProvider` | interface | Core ACL SPI — `canAccess`, `grant`, `revoke`, `revokeAll`, `registerParent`, `accessibleResources` |
| `AclAction` | enum | `READ`, `WRITE`, `ADMIN`, `CLAIM` |
| `AclEntry` | record | `(actorId, resourceId, AclAction, grantedAt, expiresAt, tenancyId)` with `isExpired()` |
| `AclResourceType` | constants | `CASE`, `PLAN_ITEM`, `WORK_ITEM`, `EVENT_LOG`, `CASE_DEFINITION` |
| `AccessDeniedException` | exception | Carries `actorId`, `resourceId`, `action` |

**Group-based grants:** Both implementations resolve groups via `GroupMembershipProvider.groupsOf(actorId)` and build a candidate set including `"group:" + groupName`. Grants made to `"group:managers"` are resolved for any actor in that group.

**Parent-child hierarchy:** `registerParent(child, parent)` enables ACL inheritance — `canAccess` walks the hierarchy recursively with a depth guard of 20.

**Contract test:** `AccessControlProviderContractTest` in `platform-api/` provides 22 tests both implementations must pass (basic grant/revoke, group-based grants, parent-child inheritance, expiry, idempotent grants, resource type filtering, deduplication).

| Module | Artifact | CDI | Purpose |
|--------|----------|-----|---------|
| `acl-inmem/` | `casehub-platform-acl-inmem` | `@Alternative @Priority(10) @ApplicationScoped` | ConcurrentHashMap-backed; synchronous wrapped in `CompletableFuture` |
| `acl-jpa/` | `casehub-platform-acl-jpa` | `@ApplicationScoped` | Hibernate Reactive + Panache; audit logging (`acl_audit_log` table with GRANT/REVOKE ops, `performedBy` from `CurrentPrincipal`); three JPA entities: `AclEntryEntity`, `AclAuditLogEntity`, `ResourceParentEntity` |

### Governance

The governance module provides `PolicyEnforcer` for retry + timeout + backoff policy execution.

| Type | Kind | Purpose |
|------|------|---------|
| `ExecutionPolicy` | record (in `platform-api/`) | `timeoutMs` + `RetryPolicy`; factory `noRetry()` |
| `RetryPolicy` | record (in `platform-api/`) | `maxAttempts` (default 3), `delayMs` (default 10s), `BackoffStrategy`, `maxDelayMs` |
| `BackoffStrategy` | enum (in `platform-api/`) | `FIXED`, `EXPONENTIAL`, `EXPONENTIAL_WITH_JITTER` |
| `DefaultPolicyEnforcer` | class (in `governance/`) | `@ApplicationScoped`; uses virtual thread executor; FIXED/EXPONENTIAL/JITTER backoff with optional `maxDelayMs` cap |

**Exception hierarchy:** `PolicyEnforcementException` (base) with subtypes `TimeoutPolicyException`, `RetryExhaustedException`, `InterruptedPolicyException`.

| Module | Artifact | CDI | Purpose |
|--------|----------|-----|---------|
| `governance/` | `casehub-platform-governance` | `@ApplicationScoped` | `DefaultPolicyEnforcer` — blocking policy execution on worker threads; virtual thread executor; `@PreDestroy` shutdown |

### Credentials

The `CredentialResolver` SPI (`platform-api/`) resolves **outbound** endpoint credentials by logical reference name. Returns `Map<String, String>` keyed by `CredentialPropertyKeys` constants (`USER`, `PASSWORD`, `BEARER_TOKEN`, `API_KEY`, `EXPIRES_AT`, `SIGNING_SECRET`). Distinct from **inbound** Verifiable Credential validation in `io.casehub.platform.api.identity`.

| Module | Artifact | CDI | Purpose |
|--------|----------|-----|---------|
| `credentials-quarkus/` | `casehub-platform-credentials-quarkus` | `@Alternative @Priority(1) @ApplicationScoped` | Bridge from `CredentialResolver` to Quarkus `CredentialsProvider`; `@PostConstruct` validates exactly one Quarkus provider exists; displaces `@DefaultBean` when on classpath |

---

## Expression Evaluation

The `expression/` module provides pluggable expression evaluation through the `ExpressionEngine` SPI (defined in `platform-api/`).

### SPI Types (`platform-api/`)

| Type | Kind | Purpose |
|------|------|---------|
| `ExpressionEngine` | interface | Factory: `type()`, `compile(expression, contextType, resultType)`, `validate(expression)` |
| `ExpressionEngineRegistry` | interface | Registry: `register()`, `resolve(type)`, `compile(type, ...)`, `validate(type, expression)` |
| `CompiledExpression<C,R>` | interface | Compiled, type-safe expression: `type()`, `eval(C context)` |
| `ExpressionEvaluator` | interface | Marker for uncompiled expression descriptors — `String type()` discriminator for registry dispatch |
| `JQExpressionEvaluator` | record | `record(String expression) implements ExpressionEvaluator` — `type() = "jq"` |
| `MvelExpressionEvaluator` | record | `record(String expression) implements ExpressionEvaluator` — `type() = "mvel"` |
| `LambdaExpression<C,R>` | class | Wraps a `Function<C,R>` — `type() = "lambda"`; intentionally outside the registry flow (no `LambdaExpressionEngine` exists) |
| `ConfigManager` | interface | Config access for JQ `$config` injection |
| `SecretManager` | interface | Secret resolution for JQ `$secret` injection |

### Engines

| Engine | Type Key | Backend | Context Type | Notes |
|--------|----------|---------|-------------|-------|
| `JQExpressionEngine` | `"jq"` | jackson-jq 1.6 | `JsonNode` | Boolean and List compiled expression variants; `ConcurrentHashMap`-cached `JsonQuery` instances |
| `MvelExpressionEngine` | `"mvel"` | MVEL3 3.0.0-SNAPSHOT transpiler | `Map<String, Object>` | Lazy compilation via double-checked locking — first `eval()` triggers MVEL3 compilation with runtime type context; `validate()` only checks for blank expressions |

**Legacy:** `JQEvaluator @ApplicationScoped` — the "canonical Foundation-tier JQ evaluator" with `$secret` and `$config` scope injection via `SecretManager`/`ConfigManager`. Referenced by protocol `PP-20260522-jq-evaluation-canonical`.

`DefaultExpressionEngineRegistry @ApplicationScoped` discovers all `ExpressionEngine` beans at `@PostConstruct` and dispatches `compile()`/`validate()` by type key. The subscription engine uses this to compile filter expressions into `FilterExpression<T>` predicates for DataSource alpha network routing.

---

## Event Streams

Event stream connectors bridge external messaging systems into the platform. All five build `CloudEvent` instances, set the `tenancyid` extension, and fire via `Event<CloudEvent>.fireAsync()`. All resolve endpoint metadata from `EndpointRegistry` using `EndpointPropertyKeys` constants.

| Module | Artifact | Transport | Binding | Notes |
|--------|----------|-----------|---------|-------|
| `streams-kafka/` | `casehub-platform-streams-kafka` | Apache Kafka | Static `@Incoming("casehub-kafka-stream")` | Correlates configured topics with `EndpointDescriptor` at startup; does NOT observe `EndpointRegistered`; mutually exclusive with Camel for same topic |
| `streams-amqp/` | `casehub-platform-streams-amqp` | AMQP | Static `@Incoming("casehub-amqp-stream")` | One address per channel (SmallRye limitation); for multi-queue fan-in use streams-camel |
| `streams-webhook/` | `casehub-platform-streams-webhook` | Inbound HTTP | `POST /streams/webhook/{tenancyId}/{streamId}` | Structured CloudEvents (`application/cloudevents+json`) only; self-registers platform-global endpoint; requires `casehub.streams.webhook.public-url` |
| `streams-poll/` | `casehub-platform-streams-poll` | HTTP GET polling | `@Scheduled(every = "${casehub.streams.poll.interval:60s}")` | Discovers `HTTP` + `QUERY` endpoints; per-endpoint failure isolation; uses `java.net.http.HttpClient` |
| `streams-camel/` | `casehub-platform-streams-camel` | Apache Camel | Dynamic routes via `camelContext.addRoutes()` | The only connector that observes `@ObservesAsync EndpointRegistered` for runtime-dynamic route addition; idempotent via `routedUris` set; consumer app must add Camel component dependencies |

All stream connectors depend on `platform-api`, `platform`, and `endpoints-memory`.

---

## Notification and Subscription System

The notification and subscription system is a multi-module architecture spanning SPIs (in `platform-api/`), persistence backends, a subscription matching engine wired to the DataSource alpha network, a multi-path dispatch pipeline, and a REST+SSE presentation layer.

### Key Abstractions

| Type | Location | Purpose |
|------|----------|---------|
| `NotificationEvent` | `notification-api/` | Domain event with `severity`, `type` (`EventType`), `payload`, `timestamp`, `sourceId`, `actorId`, `tenancyId` |
| `EventType` | `notification-api/` | Value type — unique identifier (`EventTypeId`) + `canonicalName` + optional `displayName` |
| `EventTypeId` | `notification-api/` | Composite key: `namespace` + `name` (both non-blank, ≤200 chars) |
| `EventTypeRegistry` | `notification-api/spi/` | SPI for event type registration and lookup — `register(EventType)`, `find(EventTypeId)`, `all()`, `allInNamespace(String)` |
| `Channel` | `notification-api/` | Delivery target — has `name`, `enabledEventTypes`, `disabledEventTypes`, type (`CONNECTOR`, `SUBSCRIPTION`) |
| `ChannelPreference` | `notification-api/` | Per-user channel opt-in/opt-out settings — `userId`, `channelId`, `suppressionRules`, `digestSchedule` (nullable) |
| `ConnectorChannel` | `notification-api/` | Channel subtype for outbound connector delivery — carries `connectorId` + `destination` |
| `SubscriptionChannel` | `notification-api/` | Channel subtype for in-app subscription — subscribers receive notifications without external delivery |
| `DigestSchedule` | `notification-api/digest/` | When digests flush — `DAILY_AT(hour, minute, zone)`, `WEEKLY_AT(dayOfWeek, hour, minute, zone)` |
| `DigestBuffer` | `notification-api/spi/` | SPI for buffering notifications for digest aggregation — `buffer(DigestSummary)`, `flush(userId)` |
| `DigestSummary` | `notification-api/digest/` | Aggregate digest record — `userId`, `channelId`, `summaries` (per `groupBy` key), `timestamp` |
| `ChannelRouter` | `notification-api/spi/` | SPI for selecting which channels receive a notification — `route(NotificationEvent) → List<Channel>` |
| `SuppressionEvaluator` | `notification-dispatch/` | Evaluates user suppression rules and quiet-hours buffers |
| `NotificationDispatcher` | `notification-dispatch/` | Three-path delivery: digest buffer (external + schedule + non-URGENT), suppress (rules), or deliver (immediate) |
| `DigestFlushScheduler` | `notification-dispatch/` | `@Scheduled` digest flusher with per-key error isolation, suppression deferral, orphan drain |
| `EntityWatcherProvider` | `notification-dispatch/spi/` | SPI for discovering which users are watching which entities — `getWatchers(entityId) → Set<String>` |

**New in platform#144:** Notification digest buffering — timer-driven aggregation for external channels. Non-URGENT notifications with a digest schedule are buffered and flushed on the configured schedule. URGENT notifications always deliver immediately. V1 and V2 Flyway migrations for digest buffer storage.

**New in platform#155, #160:** `EventTypeRegistry` SPI — domain consumers register their event types programmatically; subscribers and channel filters reference them via `EventTypeId`. `WeeklyAt` digest schedule added alongside `DailyAt`.

**New in platform#156:** `EntityWatcherProvider` SPI + `ENTITY_WATCHERS` target type — channels can use entity-based subscriber routing (e.g. "notify all watchers of issue #123") without requiring explicit subscriptions.

**New in platform#157, #159, #161, #162, #163:** Digest groupBy, quiet hours buffering, digest status endpoint, additional schedule types, MethodHandles performance optimization.

### Data Flow

1. Domain modules produce `SubscribableEvent` objects and insert them into the notification DataSource (registered at path `casehub/platform/notifications`)
2. `SubscriptionEngine` (in `subscriptions/`) evaluates wired subscriptions against the alpha network, fires `SubscriptionMatched` CDI event
3. `NotificationDispatcher` (in `notification-dispatch/`) observes `SubscriptionMatched`, resolves targets, applies template, checks suppression, routes to channels
4. `NotificationStore` (in `notifications-inmem/` or `notifications-jpa/`) persists the notification record, fires `NotificationCreated`
5. `NotificationResource` and `NotificationSseResource` (in `notifications/`) expose stored notifications via REST and push real-time updates via SSE
6. `DeliveryChannelRegistry` (in `delivery-channel-inmem/`) maps channels to `NotificationDeliverer` implementations
7. Delivery attempts tracked by `DeliveryAttemptStore`; digests buffered by `DigestBuffer`; preferences/suppression by `NotificationPreferenceStore`/`SuppressionStore`

### Modules

| Module | Artifact | CDI | Purpose |
|--------|----------|-----|---------|
| `notifications/` | `casehub-platform-notifications` | `@ApplicationScoped` | REST + SSE presentation layer — `NotificationResource` (list, mark-read, dismiss, unread-count), `NotificationSseResource` (push via SSE with stale emitter sweep), `NotificationPreferenceResource`, `SuppressionResource`, `DeliveryChannelResource`, `DigestStatusResource` |
| `notifications-inmem/` | `casehub-platform-notifications-inmem` | `@Alternative @Priority(100)` | In-memory `NotificationStore` + `ReactiveNotificationStore` — bounded size eviction; Base64 cursor pagination; fires CDI events |
| `notifications-jpa/` | `casehub-platform-notifications-jpa` | `@ApplicationScoped` | JPA `NotificationStore` + `ReactiveNotificationStore` (Hibernate Reactive Panache) — keyset cursor pagination; `NotificationRetentionScheduler` (purge READ/DISMISSED >90d, UNREAD >365d); Flyway at `classpath:db/notification/migration` |
| `notification-dispatch/` | `casehub-platform-notification-dispatch` | `@ApplicationScoped` | Three-path delivery: digest buffer (external + schedule + non-URGENT), suppress (rules), or deliver (immediate). `NotificationDispatcher`, `DigestFlushScheduler`, `SuppressionEvaluator` |
| `notification-settings-inmem/` | `casehub-platform-notification-settings-inmem` | `@Alternative @Priority(100)` | In-memory `NotificationPreferenceStore` + `SuppressionStore` — channel preferences, quiet hours, mute rules (with lazy expiry), snooze state |
| `notification-settings-jpa/` | `casehub-platform-notification-settings-jpa` | `@ApplicationScoped` | JPA `NotificationPreferenceStore` + `SuppressionStore` (blocking ORM Panache) — channel defaults and quiet hours as JSON TEXT columns; `SuppressionRetentionScheduler` (daily 02:00 purge of expired mutes/snooze); Flyway at `classpath:db/notification-settings/migration` |
| `delivery-channel-inmem/` | `casehub-platform-delivery-channel-inmem` | `@ApplicationScoped` | **Production implementation** (not a test double) — `DeliveryChannelRegistry` mapping channelId to `(DeliveryChannelDescriptor, NotificationDeliverer)` pairs; channels are static, not dynamic; no JPA variant needed |
| `delivery-tracking-inmem/` | `casehub-platform-delivery-tracking-inmem` | `@Alternative @Priority(100)` | In-memory `DeliveryAttemptStore` — bounded size; synchronized `claimRetryable` |
| `delivery-tracking-jpa/` | `casehub-platform-delivery-tracking-jpa` | `@ApplicationScoped` | JPA `DeliveryAttemptStore` — `claimRetryable` uses `PESSIMISTIC_WRITE` with `SKIP LOCKED` for concurrent-safe batch claim; built-in retention purge; Flyway at `classpath:db/delivery-tracking/migration` |
| `digest-inmem/` | `casehub-platform-digest-inmem` | `@Alternative @Priority(100)` | In-memory `DigestBuffer` — bounded size; retention-based expiry; secondary user index |
| `digest-jpa/` | `casehub-platform-digest-jpa` | `@ApplicationScoped` | JPA `DigestBuffer` — drain via SELECT+DELETE in transaction; Flyway at `classpath:db/digest/migration` |
| `subscriptions/` | `casehub-platform-subscriptions` | `@ApplicationScoped` | Subscription matching engine + REST — `SubscriptionEngine` wires DataSource alpha network with filter expression compilation (JQ/MVEL via `ExpressionEngineRegistry`); `EventTypeObjectType` supports exact match and prefix glob; hot-wire/rewire/unwire via CDI event observers; REST CRUD at `/subscriptions` |
| `subscriptions-inmem/` | `casehub-platform-subscriptions-inmem` | `@Alternative @Priority(100)` | In-memory `SubscriptionStore` + `ReactiveSubscriptionStore` — scope-aware (USER enforces ownerId, SYSTEM is tenant-only); fires CDI events |
| `subscriptions-jpa/` | `casehub-platform-subscriptions-jpa` | `@ApplicationScoped` | JPA `SubscriptionStore` + `ReactiveSubscriptionStore` (Hibernate Reactive Panache) — OR-disjunction scope queries; filters/targets/template stored as JSON TEXT; Flyway at `classpath:db/subscription/migration` |

---

## Mock Implementation Pattern

The original three SPIs (`PreferenceProvider`, `CurrentPrincipal`, `GroupMembershipProvider`) get `@DefaultBean @ApplicationScoped` configurable mocks in `platform/`. `CaseMemoryStore` follows the same structural pattern but uses a silent no-op rather than a configurable mock — see the CaseMemoryStore section above for the rationale. The shared pattern for all four:

- `@DefaultBean` — yields to any `@ApplicationScoped` implementation; no exclusion config needed in consumers
- `@ApplicationScoped` (not `@RequestScoped`) — no request context in dev/test mode
- `@ConfigProperty` with `Optional<T>` — SmallRye Config throws `NoSuchElementException` for absent Map/List prefixes; `Optional` absorbs cleanly
- No hardcoded business values — real defaults live in harness YAML files; `key.defaultValue()` is a null guard

**`persistence-memory/` is not created for preferences.** The `persistence-memory/` module pattern (from `casehub-work`) is warranted only when in-memory has a production use case (e.g., ephemeral installs without a database). Preferences have a file-based production alternative (`config/` module), so in-memory is genuinely test-only and belongs in `testing/`. Not every `@Alternative` implementation needs its own persistence module.

---

## Testing Module

`casehub-platform-testing` provides `@Alternative @Priority(1)` test fixtures for identity SPIs:

- `FixedCurrentPrincipal` — programmatic actorId/groups/tenancyId/crossTenantAdmin control with `reset()` support
- `InMemoryGroupMembershipProvider` — in-memory group membership store

**No `InMemoryPreferenceProvider`.** Because `PreferenceKey<T>` carries a `parser`, `MockPreferenceProvider.get(key)` calls `key.parse(raw)` on config strings — typed values come from `application.properties` without a separate test fixture. This is why the testing module has identity fixtures but not preference fixtures.

Add as a test-scoped dependency:

```xml
<dependency>
    <groupId>io.casehub</groupId>
    <artifactId>casehub-platform-testing</artifactId>
    <scope>test</scope>
</dependency>
```

---

## Anti-Patterns

**Do not define parallel path, scope, preference, or principal types.** `casehub-platform-api` owns these. If an existing type does not quite fit, extend it or open an issue — do not create a new one.

**Do not use `@ConfigMapping` for case-type business rules.** `@ConfigMapping` is for deployment configuration that is the same for every case. Per-case-type business rules are `PreferenceProvider` territory.

**Do not call `SecurityIdentity` from `platform-api/`.** Zero dependencies means zero Quarkus imports. `CurrentPrincipal` is the abstraction that keeps `platform-api/` clean.

**Do not make `CurrentPrincipal` `@ApplicationScoped` in a real deployment.** The mock is `@ApplicationScoped` for a reason (no request context in dev). Real implementations must be `@RequestScoped`.

**Do not inject `Principal` directly in Quarkus.** Quarkus's `Principal` injection is unreliable in tests and some filter-order contexts. Use `SecurityIdentity` or `CurrentPrincipal` — both are well-defined.

---

## Module Roadmap

| Module | Status | Purpose |
|--------|--------|---------|
| `platform-api/` | ✅ shipped | Zero-dep SPIs: `Path`, `PreferenceProvider`, `CurrentPrincipal`, `GroupMembershipProvider`, `CaseMemoryStore`, `DataSource`, `AccessControlProvider`, `CredentialResolver`, `ExpressionEngine`, `SubscriptionStore`, `NotificationStore`, `DeliveryAttemptStore`, `DigestBuffer`, `NamedStrategy`, `StrategyResolver`, `ActorStateContributor`, `ExecutionPolicy` + value types |
| `platform/` | ✅ shipped | `@DefaultBean` mocks (configurable) and no-ops (silent); `ReactiveCaseMemoryStore` SPI; `BlockingToReactiveBridge @DefaultBean` |
| `testing/` | ✅ shipped | `@Alternative @Priority(1)` identity fixtures |
| `config/` | ✅ shipped | Scope-aware YAML + SmallRye Config overrides — displaces mock when on classpath |
| `oidc/` | ✅ shipped | `@RequestScoped CurrentPrincipal` backed by `SecurityIdentity` + JWT — displaces mock when on classpath |
| `expression/` | ✅ shipped | JQ + MVEL3 expression evaluation — `ExpressionEngineRegistry` dispatches by type; used by casehub-engine, casehub-work-queues, and subscription filter compilation |
| `persistence-jpa/` | ✅ shipped (#6) | JPA-backed scoped preference overrides — Flyway, @ApplicationScoped, scope-aware hierarchy |
| `persistence-mongodb/` | ✅ shipped (#7) | MongoDB alternative for preferences — @Alternative @Priority(1), beats JPA when co-deployed, no Flyway |
| `datasource-alpha/` | ✅ shipped | Rete-style alpha network — `AlphaDataSource` with type nodes, filter nodes, fan-out delivery, self-pruning deregistration lifecycle |
| `datasource-inmem/` | ✅ shipped | `@Alternative @Priority(100)` in-memory `DataSourceRegistry` — dual ConcurrentHashMap stores; Tier 4; test or ephemeral installs |
| `datasource-jpa/` | ✅ shipped | `@ApplicationScoped` JPA `DataSourceRegistry` — startup reconciliation; `@Transactional` register/deregister/update; `datasource_descriptor` table |
| `identity/` | ✅ shipped | DID infrastructure — `CompositeDIDResolver` (`did:key` with secp256k1, `did:web` with SSRF protection, SCIM resolver), `CompositeActorDIDProvider` (config + SCIM sources), `JwtVCValidator`, `AgentIdentityVerificationService`; TTL caching via `AbstractCachingIdentityProvider` |
| `acl-inmem/` | ✅ shipped | `@Alternative @Priority(10)` in-memory `AccessControlProvider` — ConcurrentHashMap with group-based grants and parent-child hierarchy (depth guard 20) |
| `acl-jpa/` | ✅ shipped | `@ApplicationScoped` JPA `AccessControlProvider` — Hibernate Reactive + Panache; audit logging (`acl_audit_log` table); `AclEntryEntity`, `AclAuditLogEntity`, `ResourceParentEntity` |
| `governance/` | ✅ shipped | `DefaultPolicyEnforcer @ApplicationScoped` — retry + timeout + backoff (FIXED/EXPONENTIAL/JITTER) using virtual thread executor |
| `credentials-quarkus/` | ✅ shipped | `@Alternative @Priority(1)` bridge from `CredentialResolver` to Quarkus `CredentialsProvider` — validates exactly one provider at `@PostConstruct` |
| `scim/` | ✅ shipped (#45) | SCIM 2.0 GroupMembershipProvider — @ApplicationScoped, displaces mock by classpath presence |
| `memory-inmem/` | ⛔ removed from build | Migrated to casehub-neocortex (neocortex#56). Directory remains on disk. |
| `memory-jpa/` | ⛔ removed from build | Migrated to casehub-neocortex. Directory remains on disk. |
| `memory-sqlite/` | ⛔ removed from build | Migrated to casehub-neocortex. Directory remains on disk. |
| `memory-mem0/` | ⛔ removed from build | Migrated to casehub-neocortex. Directory remains on disk. |
| `memory-graphiti/` | ⛔ removed from build | Migrated to casehub-neocortex. Directory remains on disk. |
| `agent-api/` | ✅ shipped (#55, #58) | AgentProvider SPI — `run(AgentSessionConfig) → Multi<AgentEvent>`; Mutiny only, no Quarkus; package: `io.casehub.platform.agent`. **Multi-turn (#58):** `AgentSession` interface — serial `query()`/`interrupt()`/`close(Duration)`; `AgentProvider.openSession(AgentSessionInit)` factory. `AgentSessionInit` carries systemPrompt, mcpServers, timeout, correlationId (no userPrompt — prompts passed per-turn to `query()`). `NoOpAgentSession` in `platform/` returned by `NoOpAgentProvider.openSession()`. |
| `agent-claude/` | ✅ shipped (#55, #58, eidos#52) | `ClaudeAgentProvider @ApplicationScoped` + `ClaudeAgentClient @Startup` — activates by classpath presence; requires Claude CLI; concurrent-session semaphore (configurable); wall-clock timeout; three exception types: `AgentProcessException`, `AgentSessionLimitException`, `AgentTimeoutException`. **Two subprocess paths:** `invoke()` → `ClaudeOneShotProcess` (direct `ProcessBuilder`, immediate `destroyForcibly()` — fixes zombie subprocess accumulation when parallel `invoke()` calls all timeout, eidos#52); `openSession()` → `ClaudeAgentSession` (SDK session mode). **Multi-turn (#58):** IDLE/ACTIVE/CLOSED state machine; per-turn wall-clock timeout; true-drain `close(Duration)`; `interrupt()` fire-and-forget (TOCTOU-guarded); semaphore held for session lifetime. `ClaudeAgentClient` CDI constructor requires `ObjectMapper` alongside `ClaudeAgentProperties`. |
| `agent-langchain4j/` | ✅ shipped (#100, renamed #105) | Bidirectional LangChain4j interop — `ChatModelAgentProvider` (any ChatModel → AgentProvider) + `AgentProviderChatModel` (any AgentProvider → ChatModel). No longer Claude-specific. `@Alternative @Priority(10) @ApplicationScoped`. **Incompatible with `engine.Agent`** which forces `ResponseFormatType.JSON`. `casehub.platform.agent.langchain4j.closeTimeout` (default PT30S). No quarkus:build goal. |
| `endpoints-memory/` | ✅ shipped (#73) | `InMemoryEndpointRegistry @Alternative @Priority(100)` — volatile ConcurrentHashMap `EndpointRegistry`; ephemeral (data lost on restart); Tier 4 CDI (beats future JPA and NoSQL adapters); add test scope for isolation, compile scope for ephemeral installs |
| `endpoints-config/` | ✅ shipped (#88) | YAML-backed endpoint populator — `@Startup @ApplicationScoped`; reads `casehub.platform.endpoints.files`; `${VAR}` interpolation (system property → env var → startup failure if unresolved); multi-file support; path separator read via `@ConfigProperty` directly (no `PathParserConfigurator` cross-bean dependency); populator not registry |
| `notifications/` | ✅ shipped | REST + SSE presentation layer — list, mark-read, dismiss, unread-count, real-time push via SSE |
| `notifications-inmem/` | ✅ shipped | `@Alternative @Priority(100)` in-memory `NotificationStore` — bounded size eviction, cursor pagination, CDI events |
| `notifications-jpa/` | ✅ shipped | `@ApplicationScoped` JPA `NotificationStore` (Hibernate Reactive Panache) — keyset cursor pagination, retention scheduler, Flyway |
| `notification-dispatch/` | ✅ shipped | Three-path delivery: digest buffer, suppress, or deliver immediately. `NotificationDispatcher`, `DigestFlushScheduler`, `SuppressionEvaluator` |
| `notification-settings-inmem/` | ✅ shipped | `@Alternative @Priority(100)` in-memory preference/suppression store — channel preferences, quiet hours, mute rules, snooze |
| `notification-settings-jpa/` | ✅ shipped | `@ApplicationScoped` JPA preference/suppression store — JSON TEXT columns, retention scheduler, Flyway |
| `delivery-channel-inmem/` | ✅ shipped | `@ApplicationScoped` channel-to-deliverer registry — **production implementation** (channels are static, no JPA variant needed) |
| `delivery-tracking-inmem/` | ✅ shipped | `@Alternative @Priority(100)` in-memory `DeliveryAttemptStore` — bounded size, synchronized claim |
| `delivery-tracking-jpa/` | ✅ shipped | `@ApplicationScoped` JPA `DeliveryAttemptStore` — `PESSIMISTIC_WRITE` with `SKIP LOCKED` for concurrent-safe batch claim; retention purge; Flyway |
| `digest-inmem/` | ✅ shipped | `@Alternative @Priority(100)` in-memory `DigestBuffer` — bounded size, retention-based expiry, secondary user index |
| `digest-jpa/` | ✅ shipped | `@ApplicationScoped` JPA `DigestBuffer` — drain via SELECT+DELETE in transaction; Flyway |
| `subscriptions/` | ✅ shipped | Subscription matching engine + REST — `SubscriptionEngine` wires DataSource alpha network; `EventTypeObjectType` for exact match and prefix glob; expression compilation via `ExpressionEngineRegistry` |
| `subscriptions-inmem/` | ✅ shipped | `@Alternative @Priority(100)` in-memory `SubscriptionStore` — scope-aware, CDI events |
| `subscriptions-jpa/` | ✅ shipped | `@ApplicationScoped` JPA `SubscriptionStore` (Hibernate Reactive Panache) — OR-disjunction scope queries, JSON TEXT columns, Flyway |
| `streams-kafka/` | ✅ shipped | Kafka event stream connector — static `@Incoming` binding; correlates topics with `EndpointDescriptor` at startup |
| `streams-amqp/` | ✅ shipped | AMQP event stream connector — static `@Incoming` binding; one address per channel |
| `streams-webhook/` | ✅ shipped | Webhook event stream connector — `POST /streams/webhook/{tenancyId}/{streamId}`; structured CloudEvents only |
| `streams-poll/` | ✅ shipped | Polling event stream connector — `@Scheduled` HTTP GET; per-endpoint failure isolation |
| `streams-camel/` | ✅ shipped | Apache Camel event stream connector — the only connector with runtime-dynamic route addition via `@ObservesAsync EndpointRegistered` |
| `preferences-editor/` | 🔜 #8 | Admin write path for preferences — REST API, separate from providers |

`PreferenceProvider` is permanently read-only. The editor module writes directly to the backend; providers never own the write path.

---

## See Also

- `casehub/garden: docs/protocols/casehub/typed-preference-keys.md` — `PreferenceKey<T>` contract
- `casehub/garden: docs/protocols/casehub/platform-spi-contract.md` — implementation rules for all three SPIs
- `casehub/garden: docs/protocols/universal/module-tier-structure.md` — Tier 1/2/3 rules and `persistence-memory/` decision guide
- ADRs in `casehubio/platform`: 0001 (Path API), 0002 (PreferenceKey contract), 0003 (null-returning get)
