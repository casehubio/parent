# casehub-engine — Platform Deep Dive

**GitHub:** [casehubio/engine](https://github.com/casehubio/engine) (local: `casehub-engine`)  
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

> **Note:** The original `casehub` repo (local: `~/claude/casehub-poc`) is retiring. Do not add features there. All active development is in `casehub-engine`.

---

## Purpose

Hybrid choreography+orchestration coordination engine for multi-agent work. Implements the Blackboard Architecture with CMMN terminology. Coordinates workers (AI agents, humans) via case definitions, binding rules, and optional synchronous orchestration.

---

## Module Structure

| Module | Type | Purpose |
|---|---|---|
| `engine-model` | Pure POJOs (no Quarkus) | Core domain model — case definitions, running case state, and persistence SPIs |
| `engine` | Quarkus module | Choreography handlers, orchestration, worker scheduling, Quartz integration |
| `api` | SPI definitions | 8 worker provisioner SPIs (4 blocking + 4 reactive) |
| `casehub-blackboard` | Optional module | CMMN/Blackboard orchestration layer |
| `casehub-ledger` | Optional module | Tamper-evident case lifecycle ledger; extends the ledger entry model |
| `casehub-work-adapter` | Module | Bridges work item lifecycle events to plan item transitions |
| `casehub-persistence-hibernate` | Module | JPA/Panache persistence implementations |

---

## Key Abstractions

### Core Model (`engine-model`)

The core model covers: case definitions (capabilities, workers, bindings, goals, milestones in YAML DSL), running case instances with lifecycle status, an append-only internal audit trail for restart recovery, and CDI lifecycle events fired on case status transitions.

See `docs/DESIGN.md` for class structure and status enumeration.

### Engine Handlers

The engine contains CDI handlers for the two execution paths: choreography (evaluates bindings on context change) and orchestration (suspends case, awaits worker completion, resumes). Worker scheduling runs via Quartz. A restart-durable correlation registry bridges the orchestration path across restarts.

`WorkBroker` (from `casehub-work-core`) is used for worker selection. casehub-engine does NOT depend on the casehub-work runtime.

See `docs/DESIGN.md` for handler responsibilities and the choreography vs orchestration decision boundary.

### Worker Provisioner SPIs (`api/spi/`)

These are operational contracts — environment-specific implementations belong in the deploying app (Claudony):

| SPI | Purpose |
|---|---|
| `WorkerProvisioner` / `ReactiveWorkerProvisioner` | Provision and terminate workers |
| `WorkerStatusListener` / `ReactiveWorkerStatusListener` | Worker lifecycle callbacks (started, completed, stalled) |
| `CaseChannelProvider` / `ReactiveCaseChannelProvider` | Open/close/post to backend-agnostic channels |
| `WorkerContextProvider` / `ReactiveWorkerContextProvider` | Build worker startup context from ledger lineage |

Each SPI ships with a no-op default implementation that yields automatically to any consumer-supplied implementation via CDI priority rules.

See `docs/DESIGN.md` for default implementations and configuration.

### Ledger Integration (`casehub-ledger`)

An optional module that records case lifecycle events as tamper-evident ledger entries, extending `casehub-ledger`'s entry model. Not yet merged to main.

See `docs/DESIGN.md` for the ledger entry structure.

### Work Adapter (`casehub-work-adapter`)

Two-way bridge between casehub-work and CaseHub plan items. Inbound: translates WorkItem lifecycle events into PlanItem transitions and fires context-change events. Outbound: handles human task scheduling — creates WorkItems directly or from templates, with atomicity guarantees between WorkItem creation and PlanItem state.

See `docs/DESIGN.md` for the adapter contracts and atomicity guarantees (engine#273).

---

## Depends On

| Repo | How |
|---|---|
| `casehub-work-core` | `WorkBroker` and selection strategies — NOT the casehub-work runtime |
| `casehub-ledger` | Optional, via `casehub-ledger` module |

## Depended On By

| Repo | How |
|---|---|
| `claudony` | Implements the 4 worker provisioner SPIs in `claudony-casehub` module |

---

## What This Repo Explicitly Does NOT Do

- Manage human task inboxes (that is casehub-work)
- Handle agent-to-agent messaging protocols (that is casehub-qhorus)
- Provide a terminal/session UI (that is claudony)
- Implement worker provisioner SPIs — only defines the contracts
- Include Flyway migrations (Hibernate `drop-and-create` for now — no prod instances)

---

## Schema Management

No Flyway — Hibernate drop-and-create only. No Quartz JDBC store — RAM store only. See `docs/DESIGN.md` for configuration details.

---

## Two Audit Mechanisms (Known Gap)

- **EventLog** — engine-internal, append-only, used for restart recovery
- **CaseLedgerEntry** — external, tamper-evident, written on case lifecycle events

These are complementary, not redundant. A lifecycle transition that doesn't fire a case lifecycle event won't be captured in the external ledger.

---

## Current State

- Active development. Core choreography and orchestration done.
- WAITING state durability (restart-safe) done.
- `casehub-ledger` integration done but unmerged.
- Worker↔Session↔Channel triple correlation (for Claudony dashboard) not yet stored.
- Human worker integration, escalation rules, lineage-driven planning still ahead.

---

## Design Documents

- [docs/DESIGN.md](https://raw.githubusercontent.com/casehubio/engine/main/docs/DESIGN.md) — choreography+orchestration models, worker SPI contracts, ledger integration
- [adr/INDEX.md](https://raw.githubusercontent.com/casehubio/engine/main/adr/INDEX.md) — architectural decision records (ADR-0003 naming, ADR-0004 claim SLA, ADR-0005 provisioner SPI placement, ADR-0006 worker registration as normative act)
