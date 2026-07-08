# Boundary Rules

> **Scope:** All cross-repo "do not" rules — what must NOT be placed where
> **Audience:** All

**Any casehub repo may depend on `casehub-platform-api`.** It is a zero-external-dependency pure-Java module — taking a compile dependency on it does not force Quarkus, JPA, or any framework onto consumers. Foundation repos (`casehub-work-api`, `casehub-ledger-api`, etc.) may use `Path`, `Preferences`, `CurrentPrincipal` and other platform types in their own SPI signatures.

**Do not define parallel path, scope, preference, or principal types.** `casehub-platform-api` owns `Path`, `SettingsScope`, `PreferenceKey`, `Preferences`, `PreferenceProvider`, `CurrentPrincipal`, and `GroupMembershipProvider`. Repos that need these concepts must depend on `casehub-platform-api` and implement its SPIs — they must not define their own equivalent types.

**Do not add orchestration logic to `casehub-work`.** When a WorkItem completes, casehub-work fires a CDI event and stops. Homogeneous M-of-N group completion is casehub-work. Heterogeneous plan-level completion is casehub-engine. "Mark the WorkItem EXPIRED when its deadline passes" is casehub-work.

**Do not add WorkItem inbox management to `casehub-engine`.** casehub-engine depends on `casehub-work-core` (`WorkBroker`) only. WorkItem entities, Flyway migrations, REST endpoints must not flow into the engine.

**Do not add trust scoring to `casehub-work` or `casehub-engine`.** Trust lives in casehub-ledger and is surfaced via CDI routing events (`TrustScoreRoutingPublisher`). Consumers observe those events — they never compute trust themselves.

**Do not duplicate notification infrastructure.** `casehub-connectors` owns Slack/Teams/SMS/email. `casehub-work-notifications` must delegate here.

**Do not implement Qhorus channel semantics in `claudony`.** Claudony embeds Qhorus and adds SPI implementations. It must not re-implement channel, message, or commitment logic. Implementing `ChannelBackend` or `MessageObserver` SPIs from `casehub-qhorus-api` is not re-implementation — it is correct SPI usage.

**Do not call `QhorusMcpTools` or `ReactiveQhorusMcpTools` from consumer service code.** Those classes are the MCP tool dispatch layer for external callers (Claude Code); they carry `@WrapBusinessError` exception semantics that internal consumers must not be exposed to. Consumer service code has three correct integration points: (1) **Dashboard/UI consumers** needing composed views (channel with message count, instance with capability tags, timeline entries) — inject `QhorusDashboardService`. (2) **Service-layer integrations** that need to send messages — call `MessageService.dispatch(MessageDispatch)` (blocking) or `ReactiveMessageService.dispatch(MessageDispatch) → Uni<DispatchResult>` (reactive). These are the enforcement gates: paused check, ACL, rate limiting, LAST_WRITE semantics, ledger write, and fan-out all happen inside `dispatch()`. Do not bypass to entity stores for write operations. (3) **Reactive event-driven integrations** — implement `ChannelBackend` or `MessageObserver` SPI. Note: injecting entity services directly is also wrong for dashboard consumers — `ReactiveChannelService.listAll()` returns entities without message counts, requiring store-layer injection and creating worse coupling. See `../garden/docs/protocols/casehub/qhorus-consumer-integration-pattern.md`.

**Choose `ChannelBackend` vs `MessageObserver` based on scope.** `ChannelBackend` is per-channel and knows its context — use it when a consumer needs to act on messages from a specific channel (e.g. Claudony panel display). `MessageObserver` is a global broadcast across all channels — use it for cross-cutting concerns (e.g. clinical PI response monitoring). For topology guidance (LOCAL CDI vs CLUSTER-scoped transport) see [`docs/repos/casehub-qhorus.md`](../repos/casehub-qhorus.md) and [qhorus `docs/messaging-architecture.md`](https://github.com/casehubio/qhorus/blob/main/docs/messaging-architecture.md).

**Do not put CaseHub SPI implementations in `casehub-engine`.** casehub-engine defines them; deployment-specific implementations belong in the deploying application.

**Do not use `casehub-work` runtime in `casehub-engine`.** The engine depends on `casehub-work-core` only.

**Use `CaseSignalSink` (in `casehub-work-api`) as the only path for external events that must unblock a waiting case.** casehub-work injects and calls `CaseSignalSink` at SLA escalation time; the implementation in `casehub-engine-work-adapter` translates to `CaseHubRuntime.signal()`. Qhorus message signals route via `QhorusMessageSignalBridge` in engine runtime. Do not add case-signaling logic to any other module.

**Do not add domain logic to foundation repos.** If the capability requires knowledge of software development, clinical trials, or financial crime, it belongs in an application repo.

**Do not implement CBR retrieval logic in application repos.** Case similarity matching belongs in `casehub-neocortex` via the `CaseRetriever` SPI. Application repos provide domain-specific feature vectors (what fields describe a case) and similarity thresholds; the retrieval mechanism itself must not be re-implemented per domain. See [`docs/CBR-CAPABILITY.md`](../CBR-CAPABILITY.md).

**Do not implement implementation-selection trust routing in application repos.** When multiple `TaskDefinition` implementations compete for the same capability, routing between them is a `casehub-engine` concern (`ImplementationRoutingStrategy` — gap, to be filed). Application-layer workarounds (`canActivate()` gating via a selector bean) are temporary and must migrate to the engine SPI once it exists. See [`docs/CBR-CAPABILITY.md`](../CBR-CAPABILITY.md) §Reuse.

**Do not re-implement CapabilityHealth probe semantics in casehub-engine.** Engine calls `CapabilityHealth.probe()` via the `casehub-eidos-api` SPI contract from `WorkOrchestrator`. Engine provides a `NoOpCapabilityHealth @DefaultBean` for deployments without eidos — that is the full extent of engine's responsibility. Do not add `AgentDescriptor`, vocabulary, or epistemic domain logic to engine types. `Worker` carries an optional `AgentDescriptor` field for probe dispatch only — not for identity, registry, or vocabulary operations.

**Named MCP server convention.** Library modules that expose MCP tools must use `@McpServer("<library-name>")` to scope their tools to a named server. The default (unnamed) MCP server belongs to the application. This prevents library tools from colliding with application tools and lets applications compose multiple library MCP surfaces. Established by claudony#105 and qhorus#306.
