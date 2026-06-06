---
id: ADR-0004
title: "casehub-iot supports three deployment modes: local, bridge, and hybrid"
status: accepted
date: 2026-06-05
deciders: mdproctor
---

## Context

Home automation users have strong and conflicting preferences: the HA/OpenHAB community is strongly local-first (privacy, reliability, distrust of cloud after multiple platform shutdowns), while property management use cases benefit from centralised cloud SaaS managing many sites. A single deployment model cannot serve both.

## Decision

`casehub-iot` supports three deployment modes, all using the same automation code:

1. **Local** — everything on-premises; no internet dependency
2. **Bridge** — lightweight `iot-bridge` process runs locally, connects to HA/OpenHAB, forwards `StateChangeEvent`s to cloud CaseHub, relays `DeviceCommand`s back
3. **Hybrid** — latency-sensitive Drools rules run at edge (inside the bridge); orchestration, optimisation, HITL, ledger, and memory run in cloud

## Rationale

Research confirmed this three-tier architecture is absent from all shipping home automation products. The market has bifurcated into local-only (HA, Hubitat, OpenHAB, Crestron) and cloud-primary (SmartThings, Google Home, Alexa), with nothing occupying the middle ground. No existing product acts as an orchestration layer above existing hubs, intelligently splits execution by latency sensitivity, or offers all three modes from one codebase.

`StateChangeEvent` is already a clean serializable type — it is the natural wire protocol between bridge and cloud in hybrid mode. Community automations written against `casehub-iot-api` run identically in all three modes.

The property management SaaS wedge (Mode 2) drives commercial viability while Mode 1 drives open-source community adoption. Mode 3 satisfies technically sophisticated users who want cloud intelligence without sacrificing local responsiveness.

## Consequences

- `iot-bridge` module added to `casehub-iot` repo — lightweight Quarkus app
- Bridge config: `casehub.iot.bridge.cloud-endpoint`, `tenant-id`, `token`, `local-automations`, `cloud-automations`
- `StateChangeEvent` must remain serializable — no non-serializable fields
- Offline resilience in hybrid mode is deferred to bridge implementation detail
