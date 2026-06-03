---
id: PP-20260603-ba301d
title: "casehub-eidos: validate new capabilities with in-memory PoC before JPA infrastructure"
type: rule
scope: repo
applies_to: "casehub-eidos — any new persistence-backed capability (graph, registry extension, state store)"
severity: important
refs:
  - repos/casehub-eidos.md
violation_hint: "JPA entities and Flyway migrations written before the API design has been exercised through a pure in-memory scenario test"
created: 2026-06-03
---

Before implementing JPA entities, Flyway migrations, and CDI beans for a new casehub-eidos capability,
validate the concept with a pure in-memory POJO and plain JUnit 5 tests in `examples/agent-scenarios/`.
The PoC must exercise: the candidate API directly, the primary query semantics under realistic data, and
a comparison scenario that proves any extension point (e.g. `TaskSemanticEnricher`) adds discriminating
value. The PoC gate catches API design errors and query logic bugs before they are baked into the schema.
Only after all PoC tests pass should JPA entities, migrations, and Quarkus CDI wiring be written.
This gate is enforced by implementation planning — Phase 4a must complete before Phase 4b begins.
