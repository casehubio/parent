# casehub-soc — Platform Deep Dive

**GitHub:** [casehubio/soc](https://github.com/casehubio/soc)
**Platform doc:** [PLATFORM.md](https://raw.githubusercontent.com/casehubio/parent/main/docs/PLATFORM.md)

---

## Purpose

Security Operations Center application. Multi-agent cyber incident response with trust-weighted triage, CBR-based incident correlation, normative accountability for containment actions, and compliance evidence for SOC2, DORA, and NIS2.

Exercises every CaseHub primitive: qhorus channels map to the 3-tier SOC model (core ops / intelligence / orchestration), trust scoring evolves as agents prove accuracy, CBR from past incidents feeds triage, oversight gates authorize irreversible containment, commitment lifecycle enforces response SLA, audit ledger provides tamper-evident compliance trail.

---

## Module Structure

| Module | Type | Purpose |
|---|---|---|
| `casehub-soc-api` | Pure-Java SPI (no Quarkus) | Domain model, SPI interfaces, capability tags |
| `casehub-soc-app` | Quarkus application | REST resources, JPA entities, foundation wiring, case plan models |

---

## Current State

Scaffold — Maven structure, documentation, workspace ready. No implementation yet.

Domain research and design phase is the immediate next step.

---

## Design Documents

- CLAUDE.md — project conventions and design philosophy
- HANDOFF.md — session handover (workspace)
