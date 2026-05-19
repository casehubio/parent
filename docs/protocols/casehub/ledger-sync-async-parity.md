---
id: PP-20260517-15bf75
title: "RETIRED — superseded by PP-20260519-f2e160 and PP-20260519-39a9a5"
type: principle
scope: platform
applies_to: "Retired 2026-05-19"
severity: guidance
refs:
  - docs/protocols/universal/reactive-blocking-tier-separation.md
  - docs/protocols/casehub/reactive-service-build-gating.md
violation_hint: "n/a — retired"
created: 2026-05-17
---

**RETIRED 2026-05-19.** The narrow ledger-specific framing was generalised into two
replacement protocols:

- **PP-20260519-f2e160** (`universal/reactive-blocking-tier-separation.md`) — the universal
  principle: service beans must not carry dependencies on capabilities optional in consuming
  deployments; blocking and reactive tiers are separate beans.

- **PP-20260519-39a9a5** (`casehub/reactive-service-build-gating.md`) — the Quarkus/casehub
  mechanism: `Reactive*Service` naming, `@IfBuildProperty` gating,
  `casehub.<module>.reactive.enabled` property, `@DefaultBean` test shims.

The parity requirement (both variants must exist when a capability is meaningful in both
deployment contexts) is preserved in the replacement protocols. Co-location on the same
service class is no longer required — each tier lives in its own bean.
