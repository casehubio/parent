---
id: PP-20260520-5d0b91
title: "HITL runtime requires casehub-engine-work-adapter and casehub-engine-blackboard — explicit opt-in"
type: rule
scope: platform
applies_to: "all CaseHub harnesses (devtown, aml, clinical) that use humanTask YAML bindings"
severity: important
refs:
  - PP-20260520-b2a932 (yaml-humantask-binding-type.md)
  - casehub-engine-work-adapter pom.xml
  - PP-20260514-d69243 (work-adapter-test-subcase-group-repository.md)
violation_hint: "Missing dep: humanTask binding fires HumanTaskScheduleEvent but HumanTaskScheduleHandler is not on the classpath — WorkItem is never created. Missing blackboard: BlackboardRegistry lookup fails silently."
created: 2026-05-20
---

`casehub-engine-work-adapter` and `casehub-engine-blackboard` are not bundled in
`casehub-engine`. Any harness using `humanTask:` YAML bindings must add
`casehub-engine-work-adapter` (which brings `casehub-engine-blackboard` transitively)
to its production `pom.xml`. Both modules also require `quarkus.index-dependency`
entries in test `application.properties` so their CDI beans are discovered. Additionally,
`MemorySubCaseGroupRepository` must be activated via `quarkus.arc.selected-alternatives`
(without `%test.` prefix — this is a build-time property). See PP-20260514-d69243.
