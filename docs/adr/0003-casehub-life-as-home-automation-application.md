---
id: ADR-0003
title: "casehub-life is the application layer for home automation — no separate casehub-home repo"
status: accepted
date: 2026-06-05
deciders: mdproctor
---

## Context

With `casehub-iot` established as the foundation, the application layer — home automation case types, trigger rules, community automations, device command authorization — needed a home. A new `casehub-home` repo was considered.

## Decision

Home automation lives in `casehub-life`. No `casehub-home` repo is created.

## Rationale

Home automation IS household management. `LifeDomain.HOUSEHOLD` already exists in casehub-life. The compelling value propositions — "your home and your life are one system" (HolidayTrip case triggers HolidayHomeMode case), morning routine as life coordination, security escalation through household permission topology — only work elegantly when device-driven cases and life cases live in the same application. Cross-app event bridging would be required otherwise, adding complexity with no benefit.

casehub-life's tutorial structure (Layers 1–8) naturally extends to Layer 9 (`casehub-iot` integration) without a new repo. The existing OpenClaw integration (Layer 7) applies directly to home automation AI agents — same `WorkerProvisioner` pattern, same Qhorus channels, same trust scoring.

## Consequences

- casehub-life gains a new dependency: `casehub-iot-api` + one platform provider
- Layer 9 sub-layers (9a–9e) added to the casehub-life tutorial sequence
- Community automations deploy into casehub-life as Quarkus extensions
- No `casehub-home` repo — explicitly rejected to avoid splitting one coherent domain
