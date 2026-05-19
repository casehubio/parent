# casehub-work — Platform Deep Dive

**GitHub:** [casehubio/work](https://github.com/casehubio/work)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Human task lifecycle management extension. Provides a human task inbox (WorkItem) with status lifecycle, SLA, delegation, escalation, spawn, and audit trail. Usable standalone or integrated with CaseHub and Qhorus.

A `WorkItem` is deliberately NOT called `Task` — CNCF Serverless Workflow and CaseHub both have `Task` concepts with different semantics.

---

## Module Structure

| Module | Type | Purpose |
|---|---|---|
| `casehub-work-api` | Pure-Java SPI (no Quarkus) | All SPIs: worker selection, registry, workload provision, escalation, spawn, skill profiling, notification channel |
| `casehub-work-core` | Jandex library (no JPA) | `WorkBroker` and built-in selection strategies — used directly by casehub-engine |
| `runtime` | Full Quarkus extension | WorkItem entity, services, REST API, filter engine |
| `casehub-work-ledger` | Optional module | Attaches casehub-ledger for WorkItem ledger entries |
| `casehub-work-queues` | Optional module | Label-based queue views |
| `casehub-work-ai` | Optional module | AI-backed worker selection strategy and low-confidence filter routing |
| `casehub-work-notifications` | Optional module | Slack/Teams/webhook outbound notifications |
| `casehub-work-reports` | Optional module | SLA compliance reporting |
| `work-flow` | Optional module | Quarkus-Flow CDI bridge |
| `casehub-work-testing` | Test utilities | In-memory stores for WorkItem and audit entries |

---

## Key Abstractions

### WorkItem Entity

10-status lifecycle from creation through terminal states (pending, assigned, in-progress, completed, cancelled, expired, delegated, rejected, on-hold, claim-expired).

See `docs/DESIGN.md` for status enumeration and field model.

### Core Services

Services cover: WorkItem lifecycle management (create, claim, complete, delegate, expire, cancel) with schema validation against templates; template CRUD and instantiation with payload override support; worker assignment via pluggable selection strategies; conflict-of-interest exclusion policy; M-of-N parallel group completion coordination; child spawning with idempotency; label-based filter routing; and SLA compliance reporting.

See `docs/DESIGN.md` for service class structure and the M-of-N coordination model.

### REST API

REST endpoints cover: WorkItem inbox and creation, lifecycle transitions (start, complete, cancel, delegate), audit history, child instance queries with group progress, SLA compliance reports, dynamic filter rules, and child WorkItem spawning.

See `docs/DESIGN.md` for the full endpoint inventory.

### CDI Events

A lifecycle event fires on every status transition, carrying the transition details and an optional named outcome (the named completion classification from the WorkItem's template). The outcome field lets downstream adapters switch on completion type without parsing the resolution payload.

See `docs/DESIGN.md` for event payload shape.

---

## Depends On

- `casehub-ledger` — optional only, via `casehub-work-ledger` module. Core has zero casehubio deps.

## Depended On By

| Repo | How |
|---|---|
| `casehub-engine` | `casehub-work-core` only — `WorkBroker` for worker selection. NOT the full runtime. |
| `claudony` | Future, via `casehub-work-casehub` adapter (currently blocked on CaseHub stability) |

---

## What This Repo Explicitly Does NOT Do

- Orchestrate — it fires events and provides primitives. It does not decide what completing a WorkItem means.
- **Heterogeneous plan-item completion** — whether named plan items A, B, and C have all completed to advance a Stage; that is CaseHub (see LAYERING.md). Homogeneous M-of-N group completion IS casehub-work (multi-instance coordinator).
- Interpret `callerRef` — stored and echoed opaquely.
- Provision or manage AI agents (that is CaseHub/Claudony).
- Know when to spawn child WorkItems (callers drive spawn via `SpawnPort`).

---

## The Core/Runtime Split (Critical for casehub-engine)

`casehub-work-core` is a Jandex library (not a Quarkus extension) containing only `WorkBroker` and selection strategies. casehub-engine depends on this module — it gets worker routing without pulling in WorkItem entities, Flyway migrations, REST resources, or datasource requirements.

The `WorkBroker` is generic: it routes any work unit, not just WorkItems.

---

## Notification Concern

`casehub-work-notifications` currently ships Slack/Teams/webhook directly. This overlaps with `casehub-connectors`. Future direction: delegate to `casehub-connectors` connector SPI rather than maintaining a parallel implementation.

---

## Current State

- 637+ tests passing in runtime module; native image validated at 0.084s startup
- All major epics complete: Business-Hours Deadlines (#101), SLA Compliance Reporting (#104), Multi-Instance Tasks (#106)
- Pending: `casehub-work-qhorus` adapter (MCP tools for agent-driven approval flows)

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/work/main/docs/DESIGN.md) — implementation-tracking design doc
- [docs/architecture/LAYERING.md](https://raw.githubusercontent.com/casehubio/work/main/docs/architecture/LAYERING.md) — definitive boundary statement between casehub-work and CaseHub
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/work/main/adr/INDEX.md) — architectural decision records
