# casehub-fsitrading — Platform Deep Dive

**GitHub:** [casehubio/fsitrading](https://github.com/casehubio/fsitrading)
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Financial Services Trading application. Multi-agent trading automation, overnight bot management, market situation detection and response, and regulatory compliance for algorithmic trading (MiFID II, Dodd-Frank, MAR).

Exercises every CaseHub primitive: trust-weighted strategy selection via Bayesian Beta scoring, CBR from past market events for situation detection, oversight gates for high-risk trade authorization, commitment lifecycle for response SLA enforcement, audit ledger for tamper-evident regulatory compliance, stream modules for market data ingestion via CloudEvent adapters.

---

## Module Structure

| Module | Type | Purpose |
|---|---|---|
| `casehub-fsitrading-api` | Pure-Java SPI (no Quarkus) | Domain model, SPI interfaces, capability tags |
| `casehub-fsitrading-app` | Quarkus application | REST resources, JPA entities, foundation wiring, case plan models |

---

## Current State

Scaffold — Maven structure, documentation, workspace ready. No implementation yet.

Domain research and design phase is the immediate next step.

---

## Design Documents

- CLAUDE.md — project conventions and design philosophy
- HANDOFF.md — session handover (workspace)
