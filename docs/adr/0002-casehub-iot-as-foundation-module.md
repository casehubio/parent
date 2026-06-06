---
id: ADR-0002
title: "casehub-iot as a foundation module, peer to casehub-connectors"
status: accepted
date: 2026-06-05
deciders: mdproctor
---

## Context

Home automation device integration (Home Assistant, OpenHAB) was needed for casehub-life's household management domain. The question was whether the device abstraction layer — `DeviceProvider` SPI, `DeviceEntity` hierarchy, `StateChangeEvent`, `DeviceCommand` — should live inside casehub-life or as a standalone module.

## Decision

Extract device abstraction into a new foundation repo, `casehub-iot`, peer to `casehub-connectors`. Application repos (casehub-life initially) consume it as a dependency.

## Rationale

The same HA/OpenHAB device layer could power casehub-life, a future property management application, elder care monitoring, and industrial IoT scenarios. Application-scoping would require extraction later under pressure. Foundation-first is consistent with how `casehub-connectors` handles messaging infrastructure — that module is similarly cross-cutting and reusable across application repos.

`casehub-iot-api` is a public API surface — community automations written against it will run identically on any platform. This requires semver discipline from day one, which is only practical if the module is independent of any single application's release cycle.

## Consequences

- `casehub-iot` is a new peer repo in the build order, publishing before `casehub-life`
- `casehub-iot-api` carries semver discipline — no breaking changes without a major version bump
- Any future application wanting device integration adds `casehub-iot-homeassistant` or `casehub-iot-openhab` as a dependency without duplicating provider code
