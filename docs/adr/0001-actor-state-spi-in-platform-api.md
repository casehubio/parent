# 0001 — Use-case-specific SPI placement in casehub-platform-api

Date: 2026-06-02
Status: Accepted

## Context and Problem Statement

The actor state view (`GET /actors/{actorId}/state`, parent#56) requires an `ActorStateContributor` SPI — an interface implemented by 4+ modules (ledger, work, qhorus, engine) and collected by an aggregator. No single domain api module can host it because all four modules are peers that must not depend on each other. The question is whether to place this SPI in `casehub-platform-api` or invent another home for it.

## Decision Drivers

* `casehub-platform-api` is already on the classpath of all four contributing modules (a zero-dep pure-Java library)
* The SPI uses only stdlib types (UUID, Instant, String, double) — no domain types cross the boundary
* Adding a fifth module (e.g. `casehub-engine-actor-api`) would create a new cross-repo dependency just to hold two interfaces

## Considered Options

* **Option A** — Place `ActorStateContributor` + `ActorStateAccumulator` in `casehub-platform-api`
* **Option B** — Place them in `casehub-engine-common` (internal engine SPI module)
* **Option C** — Place them in a new `casehub-actor-api` module

## Decision Outcome

Chosen option: **Option A**, because both interfaces use zero domain types and are needed by ≥4 peer repos that already import `casehub-platform-api`. This satisfies the platform-api scope rule verbatim.

### Positive Consequences

* No new module, no new cross-repo dependency
* Any future contributor (e.g. a new domain module) adds a class and is discovered by CDI — zero aggregator changes required
* Migration path is clear: contributor implementations can move from `casehub-engine-actor-state` into their home modules once the platform matures, with no interface changes required

### Negative Consequences / Tradeoffs

* This is the first *behaviour* SPI in `casehub-platform-api` (previous SPIs — `CurrentPrincipal`, `PreferenceProvider` — are infrastructure primitives). Sets a precedent that must be applied carefully: only SPIs whose implementations span ≥4 peer repos and use zero domain types belong here.

## Pros and Cons of the Options

### Option A — casehub-platform-api

* ✅ Zero new deps — all contributors already import it
* ✅ CDI `@Any Instance<ActorStateContributor>` works out of the box
* ✅ stdlib types only — interface never forces domain imports on consumers
* ❌ Extends platform-api scope beyond infrastructure primitives (first use-case SPI)

### Option B — casehub-engine-common

* ✅ Lives with other engine SPIs (WorkerExecutionManager, etc.)
* ❌ work, qhorus, ledger would need a new dep on casehub-engine-common — inverts the natural dependency direction (engine integrates work/qhorus, not vice versa)

### Option C — New casehub-actor-api module

* ✅ Cleanest isolation
* ❌ New cross-repo dep for all 4 contributors plus the aggregator
* ❌ Overhead of a new published artifact for two interfaces

## Links

* [parent#56](https://github.com/casehubio/parent/issues/56) — actor state view implementation
* [docs/protocols/casehub/platform-api-scope.md](../protocols/casehub/platform-api-scope.md) — scope rule referenced
