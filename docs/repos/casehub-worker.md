# casehub-worker

**Repo:** [casehubio/casehub-worker](https://github.com/casehubio/casehub-worker)
**Tier:** Foundation
**Role:** Automated task primitives — `Worker`, `Capability`, `WorkerFunction`, execution policy

---

## Overview

`casehub-worker` is the foundation-tier home for automated task primitives. It is the peer of `casehub-work` (human tasks) — while `casehub-work` owns `WorkItem` lifecycle, `casehub-worker` owns the identity, function, and capability vocabulary for automated workers.

Extracted from `casehub-engine-api` (desiredstate#40, engine#543). The extraction makes Workers a shareable foundation primitive — `casehub-desiredstate` and other downstream consumers can depend on `casehub-worker-api` without pulling in the full engine.

---

## Modules

| Module | artifactId | What it is |
|--------|-----------|------------|
| `api/` | `casehub-worker-api` | Pure-Java value types + `WorkerFunction<T>` interface. Depends on `casehub-platform-api` for `ExecutionPolicy`. No Quarkus, no JPA. |
| `runtime/` | `casehub-worker` | `DefaultWorkerExecutor` — capability-aware execution: `execute(Worker, Capability, Object)` with typed input support, JSON Schema validation (`SchemaValidator`), policy enforcement (`PolicyEnforcer`), and OTel instrumentation. |
| `testing/` | `casehub-worker-testing` | `MockWorkerExecutor` (`@DefaultBean @ApplicationScoped` — mirrors validation guards but skips schema/policy enforcement), `TestWorkerBuilder` (`syncWithCapability()` convenience with optional custom schemas, `WorkerWithCapability` record) — `@QuarkusTest` isolation. |

---

## Key Types (`casehub-worker-api`)

| Type | Kind | Purpose |
|------|------|---------|
| `Worker` | record | Named automated task with `capabilityNames` (`Set<String>`), function, execution policy, description. Builder: `capabilityName(String)` (single), `capabilityNames(String...)` (multiple), `noFunction()` (sets `WorkerFunction.NONE`), `<T>fn()` (typed builder entry point returning `TypedFunctionBuilder<T>`) |
| `Capability` | record | Named capability tag with input/output schema — used for routing and validation. Fields: `name`, `inputSchema` (JSON Schema string), `outputSchema` (JSON Schema string), `description` (optional). Schema validation enforced by `DefaultWorkerExecutor`. |
| `WorkerFunction<T>` | interface (generic) | Parameterised by input type `T`. `inputType()` returns `Class<T>`. Inner `Sync<T>(Class<T> inputType, Function<T, WorkerResult> fn)` record for typed execution. `None` record implements `WorkerFunction<Void>`. Static `NONE` constant. |
| `TypedFunctionBuilder<T>` | class | Builder helper for type-safe function binding via varargs type-token trick: `builder.<MyPojo>fn().apply(pojo -> ...)`. Creates `WorkerFunction.Sync` with the runtime type. |
| `WorkerResult` | record | `output` (`Map<String, Object>`) + `outcome` (`WorkerOutcome`). Factory methods: `of(output)`, `of(output, PlannedAction)`, plus `declined`, `failed`, `expired` — each with a partial-output overload (`reason, partialOutput`) for returning intermediate results on non-success. |
| `WorkerOutcome` | sealed interface | `Success(PlannedAction)`, `Declined(String reason)`, `Failed(String reason)`, `Expired(String reason)` |
| `PlannedAction` | record | Structured follow-on action — `description`, `actionType`, `parameters` (Map, defaults to empty). Returned via `WorkerOutcome.Success(PlannedAction)` |

---

## Execution Model (`casehub-worker` runtime)

`WorkerExecutor` interface: `WorkerResult execute(Worker worker, Capability capability, Object input)` — third parameter is `Object` (not `Map`), supporting typed POJO inputs via `WorkerFunction<T>`.

`DefaultWorkerExecutor` (`@ApplicationScoped`) performs, in order:
1. Null check on capability
2. Capability membership check: `worker.capabilityNames().contains(capability.name())`
3. Sync-only check: only `WorkerFunction.Sync` supported
4. Input type check: `sync.inputType().isInstance(input)` — rejects mismatched types
5. Schema parsing: `schemaValidator.ensureSchemaParsed()` on both input and output schemas (fail-fast on malformed schemas)
6. OTel span: `worker.execute` with `worker.name` and `worker.capability` attributes
7. Input schema validation — if invalid, returns `WorkerResult.failed(error)` without calling the function
8. Function execution via `PolicyEnforcer.execute()` (retries, timeout per `ExecutionPolicy`)
9. Output schema validation (on `Success` only) — **warn-only**: logs but returns success
10. `TimeoutPolicyException` maps to `WorkerResult.expired()`; other exceptions map to `WorkerResult.failed()`

**`SchemaValidator`** (`@ApplicationScoped`) — uses `com.networknt.json-schema-validator` with JSON Schema 2020-12. Caches parsed schemas in `ConcurrentHashMap`. Empty schema `"{}"` treated as skip-validation. Validates by converting input/output to `JsonNode` via Jackson.

---

## Dependency Rules

```
casehub-worker-api  →  casehub-platform-api (ExecutionPolicy only — pure Java, no Quarkus)
casehub-worker      →  casehub-worker-api, casehub-platform-governance, quarkus-arc, opentelemetry-api, json-schema-validator
casehub-worker-testing → casehub-worker-api
```

**Add to consumers:**
```xml
<!-- Compile dep -->
<dependency>
  <groupId>io.casehub</groupId>
  <artifactId>casehub-worker-api</artifactId>
</dependency>

<!-- Test scope -->
<dependency>
  <groupId>io.casehub</groupId>
  <artifactId>casehub-worker-testing</artifactId>
  <scope>test</scope>
</dependency>
```

Version managed by `casehub-parent` BOM (`version.io.casehub.worker`).

---

## Consumed By

| Repo | Module | What it uses |
|------|--------|-------------|
| `casehub-engine` | `runtime` | `Worker`, `Capability`, `WorkerFunction` — execution path (engine#543) |
| `casehub-desiredstate` | `runtime` | `Worker`, `Capability` — node provisioning in desiredstate graph (desiredstate#41) |

---

## Structural Notes

- `api/` depends only on `casehub-platform-api` (for `ExecutionPolicy`) — no Quarkus, no JPA, safe in any Java module
- `WorkerFunction<T>` implementations live in consuming repos (`AgentWorkerFunction`, `FlowWorkerFunction` in `casehub-engine-api`)
- `MockWorkerExecutor` is `@DefaultBean @ApplicationScoped` — displaced by the runtime `DefaultWorkerExecutor` when present. Mirrors validation guards (capability membership, Sync-only, input type) but skips schema validation and policy enforcement.
- Governance types (`ExecutionPolicy`, `RetryPolicy`, `BackoffStrategy`) live in `casehub-platform-governance`, not here
- Input schema validation is **blocking** (function never called if input is invalid); output schema validation is **warn-only** (logs but returns success) — intentional asymmetry to prevent bad data from entering while not breaking workers with evolving output schemas
