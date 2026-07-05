# casehub-platform — SPI Layer Rationale and Quarkus Integration

**Repo:** `casehubio/platform`
**Tier:** Foundation (first in build order, zero casehubio dependencies)
**Purpose:** Zero-dependency SPIs and types shared across all casehub modules.

This document answers the question developers will always ask: *"Why does casehub define its own identity, preferences, and path types when Quarkus already has those things?"* The short answer is that casehub-platform is not a parallel system — it is a thin, zero-dependency domain layer that Quarkus-specific code implements. The long answer is below.

---

## The Three-Layer Model

```
platform-api/   ← Tier 1: zero dependencies — pure Java interfaces and records
platform/       ← Tier 3: Quarkus @DefaultBean mocks, @ConfigProperty
testing/        ← companion: @Alternative @Priority(1) test fixtures (CDI API only)
config/         ← optional: scope-aware YAML + SmallRye Config preference provider
oidc/           ← optional: @RequestScoped CurrentPrincipal backed by SecurityIdentity + JWT
memory-inmem/   ← LEGACY STUB — memory backends migrated to casehub-neocortex (neocortex#56); pending removal
memory-jpa/     ← LEGACY STUB — see above
memory-sqlite/  ← LEGACY STUB — see above
memory-mem0/    ← LEGACY STUB — see above
memory-graphiti/ ← LEGACY STUB — see above
agent-api/      ← optional: AgentProvider SPI (Mutiny only, no Quarkus) — package: io.casehub.platform.agent
agent-claude/   ← optional: ClaudeAgentProvider @ApplicationScoped + ClaudeAgentClient @Startup — activates by classpath presence; requires Claude CLI; concurrent-session semaphore. Two subprocess paths: invoke() → ClaudeOneShotProcess (direct ProcessBuilder, immediate destroyForcibly() on cancellation — fixes zombie subprocess accumulation, eidos#52); openSession(AgentSessionInit) → ClaudeAgentSession (SDK session mode, IDLE/ACTIVE/CLOSED state machine, per-turn wall-clock timeout, true-drain close(), interrupt() fire-and-forget, semaphore held for session lifetime). ClaudeAgentClient CDI constructor requires ObjectMapper alongside ClaudeAgentProperties.
endpoints-memory/ ← optional: @Alternative @Priority(100) InMemoryEndpointRegistry — volatile tenant-scoped endpoint registry; CDI Tier 4; data lost on restart
endpoints-config/ ← optional: @Startup @ApplicationScoped YAML-backed endpoint populator — reads casehub.platform.endpoints.files; calls EndpointRegistry.register(); populator not registry; path separator read directly from @ConfigProperty (no PathParserConfigurator dependency)
```

`platform-api/` must never import Quarkus, CDI, JPA, or any casehubio artifact. This constraint is what makes the SPIs useful to every module in the stack — including modules that have no Quarkus dependency of their own.

**Package structure in `platform-api/`:** `identity` (`CurrentPrincipal`, `GroupMembershipProvider`, `GroupMember`, `ActorType`, `ActorTypeResolver`), `preferences` (`PreferenceProvider`, `PreferenceKey`, `Preferences`, `SettingsScope`), `path` (`Path`), `endpoints` (`EndpointRegistry`, `EndpointDescriptor`, `EndpointPermissions` (static: `assertTenant(tenancyId, principal)` — write-auth for runtime registration), `EndpointType`, `EndpointProtocol`, `EndpointCapability`, `EndpointQuery`, `EndpointPropertyKeys`), `memory` (`CaseMemoryStore`, `GraphCaseMemoryStore` (graph-native SPI extension — adds `graphQuery(GraphMemoryQuery)` for temporal queries), `MemoryCapability` (self-description enum — adapters declare `capabilities()`; callers use `requireCapability()` for typed exceptions), `MemoryInput`, `Memory`, `MemoryQuery`, `GraphMemoryQuery`, `EraseRequest`, `MemoryDomain`, `MemoryPermissions`). `ReactiveCaseMemoryStore` lives in `platform/`, not `platform-api/` — Mutiny is a Quarkus dep and would violate the zero-dep constraint.

`config/` and `oidc/` are optional — consumers add them as compile-scope dependencies to activate the capability. Each displaces its corresponding `@DefaultBean` mock automatically via CDI without exclusion config.

---

## Path

**Problem:** casehub needs a hierarchical, scope-labelling type — for case types
(`casehubio/devtown/pr-review`), preference scopes, and label paths. It must be
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

**Adapter implementations (submodules in this repo — add as dependency to activate):**

| Module | Artifact | CDI priority | Backend | Scope | Best for |
|--------|----------|-------------|---------|-------|----------|
| `memory-inmem/` | `casehub-platform-memory-inmem` | @Alternative @Priority(1) | ConcurrentHashMap — volatile | test or compile | Test isolation per @QuarkusTest; ephemeral installs without a database |
| `memory-jpa/` | `casehub-platform-memory-jpa` | @ApplicationScoped | PostgreSQL + Flyway V1000 | compile | Default persistence; FTS via `websearch_to_tsquery` when `MemoryQuery.question` is set |
| `memory-sqlite/` | `casehub-platform-memory-sqlite` | @Alternative @Priority(1) | SQLite + HikariCP WAL + FTS5 | compile | Durable single-process deployments. Configure `casehub.memory.sqlite.path` |
| `memory-mem0/` | `casehub-platform-memory-mem0` | @Alternative @Priority(1) | Mem0 REST API + pgvector | compile | Vector embedding + semantic search. Configure `casehub.memory.mem0.api-key`, `quarkus.rest-client.mem0.url`. `infer=false` preserves 1:1 `store()`/memoryId contract. Do NOT combine with memory-inmem or memory-sqlite. |
| `memory-graphiti/` | `casehub-platform-memory-graphiti` | @Alternative @Priority(2) | Graphiti REST API | compile | Temporal knowledge graph with LLM entity extraction (async). Extends `GraphCaseMemoryStore` SPI — adds `graphQuery(GraphMemoryQuery)` for temporal queries. Configure `quarkus.rest-client.graphiti.url`, `casehub.memory.graphiti.api-key`. Backend: Neo4j, FalkorDB, or Kuzu. |

All adapters displace `NoOpCaseMemoryStore @DefaultBean` automatically by classpath presence. Do not combine adapters in the same scope — `@Priority(1)` wins and lower-priority stores are bypassed.

Consumers must add `classpath:db/memory/migration` to `quarkus.flyway.locations` when using `memory-jpa/`. `memory-sqlite/` uses programmatic Flyway at `classpath:db/memory-sqlite/migration` — no `quarkus.flyway.locations` entry needed.

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
| `platform-api/` | ✅ shipped | Zero-dep SPIs: `Path`, `PreferenceProvider`, `CurrentPrincipal`, `GroupMembershipProvider`, `CaseMemoryStore` + value types |
| `platform/` | ✅ shipped | `@DefaultBean` mocks (configurable) and no-ops (silent); `ReactiveCaseMemoryStore` SPI; `BlockingToReactiveBridge @DefaultBean` |
| `testing/` | ✅ shipped | `@Alternative @Priority(1)` identity fixtures |
| `config/` | ✅ shipped | Scope-aware YAML + SmallRye Config overrides — displaces mock when on classpath |
| `oidc/` | ✅ shipped | `@RequestScoped CurrentPrincipal` backed by `SecurityIdentity` + JWT — displaces mock when on classpath |
| `expression/` | ✅ shipped | JQ expression evaluation (`JQEvaluator`) — used by casehub-engine and casehub-work-queues |
| `persistence-jpa/` | ✅ shipped (#6) | JPA-backed scoped preference overrides — Flyway, @ApplicationScoped, scope-aware hierarchy |
| `persistence-mongodb/` | ✅ shipped (#7) | MongoDB alternative for preferences — @Alternative @Priority(1), beats JPA when co-deployed, no Flyway |
| `memory-inmem/` | ✅ shipped (#32) | Volatile CaseMemoryStore — ConcurrentHashMap, @Alternative @Priority(1). Test-scope for isolation; compile for ephemeral installs |
| `memory-jpa/` | ✅ shipped (#32) | JPA CaseMemoryStore — PostgreSQL, Flyway V1000 at `classpath:db/memory/migration`, FTS via websearch_to_tsquery |
| `memory-sqlite/` | ✅ shipped (#37) | SQLite CaseMemoryStore — xerial JDBC + HikariCP WAL + FTS5, programmatic Flyway at `classpath:db/memory-sqlite/migration`. @Alternative @Priority(1). Configure `casehub.memory.sqlite.path` |
| `scim/` | ✅ shipped (#45) | SCIM 2.0 GroupMembershipProvider — @ApplicationScoped, displaces mock by classpath presence |
| `memory-mem0/` | ✅ shipped (#33) | Mem0 REST CaseMemoryStore — @Alternative @Priority(1); vector embeddings via Mem0 OSS (Docker + pgvector); infer:false; compound user_id for tenant isolation; RELEVANCE via POST /search with top_k + threshold |
| `memory-graphiti/` | ✅ shipped (#34) | `@Alternative @Priority(2)` Graphiti REST `GraphCaseMemoryStore` — temporal knowledge graph (Neo4j/FalkorDB/Kuzu); LLM entity extraction (async); `graphQuery(GraphMemoryQuery)` for temporal queries; extends `CaseMemoryStore` with graph-native SPI |
| `agent-api/` | ✅ shipped (#55, #58) | AgentProvider SPI — `run(AgentSessionConfig) → Multi<AgentEvent>`; Mutiny only, no Quarkus; package: `io.casehub.platform.agent`. **Multi-turn (#58):** `AgentSession` interface — serial `query()`/`interrupt()`/`close(Duration)`; `AgentProvider.openSession(AgentSessionInit)` factory. `AgentSessionInit` carries systemPrompt, mcpServers, timeout, correlationId (no userPrompt — prompts passed per-turn to `query()`). `NoOpAgentSession` in `platform/` returned by `NoOpAgentProvider.openSession()`. |
| `agent-claude/` | ✅ shipped (#55, #58, eidos#52) | `ClaudeAgentProvider @ApplicationScoped` + `ClaudeAgentClient @Startup` — activates by classpath presence; requires Claude CLI; concurrent-session semaphore (configurable); wall-clock timeout; three exception types: `AgentProcessException`, `AgentSessionLimitException`, `AgentTimeoutException`. **Two subprocess paths:** `invoke()` → `ClaudeOneShotProcess` (direct `ProcessBuilder`, immediate `destroyForcibly()` — fixes zombie subprocess accumulation when parallel `invoke()` calls all timeout, eidos#52); `openSession()` → `ClaudeAgentSession` (SDK session mode). **Multi-turn (#58):** IDLE/ACTIVE/CLOSED state machine; per-turn wall-clock timeout; true-drain `close(Duration)`; `interrupt()` fire-and-forget (TOCTOU-guarded); semaphore held for session lifetime. `ClaudeAgentClient` CDI constructor requires `ObjectMapper` alongside `ClaudeAgentProperties`. |
| `agent-langchain4j/` | ✅ shipped (#100, renamed #105) | Bidirectional LangChain4j interop — `ChatModelAgentProvider` (any ChatModel → AgentProvider) + `AgentProviderChatModel` (any AgentProvider → ChatModel). No longer Claude-specific. `@Alternative @Priority(10) @ApplicationScoped`. **Incompatible with `engine.Agent`** which forces `ResponseFormatType.JSON`. `casehub.platform.agent.langchain4j.closeTimeout` (default PT30S). No quarkus:build goal. |
| `endpoints-memory/` | ✅ shipped (#73) | `InMemoryEndpointRegistry @Alternative @Priority(100)` — volatile ConcurrentHashMap `EndpointRegistry`; ephemeral (data lost on restart); Tier 4 CDI (beats future JPA and NoSQL adapters); add test scope for isolation, compile scope for ephemeral installs |
| `endpoints-config/` | ✅ shipped (#88) | YAML-backed endpoint populator — `@Startup @ApplicationScoped`; reads `casehub.platform.endpoints.files`; `${VAR}` interpolation (system property → env var → startup failure if unresolved); multi-file support; path separator read via `@ConfigProperty` directly (no `PathParserConfigurator` cross-bean dependency); populator not registry |
| `preferences-editor/` | 🔜 #8 | Admin write path for preferences — REST API, separate from providers |

`PreferenceProvider` is permanently read-only. The editor module writes directly to the backend; providers never own the write path.

---

## See Also

- `casehub/garden: docs/protocols/casehub/typed-preference-keys.md` — `PreferenceKey<T>` contract
- `casehub/garden: docs/protocols/casehub/platform-spi-contract.md` — implementation rules for all three SPIs
- `casehub/garden: docs/protocols/universal/module-tier-structure.md` — Tier 1/2/3 rules and `persistence-memory/` decision guide
- ADRs in `casehubio/platform`: 0001 (Path API), 0002 (PreferenceKey contract), 0003 (null-returning get)
