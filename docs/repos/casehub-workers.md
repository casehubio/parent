# casehub-workers

**GitHub:** [casehubio/workers](https://github.com/casehubio/workers)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Worker dispatch infrastructure for the CaseHub ecosystem. Each module implements a specific dispatch mechanism (HTTP, Camel, MCP, GitHub Actions, Script) using the shared `WorkerRuntime` SPI defined in `workers-common`. Application-tier repos add worker modules as classpath dependencies to gain dispatch capabilities -- the `WorkerLifecycleOrchestrator` auto-discovers and initializes all `WorkerRuntime` beans at startup.

This repo provides the *how* of worker execution (transport, session management, fault handling, retry). The *what* of workers (identity, function, capability vocabulary) lives in `casehub-worker`. The *when* (dispatch scheduling, case orchestration) lives in `casehub-engine`.

---

## Module Structure

| Module | artifactId | Contents |
|--------|-----------|----------|
| `workers-common/` | `casehub-workers-common` | Shared infrastructure: `WorkerRuntime` SPI, `WorkerLifecycleOrchestrator`, `AsyncWorkerCompletionRegistry`, `WorkerFaultHandler` (retry with backoff), `WorkerCapabilityResolver<T>`, `WorkerProvisionerSupport`, `WorkerRetrySupport`, `WorkerStatusPublisher`, CDI events (`WorkerFaultEvent`, `CompletionExpiredEvent`, `FaultCallbackEvent`). |
| `workers-http/` | `casehub-workers-http` | HTTP dispatch: `HttpWorkerRuntime`, `HttpEndpointResolver`, `HttpWorkerExecutionManager`, `HttpReactiveWorkerProvisioner`, `ExchangeMode` enum, `ResolvedEndpoint` record, `HttpWorkerRoute`, fault handler. |
| `workers-camel/` | `casehub-workers-camel` | Apache Camel dispatch: `CamelWorkerRuntime`, `CamelCapabilityResolver`, `CamelWorkerExecutionManager`, `CamelReactiveWorkerProvisioner`, `CamelWorkerRoute`, custom Camel component (`casehub:` URI scheme — `CasehubComponent`, `CasehubEndpoint`, `CasehubProducer`), fault handler. |
| `workers-github-actions/` | `casehub-workers-github-actions` | GitHub Actions dispatch: `GitHubActionsWorkerRuntime`, `GitHubActionsTokenResolver`, `GitHubActionsWorkerExecutionManager`, `GitHubActionsReactiveWorkerProvisioner`, fault handler. |
| `workers-mcp/` | `casehub-workers-mcp` | MCP (Model Context Protocol) dispatch: `McpWorkerRuntime` (with `tools/list` discovery), `McpServerResolver`, `McpSessionManager`, `McpSession` (JSON-RPC over HTTP with `Mcp-Session-Id`), `McpWorkerExecutionManager`, `McpReactiveWorkerProvisioner`, `ResolvedMcpServer`, `ServerInitResult`, fault handler. |
| `workers-script/` | `casehub-workers-script` | Script dispatch: `ScriptWorkerRuntime`, `ScriptDefinitionResolver`, `ScriptDefinition`, `ScriptWorkerExecutionManager`, `ScriptReactiveWorkerProvisioner`, fault handler. |
| `workers-k8s/` | `casehub-workers-k8s` | Kubernetes Job dispatch: `K8sWorkerRuntime`, `K8sJobSpecBuilder`, `K8sWorkerExecutionManager`, `K8sReactiveWorkerProvisioner`, fault handler. Restart recovery via enriched Job labels — reconstructs `PendingCompletion` from K8s metadata when registry is empty (workers#17). Eager resolver initialization via `@PostConstruct` eliminates startup race (workers#17). |
| `workers-testing/` | `casehub-workers-testing` | `WorkerTestSupport` -- factory methods for test `CaseInstance`, `Worker`, `Capability` instances. |

---

## Key Abstractions

### WorkerRuntime SPI

Defined in `workers-common`. Lifecycle contract for a worker runtime -- the infrastructure that executes dispatched work for a specific worker type. Not a task instance, but an executor.

```java
public interface WorkerRuntime {
    String workerType();              // e.g. "mcp", "http", "camel"
    WorkerRuntimeStatus status();     // PENDING, RUNNING, FAULTED, STOPPED
    Uni<Void> initialize();           // PENDING -> RUNNING or FAULTED
    Uni<Void> shutdown();             // -> STOPPED
    Set<String> capabilities();       // valid after initialize()
}
```

Implementations must be `@ApplicationScoped`. The orchestrator discovers all beans via CDI and calls `initialize()` at startup. Post-initialization failures (connection errors, server unavailability) are handled by the per-dispatch fault pipeline -- they do not change runtime status.

### WorkerLifecycleOrchestrator

`@ApplicationScoped` CDI bean. Observes `StartupEvent` at `APPLICATION + 10` priority. Iterates all `WorkerRuntime` beans, calls `initialize()`, logs capabilities. Calls `shutdown()` on `@PreDestroy`. Handles initialization failures gracefully -- a failing worker does not prevent other workers from starting.

### Module Architecture Pattern

Every worker module follows a consistent five-class pattern:

| Class | Role |
|-------|------|
| `{Type}WorkerRuntime` | Implements `WorkerRuntime`. Initializes transport and discovers capabilities. |
| `{Type}CapabilityResolver` / `{Type}ServerResolver` | Implements `WorkerCapabilityResolver<T>`. Maps capability tags to concrete targets (endpoints, servers, definitions). |
| `{Type}WorkerExecutionManager` | Implements `WorkerExecutionManager`. Dispatches work at execution time -- serializes input, sends to target, handles response. |
| `{Type}ReactiveWorkerProvisioner` | Implements `ReactiveWorkerProvisioner`. Capability probe at case planning time -- validates that the worker can handle requested capabilities. |
| `{Type}WorkerFaultEventHandler` | Observes Vert.x EventBus messages on module-specific fault address. Delegates to `WorkerFaultHandler` for retry logic. |

### AsyncWorkerCompletionRegistry

`@ApplicationScoped` bean in `workers-common`. Tracks pending asynchronous worker dispatches. Each dispatch gets a `PendingCompletion` record with a TTL. A `@Scheduled` expiry check (default every 5 minutes) fires `CompletionExpiredEvent` for stale entries. Used by async worker modules (HTTP callback, GitHub Actions webhook) to correlate completion signals back to the originating dispatch.

### WorkerFaultHandler

`@ApplicationScoped` bean in `workers-common`. Central retry logic for all worker modules. On fault: persists failure log, checks retry count against `RetryPolicy`, computes backoff delay (supports `RetryAfterException` for server-specified delays), reloads event log entry and resubmits via `WorkerExecutionManager`. Marks `PermanentFaultException` as non-retryable. Publishes `retriesExhausted` event when all attempts are consumed.

### WorkerCapabilityResolver\<T\>

Generic SPI for resolving capability tags to transport-specific targets. `resolve(capabilityTag, tenancyId) -> T`, `firstMatch(capabilities, tenancyId)`, `capabilities()`. Each module provides its own implementation with the appropriate target type.

### WorkerCallbackResource

JAX-RS resource in `workers-common`. Receives completion callbacks at `/workers/callback/{dispatchId}` from async worker transports. Completes the pending entry in `AsyncWorkerCompletionRegistry` and publishes completion via `WorkflowCompletionPublisher`.

### BindingName Correlation (workers#18)

`bindingName` propagation from casehub-engine through worker dispatch enables tracing which YAML binding triggered a worker execution. `WorkerCorrelationContext` carries `bindingName` alongside `caseId` and `eventLogId`. All 6 worker modules override the 6-arg `submit()` to thread `bindingName` through to transport-specific metadata:

- **K8s:** persisted as `casehub.binding-name` Job label annotation for restart recovery
- **HTTP/MCP/Script/Camel/GitHub Actions:** passed via context payload, logged in fault events

`WorkerFaultHandler` includes `bindingName` in retry and exhaustion events. Engine consumes this for per-binding failure tracking (engine#676).

---

## Dispatch Mechanisms

### HTTP (`workers-http`)

Config-driven endpoint resolution via `HttpEndpointResolver`. Each capability maps to a URL + method + headers. Two exchange modes:
- `SYNC` -- request/response, result extracted from response body.
- `ASYNC` -- fire-and-forget with callback URL for completion notification.

`HttpWorkerRoute` defines the Vert.x EventBus address for fault routing.

### Camel (`workers-camel`)

Integrates with Apache Camel via the Quarkus Camel extension. Provides a custom `casehub:` Camel component (`CasehubComponent`, `CasehubEndpoint`, `CasehubProducer`) that bridges Camel routes to the CaseHub worker infrastructure. `CamelCapabilityResolver` maps capability tags to Camel route URIs. Camel routes can produce or consume worker dispatches.

### MCP (`workers-mcp`)

Model Context Protocol dispatch over HTTP (Streamable HTTP transport). `McpSessionManager` manages sessions per server -- handles initialization handshake, `Mcp-Session-Id` tracking, and protocol version negotiation. `McpServerResolver` loads server configurations and optionally discovers capabilities via `tools/list` JSON-RPC call. Sessions are reused across dispatches. If any server fails initialization, others can still proceed -- the runtime reaches `RUNNING` if at least one server succeeds.

### GitHub Actions (`workers-github-actions`)

Dispatches work by triggering GitHub Actions workflow runs via the GitHub API. `GitHubActionsTokenResolver` manages authentication tokens. Async completion via webhook callback -- the workflow sends results back to `WorkerCallbackResource`.

### Script (`workers-script`)

Local script execution. `ScriptDefinitionResolver` maps capability tags to `ScriptDefinition` records containing the script path and execution parameters. `ScriptWorkerExecutionManager` executes scripts as local processes.

### Kubernetes (`workers-k8s`)

Kubernetes Job-based worker dispatch. `K8sWorkerRuntime` initializes K8s client and discovers capabilities from `K8sJobSpecResolver`. Each capability maps to a Job spec template. `K8sWorkerExecutionManager` creates Jobs on demand, monitors completion via K8s API watch.

**Restart recovery (workers#17):** Enriched Job labels carry recovery metadata:
- `casehub.case-id` — originating case UUID
- `casehub.worker-name` — worker identifier
- `casehub.event-log-id` — engine event log entry for retry/audit correlation
- `casehub.binding-name` — YAML binding that triggered the dispatch
- `casehub.idempotency-key` — prevents duplicate Job creation

On restart, `processTerminal()` checks if the Job still exists in K8s. If `PendingCompletion` is missing from the registry but the Job is still running, reconstructs the registry entry from Job labels. `schedulePersistedEvent()` (called by engine recovery) checks K8s for existing Jobs matching the event-log-id; only re-dispatches if no Job is found. Eager resolver initialization via `@PostConstruct` ensures capabilities are loaded before engine recovery runs.

---

## Depends On

| Repo | Module | How |
|------|--------|-----|
| `casehub-platform` | `platform-api` | Governance types (`RetryPolicy`, `BackoffStrategy`), tenancy |
| `casehub-worker` | `worker-api` | `Worker`, `Capability`, `WorkerFunction`, `WorkerResult` |
| `casehub-engine` | `engine-common` | `CaseInstance`, `EventLogRepository`, `WorkerExecutionManager` SPI |
| Quarkus Camel BOM | `quarkus-camel-bom` | Camel module only |

## Depended On By

| Repo | What it uses |
|------|-------------|
| Application-tier repos that need worker dispatch | Add specific worker modules as classpath dependencies; `WorkerLifecycleOrchestrator` auto-discovers them |

---

## Does NOT Do

- Define worker identity, function, or capability vocabulary -- that is `casehub-worker`
- Schedule or orchestrate work -- that is `casehub-engine`
- Provide `WorkerFunction` implementations -- those live in consuming repos (e.g. `AgentWorkerFunction` in engine)
- Manage worker state machines or task instances -- `WorkerRuntime` is an executor lifecycle, not a task instance lifecycle
- Provide a UI or management API for worker configuration -- workers are configured via Quarkus config properties
- Run as a standalone application -- these are library modules consumed by application-tier deployments

---

## Current State

- All 7 modules (common, http, camel, github-actions, mcp, script, testing) on main with tests.
- Consistent five-class pattern across all dispatch modules.
- MCP module supports Streamable HTTP transport with `tools/list` capability discovery.
- Camel module includes a custom `casehub:` Camel component for bidirectional integration.
- `AsyncWorkerCompletionRegistry` with TTL-based expiry for async dispatch patterns.
- `WorkerFaultHandler` with configurable retry, backoff, `RetryAfterException` support, and permanent fault detection.
