---
id: PP-20260603-9918e6
title: "casehub-eidos SPI methods scoped to an agent must include tenancyId"
type: rule
scope: repo
applies_to: "casehub-eidos-api SPI interfaces; any new SPI method that identifies or queries a specific agent"
severity: critical
refs:
  - repos/casehub-eidos.md
violation_hint: "A SPI method that accepts agentId but not tenancyId — e.g. query(String agentId) instead of query(String agentId, String tenancyId)"
created: 2026-06-03
---

`agentId` is not globally unique in casehub-eidos: the same agent persona can exist in multiple tenancies.
Any SPI method that identifies or scopes to a specific agent must accept both `agentId` and `tenancyId`
as parameters. A JPA store that implements such a SPI cannot correctly scope its queries without tenancyId —
the natural key for all agent records is the composite `(agent_id, tenancy_id)`. This rule applies to
every method that reads, writes, or deletes agent-specific state: registry lookups, state store operations,
graph queries, and any future agent-scoped SPI. Violation pattern: `void record(String agentId, ...)` or
`Optional<T> query(String agentId)` — both missing the tenancy dimension that makes the lookup correct.
