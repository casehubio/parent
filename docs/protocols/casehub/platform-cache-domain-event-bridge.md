---
id: PP-20260601-f7c2b2
title: "Platform beans that cannot observe domain events get a thin domain-side bridge observer"
type: rule
scope: platform
applies_to: "Any casehub platform bean with a TTL cache that must be invalidated by a domain event"
severity: important
refs:
  - ../../repos/casehub-identity.md
  - ../../PLATFORM.md
violation_hint: "Platform bean observes a domain event directly — creates a backwards dependency from platform to the domain module"
created: 2026-06-01
---

When a platform bean (e.g. `ScimActorDIDProvider` in `casehub-platform-identity`) holds a
TTL cache that must be invalidated on a domain event (e.g. `AgentKeyRotatedEvent` in
`casehub-ledger`), the platform bean must NOT observe the event directly — that would
create a backwards dependency from platform to the domain module. Instead, the domain
module provides a thin `@ApplicationScoped` observer bean (e.g. `IdentityCacheInvalidator`)
that observes the domain event and calls the platform bean's public invalidation API
(`invalidate(key)` or `invalidateAll()`). The event stays in its owning domain; the domain
provides the bridge; the platform stays dependency-free.
