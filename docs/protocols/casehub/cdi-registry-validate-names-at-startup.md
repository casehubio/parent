---
id: PP-20260603-fa1bf0
title: "CDI self-registering strategy registries must validate member identity at construction time"
type: rule
scope: platform
applies_to: "Any casehubio CDI bean that collects @Any Instance<T> at startup and looks up members by a string name returned from a method (e.g. backendId(), projectionName(), agentId())"
severity: important
refs:
  - ../../repos/casehub-qhorus.md
  - agent-descriptor-compact-constructor-validation.md
violation_hint: "Registry checks for null/blank/duplicate names inside get(name) at call time rather than at construction — startup completes silently, the error surfaces as a confusing IAE or NPE at the first tool call rather than at deployment."
created: 2026-06-03
---

When a CDI bean collects `@Any Instance<T>` at startup and indexes members by a string identity (e.g. `backendId()`, `projectionName()`), it must validate member identity during construction (`@PostConstruct` or an injected-constructor body), not lazily at lookup time. Specifically: throw `IllegalStateException` if any member returns null or blank from its identity method, and throw `IllegalStateException` if two members return the same identity string. Both checks must run before the registry is considered usable. This guarantees that every misconfiguration surfaces at deployment time with a clear error naming the offending bean, not at first use with a confusing lookup failure. Consumers expecting a named member to exist can trust the registry is internally consistent without null-guarding at every call site. Examples: `ProjectionRegistry` (validates `projectionName()` null/blank/duplicate), `ChannelGateway` backend registration (validates `backendId()` uniqueness). See the companion `agent-descriptor-compact-constructor-validation` protocol for the analogous rule applied to record compact constructors rather than CDI registries.
