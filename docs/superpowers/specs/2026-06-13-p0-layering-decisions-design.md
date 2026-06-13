# P0 Layering Decisions — CloudEvents, Platform Streams, and Deployment YAML Compiler

**Date:** 2026-06-13 (revised 2026-06-14)
**Status:** Decided
**Issue:** casehubio/parent#235
**Scope:** Cross-cutting — casehub-platform, casehub-ras, casehub-ops, casehub-desiredstate
**Supersedes:** Research doc §5 open questions 1–3 (`docs/superpowers/research/2026-06-12-platform-evolution-desiredstate-ras-deployment.md`)

---

## Context

Three P0 architectural questions were left open after the 2026-06-12 platform evolution session. All three block implementation of casehub-ras, the platform stream modules, and casehub-ops/deployment.

---

## Implementation — Child Specs

| Decision | Repo | Issue | Spec topic |
|----------|------|-------|------------|
| 1 + 2 — CloudEvent + stream modules | [casehubio/platform](https://github.com/casehubio/platform/issues/98) | platform#98 | `CloudEvent` in `platform-api`, `EndpointRegistered` CDI event + contract, `STREAM_EVENT_TYPE` property key, 5 stream submodules |
| 3 — Deployment components | [casehubio/casehub-ops](https://github.com/casehubio/casehub-ops/issues/6) | casehub-ops#6 | `DeploymentGoalCompiler`, `StreamEndpointNodeProvisioner`, `CasehubDeploymentActualStateAdapter`, `CasehubDeploymentStartup` (bootstrap bean) |
| 3 — Channel node provisioner | [casehubio/qhorus](https://github.com/casehubio/qhorus/issues/279) | qhorus#279 | Channel creation SPI in `casehub-qhorus-api`, `ChannelNodeSpec`, `QhorusNodeTypes`, `QhorusChannelNodeProvisioner`, `QhorusChannelActualStateAdapter` |
| 3 — Situation node provisioner | casehubio/casehub-ras (new issue) | TBD | `SituationNodeSpec`, `RasNodeTypes`, `RasSituationNodeProvisioner`, `RasSituationActualStateAdapter` |
| 3 — Agent node provisioner | casehubio/claudony (new issue) | TBD | `AgentNodeSpec`, `AgentNodeTypes`, `AgentInstanceNodeProvisioner`, `AgentInstanceActualStateAdapter` |
| 3 — Multi-provisioner dispatch | casehubio/casehub-desiredstate (new issue) | TBD | `canHandle(DesiredNode)` on `NodeProvisioner`, `canObserve(DesiredNode)` + `NodeStatus readActual(DesiredNode, ProvisionContext)` on `ActualStateAdapter`, `CompositeTransitionExecutor` in `casehub-desiredstate-composite` |
| Adapter — IoT | [casehubio/iot](https://github.com/casehubio/iot/issues/19) | iot#19 | `StateChangeEvent → CloudEvent` |
| Adapter — Qhorus | qhorus#279 | qhorus#279 | `MessageReceivedEvent → CloudEvent` (same issue as channel SPI) |
| Adapter — Connectors | [casehubio/connectors](https://github.com/casehubio/connectors/issues/20) | connectors#20 | `InboundMessage → CloudEvent` |

**Review order:** platform#98 first. The casehub-desiredstate multi-provisioner issue must land before casehub-ops#6, qhorus#279, and the RAS/claudony provisioner issues.

---

## Decision 1 — CloudEvent as the Platform's Typed Event Envelope

### Decision

Use `io.cloudevents.CloudEvent` from the CloudEvents Java SDK (`io.cloudevents:cloudevents-core`) directly as the CDI event type. `casehub-platform-api` takes a `compile` scope dependency on `cloudevents-core`. No wrapper type.

### Type structure

Producers fire `Event<CloudEvent>.fireAsync()`. Consumers observe `@ObservesAsync CloudEvent`.

| CloudEvent field | Purpose in CasehHub |
|---|---|
| `type` | Logical event type — reverse-DNS. From `EndpointDescriptor.properties().get(EndpointPropertyKeys.STREAM_EVENT_TYPE)`. |
| `source` | Logical producer URI |
| `subject` | The entity the event concerns — `device/thermostat-1`, `patient/1234` |
| `id` | UUID at ingestion |
| `time` | Message timestamp or `Instant.now()` |
| `data` | Typed payload |
| `tenancyid` (extension) | CasehHub tenant ID (lowercase, ≤20 chars) |

### CloudEvent type property key

Add to `EndpointPropertyKeys` as part of platform#98:

```java
public static final String STREAM_EVENT_TYPE = "stream-event-type";
```

All stream modules read this from the registered `EndpointDescriptor` to set the CloudEvent `type` field.

### Tenancy in async processing — P0 position

Observers extract `tenancyid` directly from the `CloudEvent`: `event.getExtension("tenancyid")`. CDI `@ObservesAsync` fires off-thread with no request scope. A `StreamContext` SPI for propagating tenancy into downstream call chains is P1 (mechanism unresolved — see P1.8).

---

## Decision 2 — Platform Stream Modules as casehub-platform Submodules

### Modules

| Module | Transport | Notes |
|--------|-----------|-------|
| `platform-streams-kafka` | Quarkus SmallRye reactive messaging | Static topics via `application.properties`; native CloudEvents deserialization |
| `platform-streams-amqp` | Quarkus AMQP reactive messaging | Requires `AMQP` added to `EndpointProtocol` |
| `platform-streams-webhook` | Quarkus REST `@POST` | CloudEvents HTTP binding; registers itself in `EndpointRegistry` as inbound receiver |
| `platform-streams-poll` | Quarkus `@Scheduled` + REST client | Polls `EndpointProtocol.HTTP` + `EndpointCapability.QUERY` endpoints from `EndpointRegistry` at a configurable interval. Global config: `casehub.streams.poll.interval=60s` (default 60 seconds). Per-endpoint intervals are P1+. |
| `platform-streams-camel` | Apache Camel | Observes `EndpointRegistered` for `EndpointProtocol.CAMEL` only — see below |

### EndpointRegistered CDI event

New record in `casehub-platform-api`:

```java
public record EndpointRegistered(EndpointDescriptor descriptor) {}
```

**Firing contract:** Only implementations that actually store the endpoint fire `EndpointRegistered`. Currently there are exactly two `EndpointRegistry` implementations:

- `InMemoryEndpointRegistry.register()` — fires `Event<EndpointRegistered>.fireAsync()` after `store.put()`. Requires injecting `Event<EndpointRegistered>` as a CDI dependency.
- `NoOpEndpointRegistry.register()` — remains a silent `{}`. Must NOT fire `EndpointRegistered`: a no-op registry signals "no endpoints exist"; firing the event would trigger stream routes for phantom endpoints.

This contract is documented in the `EndpointRegistry` interface Javadoc and enforced by a test in `InMemoryEndpointRegistryTest` verifying that `EndpointRegistered` is fired on `register()`. Any future `EndpointRegistry` implementation (JPA-backed, etc.) must document whether it fires `EndpointRegistered` — the interface Javadoc states this as a required obligation for non-no-op implementations.

**Why this decoupling matters:** `StreamEndpointNodeProvisioner` in casehub-ops calls only `EndpointRegistry.register()`. Stream modules self-configure from the `EndpointRegistered` event. This eliminates any casehub-ops → stream-module compile dependency. Adding a new stream module requires no ops change.

### CAMEL and KAFKA are mutually exclusive deployment choices

`platform-streams-camel` observes `EndpointRegistered` for `EndpointProtocol.CAMEL` **only** — never for `EndpointProtocol.KAFKA`.

When an `EndpointDescriptor` with `EndpointProtocol.CAMEL` is registered, `platform-streams-camel` starts a new Camel route via `CamelContext.addRoutes()`. This enables runtime dynamic topology: new CAMEL endpoints provisioned by desiredstate reconciliation are picked up immediately.

KAFKA via Camel (`platform-streams-camel` with a Camel Kafka component) is an alternative to `platform-streams-kafka` — not a complement. Both consuming the same Kafka topic from the same consumer group would partition-split messages between them, causing silent partial loss with no error. The deployment choice is:
- Static topics known at deploy time → `platform-streams-kafka` (SmallRye `@Incoming`, `application.properties`)
- Dynamic topics registered at runtime → `platform-streams-camel` with Camel Kafka component, NO `platform-streams-kafka` on the classpath for those topics

This is a deployment constraint, not a code constraint. It must be documented in platform#98.

### AMQP requires EndpointProtocol addition

`EndpointProtocol` currently: `HTTP, GRPC, KAFKA, MCP, CAMEL, QHORUS` — no `AMQP`. Add `AMQP` as part of platform#98.

### EndpointProtocol.QHORUS — no stream module needed

`EndpointProtocol.QHORUS` is for invoking Qhorus (outbound). `QhorusCloudEventAdapter` (qhorus#279) maps `MessageReceivedEvent` to `CloudEvent` via CDI. No `platform-streams-qhorus` module.

### Webhook module — EndpointRegistry as inbound receiver

`platform-streams-webhook` registers with `EndpointType.SERVICE`, `EndpointProtocol.HTTP`, `EndpointCapability.RECEIVE`. The `url` property stores the public inbound address external systems POST to. `EndpointCapability.RECEIVE` is the correct mechanism — its Javadoc example is "HTTP webhook receiver: RECEIVE."

The public URL cannot be auto-derived (it sits behind a reverse proxy). It is a Quarkus config property that the operator must set before deployment:

```
casehub.streams.webhook.public-url=https://casehub.example.com/streams/webhook
```

**Two distinct EndpointRegistry entries for webhook:** `platform-streams-webhook` self-registers its physical receiver at a fixed path (e.g. `Path.of("platform", "streams", "webhook")`) at startup — this is the module advertising its availability. `StreamEndpointNodeProvisioner` registers each logical webhook stream source at a per-stream path (e.g. `Path.of("streams", streamSpec.id())`) — this is the deployment declaring "incoming data on this stream should fire CloudEvents." Both entries carry the same physical URL from `casehub.streams.webhook.public-url`. This is not a conflict: the paths are different, the semantics are different (physical receiver vs logical stream source). The stream module uses the per-stream entry to know the `STREAM_EVENT_TYPE` and `tenancyId` for each incoming POST.

### Camel startup timing window

`platform-streams-camel` observes `@ObservesAsync EndpointRegistered`. During application startup, some `EndpointRegistered` events may arrive before `CamelContext` reaches `ServiceStatus.Started`. Calling `CamelContext.addRoutes()` on a context in STARTING or INITIALIZING state has undefined behavior — routes may be registered but not started.

Required behavior for `platform-streams-camel`: buffer `EndpointDescriptor` entries received before `CamelContext` is fully started, then process them in a `@Observes io.quarkus.runtime.StartupEvent` handler. Quarkus guarantees `io.quarkus.runtime.StartupEvent` fires after all CDI beans are initialized and after Quarkus Camel has started the `CamelContext` — routes added in this handler are safe. Runtime registrations (after startup) call `addRoutes()` directly.

### CloudEvent construction convention

All stream modules set:
- `type` from `EndpointDescriptor.properties().get(EndpointPropertyKeys.STREAM_EVENT_TYPE)`
- `source` as logical producer URI
- `subject` as entity the event concerns
- `id` as UUID at ingestion
- `time` as message timestamp or `Instant.now()`
- `tenancyid` extension — **source varies by module:**

| Module | `tenancyid` source | Reason |
|--------|-------------------|--------|
| `platform-streams-kafka` | Kafka header `X-Tenancy-ID` | Internal producer; header is operator-controlled (same cluster) |
| `platform-streams-amqp` | AMQP message property `X-Tenancy-ID` | Internal producer; property is operator-controlled |
| `platform-streams-webhook` | `EndpointDescriptor.tenancyId()` | External caller — must not be trusted to self-identify; operator-set at registration |
| `platform-streams-poll` | `EndpointDescriptor.tenancyId()` | Operator-configured polling target; tenancyId is set at endpoint registration |
| `platform-streams-camel` | `EndpointDescriptor.tenancyId()` | Camel route is operator-defined; tenancyId is set at endpoint registration |

Using `X-Tenancy-ID` from an HTTP request (webhook) allows any external caller to claim any tenant's identity — a security gap. `EndpointDescriptor.tenancyId()` is set by the operator at registration time and is not caller-influenced.

---

## Decision 3 — casehub-ops/deployment: Multi-Domain Architecture

### Prerequisite: casehub-desiredstate SPI additions and CompositeTransitionExecutor

The following breaking changes to `casehub-desiredstate` must land first as a single issue.

**`NodeProvisioner` SPI** adds `boolean canHandle(DesiredNode node)`:
```java
public interface NodeProvisioner {
    boolean canHandle(DesiredNode node);
    ProvisionResult provision(DesiredNode node, ProvisionContext context);
    DeprovisionResult deprovision(DesiredNode node, DeprovisionContext context);
}
```

**`ActualStateAdapter` SPI** changes to per-node signature (symmetric with `NodeProvisioner`):
```java
public interface ActualStateAdapter {
    boolean canObserve(DesiredNode node);
    NodeStatus readActual(DesiredNode node, ProvisionContext context);
}
```

The old `ActualState readActual(DesiredStateGraph desired)` is removed. `ReconciliationLoop` currently injects a single `ActualStateAdapter actualStateAdapter` and calls `actualStateAdapter.readActual(desired)` — this call no longer exists after the signature change. `ReconciliationLoop` must change to `@All Instance<ActualStateAdapter>` and build the `ActualState` map per-node via `canObserve()` dispatch inline. This is part of the prerequisite issue scope and is a change to the desiredstate `runtime` module.

**Breaking implementations (full migration list):**
- `DungeonActualStateAdapter` (examples/dungeon) — old signature
- `MockActualStateAdapter` (testing/) — old signature
- `TestActualStateAdapter` nested in `ReconciliationLoopTest` (runtime tests) — old signature
- All three must be updated as part of the prerequisite issue

**`CompositeTransitionExecutor`** in a new `casehub-desiredstate-composite` module:
- `@ApplicationScoped` — no `@DefaultBean`
- Injects `@All Instance<NodeProvisioner>` for provisioner dispatch
- Displaces `SimpleTransitionExecutor @DefaultBean` by classpath presence — exactly the pattern of `CaseTransitionExecutor` in `casehub-desiredstate-engine-adapter`
- Does NOT inject `@All Instance<ActualStateAdapter>` — that dispatch is handled inline by `ReconciliationLoop`
- `SimpleTransitionExecutor` is untouched; single-domain uses (dungeon example, unit tests) continue working

**Failure modes `CompositeTransitionExecutor` must enforce:**

1. **No provisioner claims a node** → fail the transition step with a clear error. New node types without a registered provisioner must not silently succeed.

2. **Multiple provisioners claim the same node** → throw `AmbiguousProvisionerException` naming all claimants. CDI discovery order is not stable; first-match is not acceptable. This is validated on each `execute()` call when dispatching a node — same urgency as the zero-provisioner case.

3. **No adapter observes a node** → return `NodeStatus.UNKNOWN` (acceptable — some node types may have no observable state, or their adapter is not yet deployed).

4. **Multiple adapters observe the same node** → throw an ambiguity error, same as the provisioner case.

### Component ownership by domain

| Node type | NodeType constant | NodeSpec type | Owner of constant + NodeSpec |
|---|---|---|---|
| `"stream-endpoint"` | `StreamNodeTypes.STREAM_ENDPOINT` | `StreamEndpointSpec` | **casehub-ops/deployment** |
| `"channel"` | `QhorusNodeTypes.CHANNEL` | `ChannelNodeSpec` | casehub-qhorus-api |
| `"situation"` | `RasNodeTypes.SITUATION` | `SituationNodeSpec` | casehub-ras-api |
| `"agent"` | `AgentNodeTypes.AGENT` | `AgentNodeSpec` | claudony-api |

**StreamNodeTypes and StreamEndpointSpec live in casehub-ops/deployment** — not casehub-platform-api.

`casehub-desiredstate-api` already has `casehub-platform-api` as a compile dependency. Placing `StreamNodeTypes` (which wraps `NodeType`) and `StreamEndpointSpec` (which implements `NodeSpec`) in `casehub-platform-api` would require `casehub-platform-api → casehub-desiredstate-api` for those types — creating a confirmed circular Maven dependency. Only casehub-ops manages stream-endpoint nodes, so only casehub-ops needs these types. No other repo is affected.

The longer-term architectural option (Option B) — moving `NodeType` and `NodeSpec` themselves from `casehub-desiredstate-api` to `casehub-platform-api`, which would let all domain API modules place their types there safely — is a valid design that satisfies the platform-api-scope protocol. However, `NodeType` and `NodeSpec` are desiredstate-specific infrastructure types for graph nodes; they differ from truly cross-cutting platform primitives like `Path` or `CurrentPrincipal`. Option B is tracked as a separate issue (not bundled with #233 which is specifically about GoalCompiler evolution).

casehub-ops declares compile dependencies on `casehub-qhorus-api`, `casehub-ras-api`, and `claudony-api` for both the NodeType constants AND the NodeSpec types. `DeploymentGoalCompiler` constructs instances of these NodeSpec types. The provisioners (in qhorus, ras, claudony) import their own API modules and cast `node.spec()` to the appropriate type — no circular dependency.

### ProvisionContext name collision

`io.casehub.desiredstate.api.ProvisionContext` is `record(String tenancyId, DesiredStateGraph graph)`.
`io.casehub.api.model.ProvisionContext` is `record(UUID caseId, String taskType, WorkerContext, PropagationContext, ...)`.
These are entirely different types with the same name. All code referencing either must use fully-qualified names.

### CasehubDeploymentSpec

```java
public record CasehubDeploymentSpec(
    String name,
    String tenancyId,          // the tenant this deployment is scoped to.
                               // Passed to ReconciliationLoop.start(tenancyId, graph).
                               // Use TenancyConstants.DEFAULT_TENANT_ID for single-tenant deployments.
    List<StreamSpec> streams,
    DetectionSpec detection,
    List<AgentSpec> agents,
    List<ChannelSpec> channels
    // connectors: removed — CDI observer model is deploy-time, not provisionable; P2.13
    // trust: removed — PreferenceProvider is read-only; P2.11
) {}

public record StreamSpec(
    String id,
    String transport,           // "kafka" | "amqp" | "camel" | "webhook" | "poll"
    String topic,               // for kafka/amqp; null for webhook/poll
    String streamType           // reverse-DNS CloudEvent type
) {}

public record DetectionSpec(List<SituationSpec> situations) {}

public record SituationSpec(
    String id,
    List<String> watch,         // StreamSpec ids
    String gangliaType,         // opaque String interpreted by RasSituationNodeProvisioner
                                // known values (not exhaustive): "java-switch", "drools-cep",
                                // "bayesian", "llm" — RAS validates; ops treats as opaque
    double minConfidence,
    String triggerCase,
    String priority             // opaque String interpreted by RasSituationNodeProvisioner.
                                // known values (not exhaustive): "HIGH" | "MEDIUM" | "LOW".
                                // Ops treats as opaque; RAS validates.
) {}

public record AgentSpec(
    String id,
    String slot,              // functional role/type of agent to provision — corresponds to
                              // AgentDescriptor.slot in casehub-eidos (required field).
                              // Examples: "safety-monitor", "reviewer", "supervisor".
                              // Opaque to ops; AgentInstanceNodeProvisioner validates and uses it
                              // to configure the provisioned instance (system prompt, capabilities).
    int count,                // number of instances to provision for this slot
    String provisioner,       // opaque identifier of the backend: "claudony" | "openclaw" | future.
                              // Validated by AgentInstanceNodeProvisioner.
    double minTrust,          // minimum trust score threshold for routing decisions
    List<String> channels     // channel names this agent is assigned to — used by DeploymentGoalCompiler
                              // to wire graph dependencies: each agent node depends on each named channel node.
                              // The agent provisioner uses these to configure channel access for the instance.
) {}

public record ChannelSpec(
    String name,
    String type,          // opaque String interpreted by QhorusChannelNodeProvisioner.
                          // Known values (not exhaustive, not backed by a Java type):
                          // "work" | "observe" | "oversight" — the normative 3-channel layout
                          // from PLATFORM.md §Agent mesh alignment. Provisioner validates.
    List<String> acl
) {}
```

### DeploymentGoalCompiler — pure translation (casehub-ops)

`compile(CasehubDeploymentSpec, DesiredStateGraphFactory)` iterates each section and produces `DesiredNode` entries using domain API module types. No calls to live systems.

Dependency ordering:
- `"situation"` nodes depend on their `watch` stream-endpoints
- `"agent"` nodes depend on each channel named in `AgentSpec.channels` — the compiler wires an explicit graph dependency for each named channel, so channels are provisioned before agents that use them

### StreamEndpointNodeProvisioner — casehub-ops

`canHandle(node)`: `node.type().value().equals(StreamNodeTypes.STREAM_ENDPOINT)` where `StreamNodeTypes` is defined in `casehub-ops/deployment`

On `provision`: calls `EndpointRegistry.register()` with the `EndpointDescriptor` constructed from the node's `StreamEndpointSpec`. `EndpointRegistered` fires automatically; stream modules self-configure. No transport implementation knowledge in casehub-ops.

**StreamSpec → EndpointDescriptor mapping conventions:**

| StreamSpec.transport | EndpointType | EndpointProtocol | EndpointCapability | Notes |
|---|---|---|---|---|
| `"kafka"` | `SYSTEM` (external broker) | `KAFKA` | `RECEIVE` | Kafka consumer — broker pushes to consumer |
| `"amqp"` | `SYSTEM` (external broker) | `AMQP` | `RECEIVE` | AMQP consumer — same push semantics |
| `"camel"` | `WORKER` (data processing route) | `CAMEL` | `RECEIVE` | Camel route delivers to CDI observer |
| `"webhook"` | `SERVICE` (internal receiver) | `HTTP` | `RECEIVE` | External system pushes HTTP POST to us |
| `"poll"` | `SYSTEM` (external REST target) | `HTTP` | `QUERY` | We initiate HTTP GET — pull, not push |

`RECEIVE` = "Endpoint can push data to the caller" (Kafka consume, webhook delivery). `QUERY` = "Caller can issue a read request and receive a synchronous response" (HTTP GET). The distinction matters for `EndpointRegistry.discover()` filtering — the poll module discovers only `QUERY` endpoints; the webhook module registers only `RECEIVE` endpoints; both use `EndpointProtocol.HTTP` but are disambiguated by capability.

**Path:** `Path.of("streams", streamSpec.id())` per tenant. Must be unique; casehub-ops/deployment owns the convention.

**Properties:**

| Property key | Applies to | Value |
|---|---|---|
| `EndpointPropertyKeys.TOPIC` | kafka, amqp | `StreamSpec.topic` |
| `EndpointPropertyKeys.STREAM_EVENT_TYPE` | all | `StreamSpec.streamType` |
| `EndpointPropertyKeys.URL` | camel | Camel endpoint URI — e.g. `kafka:my-topic?brokers=broker:9092` (Camel Kafka), `direct:my-route` (internal route), `amqp:queue:my-queue` (Camel AMQP) |

For `kafka` and `amqp`, `EndpointPropertyKeys.URL` does NOT apply — the URL Javadoc lists HTTP, GRPC, MCP, CAMEL, QHORUS; KAFKA is absent. The `EndpointPropertyKeys` Javadoc explicitly notes that "bootstrap servers" are "deployment-local properties" not reserved in `EndpointPropertyKeys`. Kafka broker connection is configured via Quarkus standard config (`kafka.bootstrap.servers`) outside the EndpointDescriptor. The EndpointDescriptor for a KAFKA stream endpoint carries `TOPIC` and `STREAM_EVENT_TYPE` only.

**credentialRef:** null for P0; set when stream endpoint requires credential lookup (Kafka SASL, authenticated REST polling).

**CloudEvent `subject` derivation for raw messages:** If the incoming message is a native CloudEvent (detected by `application/cloudevents+json` or binary CloudEvents content type), the existing `subject` field is preserved. For raw payloads (plain JSON, text), `subject` is null — CloudEvents allows a null subject. Per-stream subject extraction from payload fields is P1+.

`canObserve(node)`: same predicate as `canHandle()`.

`readActual(node, context)`: `EndpointRegistry.resolve(path, tenancyId)` → PRESENT if found, ABSENT if not.

### QhorusChannelNodeProvisioner — casehub-qhorus

**Prerequisite:** channel creation/deletion SPI promoted to `casehub-qhorus-api`. Currently `ChannelService` is `io.casehub.qhorus.runtime.channel.ChannelService` — internal class. qhorus#279 must include this API promotion.

`canHandle(node)`: `node.type().value().equals(QhorusNodeTypes.CHANNEL)`

On `provision`: calls channel management SPI. Casts `node.spec()` to `ChannelNodeSpec` (defined in casehub-qhorus-api).

### RasSituationNodeProvisioner — casehub-ras

`canHandle(node)`: `node.type().value().equals(RasNodeTypes.SITUATION)`

On `provision`: registers `SituationDefinition` in `RasEngine`. Casts `node.spec()` to `SituationNodeSpec` (defined in casehub-ras-api). `gangliaType` is an opaque string from `SituationNodeSpec` — RAS validates it knows the type.

### AgentInstanceNodeProvisioner — claudony

`WorkerProvisioner` (`io.casehub.api.spi.WorkerProvisioner`) is case-scoped: `provision(Set<String> capabilities, io.casehub.api.model.ProvisionContext context)` requires `caseId`, `taskType`, `workerContext`. This is for spinning up workers for a running case — different from provisioning persistent deployment-level agent instances. A new SPI is needed in claudony. Tracked separately.

### CasehubDeploymentStartup — bootstrap bean (casehub-ops)

`@ApplicationScoped` bean with `@Observes io.quarkus.runtime.StartupEvent` — the integration point that connects the compiled graph to the reconciliation loop. Without it, the compiler produces a graph that nobody submits to `ReconciliationLoop`; the provisioners have nothing to do.

Responsibilities:
1. Read the deployment YAML from classpath or from `casehub.deployment.yaml` config property
2. Parse it into `CasehubDeploymentSpec` (Jackson/YAML mapper)
3. Call `DeploymentGoalCompiler.compile(spec, factory)` → `DesiredStateGraph`
4. Call `ReconciliationLoop.start(spec.tenancyId(), graph)`

`ReconciliationLoop.start(String tenancyId, DesiredStateGraph desired)` is the confirmed entry point — line 110 of the desiredstate runtime. `tenancyId` comes from `CasehubDeploymentSpec.tenancyId()` — a deployment YAML is inherently tenant-scoped. Use `TenancyConstants.DEFAULT_TENANT_ID` in the YAML for single-tenant deployments.

### GoalCompiler trajectory

`GoalCompiler<G>` in `casehub-desiredstate-api` is short-term positioning (see casehubio/parent#233 for platform-level evolution to `GoalCompiler<G, P>`). Factory parameter removal is an intentional future break. `GoalExecutor<P>` (execution counterpart) is part of the same #233 work.

---

## Impact on Existing Platform

### casehub-ras-api

Observes `@ObservesAsync CloudEvent` from `casehub-platform-api`.

### Adapters

- `casehub-iot`: `StateChangeEvent → CloudEvent` (type `io.casehub.iot.<deviceClass>`)
- `casehub-qhorus`: `MessageReceivedEvent → CloudEvent` (type `io.casehub.qhorus.message.<messageType>`)
- `casehub-connectors`: `InboundMessage → CloudEvent` via `@ObservesAsync InboundMessage` fired by `InboundConnectorService` (type `io.casehub.connectors.inbound.<connectorType>`)

### PLATFORM.md updates required

- Add `CloudEvent` CDI event type + `EndpointRegistered` + `STREAM_EVENT_TYPE` to Capability Ownership table
- Add platform stream modules to Repository Map (Foundation tier submodules)
- Add `AMQP` to `EndpointProtocol` description
- Update `casehub-ras` capability row
- Update casehub-ops Repository Map entry
- Add `CompositeTransitionExecutor` to casehub-desiredstate description
- Add node type + NodeSpec constant conventions
- **Add to Cross-Repo Dependency Map:**
  - `casehub-ops` → `casehub-qhorus-api` (NodeType constants + `ChannelNodeSpec`)
  - `casehub-ops` → `casehub-ras-api` (NodeType constants + `SituationNodeSpec`)
  - `casehub-ops` → `claudony-api` (NodeType constants + `AgentNodeSpec`)
  - `casehub-desiredstate-composite` → `casehub-desiredstate-api` (SPI interfaces)
  - **`casehub-qhorus-api` → `casehub-desiredstate-api`** (for `NodeSpec` implemented by `ChannelNodeSpec`) — new dep; `casehub-qhorus-api/pom.xml` currently has no desiredstate dependency
  - **`casehub-ras-api` → `casehub-desiredstate-api`** (for `NodeSpec` implemented by `SituationNodeSpec`) — new dep
  - **`claudony-api` → `casehub-desiredstate-api`** (for `NodeSpec` implemented by `AgentNodeSpec`) — new dep

  **Build-order consequence:** these three new deps require `casehub-desiredstate-api` to be published before `casehub-qhorus`, `casehub-ras`, and `claudony` build. Currently `casehub-qhorus` (Foundation tier) has no desiredstate dependency. This is a non-trivial CI/CD pipeline change. See the Option B tracking entry in What's Open — Option B (moving `NodeType`/`NodeSpec` to `casehub-platform-api`) eliminates all three of these new deps, since all three repos already depend on `casehub-platform-api`.

---

## What Remains Open (P1+)

| # | Question | Blocks |
|---|----------|--------|
| **Prereq** | casehub-desiredstate: `canHandle(DesiredNode)` on `NodeProvisioner`; `canObserve(DesiredNode)` + `NodeStatus readActual(DesiredNode, ProvisionContext)` on `ActualStateAdapter` (removes `ActualState readActual(DesiredStateGraph)`); `ReconciliationLoop` changes to `@All Instance<ActualStateAdapter>` + per-node dispatch in runtime module; `CompositeTransitionExecutor` with fail-loud for zero/ambiguous provisioners. Migration: `DungeonActualStateAdapter` (examples/), `MockActualStateAdapter` (testing/), `TestActualStateAdapter` nested in `ReconciliationLoopTest`. | All domain provisioner implementations |
| **Tracked** | casehub-desiredstate + casehub-platform-api (new issue, cross-ref parent#235): move `NodeType` + `NodeSpec` from `casehub-desiredstate-api` to `casehub-platform-api` — removes the constraint that forces stream-endpoint constants into casehub-ops; removes the need for `casehub-qhorus-api`, `casehub-ras-api`, and `claudony-api` to take a new compile dependency on `casehub-desiredstate-api` (and the build-order constraint that implies — these repos currently have no desiredstate dependency); enables all domain API modules to define NodeType/NodeSpec via their existing `casehub-platform-api` dep. Breaking: all importers of `io.casehub.desiredstate.api.NodeType`/`NodeSpec` change package. Separate issue, not bundled with #233. | Option B long-term |
| **Prereq** | casehub-qhorus: channel creation/deletion SPI in `casehub-qhorus-api`, `ChannelNodeSpec`, `QhorusNodeTypes` | qhorus#279 provisioner part |
| **Prereq** | claudony: persistent agent lifecycle SPI + `AgentNodeSpec`, `AgentNodeTypes`, `AgentInstanceNodeProvisioner` | Agent nodes |
| **Prereq** | casehub-ras: `SituationNodeSpec`, `RasNodeTypes`, `RasSituationNodeProvisioner`, `RasSituationActualStateAdapter` | Situation nodes |
| P1.4 | KAFKA/Camel mutual exclusion must be documented in platform#98 — deployment guidance on when to use each, and that running both for the same topic causes silent partial loss | Deployment UX |
| P1.8 | `StreamContext` SPI — tenancy propagation in async chains not holding a `CloudEvent` | Async tenancy propagation |
| P2.5 | `SituationStore` persistence | casehub-ras production readiness |
| P2.6 | Drools CEP session model | casehub-ras Drools ganglion |
| P2.7 | Ganglion-as-case pattern | casehub-ras SPI design |
| P2.11 | `WritablePreferenceProvider` SPI — platform#8 tracks the write model. Trust config managed via git YAML until this exists. | Trust-config as a provisioned node |
| P2.13 | Connector routing SPI — outbound connector routing (which events trigger which connector) is CDI observer wiring, not runtime-provisionable. Needs a runtime dispatch table SPI before connectors can be deployment nodes. | Connector nodes |
| P3.9 | `StreamEventLedgerEntry` home | Audit trail completeness |
| P3.10 | Self-governance bootstrap | casehub-ops operational story |
