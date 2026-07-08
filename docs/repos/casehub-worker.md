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
| `api/` | `casehub-worker-api` | Pure-Java value types + `WorkerFunction` interface. No Quarkus, no JPA. |
| `runtime/` | `casehub-worker` | `DefaultWorkerExecutor` — capability-aware execution: `execute(Worker, Capability, Map)` with validation guards (null check, capability membership) and OTel `worker.capability` span attribute. |
| `testing/` | `casehub-worker-testing` | `MockWorkerExecutor` (`@DefaultBean @ApplicationScoped`), `TestWorkerBuilder` (`syncWithCapability()` convenience, `WorkerWithCapability` record) — `@QuarkusTest` isolation. |

---

## Key Types (`casehub-worker-api`)

| Type | Kind | Purpose |
|------|------|---------|
| `Worker` | record | Named automated task with function, capabilities, execution policy |
| `Capability` | record | Named capability tag with input/output schema — used for routing and validation. Fields: `name`, `inputSchema` (JSON Schema string), `outputSchema` (JSON Schema string), `description` (optional). Schema validation enforced by `DefaultWorkerExecutor` (worker#7). |
| `WorkerFunction` | interface | Strategy interface — implement to define worker behaviour |
| `WorkerResult` | record | Output of a worker execution — success or failure with output map |
| `WorkerOutcome` | sealed interface | `Success(PlannedAction)`, `Declined(String reason)`, `Failed(String reason)`, `Expired(String reason)` |
| `PlannedAction` | record | Structured follow-on action — returned via `WorkerOutcome.Success(PlannedAction)` |

---

## Dependency Rules

```
casehub-worker-api  →  (none — pure Java)
casehub-worker      →  casehub-worker-api, casehub-platform-api, casehub-platform-governance
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

- `api/` has zero framework dependencies — safe to use in any Java module without container constraints
- `WorkerFunction` implementations live in consuming repos (`AgentWorkerFunction`, `FlowWorkerFunction` in `casehub-engine-api`)
- `MockWorkerExecutor` is `@DefaultBean @ApplicationScoped` — displaced by the runtime `DefaultWorkerExecutor` when present
- Governance types (`ExecutionPolicy`, `RetryPolicy`, `BackoffStrategy`) live in `casehub-platform-governance`, not here
