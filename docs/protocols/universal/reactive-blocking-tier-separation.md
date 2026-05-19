---
id: PP-20260519-f2e160
title: "Service beans must not carry dependencies on capabilities that are optional in consuming deployments"
type: principle
scope: universal
applies_to: "Any extension library or framework module that exposes service beans to consumers with heterogeneous deployment contexts"
severity: important
refs: []
violation_hint: "A service bean injects a dependency that is unavailable in a subset of valid deployments, causing build or startup failure in those deployments"
created: 2026-05-19
---

When an extension library provides service beans that must work across deployment contexts
with different capability sets (e.g. blocking-only vs reactive-enabled, JDBC vs MongoDB,
offline vs networked), each service bean must declare dependencies only on capabilities
that are present in every valid deployment of that bean. Where a capability is optional,
the service that depends on it is itself optional — either absent from deployments that
lack the capability, or explicitly gated so that it is never instantiated there. The
blocking and reactive tiers of a service are separate beans: the blocking tier has no
reactive dependencies; the reactive tier has no blocking workarounds. Neither tier
degrades silently into the other.
