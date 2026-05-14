---
id: PP-20260514-d69243
title: "work-adapter @QuarkusTest requires MemorySubCaseGroupRepository in selected-alternatives"
type: rule
scope: repo
applies_to: "casehub-engine-work-adapter test module (src/test/resources/application.properties)"
severity: important
refs:
  - work-adapter/src/test/resources/application.properties
violation_hint: "@QuarkusTest fails at boot: 'Unsatisfied dependency for type io.casehub.engine.spi.SubCaseGroupRepository'"
created: 2026-05-14
---

The `casehub-engine-work-adapter` module's `@QuarkusTest` suite uses `casehub-persistence-memory`
for in-memory SPI implementations. `SubCaseGroupRepository` is an SPI declared in
`casehub-engine-common` and required by CDI validation at boot time — it has no default
implementation. Add `io.casehub.persistence.memory.MemorySubCaseGroupRepository` to
`quarkus.arc.selected-alternatives` in `work-adapter/src/test/resources/application.properties`.
The same rule applies to any engine module that adds `casehub-persistence-memory` as a test
dependency and uses `quarkus.arc.selected-alternatives` for in-memory SPI activation.
