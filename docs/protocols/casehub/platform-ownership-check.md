---
id: PP-20260531-dd7062
title: "Platform ownership check — pause before implementing infrastructure in a domain repo"
type: rule
scope: platform
applies_to: "Any casehubio domain repo implementing a new class or module"
severity: warning
refs:
  - ../../PLATFORM.md
created: 2026-05-31
---

Before implementing a new class or module in a domain repo, run this two-part check.

## Structural test

**Does the class API surface reference any of this repo's domain entities** (`LedgerEntry`, `WorkItem`, `Channel`, etc.)?

- **Yes** → domain logic. No check needed. Implement here.
- **No** → proceed to capability filter.

## Capability filter

**Does it implement a named capability** — a standard protocol (such as SCIM, DID, OAuth, JWT VC), an SPI, or a service with a meaningful contract?

- **Yes** → trigger HITL (see below).
- **No** → trivial utility. Implement here.

## HITL prompt

When both filters pass, stop and ask:

> "This class has no domain entity types in its API — it may be platform infrastructure. Should this live in platform before implementing it here?"

Wait for a decision. Do not implement until the placement question is resolved.

## Rationale

A repo owns infrastructure only if it is the definitive provider of that capability. If a repo uses a capability solely to serve its own domain concerns, it is a consumer — the infrastructure belongs in platform regardless of where it was first implemented. Development order does not determine ownership.

## Does not trigger for

- Domain entities, repositories, enrichers, and services whose API references domain types
- `@DefaultBean` no-op stubs that exist solely to satisfy a local SPI
- Trivial adapters wiring domain types to infrastructure
